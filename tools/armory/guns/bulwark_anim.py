"""Bulwark AR timing (TACZ's bundled AR-rifle sounds); empty reloads end on the bolt release."""
from bulwark import MAG_DEG
from smg_anim import SmgSpec, all_animations

H = 'tacz:hk416d/hk416d_'
SPEC = SmgSpec(
    sounds={
        'raise': H + 'raise', 'magout': H + 'reload_fast_magout', 'maghit': H + 'reload_magin_01',
        'magin': H + 'reload_magin_v2_01', 'end': H + 'reload_end',
        'empty_start': H + 'reload_fast_raise', 'empty_turn': H + 'reload_empty_xmag_magout',
        'mag_drop': H + 'reload_empty_mag_drop', 'charge': H + 'reload_empty_fast_chamber',
        'empty_end': H + 'reload_empty_fast_end',
        'inspect_start': H + 'inspect_01', 'inspect_rotate': H + 'inspect_02', 'inspect_turn': H + 'inspect_03',
        'inspect_end': H + 'inspect_05',
    },
    grip_deg=MAG_DEG,
    mag_out=1.6,
    hand_to_mag=(0, -3.4, 6.4),
    bolt_travel=1.3,
    kick=1.25,
    extra={'empty_action': 'release', 'hand_to_release': (-0.6, 0.2, 9.0), 'reload_tilt': [-8, -18, -32],
           'reload_near': [-1.0, 1.2, -1.6], 'inspect_near': [0.4, 0.8, -2.2], 'inspect_left': [-6, -38, -14], 'inspect_right': [-4, 22, 8]},
)


def animations():
    return all_animations(SPEC)
