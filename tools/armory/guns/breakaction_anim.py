"""Break-action (double-barrel) animations, timed to TACZ's double-barrel reload and inspect sounds.

Bones: root, barrels (rotate about the hinge: positive x drops the muzzle), lever, extractor, shell_1/shell_2
(children of the extractor), lefthand (follows the fore-end down, fetches shells), camera, constraint.
"""
from dataclasses import dataclass, field

from anim import Anim, CONSTRAINT


@dataclass
class BreakSpec:
    open_deg: float = 52.0          # barrels open this far
    lever_deg: float = -20.0
    extract: float = 0.35           # extractor stroke
    kick: float = 1.0
    extra: dict = field(default_factory=dict)


# left-hand offsets: with the fore-end when the barrels are down, and at the breech with fresh shells
HAND_DOWN = [0, -2.4, 0.9]
HAND_AWAY = [4.4, -8.7, 3.8]


def idle(spec):
    a = Anim(0.0333).with_hands()
    a.static('root', rotation=[0, 0, 0], position=[0, 0, 0])
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def shoot(spec, both):
    k = spec.kick * (1.45 if both else 1.0)
    L = 1.0 if both else 0.8
    a = Anim(L).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.033: [3.5 * k, 0, 5 * k], 0.066: [-19 * k, 0, -9 * k], 0.1: [-21 * k, 0, -7 * k],
                   0.2: [-14 * k, 0.3, -5 * k], 0.33: [-3.5 * k, -0.8, -2.4], 0.45: [2.6, 0.4, 1.5], 0.6: [0, -0.8, -0.4],
                   0.75: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.033: [0, 0.3 * k, 1.2 * k], 0.066: [0, 0.9 * k, 3.2 * k], 0.15: [0, 0.6 * k, 2.4 * k],
                   0.3: [0, 0.1, 0.6 * k], 0.45: [0, -0.15, -0.2], 0.65: [0, 0, 0], L: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.033: [-1.0 * k, 0, 1.4 * k], 0.07: [0.8 * k, 0, -1.2 * k], 0.12: [-0.3 * k, 0, 0.5 * k],
                     0.22: [0, 0, 0], L: [0, 0, 0]})
    a.rot('trigger', {0: [14, 0, 0], 0.12: [0, 0, 0]}, smooth=False)
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def draw(spec):
    a = Anim(0.6).with_hands()
    a.rot('root', {0: [20, -26, 58], 0.1: [15, -14, 32], 0.2: [7, -3, 5.6], 0.3: [-0.8, -0.8, 1.8], 0.42: [0.4, 0, -0.4],
                   0.55: [0, 0, 0], 0.6: [0, 0, 0]})
    a.pos('root', {0: [2, -12, 6], 0.1: [1.2, -6, 3], 0.2: [0.3, -1.2, 0.8], 0.3: [0, 0.2, -0.1], 0.45: [0, 0, 0], 0.6: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.15: [0.6, 0, -0.6], 0.32: [-0.3, 0, 0.3], 0.5: [0, 0, 0], 0.6: [0, 0, 0]})
    return a


def put_away(spec):
    a = Anim(0.5).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.12: [5, -5, 8], 0.45: [20, -26, 58], 0.5: [20, -26, 58]})
    a.pos('root', {0: [0, 0, 0], 0.12: [0.3, -1, 0.5], 0.45: [2, -12, 6], 0.5: [2, -12, 6]})
    return a


def _open(a, spec, t_lever, t_open, t_done):
    """Lever across, barrels drop; the left hand rides down with the fore-end."""
    a.rot('lever', {0: [0, 0, 0], t_lever: [0, 0, 0], t_lever + 0.06: [0, spec.lever_deg, 0]}, smooth=False)
    a.rot('barrels', {0: [0, 0, 0], t_open: [0, 0, 0], t_done: [spec.open_deg + 2, 0, 0],
                      t_done + 0.1: [spec.open_deg - 1, 0, 0], t_done + 0.2: [spec.open_deg, 0, 0]})


def _close(a, spec, t_lever, t_close, L, rot_keys):
    a.rot('barrels', rot_keys | {t_close: [spec.open_deg, 0, 0], t_close + 0.08: [0, 0, 0], L: [0, 0, 0]})
    a.rot('lever', {0: [0, 0, 0], t_lever: [0, 0, 0], t_lever + 0.06: [0, spec.lever_deg, 0],
                    t_close + 0.06: [0, spec.lever_deg, 0], t_close + 0.1: [0, 0, 0], L: [0, 0, 0]}, smooth=False)


