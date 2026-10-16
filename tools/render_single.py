"""Cinematic single-shot recreation (reference s05: letterboxed silhouette at a night window).

usage: render_single.py WORKDIR OUTDIR
"""
import sys, os, json, math, subprocess

work, outdir = sys.argv[1:3]
S = '/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad'
FPS = 30
END = 11.56
CLIP = 'p044'
os.makedirs(work, exist_ok=True)
os.makedirs(outdir, exist_ok=True)
lib = json.load(open(S + '/lib.json'))[CLIP]

# best-scoring steady 11.8 s window
L = END + 0.3
best = None
t = 0.3
while t + L <= lib['dur'] - 0.2:
    i0, i1 = int(t / lib['step']), int((t + L) / lib['step'])
    sc = math.log1p(sum(lib['sharp'][i0:i1]) / (i1 - i0)) - 0.05 * sum(lib['motion'][i0:i1]) / (i1 - i0)
    if best is None or sc > best[0]:
        best = (sc, t)
    t += 0.2
t0 = float(os.environ.get('T0', best[1]))

GRADE = ("eq=contrast=1.12:saturation=1.08,"
         "colorbalance=rs=-0.05:bs=0.08:rm=-0.03:bm=0.05:bh=0.025:rh=-0.01,"
         "curves=all='0/0 0.2/0.14 0.5/0.47 0.85/0.9 1/1',vignette=angle=PI/4.2")
GLOW = ("split[a][b];[b]gblur=sigma=22,curves=all='0/0 0.55/0 1/0.9'[g];"
        "[a][g]blend=all_mode=screen:all_opacity=0.35")
# slow push-in, 2.39:1 letterbox like the reference, two soft lightning-style flashes
CROP_Y = int(os.environ.get('CROP_Y', 560))
z = f"(1+0.03*t/{END})"
vf = (f"eq=gamma=1.6,scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame,"
      f"crop=1080:1920,crop=1080:610:0:{CROP_Y},"
      f"pad=1080:1920:0:655:black,format=yuv420p")
cat = f'{work}/s05_cat.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t0:.2f}', '-t', f'{END + 0.3:.2f}', '-i', f'{S}/mezz/{CLIP}.mp4',
                '-an', '-vf', vf, '-frames:v', str(round(END * FPS)), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15',
                '-pix_fmt', 'yuv420p', '-r', str(FPS), cat], check=True)
aud = f'{work}/s05.m4a'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-t', f'{END}', '-i', f'{S}/ref/s05.mp4', '-vn',
                '-af', f'loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={END - 0.45:.2f}:d=0.45',
                '-c:a', 'aac', '-b:a', '192k', aud], check=True)
final = f'{outdir}/personal_06_window-silhouette.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', cat, '-i', aud,
                '-filter_complex', f'[0:v]{GRADE},{GLOW},noise=alls=5:allf=t[v]',
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p',
                '-r', str(FPS), '-c:a', 'copy', '-movflags', '+faststart', '-t', f'{END}', final], check=True)
json.dump({'video': os.path.basename(final), 'ref': 's05', 'length': END,
           'plan': [{'shot': 0, 'clip': CLIP, 'src_t': round(t0, 2), 'dur': END, 'flags': 'push+letterbox+flash'}]},
          open(f'{work}/s05_plan.json', 'w'), indent=1)
print('done', final, 'src_t', t0)
