import re,os,glob,subprocess
S='/tmp/claude-0/-home-user-content/a076afeb-a72e-5a9b-8eab-5652dc33f51a/scratchpad'
s=open('/home/user/content/tools/storyboards.py').read()
need=set(re.findall(r'p\d{3}',s))|{'p044','p041','p040','p039'}
done=set()
for f in glob.glob(S+'/mezz/*.mp4'):
    c=os.path.basename(f)[:-4]
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True)
    if r.returncode: os.remove(f)
    else: done.add(c)
todo=sorted(need-done)
print('need',len(need),'todo',len(todo),todo)
open(S+'/mezz_todo.txt','w').write('\n'.join(todo))
