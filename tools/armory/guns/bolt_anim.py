"""Bolt-action rifle animations: recoil, the bolt cycle after every shot, magazine reloads (the empty one
opens the bolt first and closes it after), and an inspect that checks the magazine and the chamber.

Bones: root, bullet_and_bolt (rotates about z to unlock, slides +z to open), righthand (works the bolt),
mag_and_lefthand (magazine + left hand), lefthand (from the fore-end to the magazine), camera, constraint.
"""
import math
from dataclasses import dataclass, field

from anim import Anim, CONSTRAINT
import smg_anim


@dataclass
class BoltSpec:
    sounds: dict
    lift_deg: float = 65.0            # bolt handle rotation to unlock
    travel: float = 3.2               # bolt pull
    hand_to_bolt: tuple = (-3.1, 1.4, -1.7)
    hand_bolt_rot: tuple = (14, -10, 42)
    hand_lift: tuple = (-3.45, 3.25, -1.7)
    hand_lift_rot: tuple = (15, -25, 56)
    hand_to_mag: tuple = (0.3, -1.3, 7.4)
    mag_out: float = 2.4
    kick: float = 1.0
    extra: dict = field(default_factory=dict)


def _snd(a, spec, t, key):
    if spec.sounds.get(key):
        a.sound(t, spec.sounds[key])


def idle(spec):
    a = Anim(0.0333).with_hands()
    a.static('root', rotation=[0, 0, 0], position=[0, 0, 0])
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def shoot(spec):
    k = spec.kick
    a = Anim(0.7).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.033: [1.0 * k, 0, 1.5 * k], 0.07: [-7 * k, 0.4, -2.5 * k], 0.12: [-5 * k, 0.2, -1.5 * k],
                   0.25: [-1.2 * k, -0.3, 0.5], 0.4: [0.5, 0, 0.3], 0.55: [0, 0, 0], 0.7: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.033: [0, 0.1, 0.8 * k], 0.07: [0, 0.5 * k, 2.4 * k], 0.15: [0, 0.3 * k, 1.4 * k],
                   0.3: [0, 0, 0.3], 0.5: [0, 0, 0], 0.7: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.033: [-0.6 * k, 0, 0.8 * k], 0.07: [0.5 * k, 0, -0.6 * k], 0.15: [0, 0, 0.2], 0.25: [0, 0, 0],
                     0.7: [0, 0, 0]})
    a.rot('trigger', {0: [14, 0, 0], 0.1: [0, 0, 0]}, smooth=False)
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def _cycle(a, spec, t0, hold_open=None, t_close=None):
    """Right hand to the handle, lift, pull back (and optionally hold), push forward, lock down, hand back.
    Returns the time the hand is back on the grip."""
    d, r = list(spec.hand_to_bolt), list(spec.hand_bolt_rot)
    lf, lr = list(spec.hand_lift), list(spec.hand_lift_rot)
    back = [lf[0], lf[1], lf[2] + spec.travel]
    t_lift, t_pull = t0 + 0.1, t0 + 0.2
    if hold_open is None:
        t_push, t_lock = t0 + 0.32, t0 + 0.4
    else:
        t_push, t_lock = t_close, t_close + 0.08
    t_home = t_lock + 0.22
    hand = {0: [0, 0, 0], t0: [0, 0, 0], t0 + 0.06: d, t_lift: lf, t_pull: back, t_push - 0.08: back,
            t_push: lf, t_lock: [lf[0] + 0.3, lf[1] - 0.6, lf[2]], t_home: [0, 0, 0]}
    hrot = {0: [0, 0, 0], t0: [0, 0, 0], t0 + 0.06: r, t_lift: lr, t_lock: lr, t_home: [0, 0, 0]}
    bolt_r = {0: [0, 0, 0], t0 + 0.06: [0, 0, 0], t_lift: [0, 0, spec.lift_deg], t_lock - 0.02: [0, 0, spec.lift_deg],
              t_lock: [0, 0, 0]}
    bolt_p = {0: [0, 0, 0], t_lift: [0, 0, 0], t_pull: [0, 0, spec.travel], t_push - 0.08: [0, 0, spec.travel],
              t_push: [0, 0, 0]}
    return hand, hrot, bolt_r, bolt_p, t_home


