"""Passero .22 animations: the shared pistol set, lighter and quicker, with a short slide."""
import pistol_anim
from pistol_anim import PistolSpec

S = 'tacz:glock_17/glock17_'

SPEC = PistolSpec(
    slide_travel=1.5,
    mag_out=4.6,
    kick=0.55,
    hammer=False,
    pace=0.9,
    sounds={
        'lift': S + 'reload_start', 'magout': S + 'reload_magout', 'magin': S + 'reload_magin', 'end': S + 'reload_end',
        'empty_lift': S + 'reload_start', 'empty_magout': S + 'reload_empty_magout',
        'empty_magin': S + 'reload_empty_magin', 'chamber': S + 'reload_empty_charge',
        'empty_end': S + 'reload_empty_end', 'inspect_a': S + 'inspect_raise', 'inspect_b': S + 'inspect_turn',
    },
    extra={'inspect_near': [3.2, 2.4, 2.8]},
)


def all_animations():
    return pistol_anim.all_animations(SPEC)
