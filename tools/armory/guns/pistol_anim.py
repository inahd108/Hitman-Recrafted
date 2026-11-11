"""One set of handgun animations, tuned per gun: draw, holster, fire, two reloads, inspect.

Conventions (as in TACZ's own packs): positions are model units relative to rest, +z moves
towards the shooter; rotations are degrees added to the rest rotation; negative x lifts the muzzle.
"""
import math
from dataclasses import dataclass, field

from anim import Anim, CONSTRAINT


@dataclass
class PistolSpec:
    slide_travel: float
    sounds: dict                       # logical event -> sound id (missing events are silent)
    grip_deg: float = 16.0
    mag_out: float = 5.9               # how far the magazine slides down before it leaves the grip
    kick: float = 1.0                  # recoil strength
    hammer: bool = True
    pace: float = 1.0                  # < 1 is quicker
    extra: dict = field(default_factory=dict)


def _along(spec, d):
    a = math.radians(spec.grip_deg)
    return [0.0, -math.cos(a) * d, math.sin(a) * d]


def _t(spec, t):
    return round(t * spec.pace, 4)


def _snd(a, spec, t, key):
    if spec.sounds.get(key):
        a.sound(_t(spec, t), spec.sounds[key])


def idle(spec):
    a = Anim(0.0333).with_hands()
    a.static('root', rotation=[0, 0, 0], position=[0, 0, 0])
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def bolt_caught(spec):
    a = Anim(0.0333)
    a.static('slide', position=[0, 0, spec.slide_travel])
    if spec.hammer:
        a.static('hammer', rotation=[-27.5, 0, 0])
    a.static('hold_release', rotation=[8, 0, 0])
    a.static('bullet', scale=0)
    return a


