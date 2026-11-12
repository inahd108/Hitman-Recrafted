"""Kievit animations: the break-action set (two barrels, extract, feed one or two rounds), scaled to a pocket pistol.

The barrels tip up instead of dropping (negative x about the hinge at their top rear). For loading, the gun
takes the pistol reload tilt (its left side towards the camera), so the tipped barrels and the open breech
stand clear above the fist. The pistol rig holds it in the right hand alone; the left hand comes in (bone L, as
in the pistol reloads) low and forward along the barrels, its forearm running down and out to the left rather
than back at the camera, to tip the barrels, feed rounds and snap the barrels shut. Draw and holster come from
the pistol set, and the inspect turns are the pistol's. Timing is the break-action timing; sounds are TACZ's
revolver sounds keyed to it.
"""
import breakaction_anim as B
import pistol_anim
from anim import Anim, track
from breakaction_anim import BreakSpec
from pistol_anim import PistolSpec

R = 'tacz:rhino357/rhino_'
SPEC = BreakSpec(open_deg=-52.0, lever_deg=-35.0, extract=0.3, kick=0.72, extra={'inspect_near': [2.4, 2.2, 2.4]})
DRAW = PistolSpec(slide_travel=0.0, sounds={}, hammer=False, pace=0.85)

REST_L = ([0, 0, 0], [0, 0, 0])
# Left-hand poses (bone L): the palm works low and forward along the barrels, and the forearm runs down and
# out to the left (close to the pistol racking angle), never back at the camera, so the breech stays in view.
TIP = ([-7.15, 12.06, -9.24], [-84, 6, -24])     # palm under the barrels' muzzle end
LIFT = ([-7.02, 13.79, -9.33], [-84, -6, -12])   # ... starting them up on the hinge (they swing on by themselves)
FEED = ([-6.21, 10.29, -7.04], [-72, -6, -12])   # a round held low behind the open breech
FETCH = ([-5.81, 9.49, -6.64], [-72, -6, -12])   # ... dipping for the second round
CLOSE = ([-7.01, 16.29, -10.14], [-72, -6, -12]) # palm on the tipped barrels' muzzle end
SHUT = ([-7.02, 14.89, -10.13], [-84, -6, -12])  # ... pressing them down
SHOW = [-10, -36, -28]                   # the pistol reload tilt: the gun's left side and the open breech in view
NEAR = [-0.8, 2.6, 2.2]


def _hand(a, keys):
    a.pos('L', {t: v[0] for t, v in keys.items()})
    a.rot('L', {t: v[1] for t, v in keys.items()})


def shoot():
    a = B.shoot(SPEC, False)
    # single action: the hammer falls, then the thumb draws it back for the second barrel
    a.rot('hammer', {0: [40, 0, 0], 0.3: [40, 0, 0], 0.42: [-6, 0, 0], 0.48: [0, 0, 0]}, smooth=False)
    return a


def reload(empty):
    a = B.reload(SPEC, empty)
    a.bones.pop('lefthand', None)
    L = a.length
    if empty:
        t_open, t_done, t_tip0, t_tip1, t_close = 0.23, 0.4, 0.7, 0.9, 2.05
        hand = {0: REST_L, 0.06: REST_L, 0.2: TIP, t_open: TIP, t_done: LIFT, 0.5: LIFT, 0.75: REST_L, 1.15: REST_L,
                1.35: FEED, 1.58: FEED, 1.64: FETCH, 1.72: FEED, 1.92: FEED, 2.0: CLOSE,
                t_close + 0.04: SHUT, 2.2: SHUT, 2.42: REST_L, L: REST_L}
    else:
        t_open, t_done, t_tip0, t_tip1, t_close = 0.17, 0.32, 0.42, 0.55, 1.4
        hand = {0: REST_L, 0.02: REST_L, 0.14: TIP, t_open: TIP, t_done: LIFT, 0.4: LIFT, 0.62: REST_L, 0.92: REST_L,
                1.12: FEED, 1.3: FEED, 1.35: CLOSE, t_close + 0.04: SHUT, 1.55: SHUT, 1.78: REST_L, L: REST_L}
    a.rot('root', {0: [0, 0, 0], 0.12: [-5, -14, -12], t_open: [-6, -20, -16], t_done: [-8, -26, -20],
                   t_tip0: [-9, -33, -25], t_tip1: SHOW, t_close - 0.05: [SHOW[0] + 1, SHOW[1], SHOW[2] - 1],
                   t_close + 0.05: [SHOW[0] + 4, SHOW[1] + 6, SHOW[2] + 4], t_close + 0.17: [-2, -10, -8],
                   t_close + 0.3: [0.5, 0, 0.3], L - 0.05: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.12: [-0.3, 1.0, 0.9], t_done: [-0.6, 2.0, 1.7], t_tip1: NEAR,
                   t_close - 0.05: NEAR, t_close + 0.05: [NEAR[0], NEAR[1] - 0.4, NEAR[2]],
                   t_close + 0.17: [-0.3, 0.6, 0.6], t_close + 0.3: [0, -0.05, 0], L - 0.05: [0, 0, 0], L: [0, 0, 0]})
    _hand(a, hand)
    if empty:
        for t, s in ((0.0, 'reload_raise'), (0.17, 'inspect_rift'), (0.34, 'reload_eject'), (0.62, 'reload_shell'),
                     (0.95, 'reload_clothes_light'), (1.52, 'reload_bulletin'), (1.85, 'reload_bulletin'),
                     (2.05, 'reload_cylinder_close'), (2.3, 'reload_reset')):
            a.sound(t, R + s)
    else:
        for t, s in ((0.0, 'reload_raise'), (0.05, 'inspect_rift'), (0.27, 'reload_eject'), (0.5, 'reload_shell'),
                     (0.8, 'reload_clothes_light'), (1.3, 'reload_bulletin'), (1.4, 'reload_cylinder_close'),
                     (1.6, 'reload_reset')):
            a.sound(t, R + s)
    return a


