"""Harpoen animations: draw and holster from the SMG set; a soft pneumatic shot; a one-spear reload; inspect.

The loaded spear is TACZ's `bullet_in_mag` bone: TACZ hides it once the shot is gone and shows it again when
the reload feeds a new one (data: reload.feed.empty). The reload therefore carries a second spear,
`spear_reload`, which rests hidden inside the air chamber: the left hand fetches it from below the screen,
lays it in the rail's groove ahead of its seat and slides it back until the latch clicks, exactly onto the
loaded spear's place, and it slips back into hiding a little after the feed. The hand and the carried spear
share key times and linear interpolation so they move as one.
"""
import smg_anim
from anim import Anim, CONSTRAINT
from harpoen import HIDE
from smg_anim import SmgSpec

SPEC = SmgSpec(sounds={}, kick=0.6)

FEED_T = 2.3                   # matches the gun data's reload.feed.empty
CARRY_ROT = [12, -18, 0]       # left forearm angled down and back out of the screen while it holds the spear
HOLD = [-0.95, 3.21, -1.31]    # lefthand offset: palm under the spear's shaft, spear 6 units ahead of its seat
PUSH = 6.0
SOUNDS = {
    0.1: 'tacz:hk_mp5a5/hk_mp5a5_reload_cloth', 0.9: 'tacz:rhino357/rhino_reload_clothes_light',
    1.5: 'tacz:springfield1873/springfield1873_reload_load', 2.25: 'tacz:hk_mp5a5/hk_mp5a5_reload_empty_boltclose',
    2.9: 'tacz:hk_mp5a5/hk_mp5a5_reload_end',
}


def _add(a, b):
    return [round(x + y, 4) for x, y in zip(a, b)]


def shoot():
    a = Anim(0.5).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.03: [-3.2, 0.4, 1.2], 0.1: [-1.4, 0.1, 0.5], 0.22: [0.3, 0, -0.2], 0.4: [0, 0, 0],
                   0.5: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.03: [0, 0.15, 1.3], 0.12: [0, 0.05, 0.5], 0.3: [0, 0, 0], 0.5: [0, 0, 0]})
    # the spear leaves along the rail (TACZ hides it as soon as the gun reads empty)
    a.pos('bullet_in_mag', {0: [0, 0, 0], 0.04: [0, 0, -16], 0.5: [0, 0, -16]}, smooth=False)
    a.rot('trigger', {0: [12, 0, 0], 0.12: [0, 0, 0]}, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.03: [-0.4, 0, 0.5], 0.08: [0.2, 0, -0.3], 0.16: [0, 0, 0], 0.5: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def reload():
    L = 3.5
    a = Anim(L).with_hands()
    tilt = [-6, 4, -12]
    a.rot('root', {0: [0, 0, 0], 0.35: tilt, 1.5: [-7, 4, -13], 2.2: tilt, 2.27: [-4.5, 3, -10], 2.4: tilt,
                   2.7: [-5, 3, -10], 3.2: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.35: [0.3, -0.6, 1.2], 2.2: [0.3, -0.6, 1.2], 2.27: [0.3, -0.45, 1.5],
                   2.4: [0.3, -0.6, 1.2], 3.2: [0, 0, 0], L: [0, 0, 0]})
    # left hand: off the chamber, down out of view to fetch a spear, back up holding it
    hold = HOLD
    raised = _add(HOLD, [1.55, 0.8, 0])
    below = _add(HOLD, [3.4, -8.2, 2.3])
    seated = _add(HOLD, [0, 0, PUSH])
    away = [3.0, -12.0, 6.0]
    carry = {1.0: below, 1.35: raised, 1.55: hold, 2.25: seated, 2.6: seated}
    a.pos('lefthand', {0: [0, 0, 0], 0.12: [0, 0, 0], 0.45: away, 0.95: away, **carry, 2.95: [0, 0, 0], L: [0, 0, 0]},
          smooth=False)
    a.rot('lefthand', {0: [0, 0, 0], 0.12: [0, 0, 0], 0.45: [-20, 10, -10], 0.95: [-20, 10, -10],
                       **{t: CARRY_ROT for t in carry}, 2.95: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
    # the carried spear follows the hand exactly, from its hiding place in the chamber to the loaded spear's seat
    seat = [-HIDE[0], -HIDE[1], -HIDE[2]]
    spear = {t: _add(seat, _add(v, [-hold[0], -hold[1], -hold[2] - PUSH])) for t, v in carry.items()}
    hide_t = FEED_T + 0.3
    a.pos('spear_reload', {0: [0, 0, 0], 0.999: [0, 0, 0], **spear, hide_t: seat, hide_t + 0.001: [0, 0, 0],
                           L: [0, 0, 0]}, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.35: [0.6, 0, 0.5], 1.55: [0.2, 0, 0.2], 2.25: [0.2, 0, 0.2], 2.29: [1.0, 0, -0.6],
                     2.45: [0, 0, 0], L: [0, 0, 0]})
    for t, s in SOUNDS.items():
        a.sound(t, s)
    return a


def inspect():
    """Left side, right side, then up to the eye to look down the spear, and down again."""
    L = 5.0
    a = Anim(L).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.7: [-6, -36, -14], 1.6: [-8, -40, -16], 2.2: [-4, 26, 12], 3.0: [-6, 30, 14],
                   3.5: [-10, 3, -3], 4.3: [-11, 2, -2], 4.75: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.7: [0.4, 0.8, -1.6], 1.6: [0.5, 0.9, -1.4], 2.2: [-0.4, 0.8, -1.6],
                   3.0: [-0.4, 0.9, -1.4], 3.5: [1.4, 1.6, 1.2], 4.3: [1.4, 1.7, 1.2], 4.75: [0, 0, 0], L: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.7: [0.5, -1.2, 0.3], 2.2: [0.4, 1.0, -0.3], 3.5: [-0.4, 0, 0], 4.75: [0, 0, 0],
                     L: [0, 0, 0]})
    for t, s in ((0.1, 'inspect_raise'), (1.4, 'inspect_turn'), (3.2, 'inspect_cloth'), (4.3, 'inspect_end')):
        a.sound(t, 'tacz:hk_mp5a5/hk_mp5a5_' + s)
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def animations():
    r = reload().to_json()
    return {
        'static_idle': smg_anim.idle(SPEC).to_json(),
        'static_bolt_caught': Anim(0.0333).to_json(),
        'draw': smg_anim.draw(SPEC).to_json(),
        'put_away': smg_anim.put_away(SPEC).to_json(),
        'shoot': shoot().to_json(),
        'reload_empty': r,
        'reload_tactical': r,
        'inspect': inspect().to_json(),
        'inspect_empty': inspect().to_json(),
    }
