"""Reiger 9 animations: the shared pistol set, quick and light, striker fired (no hammer)."""
import pistol_anim
from pistol_anim import PistolSpec

S = 'tacz:p320/p320_'

SPEC = PistolSpec(
    slide_travel=2.0,
    mag_out=5.5,
    kick=0.75,
    hammer=False,
    pace=0.95,
    sounds={
        'lift': S + 'reload_raise', 'magout': S + 'reload_magout', 'magin': S + 'reload_magin',
        'end': S + 'reload_fast_end', 'empty_lift': S + 'reload_empty_raise', 'empty_magout': S + 'reload_empty_magout',
        'empty_magin': S + 'reload_empty_magin', 'chamber': S + 'reload_empty_charge', 'empty_end': S + 'reload_empty_end',
        'inspect_a': S + 'inspect_empty_rotate', 'inspect_b': S + 'inspect_slidepull',
    },
    extra={'inspect_near': [2.7, 2.3, 2.6]},
)


def animations():
    return pistol_anim.all_animations(SPEC)
