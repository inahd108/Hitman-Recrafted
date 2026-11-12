"""Halcyon PDW timing (TACZ's bundled compact-PDW sounds)."""
from halcyon import GRIP_DEG
from smg_anim import SmgSpec, all_animations

S = 'tacz:hk_mp7a1/hk_mp7a1_'
SPEC = SmgSpec(
    sounds={
        'raise': S + 'reload_raise', 'magdown': S + 'reload_empty_magdown', 'magout': S + 'reload_magout',
        'maghit': S + 'reload_maghit', 'magin': S + 'reload_magin', 'end': S + 'reload_end',
        'empty_start': S + 'reload_empty_start', 'empty_turn': S + 'reload_empty_turn',
        'mag_drop': 'tacz:mag_drop_sound/mag_drop_smg_metal_dirt', 'charge': S + 'reload_empty_charge',
        'inspect_start': S + 'inspect_start', 'inspect_rotate': S + 'inspect_rotate', 'inspect_turn': S + 'inspect_turn',
        'inspect_end': S + 'inspect_end',
    },
    grip_deg=GRIP_DEG,
    extra={'inspect_near': [0.6, 1.0, -1.0]},
)


def animations():
    return all_animations(SPEC)
