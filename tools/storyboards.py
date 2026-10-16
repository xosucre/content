"""Storyboards for the personal-page recreations (2026-10-16 test).

Each reference TikTok in "Sounds folder" is recreated with the same sound and the same
cut times, using the creator's own vertical clips picked to match the vibe of each shot.
Shot lists follow the cut order of the reference (see ref/an/shots.json for the timings).
"""


def S(pairs):
    out = []
    for p in pairs:
        c, f = p.split(':') if ':' in p else (p, '')
        out.append((c, f))
    return out


VIDEOS = {
    # ---- s01: "be proud of your mistakes" : dark luxury night montage, one cut per beat
    's01': {
        'ref': 's01', 'out': 'personal_01_night-luxury.mp4',
        'shots': S([
            'p041:p', 'p039:P', 'p077', 'p044:P', 'p048:w', 'p089:W', 'p065:P', 'p130', 'p052:PF', 'p130',
            'p042:w', 'p017:W', 'p071:F', 'p118', 'p016', 'p049:P', 'p056:F', 'p033', 'p096:P', 'p091:w',
            'p022:W', 'p078:pF',
        ]),
    },
    # ---- s02: "sometimes you gotta hop off multiplayer" : travel / cars / night city
    's02': {
        'ref': 's02',  'out': 'personal_02_travel-night.mp4',
        'shots': S([
            'p078:l', 'p095:p', 'p064:Pw', 'p065:WF', 'p059|p049:pR', 'p058:P', 'p052:pw', 'p053:W', 'p056:F',
            'p079:pR', 'p049:pR', 'p056:P', 'p048:pR', 'p055:l',
        ]),
    },
    # ---- s03: dark luxury, red/blue accent light, 0.6 s cuts
    's03': {
        'ref': 's03', 'out': 'personal_03_dark-accent.mp4',
        'shots': S([
            'p048:p', 'p017:P', 'p056:w', 'p044:W', 'p041:P', 'p023:F', 'p016', 'p058:P', 'p130:w', 'p053:W',
            'p130:P', 'p062:F', 'p064', 'p065:P', 'p118:p',
        ]),
    },
    # ---- s06: "once you learn how to shoot b-roll" : fast bright b-roll montage, graded dramatic
    's06': {
        'ref': 's06', 'out': 'personal_04_broll-montage.mp4',
        'shots': S([
            'p025:p', 'p029:P', 'p062', 'p130:P', 'p016', 'p135@6.0:P', 'p044', 'p071:P', 'p063', 'p102:F',
            'p036:P', 'p099', 'p026:P', 'p030', 'p015', 'p104:Pw', 'p033:W', 'p060:w', 'p070:W', 'p020|p018:P',
            'p042', 'p040:F', 'p021:P', 'p052', 'p014:P', 'p049', 'p022:F', 'p023', 'p063:P', 'p018',
            'p029:P', 'p024', 'p038:pF',
        ]),
    },
    # ---- s09: villa / night-city montage
    's09': {
        'ref': 's09', 'out': 'personal_05_night-city.mp4',
        'shots': S([
            'p130:p', 'p049:P', 'p059', 'p056:P', 'p052', 'p053:P', 'p052:w', 'p039:W', 'p118:w', 'p043:PW',
            'p040', 'p017:F', 'p016', 'p021:P', 'p044', 'p064:P', 'p065:w', 'p130:W', 'p058:pw', 'p077:pW',
            'p078:F', 'p089', 'p062:P', 'p091:pF',
        ]),
    },
}
