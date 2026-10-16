"""Storyboards v4: the five newest references (t01..t05), same bright / clean-cut format as v3.

Never used: p010 p011 p012 (white car) and p074 (curly-haired girl) -- see EXCLUDE in render2.py.
"""
HZ = ('p047|p119|p057|p072|p131|p133|p068|p117|p113|p110|p112|p111|p050|p051|p076|p134|p128|p129|p127|p115|'
      'p109|p108|p106|p107|p054|p092|p094|p114|p123|p124|p125|p081|p075|p082|p083|p116|p084|p085|p087|p097')


def hz(n):
    pool = HZ.split('|')
    return ['|'.join(pool[(i * 3) % len(pool):] + pool[:(i * 3) % len(pool)]) for i in range(n)]


VIDEOS = {
    # t01: single dark silhouette shot ("you're still in the same position"): rooftop view from behind at dusk
    't01': {'ref': 't01', 'out': 'personal_13_back-view.mp4', 'shots': ['p073|p077|p078']},
    # t02: moody night street / luxury, 8 cuts
    't02': {'ref': 't02', 'out': 'personal_14_night-street.mp4', 'shots': [
        'p064|p065|p066', 'p130|p122', 'p052|p053', 'p053|p052|p023', 'p096|p126', 'p126|p023|p021', 'p023|p021|p062',
        'p078|p079|p080']},
    # t03: horizontal hustle montage (reference is 4:3 landscape), 29 cuts
    't03': {'ref': 't03', 'out': 'personal_15_hustle-montage.mp4', 'orient': 'h', 'shots': hz(29)},
    # t04: single shot, person lost in thought at a table
    't04': {'ref': 't04', 'out': 'personal_16_lost-in-thought.mp4', 'shots': ['p044|p042|p043']},
    # t05: man standing at night by his ride, one long shot then quick cuts
    't05': {'ref': 't05', 'out': 'personal_17_street-night.mp4', 'shots': [
        'p056|p055', 'p055|p049', 'p049|p059', 'p048|p058']},
}
