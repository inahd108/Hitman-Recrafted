"""Falco timing (TACZ's bundled .308 marksman-rifle sounds); empty reloads end on the bolt release."""
from falco import MAG_DEG
from smg_anim import SmgSpec, all_animations

S = 'tacz:scar_h/p05_ar_schotel_'
SPEC = SmgSpec(
    sounds={
        'raise': S + 'reload_raise', 'magout': S + 'reload_ubgl_magout', 'maghit': S + 'branched_reload_magin',
        'end': S + 'reload_end',
        'empty_start': S + 'reload_empty_raise', 'mag_drop': 'tacz:mag_drop_sound/iw8_phys_mag_drop_ar_metal_dirt_04',
        'charge': S + 'reload_empty_charge', 'empty_end': S + 'reload_empty_end',
        'inspect_start': S + 'inspect_raise', 'inspect_rotate': S + 'inspect_magrattle', 'inspect_turn': S + 'inspect_rotate',
        'inspect_end': S + 'inspect_end',
    },
    grip_deg=MAG_DEG,
    mag_out=1.6,
    hand_to_mag=(0, -3.2, 6.4),
    bolt_travel=1.3,
    kick=1.6,
    extra={'empty_action': 'release', 'hand_to_release': (-0.6, 0.2, 9.0), 'reload_tilt': [-8, -18, -32],
           'reload_near': [-1.0, 1.2, -1.8], 'inspect_near': [0.4, 0.8, -3.0], 'inspect_left': [-6, -36, -14],
           'inspect_right': [-4, 20, 8]},
)


def animations():
    return all_animations(SPEC)
