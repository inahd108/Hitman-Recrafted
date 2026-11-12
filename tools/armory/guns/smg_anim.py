"""Compact SMG/PDW animations: magazine in the pistol grip, left hand on a foregrip, T charging handle.

The left hand and the magazine share mag_and_lefthand (as in the pistol rig); the lefthand bone carries
the hand from the foregrip to the magazine base or the charging handle and back. Conventions as pistol_anim.
"""
import math
from dataclasses import dataclass, field

from anim import Anim, CONSTRAINT


@dataclass
class SmgSpec:
    sounds: dict
    grip_deg: float = 9.0
    mag_out: float = 5.6               # slide along the grip before it leaves the well
    hand_to_mag: tuple = (0, -3.0, 9.4)
    hand_to_charge: tuple = (-0.75, 5.3, 16.5)
    charge_rot: tuple = (55, 20, -53)          # forearm turned up and away from the camera
    bolt_travel: float = 1.2
    charge_travel: float = 1.6
    kick: float = 1.0
    extra: dict = field(default_factory=dict)


def _along(spec, d):
    a = math.radians(spec.grip_deg)
    return [0.0, -math.cos(a) * d, math.sin(a) * d]


def _snd(a, spec, t, key):
    if spec.sounds.get(key):
        a.sound(t, spec.sounds[key])


def idle(spec):
    a = Anim(0.0333).with_hands()
    a.static('root', rotation=[0, 0, 0], position=[0, 0, 0])
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def bolt_caught(spec):
    a = Anim(0.0333)
    a.static('bolt', position=[0, 0, spec.bolt_travel])
    return a


def shoot(spec):
    k = spec.kick
    a = Anim(0.4).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.02: [0.4 * k, -0.3 * k, 1.1 * k], 0.035: [-1.2 * k, 0.2 * k, 1.4 * k],
                   0.07: [-0.3 * k, -0.1, -1.4 * k], 0.12: [0.1, 0.1, 0.6 * k], 0.22: [0, 0.1, -0.4 * k], 0.32: [0, 0, 0],
                   0.4: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.02: [0, 0, 0.3 * k], 0.035: [0, -0.1, 1.0 * k], 0.07: [0, -0.1, 1.0 * k],
                   0.13: [0, -0.05, 0], 0.4: [0, 0, 0]})
    a.pos('bolt', {0: [0, 0, 0], 0.02: [0, 0, spec.bolt_travel], 0.06: [0, 0, 0]}, smooth=False)
    a.rot('trigger', {0: [12, 0, 0], 0.06: [0, 0, 0]}, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.02: [-0.3 * k, 0, 0.5 * k], 0.05: [0.2 * k, 0, -0.4 * k], 0.1: [0, 0, 0], 0.4: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def draw(spec):
    a = Anim(0.6).with_hands()
    a.rot('root', {0: [24, -24, 50], 0.1: [16, -14, 28], 0.22: [5, -3, 5], 0.32: [-1, -0.6, 1.2], 0.45: [0.3, 0, -0.3],
                   0.55: [0, 0, 0], 0.6: [0, 0, 0]})
    a.pos('root', {0: [2, -11, 4], 0.1: [1.2, -5.5, 2.4], 0.22: [0.3, -1, 0.6], 0.32: [0, 0.2, -0.1], 0.45: [0, 0, 0],
                   0.6: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.15: [0.6, 0, -0.5], 0.32: [-0.3, 0, 0.3], 0.5: [0, 0, 0], 0.6: [0, 0, 0]})
    return a


def put_away(spec):
    a = Anim(0.45).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.12: [5, -5, 8], 0.42: [24, -24, 50], 0.45: [24, -24, 50]})
    a.pos('root', {0: [0, 0, 0], 0.12: [0.3, -1, 0.4], 0.42: [2, -11, 4], 0.45: [2, -11, 4]})
    return a


