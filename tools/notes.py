"""Build the run notes + usage log from the render plans.

usage: notes.py WORKDIR OUTDIR DATE LABEL
"""
import sys, json, glob, os
work, outdir, date, label = sys.argv[1:5]
REF = {  # reference TikTok in "Sounds folder" -> original file name
    's01': 'Video 2026-10-15, 9 01 32 PM.mp4', 's02': 'Video 2026-10-15, 9 00 33 PM.mp4',
    's03': 'Video 2026-10-15, 7 51 27 PM.mp4', 's05': 'Video 2026-10-15, 9 04 12 PM.mp4',
    's06': 'Video 2026-10-15, 9 00 55 PM.mp4', 's09': 'Video 2026-10-15, 9 04 21 PM.mp4'}
TEXT = {
    's01': 'Be proud of your mistakes. Some people don\'t even have the guts to try.',
    's02': 'Sometimes you gotta hop off multiplayer and start grinding story mode',
    's03': 'Sorry, I\'m busy',
    's05': 'what this q4 feels like',
    's06': 'Once you learn how to shoot B-roll, you start seeing content literally everywhere you go.',
    's09': 'Every man needs one friend who refuses to let him stay average.'}
VIBE = {
    's01': 'night luxury montage, one cut per beat (~129 bpm)',
    's02': 'travel / cars / night city, long holds then a fast flurry',
    's03': 'dark luxury with red + blue accent light, 0.6 s cuts',
    's05': 'single cinematic shot, 2.39:1 letterbox, slow push-in',
    's06': 'fast b-roll montage, 0.2 to 0.7 s cuts',
    's09': 'night city, villas and street, mixed fast and long cuts'}
plans = [json.load(open(p)) for p in sorted(glob.glob(work + '/*_plan.json'))]
plans.sort(key=lambda p: p['video'])
lines = [f'# Run notes: {date} {label}', '',
         'All videos are 9:16 (1080x1920, 30 fps), vertical clips only, no text on screen, no SFX.',
         'Each one recreates a TikTok from "Sounds folder": same sound (outro trimmed off), same cut times, your clips.',
         'Look: one shared grade (cool shadows, deep blacks, lowered exposure, soft highlight glow, film grain).', '']
log = []
for p in plans:
    r = p['ref']
    clips = sorted({s['clip'] for s in p['plan']})
    lines += [f'## {p["video"]}', '',
              '- Type: personal lifestyle (recreation)',
              '- Orientation / length: 9:16 vertical / %.1f s' % p['length'],
              f'- Sound: audio from "{REF[r]}" (Sounds folder), 0:00 to {p["length"]:.1f}s, TikTok outro removed. '
              'To use the official sound in-app, open that saved TikTok and tap its sound.',
              f'- Reference vibe: {VIBE[r]}',
              f'- Suggested text (you add it): "{TEXT[r]}"',
              f'- Shots: {len(p["plan"])}; clips used: ' + ', '.join(clips), '']
    log.append({'date': date, 'page': 'personal', 'video': p['video'], 'sound': REF[r],
                'clips': clips, 'shots': [{'clip': s['clip'], 'src_t': s['src_t'], 'dur': s['dur']} for s in p['plan']]})
open(f'{outdir}/notes.md', 'w').write('\n'.join(lines))
lp = os.path.join(os.path.dirname(outdir.rstrip('/')), 'used_log.json')
old = json.load(open(lp)) if os.path.exists(lp) else []
json.dump(old + log, open(lp, 'w'), indent=1)
print('notes ok', len(plans))
