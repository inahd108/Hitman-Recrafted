"""Vento .357 timing and sounds (TACZ's bundled revolver sounds)."""
from revolver_anim import RevolverSpec, all_animations
from vento import CRANE_OPEN

R = 'tacz:rhino357/rhino_'
SPEC = RevolverSpec(
    sounds={
        'cock': R + 'cocked', 'raise': R + 'reload_raise', 'open': R + 'reload_cylinder_turn',
        'eject': R + 'reload_eject', 'shell': R + 'reload_shell', 'pocket': R + 'reload_clothes_light',
        'bulletin': R + 'reload_bulletin', 'spin': R + 'cylinder_spin', 'close': R + 'reload_cylinder_close',
        'reset': R + 'reload_reset', 'inspect_start': R + 'inspect_start', 'inspect_open': R + 'inspect_rift',
        'inspect_spin': R + 'cylinder_spin', 'inspect_spin_end': R + 'inspect_rotate_end',
        'inspect_reset': R + 'inspect_reset',
    },
    crane_open=CRANE_OPEN,
    extra={'inspect_near': [2.6, 2.4, 2.6]},
)


def animations():
    return all_animations(SPEC)
