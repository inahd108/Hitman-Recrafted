"""Argento .45 animations: draw, holster, fire, two reloads, inspect."""
from anim import Anim, CONSTRAINT

SLIDE_TRAVEL = 3.0            # long slide: more travel than a service pistol
S = 'tacz:m1911/m1911_'        # TACZ's bundled .45 pistol sounds
GRIP_AXIS = (0.0, -0.961, 0.276)   # down along the 16 degree grip


def along_grip(d):
    return [GRIP_AXIS[0] * d, GRIP_AXIS[1] * d, GRIP_AXIS[2] * d]


def idle():
    a = Anim(0.0333).with_hands()
    a.static('root', rotation=[0, 0, 0], position=[0, 0, 0])
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def bolt_caught():
    a = Anim(0.0333)
    a.static('slide', position=[0, 0, SLIDE_TRAVEL])
    a.static('hammer', rotation=[-27.5, 0, 0])
    a.static('hold_release', rotation=[8, 0, 0])
    a.static('bullet', scale=0)
    return a


def shoot():
    a = Anim(0.5).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.033: [0, 0, 0], 0.066: [-11.5, 1.6, -1.8], 0.16: [2.6, -1.8, -4.2],
                   0.3: [0.5, 0, 1.4], 0.44: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.033: [0, 0.22, 1.9], 0.066: [0, 0.7, 2.0], 0.16: [0, 0.05, -0.25],
                   0.3: [0, -0.1, 0], 0.44: [0, 0, 0]})
    a.pos('slide', {0: [0, 0, 0], 0.05: [0, 0, SLIDE_TRAVEL], 0.12: [0, 0, 0]}, smooth=False)
    a.rot('hammer', {0: [37.5, 0, 0], 0.033: [-27.5, 0, 0], 0.07: [0, 0, 0]}, smooth=False)
    a.rot('trigger', {0: [-12, 0, 0], 0.09: [0, 0, 0]}, smooth=False)
    a.rot('camera', {0: [0, 0, 0], 0.033: [0, 0, 0.9], 0.066: [0, 0, -0.7], 0.1: [0, 0, 0.35], 0.16: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def draw():
    a = Anim(0.72).with_hands()
    a.rot('root', {0: [48, -28, 26], 0.18: [14, -10, 9], 0.36: [-4.5, 2, -2], 0.52: [1.2, 0, 0.6], 0.68: [0, 0, 0]})
    a.pos('root', {0: [3, -11, 6], 0.18: [1, -3.5, 2], 0.36: [0, 0.35, -0.2], 0.52: [0, -0.08, 0], 0.68: [0, 0, 0]})
    a.rot('camera', {0: [0, 0, 0], 0.2: [0.6, 0, -0.5], 0.4: [-0.3, 0, 0.3], 0.6: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def put_away():
    a = Anim(0.42).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.12: [6, -4, 4], 0.4: [48, -28, 26]})
    a.pos('root', {0: [0, 0, 0], 0.12: [0.4, -1, 0.5], 0.4: [3, -11, 6]})
    a.rot('camera', {0: [0, 0, 0], 0.2: [0.5, 0, -0.4], 0.4: [0, 0, 0]})
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def _reload(empty):
    L = 2.45 if empty else 2.05
    a = Anim(L).with_hands()
    # cant the gun towards the support hand, then bring it back
    tilt = [6, 14, 34]
    back = L - 0.42
    a.rot('root', {0: [0, 0, 0], 0.22: tilt, 0.9: [5, 13, 32], 1.25: tilt, 1.32: [3, 13, 36],
                   1.42: tilt, back: [8, 6, 16] if empty else tilt, L - 0.12: [0, 0, 0], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.22: [-1.6, 1.2, 0.4], 1.3: [-1.6, 1.2, 0.4], 1.34: [-1.6, 1.65, 0.4],
                   1.44: [-1.6, 1.2, 0.4], back: [-0.8, 0.6, 0.2], L - 0.12: [0, 0, 0], L: [0, 0, 0]})
    # the support hand pulls the magazine out down the grip, swaps it, slaps the new one home
    out1 = along_grip(4.8)
    away = [-5.2, -17.0, 6.2]
    a.pos('mag_and_lefthand', {0: [0, 0, 0], 0.26: [0, 0, 0], 0.36: out1, 0.56: away, 0.86: away,
                               1.06: out1, 1.2: along_grip(1.2), 1.3: [0, 0, 0], L: [0, 0, 0]})
    a.rot('mag_and_lefthand', {0: [0, 0, 0], 0.36: [0, 0, 0], 0.56: [-60, -18, 28], 0.86: [-60, -18, 28],
                               1.06: [0, 0, 0], L: [0, 0, 0]})
    a.sound(0.0, S + ('reload_empty_lift' if empty else 'reload_lift'))
    a.sound(0.26, S + ('reload_empty_magout' if empty else 'reload_magout'))
    a.sound(1.22, S + ('reload_empty_magin' if empty else 'reload_magin'))
    if empty:
        # support hand comes up and thumbs the slide release
        a.pos('L', {0: [0, 0, 0], 1.36: [0, 0, 0], 1.5: [-6.5, 9.5, -3.2], 1.62: [-7.6, 13.6, -2.2],
                    1.7: [-7.6, 13.6, -2.2], 1.86: [-2.4, 3.0, 2.0], 2.0: [0, 0, 0], L: [0, 0, 0]})
        a.rot('L', {0: [0, 0, 0], 1.36: [0, 0, 0], 1.62: [-70, 0, -60], 1.7: [-74, 0, -64], 1.95: [0, 0, 0], L: [0, 0, 0]})
        a.pos('slide', {0: [0, 0, SLIDE_TRAVEL], 1.66: [0, 0, SLIDE_TRAVEL], 1.71: [0, 0, 0], L: [0, 0, 0]}, smooth=False)
        a.rot('hold_release', {0: [8, 0, 0], 1.66: [8, 0, 0], 1.7: [0, 0, 0]}, smooth=False)
        a.rot('hammer', {0: [-27.5, 0, 0], 1.66: [-27.5, 0, 0], 1.72: [0, 0, 0]}, smooth=False)
        a.scale('bullet', {0: 0, 0.7: 1})
        a.sound(1.66, S + 'reload_empty_chamber')
        a.sound(2.0, S + 'reload_empty_end')
    else:
        a.sound(1.7, S + 'reload_end')
    a.rot('camera', {0: [0, 0, 0], 0.3: [0, 0, 0.8], 1.3: [0, 0, 0.2], 1.34: [0.6, 0, -0.6], 1.5: [0, 0, 0], L: [0, 0, 0]})
    return a


def inspect(empty=False):
    L = 3.6
    a = Anim(L).with_hands()
    a.rot('root', {0: [0, 0, 0], 0.35: [-6, -22, -38], 1.25: [-8, -26, -42], 1.7: [8, 24, 30],
                   2.6: [10, 28, 34], 3.15: [1, 2, 2], L: [0, 0, 0]})
    a.pos('root', {0: [0, 0, 0], 0.35: [-1.4, 1.6, -0.6], 1.25: [-1.6, 1.8, -0.8], 1.7: [-0.6, 0.9, 0.4],
                   2.6: [-0.6, 1.0, 0.5], 3.15: [0, 0.1, 0], L: [0, 0, 0]})
    # press-check: the support hand eases the slide back to show brass, then lets it go
    a.pos('L', {0: [0, 0, 0], 1.8: [0, 0, 0], 2.05: [-6.2, 10.4, -1.2], 2.2: [-6.6, 11.2, 0.6],
                2.45: [-6.6, 11.2, 0.6], 2.6: [-6.2, 10.4, -1.2], 2.9: [0, 0, 0], L: [0, 0, 0]})
    a.rot('L', {0: [0, 0, 0], 1.8: [0, 0, 0], 2.05: [-80, 0, -70], 2.6: [-80, 0, -70], 2.9: [0, 0, 0], L: [0, 0, 0]})
    if empty:
        a.static('slide', position=[0, 0, SLIDE_TRAVEL])
        a.static('bullet', scale=0)
    else:
        a.pos('slide', {0: [0, 0, 0], 2.15: [0, 0, 0], 2.25: [0, 0, 1.1], 2.45: [0, 0, 1.1], 2.5: [0, 0, 0], L: [0, 0, 0]},
              smooth=False)
        a.sound(2.2, S + 'inspect_slide_pull')
    a.sound(0.0, S + 'inspect_quick')
    a.static('constraint', **CONSTRAINT['constraint'])
    return a


def all_animations():
    return {
        'static_idle': idle().to_json(),
        'static_bolt_caught': bolt_caught().to_json(),
        'draw': draw().to_json(),
        'put_away': put_away().to_json(),
        'shoot': shoot().to_json(),
        'reload_tactical': _reload(False).to_json(),
        'reload_empty': _reload(True).to_json(),
        'inspect': inspect(False).to_json(),
        'inspect_empty': inspect(True).to_json(),
    }