def shoot(spec):
    k = spec.kick
    a = Anim(0.5).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.033: [0, 0, 0], 0.066: [-11.5 * k, 1.6 * k, -1.8 * k],
                   0.16: [2.6 * k, -1.8 * k, -4.2 * k], 0.3: [0.5 * k, 0, 1.4 * k], 0.44: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.033: [0, 0.22 * k, 1.9 * k], 0.066: [0, 0.7 * k, 2.0 * k],
                   0.16: [0, 0.05, -0.25 * k], 0.3: [0, -0.1 * k, 0], 0.44: [0, 0, 0]})
    a.pos('slide', {0: [0, 0, 0], 0.05: [0, 0, spec.slide_travel], 0.12: [0, 0, 0]}, smooth=False)
    if spec.hammer:
        a.rot('hammer', {0: [37.5, 0, 0], 0.033: [-27.5, 0, 0], 0.07: [0, 0, 0]}, smooth=False)
    a.rot('trigger', {0: [-12, 0, 0], 0.09: [0, 0, 0]}, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.033: [0, 0, 0.9 * k], 0.066: [0, 0, -0.7 * k], 0.1: [0, 0, 0.35 * k],
                     0.16: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def draw(spec):
    L = _t(spec, 0.72)
    a = Anim(L).with_hands()
    a.rot('root', {0: [48, -28, 26], _t(spec, 0.18): [14, -10, 9], _t(spec, 0.36): [-4.5, 2, -2],
                   _t(spec, 0.52): [1.2, 0, 0.6], _t(spec, 0.68): [0, 0, 0]})
    a.pos('root', {0: [3, -11, 6], _t(spec, 0.18): [1, -3.5, 2], _t(spec, 0.36): [0, 0.35, -0.2],
                   _t(spec, 0.52): [0, -0.08, 0], _t(spec, 0.68): [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], _t(spec, 0.2): [0.6, 0, -0.5], _t(spec, 0.4): [-0.3, 0, 0.3],
                     _t(spec, 0.6): [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def put_away(spec):
    a = Anim(_t(spec, 0.42)).with_hands()
    a.rot('root', {0: [0, 0, 0], _t(spec, 0.12): [6, -4, 4], _t(spec, 0.4): [48, -28, 26]})
    a.pos('root', {0: [0, 0, 0], _t(spec, 0.12): [0.4, -1, 0.5], _t(spec, 0.4): [3, -11, 6]})
    a.rot('camera', {0: [0, 0, 0], _t(spec, 0.2): [0.5, 0, -0.4], _t(spec, 0.4): [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def reload(spec, empty):
    T = lambda t: _t(spec, t)          # noqa: E731
    L = T(2.45 if empty else 2.05)
    a = Anim(L).with_hands()
    tilt = [-10, -36, -28]
    near = [-0.8, 2.6, 2.2]
    back = L - T(0.42)
    a.rot('root', {0: [0, 0, 0], T(0.24): tilt, T(0.9): [-9, -34, -27], T(1.24): tilt, T(1.3): [-6, -36, -32],
                   T(1.42): tilt, back: [-6, -22, -26] if empty else tilt, L - T(0.1): [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], T(0.24): near, T(1.26): near, T(1.3): [near[0], near[1] + 0.6, near[2]],
                   T(1.42): near, back: [-0.6, 1.6, 1.4], L - T(0.1): [0, 0, 0], L: [0, 0, 0]})
    out1 = _along(spec, spec.mag_out)
    away = [3.0, -16.0, 1.5]
    a.pos('mag_and_lefthand', {0: [0, 0, 0], T(0.28): [0, 0, 0], T(0.38): out1, T(0.58): away, T(0.86): away,
                               T(1.06): out1, T(1.2): _along(spec, 1.2), T(1.3): [0, 0, 0], L: [0, 0, 0]})
    a.rot('mag_and_lefthand', {0: [0, 0, 0], T(0.38): [0, 0, 0], T(0.58): [-35, 10, -25], T(0.86): [-35, 10, -25],
                               T(1.06): [0, 0, 0], L: [0, 0, 0]})
    pre = 'empty_' if empty else ''
    _snd(a, spec, 0.0, pre + 'lift')
    _snd(a, spec, 0.28, pre + 'magout')
    _snd(a, spec, 1.22, pre + 'magin')
    if empty:
        a.pos('L', {0: [0, 0, 0], T(1.36): [0, 0, 0], T(1.5): [-6.5, 9.5, -3.2], T(1.62): [-8.0, 14.6, -1.8],
                    T(1.7): [-8.0, 14.6, -1.8], T(1.86): [-2.4, 3.0, 2.0], T(2.0): [0, 0, 0], L: [0, 0, 0]})
        a.rot('L', {0: [0, 0, 0], T(1.36): [0, 0, 0], T(1.62): [-76, 0, -70], T(1.7): [-79, 0, -72],
                    T(1.95): [0, 0, 0], L: [0, 0, 0]})
        a.pos('slide', {0: [0, 0, spec.slide_travel], T(1.66): [0, 0, spec.slide_travel], T(1.71): [0, 0, 0],
                        L: [0, 0, 0]}, smooth=False)
        a.rot('hold_release', {0: [8, 0, 0], T(1.66): [8, 0, 0], T(1.7): [0, 0, 0]}, smooth=False)
        if spec.hammer:
            a.rot('hammer', {0: [-27.5, 0, 0], T(1.66): [-27.5, 0, 0], T(1.72): [0, 0, 0]}, smooth=False)
        a.scale('bullet', {0: 0, T(0.7): 1})
        _snd(a, spec, 1.66, 'chamber')
        _snd(a, spec, 2.0, 'empty_end')
    else:
        _snd(a, spec, 1.7, 'end')
    a.rot('camera', {0: [0, 0, 0], T(0.3): [0.8, 0, 0.6], T(1.3): [0.2, 0, 0.2], T(1.34): [1.0, 0, -0.6],
                     T(1.5): [0, 0, 0], L: [0, 0, 0]})
    return a


def inspect(spec, empty=False):
    """Turn the pistol to show its left side, then its right side with the ejection port."""
    L = 4.0
    a = Anim(L).with_hands()
    left = [-6, -58, -12]
    right = [-6, 52, 12]
    a.rot('root', {0: [0, 0, 0], 0.55: left, 1.6: [-8, -62, -14], 2.15: right, 3.2: [-8, 56, 14],
                   3.65: [0, 0, 0], L: [0, 0, 0]})
    near = spec.extra.get('inspect_near', [2.0, 2.2, 2.4])
    a.pos('root', {0: [0, 0, 0], 0.55: near, 1.6: [near[0] + 0.1, near[1] + 0.1, near[2] + 0.2],
                   2.15: [near[0] - 0.4, near[1], near[2]], 3.2: [near[0] - 0.4, near[1] + 0.1, near[2] + 0.2],
                   3.65: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        a.static('slide', position=[0, 0, spec.slide_travel])
        a.static('bullet', scale=0)
    a.rot('camera', {0: [0, 0, 0], 0.55: [0.5, -1.2, 0.3], 2.15: [0.4, 1.0, -0.3], 3.65: [0, 0, 0], L: [0, 0, 0]})
    _snd(a, spec, 0.0, 'inspect_a')
    _snd(a, spec, 1.9, 'inspect_b')
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def all_animations(spec):
    return {
        'static_idle': idle(spec).to_json(),
        'static_bolt_caught': bolt_caught(spec).to_json(),
        'draw': draw(spec).to_json(),
        'put_away': put_away(spec).to_json(),
        'shoot': shoot(spec).to_json(),
        'reload_tactical': reload(spec, False).to_json(),
        'reload_empty': reload(spec, True).to_json(),
        'inspect': inspect(spec, False).to_json(),
        'inspect_empty': inspect(spec, True).to_json(),
    }
