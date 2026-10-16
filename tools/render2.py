"""Clean, bright recreation renderer (v3): hard cuts only, even exposure, light grade.

usage: render2.py STORYBOARDS.py VIDEO_KEY WORKDIR OUTDIR

- cuts land on the reference cut times (or beats); no flashes, whips, punch zooms or speed ramps
- only a barely-there 3% push on shots longer than 0.9 s
- exposure is evened out per shot toward a bright, clean look (nothing low-exposure)
- batch-wide reuse rule: a clip is used at most once per video and at most twice per batch
"""
import sys, os, json, math, subprocess, importlib.util

FPS = 30
sb_path, key, work, outdir = sys.argv[1:5]
spec = importlib.util.spec_from_file_location('sb', sb_path)
sb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sb)
V = sb.VIDEOS[key]
S = '/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad'
HORIZ = V.get('orient') == 'h'
W, H = (1920, 1080) if HORIZ else (1080, 1920)
MEZZ = S + ('/mezz_h' if HORIZ else '/mezz')
lib = json.load(open(S + ('/lib_h.json' if HORIZ else '/lib.json')))
shots_ref = json.load(open(S + '/ref/an/shots.json'))
BATCH = S + '/batch_usage.json'
batch = json.load(open(BATCH)) if os.path.exists(BATCH) else {}
os.makedirs(work, exist_ok=True)
os.makedirs(outdir, exist_ok=True)

# light, clean grade: gentle contrast, a touch of colour, warm highlights / cool shadows
GRADE = ("eq=contrast=1.06:saturation=1.10,"
         "colorbalance=rs=-0.02:bs=0.03:rh=0.03:bh=-0.02,"
         "curves=all='0/0.01 0.5/0.52 1/0.99'")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(' '.join(cmd)); print(r.stderr[-2000:]); raise SystemExit(1)


def window_stats(c, t0, L):
    d = lib[c]; st = d['step']
    i0 = int(t0 / st); i1 = max(i0 + 1, int((t0 + L) / st))
    sh, lu, mo = d['sharp'][i0:i1] or [0], d['luma'][i0:i1] or [0], d['motion'][i0:i1] or [0]
    return sum(sh) / len(sh), sum(lu) / len(lu), sum(mo) / len(mo)


def score(c, t0, L):
    s, l, m = window_stats(c, t0, L)
    pen = 1.0
    if l < 25:
        pen *= 0.5      # prefer brighter footage
    if m > 12:
        pen *= 0.4      # shaky / whip
    return math.log1p(s) * pen * (1 + min(l, 110) / 400), l


video_used, windows = set(), {}


def pick(spec_s, L, i):
    cands = []
    for item in spec_s.split('|'):
        t_fixed = None
        if '@' in item:
            item, t = item.split('@'); t_fixed = float(t)
        if item in lib and lib[item]['dur'] >= L + 0.3:
            cands.append((item, t_fixed))
    for strict in (True, False):
        for c, t_fixed in cands:
            if strict and (c in video_used or batch.get(c, 0) >= 2):
                continue
            if t_fixed is not None:
                t0 = min(t_fixed, lib[c]['dur'] - L - 0.15)
                return c, t0, window_stats(c, t0, L)[1]
            best, t = None, 0.25
            while t + L <= lib[c]['dur'] - 0.2:
                if not any(not (t + L <= a or t >= b) for a, b in windows.get(c, [])):
                    sc, l = score(c, t, L)
                    if best is None or sc > best[0]:
                        best = (sc, t, l)
                t += 0.1
            if best:
                windows.setdefault(c, []).append((best[1], best[1] + L))
                return c, best[1], best[2]
    raise SystemExit(f'no window for shot {i}: {spec_s} need {L:.2f}s')


def gamma_for(l):
    l = max(l, 4.0)
    if l < 98:
        t = l + 0.65 * (98 - l)
    elif l > 130:
        t = 130 + 0.5 * (l - 130)
    else:
        t = l
    return max(0.55, min(2.2, math.log(l / 255) / math.log(t / 255)))


def shot_filter(d, g):
    vf = [f'fps={FPS}', f'eq=gamma={g:.3f}']
    if d >= 0.9:
        z = f'(1+0.03*t/{d})'
        vf.append(f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame:flags=bicubic")
        vf.append(f'crop={W}:{H}')
    vf.append('format=yuv420p')
    return ','.join(vf)


def main():
    shots = V['shots']
    ref = shots_ref[V['ref'][1:]]
    cuts = ref['shots']
    assert len(cuts) == len(shots), (V['ref'], len(cuts), len(shots))
    end = ref['end']
    total = round(end * FPS)
    segs, plan = [], []
    for i, ((a, b), cl) in enumerate(zip(cuts, shots)):
        fa = round(a * FPS)
        fb = round(b * FPS) if i < len(cuts) - 1 else total
        n = max(1, fb - fa); d = n / FPS
        c, t0, l = pick(cl, d + 0.1, i)
        video_used.add(c)
        g = gamma_for(l)
        out = f'{work}/{V["ref"]}_{i:02d}.mp4'
        run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{d + 0.3:.3f}', '-i', f'{MEZZ}/{c}.mp4', '-an',
             '-vf', shot_filter(d, g), '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15',
             '-g', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS), out])
        segs.append(out)
        plan.append({'shot': i, 'clip': c, 'src_t': round(t0, 2), 'dur': round(d, 3), 'luma': round(l), 'gamma': round(g, 2)})
    lst = f'{work}/{V["ref"]}_list.txt'
    open(lst, 'w').write('\n'.join(f"file '{p}'" for p in segs))
    cat = f'{work}/{V["ref"]}_cat.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', cat])
    aud = f'{work}/{V["ref"]}.m4a'
    run(['ffmpeg', '-y', '-v', 'error', '-t', f'{end:.3f}', '-i', f'{S}/ref/{V["ref"]}.mp4', '-vn',
         '-af', f'loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={end - 0.4:.2f}:d=0.4', '-c:a', 'aac', '-b:a', '192k', aud])
    final = f'{outdir}/{V["out"]}'
    run(['ffmpeg', '-y', '-v', 'error', '-i', cat, '-i', aud, '-vf', f'{GRADE},noise=alls=3:allf=t',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '16M', '-bufsize', '32M', '-pix_fmt', 'yuv420p',
         '-r', str(FPS), '-c:a', 'copy', '-movflags', '+faststart', '-t', f'{end:.3f}', final])
    for c in {p['clip'] for p in plan}:
        batch[c] = batch.get(c, 0) + 1
    json.dump(batch, open(BATCH, 'w'))
    json.dump({'video': V['out'], 'ref': V['ref'], 'length': round(end, 2), 'plan': plan},
              open(f'{work}/{V["ref"]}_plan.json', 'w'), indent=1)
    print('done', final)


main()
