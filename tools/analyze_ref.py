import sys,json,subprocess,os
import numpy as np, librosa
from scenedetect import detect, ContentDetector
src,out=sys.argv[1],sys.argv[2]
sc=detect(src,ContentDetector(threshold=18,min_scene_len=4))
cuts=[(a.get_seconds(),b.get_seconds()) for a,b in sc]
wav=out+'.wav'
subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-vn','-ac','1','-ar','22050',wav])
y,sr=librosa.load(wav,sr=22050)
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time')
rms=librosa.feature.rms(y=y)[0]
dur=len(y)/sr
json.dump({'dur':dur,'cuts':cuts,'tempo':float(np.atleast_1d(tempo)[0]),'beats':[round(float(b),3) for b in beats],'rms_mean':float(rms.mean())},open(out+'.json','w'))
print(os.path.basename(src),'dur %.1f'%dur,'tempo %.0f'%np.atleast_1d(tempo)[0],'shots',len(cuts),'cuts',[round(c[0],1) for c in cuts])