def bolt(spec):
    L = 0.85
    a = Anim(L).with_hands()
    hand, hrot, br, bp, home = _cycle(a, spec, 0.0)
    hand[L] = [0, 0, 0]
    hrot[L] = [0, 0, 0]
    a.pos('righthand', hand)
    a.rot('righthand', hrot)
    a.rot('bullet_and_bolt', br, smooth=False)
    a.pos('bullet_and_bolt', bp, smooth=False)
    a.rot('root', {0: [0, 0, 0], 0.1: [0.8, 0.2, 1.4], 0.2: [-0.2, 0, 2.5], 0.32: [-1, -0.3, 1.5], 0.45: [-0.5, 0.5, 0.5],
                   0.6: [0.8, -0.4, 1.8], 0.8: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.15: [-0.1, -0.3, 0], 0.25: [0, -0.4, 0.5], 0.4: [0.1, -0.4, 0.4], 0.55: [0.1, -0.1, -0.2],
                   0.8: [0, 0, 0], L: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.2: [0.2, 0.1, 0.1], 0.35: [0.1, -0.2, 0.3], 0.5: [0.1, 0, -0.2], 0.7: [0, 0, 0], L: [0, 0, 0]})
    _snd(a, spec, 0.05, 'bolt_out')
    _snd(a, spec, 0.3, 'bolt_in')
    _snd(a, spec, 0.6, 'shell_drop')
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def _along(d):
    return [0.0, -d, 0.0]


