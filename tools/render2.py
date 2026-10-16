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
EXCLUDE = {'p074', 'p010', 'p011', 'p012'}   # curly-haired girl (back), white car
SHUFFLE = os.environ.get('SHUFFLE') == '1'
import random
random.seed(int(os.environ.get('SEED', '7')))
TAGS = {}
for tag, ids in {
    'night_view': 'p064 p065 p066 p067 p090', 'dusk_roof': 'p077 p078 p079 p080 p088 p089 p073 p081 p075 p076 p082 p083',
    'tower_up': 'p052 p053 p021 p126 p023', 'pink_elev': 'p062', 'street_person': 'p048 p049 p055 p056 p058 p059',
    'hotel_window': 'p033 p035 p036 p046 p025 p026 p027 p028', 'room_tour': 'p031 p032 p034 p095 p072',
    'bath_minibar': 'p029 p030 p037 p038', 'lobby': 'p016 p017 p018 p019 p020 p024', 'robot_lounge': 'p070 p071',
    'atrium': 'p102 p103 p104 p105 p099', 'food': 'p060 p061 p063', 'brand': 'p000 p001 p002 p003 p004 p005 p006 p007 p008',
    'factory': 'p137 p138 p139 p140 p141 p142 p143 p145 p147 p149 p151 p153', 'selfie': 'p013 p014 p015 p135',
    'neon_plaza': 'p108 p109 p110 p111 p112 p113 p115 p127 p128 p129', 'dinner': 'p131 p133', 'stairs': 'p134',
    'pool': 'p116', 'gym_window': 'p057', 'lantern': 'p096',
    'night_street_h': 'p050 p051 p054 p092 p094 p114', 'roof_h': 'p084 p085 p087', 'hotel_night_h': 'p068 p117 p119 p123 p124 p125 p097',
    'desk': 'p044 p042 p043 p047'}.items():
    for i_ in ids.split():
        TAGS[i_] = tag
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


def pick_clip(spec_s, L, i):
    cands = []
    for item in spec_s.split('|'):
        t_fixed = None
        if '@' in item:
            item, t = item.split('@'); t_fixed = float(t)
        if item in lib and item not in EXCLUDE and lib[item]['dur'] >= L + 0.4:
            cands.append((item, t_fixed))
    for strict in (True, False):
        for c, t_fixed in cands:
            if strict and (c in video_used or batch.get(c, 0) >= 2):
                continue
            return c, t_fixed
    raise SystemExit(f'no clip for shot {i}: {spec_s} need {L:.2f}s')


def pick_window(c, t_fixed, L):
    if t_fixed is not None:
        t0 = min(t_fixed, lib[c]['dur'] - L - 0.15)
        return t0, window_stats(c, t0, L)[1]
    best, t = None, 0.25
    while t + L <= lib[c]['dur'] - 0.2:
        if not any(not (t + L <= a or t >= b) for a, b in windows.get(c, [])):
            sc, l = score(c, t, L)
            if best is None or sc > best[0]:
                best = (sc, t, l)
        t += 0.1
    if best is None:
        t0 = 0.2
        return t0, window_stats(c, t0, L)[1]
    windows.setdefault(c, []).append((best[1], best[1] + L))
    return best[1], best[2]


def order_clips(assign, durs):
    """random order; neighbours must differ in tag, and each clip must be long enough for its slot."""
    n = len(assign)
    tag = lambda c: TAGS.get(c, c)
    best, best_bad = None, 10 ** 9
    for _ in range(40000):
        p = list(range(n)); random.shuffle(p)
        if any(lib[assign[p[k]][0]]['dur'] < durs[k] + 0.5 for k in range(n)):
            continue
        bad = sum(tag(assign[p[k]][0]) == tag(assign[p[k + 1]][0]) for k in range(n - 1))
        if bad < best_bad:
            best, best_bad = p, bad
        if bad == 0:
            break
    return best, best_bad


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
    ref = shots_ref.get(V['ref']) or shots_ref[V['ref'][1:]]
    cuts = ref['shots']
    assert len(cuts) == len(shots), (V['ref'], len(cuts), len(shots))
    end = ref['end']
    total = round(end * FPS)
    segs, plan = [], []
    durs, frames = [], []
    for i, (a, b) in enumerate(cuts):
        fa = round(a * FPS)
        fb = round(b * FPS) if i < len(cuts) - 1 else total
        n = max(1, fb - fa); frames.append(n); durs.append(n / FPS)
    assign = []
    for i, cl in enumerate(shots):
        c, tf = pick_clip(cl, durs[i] + 0.1, i)
        video_used.add(c)
        assign.append((c, tf))
    bad = 0
    if SHUFFLE:
        perm, bad = order_clips(assign, durs)
        assign = [assign[k] for k in perm]
    for i, (c, tf) in enumerate(assign):
        d, n = durs[i], frames[i]
        t0, l = pick_window(c, tf, d + 0.1)
        g = gamma_for(l)
        out = f'{work}/{V["ref"]}_{i:02d}.mp4'
        run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{d + 0.3:.3f}', '-i', f'{MEZZ}/{c}.mp4', '-an',
             '-vf', shot_filter(d, g), '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15',
             '-g', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS), out])
        segs.append(out)
        plan.append({'shot': i, 'clip': c, 'src_t': round(t0, 2), 'dur': round(d, 3), 'luma': round(l), 'gamma': round(g, 2)})
    print('similar neighbours left:', bad)
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
