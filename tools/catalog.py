import sys,os,json,subprocess,glob,hashlib
import numpy as np, cv2
S=sys.argv[1]; out=sys.argv[2]
os.makedirs(out+'/thumbs',exist_ok=True)
rows=[]
seen={}
for f in sorted(glob.glob(S+'/p*.mov')):
    n=os.path.basename(f)[:-4]
    sz=os.path.getsize(f)
    if sz in seen: rows.append({'id':n,'dup_of':seen[sz]}); continue
    seen[sz]=n
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,codec_name:stream_side_data=rotation:format=duration','-of','json',f]))
    s=d['streams'][0]; rot=0
    for x in s.get('side_data_list',[]): rot=x.get('rotation',rot)
    w,h=s['width'],s['height']
    if abs(rot)==90: w,h=h,w
    dur=float(d['format']['duration'])
    orient='vertical' if h>w else 'horizontal'
    # 4 sample frames via ffmpeg (autorotates), small
    fr=[]
    for t in np.linspace(dur*0.12,dur*0.88,4):
        p=f'{out}/thumbs/{n}_{int(t*10)}.jpg'
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{t:.2f}','-i',f,'-frames:v','1','-vf','scale=-2:320' if orient=='vertical' else 'scale=-2:240',p])
        im=cv2.imread(p)
        if im is not None: fr.append(im)
    luma=float(np.mean([cv2.cvtColor(i,cv2.COLOR_BGR2GRAY).mean() for i in fr])) if fr else -1
    sat=float(np.mean([cv2.cvtColor(i,cv2.COLOR_BGR2HSV)[...,1].mean() for i in fr])) if fr else -1
    rows.append({'id':n,'w':w,'h':h,'orient':orient,'dur':round(dur,1),'fps':s['r_frame_rate'],'codec':s['codec_name'],'luma':round(luma,1),'sat':round(sat,1),'rot':rot})
    for p in glob.glob(f'{out}/thumbs/{n}_*.jpg'): pass
json.dump(rows,open(out+'/catalog_raw.json','w'),indent=1)
print(len(rows))