def _eject(a, name, t, far=1.0):
    """A spent shell kicks out of its chamber, flips back over the shoulder and is gone."""
    s = far
    a.pos(name, {0: [0, 0, 0], t: [0, 0, 0], t + 0.033: [-0.2 * s, 0.1, 3.0], t + 0.067: [-0.4 * s, 0, 5.6],
                 t + 0.13: [-0.5 * s, -0.2, 6.0], t + 0.2: [-0.8 * s, -1.4, 5.0], t + 0.27: [-1.5 * s, -4.1, 3.0],
                 t + 0.33: [-2.2 * s, -7.7, 0.1], t + 0.4: [-2.7 * s, -12.7, -6.0]})


def _feed(a, name, t_show, t_seat):
    """A fresh shell appears in the left hand above the breech and is pushed home.

    The keys join the shell's eject track (written first by _eject) rather than replacing it, so the spent
    shell still flies out before the fresh one is fed.
    """
    spent = a.bones.get(name, {}).get('position', {})
    a.pos(name, {t_show - 0.001: [-2.7, -12.7, -6.0], t_show: [0.2, 0.5, 2.1], t_seat - 0.08: [0, 0.12, 0.9],
                 t_seat: [0, 0, 0]})
    merged = {**spent, **a.bones[name]['position']}
    a.bones[name]['position'] = dict(sorted(merged.items(), key=lambda kv: float(kv[0])))


