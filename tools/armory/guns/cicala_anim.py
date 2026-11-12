"""Cicala timing (TACZ's bundled bolt-action rifle sounds)."""
from bolt_anim import BoltSpec, all_animations

R = 'tacz:m700/m700_'
SPEC = BoltSpec(
    sounds={'bolt_out': R + 'bolt_out', 'bolt_in': R + 'bolt_in', 'shell_drop': R + 'shell_drop', 'raise': R + 'reload_raise',
            'magout': R + 'reload_magout', 'magin': R + 'reload_magin', 'end': R + 'reload_end'},
    kick=1.0,
)


def animations():
    return all_animations(SPEC)