def reload(spec, empty):
    L = 3.7 if empty else 2.6
    a = Anim(L).with_hands()
    if empty:
        t = {'grab': 0.75, 'out': 0.85, 'away': 1.15, 'below': 1.7, 'hit': 1.85, 'in': 1.95, 'back': 2.15}
    else:
        t = {'grab': 0.3, 'out': 0.45, 'away': 0.75, 'below': 1.25, 'hit': 1.38, 'in': 1.45, 'back': 1.65}
    tilt = [-6, -16, -26]
    near = [-0.8, 0.8, -1.4]
    end = L - 0.9
    a.rot('root', {0: [0, 0, 0], 0.3: tilt, t['hit']: [-8, -18, -28], t['in']: [-5, -15, -24], t['in'] + 0.1: tilt,
                   end: [-2, -4, -6], end + 0.4: [0.4, 0.2, 0.4], L - 0.1: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.3: near, t['in']: near, t['in'] + 0.08: [near[0], near[1] + 0.3, near[2]], end: [-0.3, 0.3, -0.5],
                   L - 0.1: [0, 0, 0], L: [0, 0, 0]})
    out = _along(spec.mag_out)
    away = [2.0, -14.0, 2.0]
    a.pos('mag_and_lefthand', {0: [0, 0, 0], t['out'] - 0.04: [0, 0, 0], t['out'] + 0.08: out, t['away']: away,
                               t['below'] - 0.15: away, t['below']: _along(1.5), t['hit']: _along(0.4), t['in']: [0, 0, 0],
                               L: [0, 0, 0]})
    a.rot('mag_and_lefthand', {0: [0, 0, 0], t['out'] + 0.08: [0, 0, 0], t['away']: [-25, 10, -20], t['below'] - 0.15: [-25, 10, -20],
                               t['below']: [4, 0, 0], t['in']: [0, 0, 0], L: [0, 0, 0]})
    hm = list(spec.hand_to_mag)
    a.pos('lefthand', {0: [0, 0, 0], t['grab'] - 0.15: [0, 0, 0], t['grab']: hm, t['in'] + 0.05: hm, t['back']: [0, 0, 0], L: [0, 0, 0]})
    a.rot('lefthand', {0: [0, 0, 0], t['grab'] - 0.15: [0, 0, 0], t['grab']: [-12, 0, 0], t['in'] + 0.05: [-12, 0, 0],
                       t['back']: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        hand, hrot, br, bp, home = _cycle(a, spec, 0.15, hold_open=True, t_close=2.45)
        # while the bolt is held open, the right hand waits by the handle
        hand[L] = [0, 0, 0]
        hrot[L] = [0, 0, 0]
        hand_open = {k: v for k, v in hand.items() if k <= 0.35}
        hand_open.update({0.55: [0, 0, 0], 2.2: [0, 0, 0], 2.3: list(spec.hand_lift)})
        hand_open.update({k: v for k, v in hand.items() if k >= 2.3})
        hrot_open = {k: v for k, v in hrot.items() if k <= 0.35}
        hrot_open.update({0.55: [0, 0, 0], 2.2: [0, 0, 0], 2.3: list(spec.hand_lift_rot)})
        hrot_open.update({k: v for k, v in hrot.items() if k >= 2.3})
        a.pos('righthand', hand_open)
        a.rot('righthand', hrot_open)
        a.rot('bullet_and_bolt', br, smooth=False)
        a.pos('bullet_and_bolt', bp, smooth=False)
        _snd(a, spec, 0.0, 'raise')
        _snd(a, spec, 0.25, 'bolt_out')
        _snd(a, spec, 0.6, 'shell_drop')
        _snd(a, spec, 0.85, 'magout')
        _snd(a, spec, 1.95, 'magin')
        _snd(a, spec, 2.45, 'bolt_in')
        _snd(a, spec, 2.8, 'end')
    else:
        _snd(a, spec, 0.0, 'raise')
        _snd(a, spec, 0.45, 'magout')
        _snd(a, spec, 1.45, 'magin')
        _snd(a, spec, 1.65, 'end')
    a.rot('camera', {0: [0, 0, 0], 0.3: [0.6, 0, 0.5], t['hit']: [0.9, 0, -0.5], t['hit'] + 0.12: [0, 0, 0], L: [0, 0, 0]})
    return a


def inspect(spec, empty=False):
    L = 5.65
    a = Anim(L).with_hands()
    near = spec.extra.get('inspect_near', [0.4, 0.6, -2.4])
    left = [-5, -34, -12]
    a.rot('root', {0: [0, 0, 0], 0.6: left, 1.8: [-7, -36, -16], 2.6: [-5, -30, -10], 3.1: [-6, 20, 8], 4.5: [-7, 22, 9],
                   4.85: [-2, 0, 2], 5.4: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.6: near, 2.6: near, 3.1: [-0.6, 0.6, -1.0], 4.5: [-0.6, 0.6, -1.0], 5.4: [0, 0, 0], L: [0, 0, 0]})
    hm = list(spec.hand_to_mag)
    a.pos('lefthand', {0: [0, 0, 0], 0.45: [0, 0, 0], 0.6: hm, 2.45: hm, 2.7: [0, 0, 0], L: [0, 0, 0]})
    a.rot('lefthand', {0: [0, 0, 0], 0.45: [0, 0, 0], 0.6: [-12, 0, 0], 2.45: [-12, 0, 0], 2.7: [0, 0, 0], L: [0, 0, 0]})
    a.pos('mag_and_lefthand', {0: [0, 0, 0], 0.62: [0, 0, 0], 0.75: _along(1.8), 2.25: _along(1.8), 2.4: [0, 0, 0], L: [0, 0, 0]})
    a.rot('mag_and_lefthand', {0: [0, 0, 0], 0.75: [0, 0, 0], 1.1: [0, 0, 16], 1.9: [0, 0, 16], 2.2: [0, 0, 0], L: [0, 0, 0]})
    hand, hrot, br, bp, home = _cycle(a, spec, 3.15, hold_open=True, t_close=4.4)
    a.pos('righthand', hand | {L: [0, 0, 0]})
    a.rot('righthand', hrot | {L: [0, 0, 0]})
    a.rot('bullet_and_bolt', br, smooth=False)
    a.pos('bullet_and_bolt', bp, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.6: [0.5, -1.0, 0.3], 3.1: [0.4, 0.8, -0.3], 4.85: [0, 0, 0], L: [0, 0, 0]})
    _snd(a, spec, 0.0, 'raise')
    _snd(a, spec, 0.65, 'magout')
    _snd(a, spec, 2.4, 'magin')
    _snd(a, spec, 3.25, 'bolt_out')
    _snd(a, spec, 4.45, 'bolt_in')
    _snd(a, spec, 4.8, 'end')
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def all_animations(spec):
    sp = smg_anim.SmgSpec(sounds={})
    return {
        'static_idle': idle(spec).to_json(),
        'static_bolt_caught': Anim(0.0333).to_json(),
        'draw': smg_anim.draw(sp).to_json(),
        'put_away': smg_anim.put_away(sp).to_json(),
        'shoot': shoot(spec).to_json(),
        'bolt': bolt(spec).to_json(),
        'reload_tactical': reload(spec, False).to_json(),
        'reload_empty': reload(spec, True).to_json(),
        'inspect': inspect(spec, False).to_json(),
        'inspect_empty': inspect(spec, True).to_json(),
    }
