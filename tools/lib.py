"""Score every mezzanine clip at 10 fps so shots can pick the best source window.

usage: lib.py MEZZ_DIR OUT.json
"""
import sys, os, json, glob
import numpy as np, cv2

mezz, out = sys.argv[1], sys.argv[2]
lib = json.load(open(out)) if os.path.exists(out) else {}
for f in sorted(glob.glob(mezz + '/p*.mp4')):
    cid = os.path.basename(f)[:-4]
    if cid in lib:
        continue
    cap = cv2.VideoCapture(f)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    luma, sharp, motion = [], [], []
    prev = None
    k = 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if k % 3 == 0:
            ok, fr = cap.retrieve()
            g = cv2.cvtColor(cv2.resize(fr, (270, 480)), cv2.COLOR_BGR2GRAY)
            luma.append(float(g.mean()))
            sharp.append(float(cv2.Laplacian(g, cv2.CV_64F).var()))
            motion.append(0.0 if prev is None else float(np.abs(g.astype(np.int16) - prev).mean()))
            prev = g.astype(np.int16)
        k += 1
    lib[cid] = {'dur': k / fps, 'step': 3 / fps, 'luma': luma, 'sharp': sharp, 'motion': motion}
    json.dump(lib, open(out, 'w'))
    print(cid, round(k / fps, 1), flush=True)