def reload(spec, empty):
    L = 2.93 if empty else 2.3
    a = Anim(L).with_hands()
    tilt = [-10, -22, -40]
    near = [-1.4, 1.4, -1.0]
    mag_t = {'grab': 0.2, 'out': 0.4, 'away': 0.62, 'below': 1.0, 'hit': 1.2, 'in': 1.433} if empty else \
        {'grab': 0.45, 'out': 0.7, 'away': 0.95, 'below': 1.0, 'hit': 1.1, 'in': 1.233}
    back = 2.55 if empty else 1.95
    a.rot('root', {0: [0, 0, 0], 0.15: [-2, 12, 20], 0.35: tilt, mag_t['hit']: [-12, -24, -42],
                   mag_t['in']: [-9, -21, -38], mag_t['in'] + 0.1: tilt, back - 0.4: [-8, -14, -24],
                   back: [1, 0.5, 1], L - 0.08: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.15: [-0.2, 1.4, -1.0], 0.35: near, mag_t['in']: near,
                   mag_t['in'] + 0.08: [near[0], near[1] + 0.4, near[2]], back - 0.4: [-0.6, 0.9, -1.0], back: [0, -0.4, 0.4],
                   L - 0.08: [0, 0, 0], L: [0, 0, 0]})
    out = _along(spec, spec.mag_out)
    away = [2.5, -15.0, 3.0]
    below = _along(spec, 2.0)
    a.pos('mag_and_lefthand', {0: [0, 0, 0], mag_t['out'] - 0.04: [0, 0, 0], mag_t['out'] + 0.08: out, mag_t['away']: away,
                               mag_t['below'] - 0.15: away, mag_t['below']: below, mag_t['hit']: _along(spec, 0.6),
                               mag_t['in']: [0, 0, 0], L: [0, 0, 0]})
    a.rot('mag_and_lefthand', {0: [0, 0, 0], mag_t['out'] + 0.08: [0, 0, 0], mag_t['away']: [-30, 10, -20],
                               mag_t['below'] - 0.15: [-30, 10, -20], mag_t['below']: [6, 0, 0], mag_t['in']: [0, 0, 0],
                               L: [0, 0, 0]})
    hm = list(spec.hand_to_mag)
    hc = list(spec.hand_to_charge)
    hand = {0: [0, 0, 0], mag_t['grab'] - 0.15: [0, 0, 0], mag_t['grab']: hm, mag_t['in'] + 0.05: hm}
    hrot = {0: [0, 0, 0], mag_t['grab'] - 0.15: [0, 0, 0], mag_t['grab']: [-12, 0, 0], mag_t['in'] + 0.05: [-12, 0, 0]}
    if empty:
        hand.update({1.6: [3, 2.5, 8], 1.75: hc, 1.95: hc, 2.05: [hc[0], hc[1], hc[2] + 2.5], 2.12: hc,
                     2.3: [3, 2.5, 8], 2.45: [0, 0, 0], L: [0, 0, 0]})
        cr = list(spec.charge_rot)
        hrot.update({1.6: [10, 8, -20], 1.75: cr, 2.12: cr, 2.3: [10, 8, -20], 2.45: [0, 0, 0], L: [0, 0, 0]})
        a.pos('bolt_pull', {0: [0, 0, 0], 1.98: [0, 0, 0], 2.05: [0, 0, spec.charge_travel], 2.1: [0, 0, 0], L: [0, 0, 0]},
              smooth=False)
        a.pos('bolt', {0: [0, 0, spec.bolt_travel], 2.05: [0, 0, spec.bolt_travel + 0.3], 2.1: [0, 0, 0], L: [0, 0, 0]},
              smooth=False)
    else:
        hand.update({mag_t['in'] + 0.3: [0, -1, 3], mag_t['in'] + 0.45: [0, 0, 0], L: [0, 0, 0]})
        hrot.update({mag_t['in'] + 0.45: [0, 0, 0], L: [0, 0, 0]})
    a.pos('lefthand', hand)
    a.rot('lefthand', hrot)
    if empty:
        _snd(a, spec, 0.0, 'empty_start')
        _snd(a, spec, 0.4, 'magout')
        _snd(a, spec, 0.4667, 'empty_turn')
        _snd(a, spec, 0.8333, 'mag_drop')
        _snd(a, spec, 1.2, 'maghit')
        _snd(a, spec, 1.4333, 'magin')
        _snd(a, spec, 2.0333, 'charge')
        _snd(a, spec, 2.4667, 'end')
    else:
        _snd(a, spec, 0.0667, 'raise')
        _snd(a, spec, 0.2333, 'magdown')
        _snd(a, spec, 0.7, 'magout')
        _snd(a, spec, 1.1, 'maghit')
        _snd(a, spec, 1.2333, 'magin')
        _snd(a, spec, 1.7667, 'end')
    a.rot('camera', {0: [0, 0, 0], 0.3: [0.6, 0, 0.5], mag_t['hit']: [1.0, 0, -0.6], mag_t['hit'] + 0.12: [0, 0, 0],
                     L: [0, 0, 0]})
    return a


