"""Snoek timing (TACZ's bundled 9 mm submachine-gun sounds); the PDW set, a little heavier."""
from smg_anim import SmgSpec, all_animations
from snoek import GRIP_DEG

S = 'tacz:hk_mp5a5/hk_mp5a5_'
SPEC = SmgSpec(
    sounds={
        'raise': S + 'reload_raise', 'magout': S + 'reload_magout', 'magin': S + 'reload_magin', 'end': S + 'reload_end',
        'empty_start': S + 'reload_raise', 'empty_turn': S + 'reload_empty_fast_rotate',
        'mag_drop': S + 'reload_empty_mag_drop', 'charge': S + 'reload_empty_boltclose', 'empty_end': S + 'reload_empty_end',
        'inspect_start': S + 'inspect_raise', 'inspect_rotate': S + 'inspect_turn', 'inspect_turn': S + 'inspect_cloth',
        'inspect_end': S + 'inspect_end',
    },
    grip_deg=GRIP_DEG,
    hand_to_charge=(-0.75, 5.0, 16.5),
    kick=0.7,
    extra={'inspect_near': [0.6, 1.0, -1.6], 'inspect_left': [-6, -40, -15], 'inspect_right': [-6, 32, 12]},
)


def animations():
    return all_animations(SPEC)