def reload(spec, empty):
    L = 2.5 if empty else 1.85
    a = Anim(L).with_hands()
    if empty:
        t_lever, t_open, t_done, t_ext, t_close = 0.17, 0.23, 0.4, 0.34, 2.05
    else:
        t_lever, t_open, t_done, t_ext, t_close = 0.03, 0.17, 0.32, 0.27, 1.4
    # push the muzzle down to break it open, then tip it muzzle-up so the open breech faces you
    show = [-30, -3, -4]
    t_tip0, t_tip1 = (0.7, 0.9) if empty else (0.42, 0.55)
    a.rot('root', {0: [0, 0, 0], 0.1: [4, 0.6, 2.2], t_open: [4.4, -0.4, 5.6], t_done: [10, 2.5, 6.9],
                   t_done + 0.1: [2.7, 2.7, 1.4], t_tip0: [0.9, 2.5, 1.9], t_tip1: show, t_close - 0.05: [-28, -2, -5],
                   t_close + 0.05: [-16.7, -2.1, -5.3], t_close + 0.15: [-3.9, -0.1, 1.5], t_close + 0.25: [0.4, 0, 0],
                   L - 0.05: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.1: [0.4, -0.3, 0.5], t_open: [0.4, 0.1, 0.7], t_done: [0.4, -0.6, 0.6],
                   t_tip0: [0.4, -0.4, 0.4], t_tip1: [-0.4, 0.2, 0.4], t_close - 0.05: [-0.4, 0.1, 0.4],
                   t_close + 0.05: [0.1, -0.8, 0.2], t_close + 0.15: [0, -0.1, 0.1], L - 0.05: [0, 0, 0], L: [0, 0, 0]})
    _open(a, spec, t_lever, t_open, t_done)
    _close(a, spec, t_lever, t_close, L, {0: [0, 0, 0], t_open: [0, 0, 0], t_done: [spec.open_deg + 2, 0, 0],
                                 t_done + 0.1: [spec.open_deg - 1, 0, 0], t_done + 0.2: [spec.open_deg, 0, 0]})
    a.pos('extractor', {0: [0, 0, 0], t_ext - 0.02: [0, 0, 0], t_ext: [0, 0, spec.extract],
                        t_close - 0.1: [0, 0, spec.extract], t_close - 0.02: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
    if empty:
        _eject(a, 'shell_1', t_ext, 1.0)
        _eject(a, 'shell_2', t_ext + 0.02, -0.7)
        _feed(a, 'shell_1', 1.38, 1.56)
        _feed(a, 'shell_2', 1.7, 1.89)
        a.scale('shell_1', {0: 1, t_ext + 0.4: 0, 1.38: 1})
        a.scale('shell_2', {0: 1, t_ext + 0.42: 0, 1.7: 1})
        hand = {0: [0, 0, 0], t_open: [0, 0, 0], t_done: HAND_DOWN, 0.5: HAND_DOWN, 0.75: HAND_AWAY,
                1.9: HAND_AWAY, t_close - 0.04: HAND_DOWN, t_close + 0.12: [0, 0, 0], L: [0, 0, 0]}
    else:
        _eject(a, 'shell_1', t_ext, 1.0)
        _feed(a, 'shell_1', 1.15, 1.33)
        a.scale('shell_1', {0: 1, t_ext + 0.4: 0, 1.15: 1})
        hand = {0: [0, 0, 0], t_open: [0, 0, 0], t_done: HAND_DOWN, 0.42: HAND_DOWN, 0.6: HAND_AWAY,
                1.25: HAND_AWAY, t_close - 0.04: HAND_DOWN, t_close + 0.12: [0, 0, 0], L: [0, 0, 0]}
    a.pos('lefthand', hand)
    away = 0.75 if empty else 0.6
    back = 1.9 if empty else 1.25
    a.rot('lefthand', {0: [0, 0, 0], t_done: [8, 0, 0], away: [-36, 22, 28], back: [-36, 22, 28],
                       t_close - 0.04: [8, 0, 0], t_close + 0.12: [0, 0, 0], L: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], t_done: [0.8, 0, 0.6], t_ext + 0.1: [-0.5, 0, -0.3], t_close: [0.3, 0, 0.2],
                     t_close + 0.08: [-1.0, 0, -0.8], t_close + 0.25: [0, 0, 0], L: [0, 0, 0]})
    return a


def inspect(spec, empty=False):
    """Left side, a turn to the right side, a look down the rib, then open it up, check the chambers and snap it shut."""
    L = 8.0
    a = Anim(L).with_hands()
    near = spec.extra.get('inspect_near', [0.6, 1.0, -1.6])
    left = [-6, -40, -18]
    right = [-6, 34, 12]
    a.rot('root', {0: [0, 0, 0], 0.7: left, 2.0: [-8, -44, -20], 2.3: [-4, -8, -6], 2.75: right, 3.9: [-8, 38, 14],
                   4.5: [-12, 6, 2], 5.4: [-10, 4, 1], 5.9: [-6, -2, 2], 6.3: [-30, -4, -5], 7.0: [-28, -3, -4],
                   7.16: [-6, -4, 3], 7.5: [1.5, -1, 0.5], 7.85: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.7: near, 2.0: [near[0] + 0.2, near[1], near[2] + 0.2], 2.3: [0.3, 0.8, -0.6],
                   2.75: [near[0] - 0.9, near[1], near[2]], 3.9: [near[0] - 0.9, near[1] + 0.1, near[2] + 0.2],
                   4.5: [0, 0.8, 0], 5.4: [0, 0.8, 0], 6.3: [-0.4, 0.3, 0.4], 7.1: [-0.4, 0.3, 0.4],
                   7.16: [0.2, 0.2, 0.2], 7.85: [0, 0, 0], L: [0, 0, 0]})
    o = 38.0
    a.rot('barrels', {0: [0, 0, 0], 6.17: [0, 0, 0], 6.33: [o + 2, 0, 0], 6.45: [o, 0, 0], 7.0: [o + 2, 0, 0],
                      7.07: [o, 0, 0], 7.13: [0, 0, 0], L: [0, 0, 0]})
    a.rot('lever', {0: [0, 0, 0], 6.07: [0, 0, 0], 6.13: [0, spec.lever_deg, 0], 7.1: [0, spec.lever_deg, 0],
                    7.14: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
    a.pos('lefthand', {0: [0, 0, 0], 6.17: [0, 0, 0], 6.33: [0, -1.8, 0.7], 7.07: [0, -1.8, 0.7], 7.16: [0, 0.2, 0],
                       7.4: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        a.static('shell_1', scale=0)
        a.static('shell_2', scale=0)
    a.rot('camera', {0: [0, 0, 0], 0.7: [0.5, -1.2, 0.3], 2.75: [0.4, 1.0, -0.3], 4.5: [-0.6, 0, 0], 6.33: [0.6, 0, 0.4],
                     7.16: [-0.8, 0, -0.6], 7.5: [0, 0, 0], L: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def all_animations(spec):
    return {
        'static_idle': idle(spec).to_json(),
        'static_bolt_caught': Anim(0.0333).to_json(),
        'draw': draw(spec).to_json(),
        'put_away': put_away(spec).to_json(),
        'shoot': shoot(spec, False).to_json(),
        'shoot_burst': shoot(spec, True).to_json(),
        'reload_tactical': reload(spec, False).to_json(),
        'reload_empty': reload(spec, True).to_json(),
        'reload_empty_easter': reload(spec, True).to_json(),
        'inspect': inspect(spec, False).to_json(),
        'inspect_empty': inspect(spec, True).to_json(),
    }
