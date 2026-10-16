import sys,json,subprocess,numpy as np,cv2
src=sys.argv[1]
cap=cv2.VideoCapture(src); fps=cap.get(cv2.CAP_PROP_FPS); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
prev=None; luma=[]; diff=[]; hdiff=[]; phist=None
while True:
    ok,f=cap.read()
    if not ok: break
    g=cv2.cvtColor(cv2.resize(f,(90,160)),cv2.COLOR_BGR2GRAY)
    luma.append(float(g.mean()))
    diff.append(0.0 if prev is None else float(np.abs(g.astype(np.int16)-prev).mean()))
    h=cv2.calcHist([cv2.resize(f,(90,160))],[0,1,2],None,[8,8,8],[0,256]*3).flatten(); h/=h.sum()
    hdiff.append(0.0 if phist is None else float(0.5*np.abs(h-phist).sum()))
    prev=g.astype(np.int16); phist=h
json.dump({'fps':fps,'luma':luma,'diff':diff,'hdiff':hdiff},open(sys.argv[2],'w'))
print(src,len(luma),fps)
