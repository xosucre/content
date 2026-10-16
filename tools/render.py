"""Render one beat-synced edit from a storyboard.

usage: render.py STORYBOARDS.py VIDEO_KEY WORKDIR OUTDIR

Each shot in a storyboard is (clip_spec, flags):
  clip_spec  "p065" or "p065@6.0" (explicit source time) or "p012|p011" (first usable wins)
  flags      P punch-in, p slow push, l slow pull, F flash-in, W whip-in, w whip-out, R speed-ramp
"""
import sys, os, json, math, subprocess, importlib.util, shutil

FPS = 30
CLEAN = os.environ.get('CLEAN') == '1'   # clean cuts only: no flash / whip / punch / ramp
sb_path, key, work, outdir = sys.argv[1:5]
spec = importlib.util.spec_from_file_location('sb', sb_path)
sb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sb)
V = sb.VIDEOS[key]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = '/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad'
MEZZ = S + '/mezz'
lib = json.load(open(S + '/lib.json'))
shots_ref = json.load(open(S + '/ref/an/shots.json'))
os.makedirs(work, exist_ok=True)
os.makedirs(outdir, exist_ok=True)

GRADE = ("eq=contrast=1.12:saturation=1.08,"
         "colorbalance=rs=-0.05:bs=0.08:rm=-0.03:bm=0.05:bh=0.025:rh=-0.01,"
         "curves=all='0/0 0.2/0.14 0.5/0.47 0.85/0.9 1/1',vignette=angle=PI/4.2")
GLOW = ("split[a][b];[b]gblur=sigma=22,curves=all='0/0 0.55/0 1/0.9'[g];"
        "[a][g]blend=all_mode=screen:all_opacity=0.35")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(' '.join(cmd))
        print(r.stderr[-2000:])
        raise SystemExit(1)


def window_score(c, t0, L):
    d = lib[c]
    st = d['step']
    i0, i1 = int(t0 / st), max(int(t0 / st) + 1, int((t0 + L) / st))
    sh = d['sharp'][i0:i1] or [0]
    lu = d['luma'][i0:i1] or [0]
    mo = d['motion'][i0:i1] or [0]
    s = sum(sh) / len(sh)
    l = sum(lu) / len(lu)
    m = sum(mo) / len(mo)
    pen = 1.0
    if l < 6:
        pen *= 0.15
    elif l < 14:
        pen *= 0.6
    if m > 14:
        pen *= 0.4          # whip / shake
    return math.log1p(s) * pen, l


used = {}


def pick(spec_s, L, shot_i):
    """returns clip, t0, mean_luma for a source window of length L seconds."""
    for item in spec_s.split('|'):
        t_fixed = None
        if '@' in item:
            item, t = item.split('@')
            t_fixed = float(t)
        c = item
        dur = lib[c]['dur']
        if dur < L + 0.3:
            continue
        if t_fixed is not None:
            t0 = min(t_fixed, dur - L - 0.15)
            return c, t0, window_score(c, t0, L)[1]
        best = None
        t = 0.25
        while t + L <= dur - 0.2:
            ov = any(not (t + L <= a or t >= b) for a, b in used.get(c, []))
            if not ov:
                sc, l = window_score(c, t, L)
                if best is None or sc > best[0]:
                    best = (sc, t, l)
            t += 0.1
        if best:
            used.setdefault(c, []).append((best[1], best[1] + L))
            return c, best[1], best[2]
    raise SystemExit(f'no window for shot {shot_i}: {spec_s} need {L:.2f}s')


def target_luma(l):
    if l > 64:
        return 64 + 0.35 * (l - 64)
    return l + 0.25 * (64 - l)


def gamma_for(l):
    l = max(l, 4.0)
    t = target_luma(l)
    return max(0.5, min(1.6, math.log(l / 255) / math.log(t / 255)))


def zoom_expr(flags, d):
    if CLEAN:
        return f'(1+0.03*t/{d})' if d >= 0.9 else '1'
    base = '1'
    if 'P' in flags:
        base = f'(1+0.13*exp(-t*7)+0.02*t/{d})'
    elif 'p' in flags:
        base = f'(1+0.08*t/{d})'
    elif 'l' in flags:
        base = f'(1.08-0.07*t/{d})'
    extra = ''
    if 'W' in flags:
        extra += '+0.22*exp(-12*t)'
    if 'w' in flags:
        extra += f'+0.22*exp(-12*({d}-t))'
    return base + extra


