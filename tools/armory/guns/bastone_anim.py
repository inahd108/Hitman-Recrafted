"""Bastone 9 animations: the shared pistol set, service-pistol pace, with a hammer."""
import pistol_anim
from pistol_anim import PistolSpec

S = 'tacz:m9a4/m9a4_'

SPEC = PistolSpec(
    slide_travel=2.2,
    mag_out=5.4,
    kick=0.85,
    sounds={
        'lift': S + 'reload_magdown', 'magout': S + 'reload_magout', 'magin': S + 'reload_magin',
        'end': S + 'reload_end', 'empty_lift': S + 'reload_magdown', 'empty_magout': S + 'reload_magout_fast',
        'empty_magin': S + 'reload_magin', 'chamber': S + 'reload_charge', 'empty_end': S + 'reload_end',
        'inspect_a': S + 'inspect_rotate', 'inspect_b': S + 'inspect_checkchamber',
    },
    extra={'inspect_near': [2.6, 2.3, 2.6]},
)


def all_animations():
    return pistol_anim.all_animations(SPEC)