def inspect(spec, empty=False):
    L = 5.1
    a = Anim(L).with_hands()
    near = spec.extra.get('inspect_near', [0.6, 1.0, -1.0])
    left = [-6, -42, -16]
    right = [-6, 36, 14]
    a.rot('root', {0: [0, 0, 0], 0.7: left, 1.05: [-7, -45, -18], 1.5: right, 1.65: [-8, 30, -10], 2.6: [-10, 26, -14],
                   2.8: [-6, 30, -8], 3.25: [-16, 8, 4], 4.2: [-14, 4, 2], 4.75: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.7: near, 1.5: [near[0] - 0.8, near[1], near[2]], 2.8: [near[0] - 0.8, near[1] + 0.3, near[2]],
                   3.25: [0, 0.8, -0.4], 4.2: [0, 0.8, -0.4], 4.75: [0, 0, 0], L: [0, 0, 0]})
    hm = list(spec.hand_to_mag)
    a.pos('lefthand', {0: [0, 0, 0], 1.45: [0, 0, 0], 1.62: hm, 2.85: hm, 3.1: [0, 0, 0], L: [0, 0, 0]})
    a.rot('lefthand', {0: [0, 0, 0], 1.45: [0, 0, 0], 1.62: [-12, 0, 0], 2.85: [-12, 0, 0], 3.1: [0, 0, 0], L: [0, 0, 0]})
    part = _along(spec, 2.6)
    a.pos('mag_and_lefthand', {0: [0, 0, 0], 1.62: [0, 0, 0], 1.75: part, 2.5: part, 2.633: _along(spec, 0.5),
                               2.8: [0, 0, 0], L: [0, 0, 0]})
    a.rot('mag_and_lefthand', {0: [0, 0, 0], 1.75: [0, 0, 0], 2.0: [0, 0, 18], 2.35: [0, 0, 18], 2.55: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        a.static('bolt', position=[0, 0, spec.bolt_travel])
    a.rot('camera', {0: [0, 0, 0], 0.7: [0.5, -1.2, 0.3], 1.5: [0.4, 1.0, -0.3], 2.633: [0.8, 0, -0.5], 3.25: [-0.4, 0, 0],
                     4.75: [0, 0, 0], L: [0, 0, 0]})
    _snd(a, spec, 0.1333, 'inspect_start')
    _snd(a, spec, 1.1, 'inspect_rotate')
    _snd(a, spec, 1.6667, 'magout')
    _snd(a, spec, 2.6333, 'maghit')
    _snd(a, spec, 2.8, 'magin')
    _snd(a, spec, 3.2333, 'inspect_turn')
    _snd(a, spec, 4.3, 'inspect_end')
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