def inspect(empty):
    """The break-action inspect (left side, right side, along the rib), then tip the barrels up and look in."""
    a = B.inspect(SPEC, empty)
    a.bones.pop('lefthand', None)
    L = a.length
    o = -40.0
    a.rot('barrels', {0: [0, 0, 0], 6.17: [0, 0, 0], 6.33: [o - 2, 0, 0], 6.45: [o, 0, 0], 7.0: [o - 2, 0, 0],
                      7.07: [o, 0, 0], 7.13: [0, 0, 0], L: [0, 0, 0]})
    pos = a.bones['root']['position']
    for k in list(pos):
        if float(k) >= 5.9:
            del pos[k]
    # the pistol inspect's stronger turns (the Reiger's) keep more of the little gun clear of the fist
    left, right = [-6, -58, -12], [-6, 52, 12]
    a.rot('root', {0: [0, 0, 0], 0.7: left, 2.0: [-8, -62, -14], 2.3: [-4, -8, -6], 2.75: right, 3.9: [-8, 56, 14],
                   4.5: [-12, 6, 2], 5.4: [-10, 4, 1], 5.9: [-6, -12, -8], 6.3: SHOW,
                   7.0: [SHOW[0] + 1, SHOW[1], SHOW[2] - 1], 7.16: [SHOW[0] + 4, SHOW[1] + 6, SHOW[2] + 4],
                   7.4: [-2, -10, -8], 7.7: [0.5, 0, 0.3], 7.9: [0, 0, 0], L: [0, 0, 0]})
    pos.update(track({5.9: [0, 0.8, 0], 6.3: NEAR, 7.0: NEAR, 7.16: [NEAR[0], NEAR[1] - 0.4, NEAR[2]],
                      7.4: [-0.3, 0.4, 0.5], 7.9: [0, 0, 0], L: [0, 0, 0]}))
    _hand(a, {0: REST_L, 5.8: REST_L, 6.1: TIP, 6.33: LIFT, 6.6: REST_L, 6.8: REST_L, 6.98: CLOSE, 7.1: SHUT,
              7.3: SHUT, 7.6: REST_L, L: REST_L})
    for t, s in ((0.0, 'inspect_start'), (2.3, 'inspect_rotate'), (6.13, 'inspect_rift'), (7.1, 'reload_cylinder_close'),
                 (7.5, 'inspect_reset')):
        a.sound(t, R + s)
    return a


def animations():
    return {
        'static_idle': B.idle(SPEC).to_json(),
        'static_bolt_caught': Anim(0.0333).to_json(),
        'draw': pistol_anim.draw(DRAW).to_json(),
        'put_away': pistol_anim.put_away(DRAW).to_json(),
        'shoot': shoot().to_json(),
        'reload_tactical': reload(False).to_json(),
        'reload_empty': reload(True).to_json(),
        'inspect': inspect(False).to_json(),
        'inspect_empty': inspect(True).to_json(),
    }
