"""Revolver animations: double-action trigger (charge_in/charge_out), recoil, swing-out reload with a
speed loader, and an inspect that spins the open cylinder.

Bones used: root, crane (rotates about z to swing out), cylinder, ejector, rounds (child of ejector),
release, hammer, trigger, loader_and_round (child of crane, hidden unless reloading) and its loader_rounds,
mag_and_lefthand (moves the left arm). Conventions as pistol_anim.
"""
from dataclasses import dataclass, field

import pistol_anim as P
from anim import Anim, CONSTRAINT


@dataclass
class RevolverSpec:
    sounds: dict
    crane_open: float = 93.0        # degrees about z that swing the cylinder clear of the frame
    hammer_cock: float = -40.0
    trigger_pull: float = 22.0
    kick: float = 1.5
    ejector_stroke: float = 0.9
    loader_seat: float = -1.33      # loader travel from 'aligned behind the cylinder' to 'rounds seated'
    extra: dict = field(default_factory=dict)


def _snd(a, spec, t, key):
    if spec.sounds.get(key):
        a.sound(t, spec.sounds[key])


def _hide_loader(a):
    a.static('loader_and_round', scale=0)
    return a


def idle(spec):
    a = _hide_loader(Anim(0.0333).with_hands())
    a.static('root', rotation=[0, 0, 0], position=[0, 0, 0])
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def charge_in(spec):
    """Long double-action pull: the hammer rises and the cylinder indexes one chamber."""
    a = _hide_loader(Anim(0.15))
    a.rot('hammer', {0: [0, 0, 0], 0.15: [spec.hammer_cock, 0, 0]}, smooth=False)
    a.rot('cylinder', {0: [0, 0, 0], 0.15: [0, 0, 60]}, smooth=False)
    a.rot('trigger', {0: [0, 0, 0], 0.15: [spec.trigger_pull, 0, 0]}, smooth=False)
    a.rot('root', {0: [0, 0, 0], 0.05: [-0.45, 0, -0.25], 0.1: [-0.2, 0, 0.1], 0.15: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.05: [0, -0.09, 0.09], 0.1: [0, -0.05, -0.03], 0.15: [0, 0, 0]})
    _snd(a, spec, 0.0, 'cock')
    return a


def charge_out(spec):
    """Trigger released before the shot: everything eases back."""
    a = _hide_loader(Anim(0.15))
    a.rot('hammer', {0: [spec.hammer_cock, 0, 0], 0.15: [0, 0, 0]}, smooth=False)
    a.rot('cylinder', {0: [0, 0, 60], 0.15: [0, 0, 0]}, smooth=False)
    a.rot('trigger', {0: [spec.trigger_pull, 0, 0], 0.15: [0, 0, 0]}, smooth=False)
    return a


