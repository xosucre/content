"""Storyboards v3: the other six references, bright + clean, whole folder in play.

Each shot lists candidate clips in preference order ("a|b|c"). The renderer enforces the
reuse rule (once per video, twice per batch) and falls back down the list.
The white car clips (p010 p011 p012) are intentionally never used.
"""

BRAND = 'p137|p139|p140|p141|p142|p143|p145|p147|p149|p151|p153|p138|p135|p132'
HOTEL = 'p033|p035|p036|p046|p031|p025|p034|p038|p037|p029|p030|p026|p027|p028|p032|p095|p060|p061|p063'
ATRIUM = 'p102|p103|p104|p105|p099'
LOBBY = 'p016|p017|p018|p019|p020|p024|p070|p071'
NIGHT = 'p064|p065|p066|p067|p079|p080|p089|p096|p021|p023|p052|p053|p062|p073|p078|p077|p088|p090|p126'
STREET = 'p048|p049|p055|p056|p058|p059'


def S(*a):
    return list(a)


VIDEOS = {
    # s07: "pov: the other side of the risk": brand-owner / sourcing story, 0.8 s cuts
    's07': {'ref': 's07', 'out': 'personal_07_brand-story.mp4', 'shots': S(
        'p142|' + BRAND, 'p000|p001', 'p001|p000', 'p140|' + BRAND, 'p138|' + BRAND, 'p149|' + BRAND,
        'p005|p004|p003', 'p015|p013', 'p147|' + BRAND, 'p008|p006', 'p139|' + BRAND)},
    # s08: "JUST START!": brand-owner day, ~1 s cuts
    's08': {'ref': 's08', 'out': 'personal_08_just-start.mp4', 'shots': S(
        'p137|' + BRAND, 'p013|p015', 'p140|' + BRAND, 'p007|p004', 'p151|' + BRAND, 'p008|p001',
        'p145|' + BRAND, 'p006|p003|p141', 'p135|' + BRAND)},
    # s10: laptop-on-the-balcony, remote work with a view
    's10': {'ref': 's10', 'out': 'personal_09_laptop-view.mp4', 'shots': S(
        'p035|' + HOTEL, 'p033|' + HOTEL, 'p036|' + HOTEL, 'p046|' + HOTEL, 'p031|' + HOTEL,
        'p038|' + HOTEL, 'p025|' + HOTEL, 'p034|' + HOTEL, 'p032|' + HOTEL)},
    # s04: beat-per-cut lifestyle montage (about 144 bpm)
    's04': {'ref': 's04', 'out': 'personal_10_lifestyle-beats.mp4', 'shots': S(
        'p016|' + LOBBY, 'p017|' + LOBBY, 'p063|' + HOTEL, 'p071|' + LOBBY, 'p102|' + ATRIUM, 'p070|' + LOBBY,
        'p029|' + HOTEL, 'p104|' + ATRIUM, 'p020|' + LOBBY, 'p099|' + ATRIUM, 'p030|' + HOTEL, 'p014|p015',
        'p018|' + LOBBY, 'p103|' + ATRIUM, 'p036|' + HOTEL, 'p024|' + LOBBY, 'p026|' + HOTEL)},
    # s11: beat-per-cut night city (about 129 bpm), bright nights only
    's11': {'ref': 's11', 'out': 'personal_11_city-lights.mp4', 'shots': S(
        'p064|' + NIGHT, 'p065|' + NIGHT, 'p052|' + NIGHT, 'p079|' + NIGHT, 'p096|' + NIGHT, 'p021|' + NIGHT,
        'p089|' + NIGHT, 'p023|' + NIGHT, 'p066|' + NIGHT, 'p053|' + NIGHT, 'p062|' + NIGHT, 'p073|' + NIGHT,
        'p080|' + NIGHT, 'p078|' + NIGHT)},
    # s12: horizontal reference -> horizontal clips only
    's12': {'ref': 's12', 'out': 'personal_12_horizontal-story.mp4', 'orient': 'h', 'shots': S(
        'p081|p075|p076', 'p057|p072', 'p075|p082|p083', 'p133|p131', 'p110|p111|p112', 'p106|p107',
        'p074|p076', 'p076|p082', 'p108|p109', 'p072|p057', 'p134|p131', 'p128|p129|p127',
        'p129|p128', 'p109|p108|p115', 'p113|p112|p111', 'p116|p047', 'p131|p133', 'p127|p128|p129')},
}
