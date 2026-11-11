"""Argento .45 animations: the shared pistol set with a long slide and the .45 sounds."""
import pistol_anim
from pistol_anim import PistolSpec

S = 'tacz:m1911/m1911_'        # TACZ's bundled .45 pistol sounds

SPEC = PistolSpec(
    slide_travel=3.0,           # long slide: more travel than a service pistol
    mag_out=5.9,                # clears the long grip
    sounds={
        'lift': S + 'reload_lift', 'magout': S + 'reload_magout', 'magin': S + 'reload_magin', 'end': S + 'reload_end',
        'empty_lift': S + 'reload_empty_lift', 'empty_magout': S + 'reload_empty_magout',
        'empty_magin': S + 'reload_empty_magin', 'chamber': S + 'reload_empty_chamber',
        'empty_end': S + 'reload_empty_end', 'inspect_a': S + 'inspect_quick', 'inspect_b': S + 'inspect_chamber',
    },
)


def all_animations():
    return pistol_anim.all_animations(SPEC)