def shoot(spec):
    k = spec.kick
    a = _hide_loader(Anim(0.6).with_hands())
    a.rot('root', {0: [0, 0, 0], 0.033: [3 * k, 0.3 * k, -2.5 * k], 0.07: [-15 * k, -1.2 * k, -2.4 * k],
                   0.11: [-9 * k, 0.2 * k, -2.2 * k], 0.2: [1.6 * k, -0.6 * k, -1.2 * k], 0.3: [0, 0.45 * k, 0],
                   0.4: [0, -0.1, 0], 0.5: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.033: [-0.2, -0.1, 0.4 * k], 0.07: [-0.4, 0.3 * k, 1.6 * k],
                   0.12: [-0.35, -0.3 * k, -0.9 * k], 0.2: [0, -0.3 * k, -0.1], 0.3: [0, -0.02, 0.05],
                   0.42: [0, 0, 0]})
    a.rot('trigger', {0: [spec.trigger_pull, 0, 0], 0.08: [spec.trigger_pull, 0, 0], 0.16: [0, 0, 0]}, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.033: [-0.4 * k, 0, 0.9 * k], 0.07: [0.3 * k, 0, -0.8 * k],
                     0.12: [0, 0, 0.35 * k], 0.2: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def draw(spec):
    return _hide_loader(P.draw(P.PistolSpec(0, {})))


def put_away(spec):
    return _hide_loader(P.put_away(P.PistolSpec(0, {})))


def reload(spec, empty):
    """Swing out, punch the ejector with the gun muzzle-up, drop it muzzle-down, feed a speed loader, close.

    The empty-gun version also spins the cylinder home with the left thumb before closing.
    """
    s = 0.67 if empty else 0.0                 # extra time for the spin
    L = 3.4667 + s
    a = Anim(L).with_hands()
    near = [-0.5, 2.3, 2.0]
    side = [-6, -28, -36]
    up = [-52, -24, -24]                       # muzzle up: cases fall out of the cylinder
    down = [16, -26, -30]                      # muzzle down: the chambers face the speed loader
    close, reset = 2.55 + s, 2.9 + s
    a.rot('root', {0: [0, 0, 0], 0.3: side, 0.62: [-4, -30, -40], 0.85: [-30, -26, -30], 1.0: up, 1.15: [-55, -24, -25],
                   1.35: [-10, -26, -28], 1.6: down, 2.0: [18, -26, -30], 2.1: down, close - 0.1: [8, -26, -32],
                   close + 0.05: [-8, -22, -14], reset: [-2, -6, -4], L - 0.12: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.3: near, 0.62: near, 1.0: [-0.4, 3.6, 2.6], 1.15: [-0.4, 3.8, 2.6],
                   1.6: [-0.2, 1.8, 1.6], 2.0: [-0.2, 1.7, 1.6], close - 0.1: [-0.3, 1.9, 1.8],
                   close + 0.05: [-0.3, 1.3, 1.2], reset: [0, 0.2, 0.2], L - 0.12: [0, 0, 0], L: [0, 0, 0]})
    # thumb the release forward, swing the crane out (and later back in)
    a.pos('release', {0: [0, 0, 0], 0.32: [0, 0, 0], 0.4: [0, 0, -0.25], 0.58: [0, 0, -0.25], 0.64: [0, 0, 0],
                      L: [0, 0, 0]}, smooth=False)
    o = spec.crane_open
    a.rot('crane', {0: [0, 0, 0], 0.4: [0, 0, 0], 0.5: [0, 0, o * 0.8], 0.56: [0, 0, o + 4], 0.62: [0, 0, o],
                    close - 0.05: [0, 0, o], close + 0.06: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
    # ejector stroke, cases fly out and vanish
    e = spec.ejector_stroke
    a.pos('ejector', {0: [0, 0, 0], 1.02: [0, 0, 0], 1.1: [0, 0, e], 1.28: [0, 0, e], 1.36: [0, 0, 0], L: [0, 0, 0]},
          smooth=False)
    a.pos('rounds', {0: [0, 0, 0], 1.1: [0, 0, 0], 1.3: [0, 0, 1.8], 1.4: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
    a.scale('rounds', {0: 1, 1.26: 0, 2.0: 1})
    # the speed loader comes up in the left hand, seats the rounds, twists free and leaves
    seat = spec.loader_seat
    a.scale('loader_and_round', {0: 0, 1.5: 1, 2.42: 0})
    a.scale('loader_rounds', {0: 1, 2.0: 0})
    a.pos('loader_and_round', {0: [5, 5, 4], 1.5: [5, 5, 4], 1.78: [0.3, 0.2, 0.8], 1.86: [0, 0, 0.35],
                               1.98: [0, 0, seat], 2.08: [0, 0, seat], 2.2: [0.2, 0.2, 1.2], 2.42: [5, 5, 4],
                               L: [5, 5, 4]})
    a.rot('loader_and_round', {0: [0, 0, 0], 2.04: [0, 0, 0], 2.1: [0, 0, 25], L: [0, 0, 25]}, smooth=False)
    # left hand: steadies the gun, pushes the cylinder out, works the ejector rod, fetches the loader
    hand = {0: [0, 0, 0], 0.32: [0, 0, 0], 0.45: [0.9, 1.1, -0.2], 0.62: [1.2, 1.4, -0.4], 0.8: [1.5, -2, 0.5],
            0.95: [3, -9, 3], 1.42: [4, -10, 3], 1.55: [4.5, -12, 3],
            1.8: [1.8, 1.0, 1.4], 1.98: [1.6, 1.0, 0.1], 2.1: [1.7, 1.0, 0.2], 2.3: [3.0, -3, 2.5], 2.45: [4, -10, 3]}
    if empty:
        hand.update({2.65: [1.0, 1.4, -0.2], 2.75: [1.1, 1.6, -0.1], 3.0: [1.0, 1.4, -0.2], 3.15: [1.2, 1.6, 0]})
    hand.update({close - 0.12: [1.4, 1.2, -0.3], close + 0.05: [0.5, 0.6, -0.2], reset + 0.15: [0, 0, 0], L: [0, 0, 0]})
    a.pos('mag_and_lefthand', hand)
    a.rot('mag_and_lefthand', {0: [0, 0, 0], 0.62: [0, 0, 0], 0.95: [-30, 10, -20], 1.55: [-30, 10, -20], 1.8: [0, 0, 0], 2.3: [0, 0, 0],
                               2.45: [-30, 10, -20], close - 0.12: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        a.rot('cylinder', {0: [0, 0, 0], 2.65: [0, 0, 0], 2.85: [0, 0, -240], 3.05: [0, 0, -330], 3.15: [0, 0, -360],
                           L: [0, 0, -360]})
    a.rot('camera', {0: [0, 0, 0], 0.3: [0.6, 0, 0.5], 1.05: [-0.8, 0, 0.3], 1.4: [0.4, 0, -0.3], 2.0: [0.6, 0, 0.2],
                     close + 0.05: [-0.8, 0, -0.6], reset: [0.2, 0, 0], L: [0, 0, 0]})
    _snd(a, spec, 0.0333, 'raise')
    _snd(a, spec, 0.3667, 'open')
    _snd(a, spec, 1.0333, 'eject')
    _snd(a, spec, 1.3667, 'shell')
    _snd(a, spec, 1.45, 'pocket')
    _snd(a, spec, 2.0, 'bulletin')
    if empty:
        _snd(a, spec, 2.8333, 'spin')
    _snd(a, spec, close + 0.0833, 'close')
    _snd(a, spec, reset, 'reset')
    return a


def inspect(spec, empty=False):
    """Show the left side, swing the cylinder out and spin it, flick it shut, then show the right side."""
    L = 5.0
    a = _hide_loader(Anim(L).with_hands())
    left = [-8, -50, -18]
    right = [-6, 50, 12]
    near = spec.extra.get('inspect_near', [2.4, 2.4, 2.6])
    a.rot('root', {0: [0, 0, 0], 0.55: left, 1.0: [-10, -54, -24], 1.3: [-6, -48, -30], 2.6: [-8, -52, -28],
                   2.8: [-12, -40, -6], 3.05: [-6, -46, -16], 3.6: right, 4.4: [-8, 54, 14], 4.8: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.55: near, 2.6: [near[0], near[1] + 0.2, near[2] + 0.2],
                   2.8: [near[0] - 0.2, near[1] - 0.3, near[2]], 3.6: [near[0] - 0.6, near[1], near[2]],
                   4.4: [near[0] - 0.6, near[1] + 0.1, near[2] + 0.2], 4.8: [0, 0, 0], L: [0, 0, 0]})
    o = spec.crane_open
    a.pos('release', {0: [0, 0, 0], 0.9: [0, 0, 0], 0.96: [0, 0, -0.25], 1.12: [0, 0, -0.25], 1.18: [0, 0, 0],
                      L: [0, 0, 0]}, smooth=False)
    a.rot('crane', {0: [0, 0, 0], 1.0: [0, 0, 0], 1.12: [0, 0, o * 0.8], 1.18: [0, 0, o + 4], 1.24: [0, 0, o],
                    2.72: [0, 0, o], 2.8: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
    a.rot('cylinder', {0: [0, 0, 0], 1.35: [0, 0, 0], 1.6: [0, 0, -260], 1.9: [0, 0, -480], 2.2: [0, 0, -630],
                       2.45: [0, 0, -700], 2.6: [0, 0, -720], L: [0, 0, -720]})
    a.pos('mag_and_lefthand', {0: [0, 0, 0], 1.25: [0, 0, 0], 1.32: [1.4, 1.5, -0.2], 1.42: [1.0, 1.2, -0.2],
                               2.55: [0.6, 0.6, 0], 2.7: [1.2, 1.4, -0.2], 2.85: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        a.static('rounds', scale=0)
    a.rot('camera', {0: [0, 0, 0], 0.55: [0.5, -1.2, 0.3], 2.8: [-0.6, 0, -0.6], 3.6: [0.4, 1.0, -0.3],
                     4.8: [0, 0, 0], L: [0, 0, 0]})
    _snd(a, spec, 0.0667, 'inspect_start')
    _snd(a, spec, 1.0, 'inspect_open')
    _snd(a, spec, 1.35, 'inspect_spin')
    _snd(a, spec, 2.62, 'inspect_spin_end')
    _snd(a, spec, 2.78, 'close')
    _snd(a, spec, 4.5, 'inspect_reset')
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def all_animations(spec):
    return {
        'static_idle': idle(spec).to_json(),
        'static_bolt_caught': Anim(0.0333).to_json(),
        'draw': draw(spec).to_json(),
        'put_away': put_away(spec).to_json(),
        'shoot': shoot(spec).to_json(),
        'charge_in': charge_in(spec).to_json(),
        'charge_out': charge_out(spec).to_json(),
        'reload_tactical': reload(spec, False).to_json(),
        'reload_empty': reload(spec, True).to_json(),
        'inspect': inspect(spec, False).to_json(),
        'inspect_empty': inspect(spec, True).to_json(),
    }