def shot_filter(flags, d, gamma, ramp):
    if CLEAN:
        flags = ''
    vf = []
    if ramp:
        k0, k1 = ramp
        Ls = 2 * d / (k0 + k1)
        vf.append('setpts=PTS-STARTPTS')
        vf.append(f"setpts='({k0}*T+({k1}-{k0})*T*T/(2*{Ls:.4f}))/TB'")
    vf.append(f'fps={FPS}')
    vf.append(f'eq=gamma={gamma:.3f}')
    z = zoom_expr(flags, d)
    if z != '1':
        vf.append(f"scale=w='trunc(1080*({z})/2)*2':h='trunc(1920*({z})/2)*2':eval=frame:flags=bicubic")
        xe = '(iw-1080)/2'
        if 'W' in flags or 'w' in flags:
            uo = f'max(0,1-({d}-t)/0.12)' if 'w' in flags else '0'
            ui = 'max(0,1-t/0.12)' if 'W' in flags else '0'
            xe = f'(iw-1080)/2*(1+0.9*({uo}-{ui}))'
        vf.append(f"crop=1080:1920:x='{xe}':y='(ih-1920)/2'")
    if 'W' in flags or 'w' in flags:
        en = []
        if 'W' in flags:
            en.append('lt(t,0.12)')
        if 'w' in flags:
            en.append(f'gt(t,{d}-0.12)')
        vf.append(f"gblur=sigma=34:sigmaV=0:enable='{'+'.join(en)}'")
    if 'F' in flags:
        vf.append('fade=t=in:st=0:d=0.14:color=white')
    vf.append('format=yuv420p')
    return ','.join(vf)


def main():
    shots = V['shots']
    ref = shots_ref[V['ref'][1:]]
    cuts = ref['shots']
    assert len(cuts) == len(shots), (len(cuts), len(shots))
    end = ref['end']
    total_frames = round(end * FPS)
    segs = []
    plan = []
    for i, ((a, b), (cl, flags)) in enumerate(zip(cuts, shots)):
        fa, fb = round(a * FPS), (round(b * FPS) if i < len(cuts) - 1 else total_frames)
        n = max(1, fb - fa)
        d = n / FPS
        ramp = (1.0, 0.5) if 'R' in flags and d >= 1.0 and not CLEAN else None
        Ls = (2 * d / 1.5) if ramp else d
        c, t0, l = pick(cl, Ls + 0.1, i)
        g = gamma_for(l)
        out = f'{work}/{V["ref"]}_{i:02d}.mp4'
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{Ls + 0.3:.3f}', '-i', f'{MEZZ}/{c}.mp4',
               '-an', '-vf', shot_filter(flags, d, g, ramp), '-frames:v', str(n),
               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-g', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS), out]
        run(cmd)
        segs.append(out)
        plan.append({'shot': i, 'clip': c, 'src_t': round(t0, 2), 'dur': round(d, 3), 'flags': flags, 'gamma': round(g, 2)})
    lst = f'{work}/{V["ref"]}_list.txt'
    open(lst, 'w').write('\n'.join(f"file '{p}'" for p in segs))
    cat = f'{work}/{V["ref"]}_cat.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', cat])
    # audio from the reference TikTok, outro trimmed off
    aud = f'{work}/{V["ref"]}.m4a'
    run(['ffmpeg', '-y', '-v', 'error', '-t', f'{end:.3f}', '-i', f'{S}/ref/{V["ref"]}.mp4', '-vn',
         '-af', f'loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={end - 0.45:.2f}:d=0.45',
         '-c:a', 'aac', '-b:a', '192k', aud])
    final = f'{outdir}/{V["out"]}'
    run(['ffmpeg', '-y', '-v', 'error', '-i', cat, '-i', aud,
         '-filter_complex', f'[0:v]{GRADE},{GLOW},noise=alls=5:allf=t[v]',
         '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p',
         '-r', str(FPS), '-c:a', 'copy', '-movflags', '+faststart', '-t', f'{end:.3f}', final])
    json.dump({'video': V['out'], 'ref': V['ref'], 'length': round(end, 2), 'plan': plan},
              open(f'{work}/{V["ref"]}_plan.json', 'w'), indent=1)
    print('done', final)


main()
