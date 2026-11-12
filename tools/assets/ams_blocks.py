"""Textures, models and blockstates for the Amsterdam blocks (our own pixel art, made in code).

    python3 tools/assets/ams_blocks.py

Blocks: canal_window (axis, lit), bulb_string (facing), bollard, lamp_post, canal_lamp,
bicycle (facing, paint).
"""
import json
import os
import random

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/recrafted')
NS = 'recrafted:block/'

LANG = {
    'block.recrafted.canal_window': 'Sash Window',
    'block.recrafted.bulb_string': 'Bridge Lights',
    'block.recrafted.bollard': 'Bollard',
    'block.recrafted.lamp_post': 'Lamp Post',
    'block.recrafted.canal_lamp': 'Canal Lantern',
    'block.recrafted.bicycle': 'Bicycle',
    'block.recrafted.gable_scroll': 'Gable Scroll',
    'block.recrafted.gable_scroll_stone': 'Sandstone Gable Scroll',
    'block.recrafted.hoist_beam': 'Hoisting Beam',
    'block.recrafted.shutter': 'Warehouse Shutter',
}

PAINTS = {'black': (28, 28, 30), 'navy': (34, 48, 84), 'red': (128, 32, 30), 'green': (36, 78, 52), 'cream': (214, 204, 176)}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def save_tex(im, name):
    path = os.path.join(ASSETS, 'textures/block', name + '.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


def write(rel, obj):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1)
        f.write('\n')


# ---- textures ---------------------------------------------------------------------------------
FRAME = (236, 233, 222)


def window_tex(lit, rnd):
    """Sash window: white frame, six panes. Lit: amber with curtains; dark: cold glass with a glint."""
    im = Image.new('RGB', (16, 16), FRAME)
    px = im.load()
    for x in range(16):
        for y in range(16):
            edge = x in (0, 15) or y in (0, 15)
            if edge:
                px[x, y] = shade(FRAME, .82)
    panes = [(x0, y0) for y0 in (2, 7, 11) for x0 in (2, 9)]
    for (x0, y0) in panes:
        h = 4 if y0 != 7 else 3
        warm = rnd.uniform(.85, 1.1)
        for x in range(x0, x0 + 5):
            for y in range(y0, y0 + h):
                t = (y - 2) / 12
                if lit:
                    c = mix((255, 214, 140), (232, 150, 62), t)
                    c = shade(c, warm)
                    if x in (x0, x0 + 4) and rnd.random() < .7:          # curtain edges
                        c = shade(mix(c, (200, 96, 60), .35), .9)
                else:
                    c = mix((70, 84, 98), (30, 38, 48), t)
                    if (x - x0) + (y - y0) in (1, 2) and x < x0 + 3:     # glint
                        c = mix(c, (150, 170, 190), .45)
                px[x, y] = c
    for y in range(1, 15):                                               # meeting rail shadow
        px[8, y] = shade(FRAME, .9)
    return im


def frame_tex():
    im = Image.new('RGB', (16, 16), FRAME)
    px = im.load()
    for x in range(16):
        for y in range(16):
            px[x, y] = shade(FRAME, .78 if x in (0, 15) or y in (0, 15) else 1)
    return im


def flat(c, noise=.05, rnd=None, size=16):
    rnd = rnd or random.Random(1)
    im = Image.new('RGB', (size, size))
    px = im.load()
    for x in range(size):
        for y in range(size):
            px[x, y] = shade(c, 1 + rnd.uniform(-noise, noise))
    return im


def bulb_tex():
    im = Image.new('RGB', (16, 16), (24, 24, 24))
    px = im.load()
    for x in range(8):
        for y in range(8):
            d = ((x - 3.5) ** 2 + (y - 3.5) ** 2) ** .5
            px[x, y] = mix((255, 250, 225), (255, 190, 90), min(1, d / 4))
    for x in range(8, 16):
        for y in range(8):
            px[x, y] = (28, 28, 30)
    return im


def lamp_glass_tex():
    im = Image.new('RGB', (16, 16))
    px = im.load()
    for x in range(16):
        for y in range(16):
            t = y / 15
            c = mix((255, 236, 180), (240, 170, 80), t)
            if x in (0, 15) or y in (0, 15):
                c = (28, 48, 36)
            px[x, y] = c
    return im


def bike_tex(paint):
    """4 colour swatches in one texture: paint, tyre, steel, saddle (each a 4-px column)."""
    rnd = random.Random(hash(paint) & 0xff)
    im = Image.new('RGB', (16, 16))
    px = im.load()
    cols = [PAINTS[paint], (22, 22, 22), (150, 152, 156), (58, 40, 30)]
    for i, c in enumerate(cols):
        for x in range(4 * i, 4 * i + 4):
            for y in range(16):
                px[x, y] = shade(c, 1 + rnd.uniform(-.06, .06) + (.12 if y < 3 else 0))
    return im


# ---- models -----------------------------------------------------------------------------------
def el(frm, to, tex='#t', uv=None, rot=None, faces=None, shade_=True):
    """Element with all six faces using one texture region."""
    uv = uv or [0, 0, 16, 16]
    fs = faces or ('north', 'south', 'east', 'west', 'up', 'down')
    e = {'from': frm, 'to': to, 'faces': {f: {'texture': tex, 'uv': uv} for f in fs}}
    if rot:
        e['rotation'] = rot
    if not shade_:
        e['shade'] = False
    return e


def bike_model(paint):
    """City bike, 25 px long along x when facing north, wheels as octagons of thin bars."""
    P, T, S, D = [0, 0, 4, 16], [4, 0, 8, 16], [8, 0, 12, 16], [12, 0, 16, 16]
    els = []
    z0, z1 = 7.5, 8.5
    for cx in (0.5, 15.5):                    # wheels, centre y 5, radius 5
        cy = 5
        for ang in (0, 45, -45):
            for (a, b) in (((cx - 2.1, cy + 4.4), (cx + 2.1, cy + 5.2)), ((cx - 2.1, cy - 5.2), (cx + 2.1, cy - 4.4))):
                rot = {'origin': [cx, cy, 8], 'axis': 'z', 'angle': ang} if ang else None
                els.append(el([a[0], a[1], z0], [b[0], b[1], z1], uv=T, rot=rot))
        for (a, b) in (((cx - 5.2, cy - 2.1), (cx - 4.4, cy + 2.1)), ((cx + 4.4, cy - 2.1), (cx + 5.2, cy + 2.1))):
            els.append(el([a[0], a[1], z0], [b[0], b[1], z1], uv=T))
        els.append(el([cx - 4.4, cy - .2, 7.9], [cx + 4.4, cy + .2, 8.1], uv=S))          # spokes
        els.append(el([cx - .2, cy - 4.4, 7.9], [cx + .2, cy + 4.4, 8.1], uv=S))
        els.append(el([cx - .6, cy - .6, 7.4], [cx + .6, cy + .6, 8.6], uv=S))            # hub
    # frame
    els.append(el([0.5, 4.6, 7.6], [8, 5.4, 8.4], uv=P))                                    # chain stay
    els.append(el([7.6, 4.5, 7.6], [8.4, 12, 8.4], uv=P, rot={'origin': [8, 5, 8], 'axis': 'z', 'angle': 22.5}))   # seat tube
    els.append(el([3, 8.6, 7.6], [11.5, 9.4, 8.4], uv=P, rot={'origin': [7.5, 9, 8], 'axis': 'z', 'angle': -45}))  # down tube
    els.append(el([5.8, 10.6, 7.6], [13.6, 11.4, 8.4], uv=P))                               # top tube
    els.append(el([-.5, 7.6, 7.6], [7, 8.4, 8.4], uv=P, rot={'origin': [2.5, 8, 8], 'axis': 'z', 'angle': 45}))    # seat stay
    els.append(el([14.1, 4.5, 7.6], [14.9, 12.5, 8.4], uv=P, rot={'origin': [14.5, 8.5, 8], 'axis': 'z', 'angle': -22.5}))  # fork
    els.append(el([13.4, 12.2, 7.5], [14.2, 13.8, 8.5], uv=S))                             # stem
    els.append(el([12.2, 13.6, 5], [13.2, 14.3, 11], uv=S))                                # handlebar
    els.append(el([12, 13.5, 4.6], [13.4, 14.4, 5.6], uv=D))                               # grips
    els.append(el([12, 13.5, 10.4], [13.4, 14.4, 11.4], uv=D))
    els.append(el([4.4, 12.4, 7.2], [8.2, 13.3, 8.8], uv=D))                               # saddle
    els.append(el([6.4, 11.6, 7.7], [6.9, 12.4, 8.3], uv=S))                               # seat post
    els.append(el([-3.5, 9.6, 7.2], [4.5, 10.2, 8.8], uv=S))                               # rear rack
    els.append(el([7.2, 4.2, 7.3], [8.8, 5.8, 8.7], uv=S))                                 # crank
    if paint in ('cream', 'navy'):
        els.append(el([16, 8.5, 6], [20, 12, 10], uv=D))                                   # front basket
    return {'textures': {'t': NS + f'bike_{paint}', 'particle': NS + f'bike_{paint}'}, 'elements': els,
            'display': {'gui': {'rotation': [20, 225, 0], 'translation': [0, 1, 0], 'scale': [0.5, 0.5, 0.5]},
                        'ground': {'translation': [0, 3, 0], 'scale': [0.4, 0.4, 0.4]},
                        'fixed': {'scale': [0.5, 0.5, 0.5]},
                        'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 2.5, 0], 'scale': [0.3, 0.3, 0.3]},
                        'firstperson_righthand': {'rotation': [0, 45, 0], 'scale': [0.3, 0.3, 0.3]}}}


def horiz_states(model_for, extra=''):
    rot = {'north': 0, 'east': 90, 'south': 180, 'west': 270}
    out = {}
    for f, r in rot.items():
        key = f'facing={f}' + extra
        out[key] = {'model': model_for} if r == 0 else {'model': model_for, 'y': r}
    return out


def main():
    rnd = random.Random(1672)
    # windows
    save_tex(window_tex(True, rnd), 'canal_window_lit')
    save_tex(window_tex(False, rnd), 'canal_window_dark')
    save_tex(frame_tex(), 'canal_window_frame')
    for state in ('lit', 'dark'):
        write(f'models/block/canal_window_{state}.json', {
            'parent': 'minecraft:block/cube',
            'textures': {'north': NS + f'canal_window_{state}', 'south': NS + f'canal_window_{state}',
                         'east': NS + 'canal_window_frame', 'west': NS + 'canal_window_frame',
                         'up': NS + 'canal_window_frame', 'down': NS + 'canal_window_frame',
                         'particle': NS + 'canal_window_frame'}})
    variants = {}
    for axis in ('x', 'z'):
        for lit in ('true', 'false'):
            m = {'model': NS + ('canal_window_lit' if lit == 'true' else 'canal_window_dark')}
            if axis == 'x':
                m['y'] = 90
            variants[f'axis={axis},lit={lit}'] = m
    write('blockstates/canal_window.json', {'variants': variants})
    write('models/item/canal_window.json', {'parent': NS + 'canal_window_lit'})

    # bridge lights: a wire with three bulbs, hung on the face of the block behind it (facing north = on its south face)
    save_tex(bulb_tex(), 'bulb_string')
    els = [el([0, 7.6, 15.2], [16, 8.1, 15.8], uv=[8, 0, 16, 8], shade_=False)]
    for x in (1.5, 7, 12.5):
        els.append(el([x, 6.4, 13.8], [x + 2, 8.4, 15.8], uv=[0, 0, 8, 8], shade_=False))
    write('models/block/bulb_string.json', {'textures': {'t': NS + 'bulb_string', 'particle': NS + 'bulb_string'},
                                            'elements': els})
    write('blockstates/bulb_string.json', {'variants': horiz_states(NS + 'bulb_string')})
    write('models/item/bulb_string.json', {'parent': NS + 'bulb_string'})

    # bollard: red-brown iron post with a collar and a cap
    save_tex(flat((104, 42, 32), .07, rnd), 'bollard')
    write('models/block/bollard.json', {'textures': {'t': NS + 'bollard', 'particle': NS + 'bollard'}, 'elements': [
        el([6, 0, 6], [10, 12, 10]), el([5.5, 8.5, 5.5], [10.5, 9.5, 10.5]), el([5.5, 12, 5.5], [10.5, 13, 10.5]),
        el([7, 13, 7], [9, 13.6, 9])]})
    write('blockstates/bollard.json', {'variants': {'': {'model': NS + 'bollard'}}})
    write('models/item/bollard.json', {'parent': NS + 'bollard'})

    # lamp post and lantern head
    save_tex(flat((30, 52, 40), .08, rnd), 'lamp_post')
    write('models/block/lamp_post.json', {'textures': {'t': NS + 'lamp_post', 'particle': NS + 'lamp_post'}, 'elements': [
        el([6.5, 0, 6.5], [9.5, 16, 9.5]), el([6, 0, 6], [10, 1, 10])]})
    write('blockstates/lamp_post.json', {'variants': {'': {'model': NS + 'lamp_post'}}})
    write('models/item/lamp_post.json', {'parent': NS + 'lamp_post'})
    save_tex(lamp_glass_tex(), 'canal_lamp_glass')
    write('models/block/canal_lamp.json', {
        'textures': {'t': NS + 'lamp_post', 'g': NS + 'canal_lamp_glass', 'particle': NS + 'lamp_post'},
        'elements': [
            el([6.5, 0, 6.5], [9.5, 2, 9.5]),
            el([5, 2, 5], [11, 3, 11]),
            el([5.5, 3, 5.5], [10.5, 9, 10.5], tex='#g', shade_=False),
            el([4.5, 9, 4.5], [11.5, 10, 11.5]),
            el([6, 10, 6], [10, 11, 10]),
            el([7.5, 11, 7.5], [8.5, 11.5, 8.5])]})
    write('blockstates/canal_lamp.json', {'variants': {'': {'model': NS + 'canal_lamp'}}})
    write('models/item/canal_lamp.json', {'parent': NS + 'canal_lamp'})

    # bicycles
    for paint in PAINTS:
        save_tex(bike_tex(paint), f'bike_{paint}')
        write(f'models/block/bicycle_{paint}.json', bike_model(paint))
    v = {}
    for paint in PAINTS:
        v.update(horiz_states(NS + f'bicycle_{paint}', f',paint={paint}'))
    write('blockstates/bicycle.json', {'variants': v})
    write('models/item/bicycle.json', {'parent': NS + 'bicycle_black'})

    # gable scrolls: a quarter round rising towards the neck, with a curl at the outer foot
    for blk, tex in (('gable_scroll', 'minecraft:block/quartz_block_bottom'), ('gable_scroll_stone', 'minecraft:block/sandstone_top')):
        for side in ('left', 'right'):
            els = []
            for y0 in range(0, 16, 2):
                yc = y0 + 1
                wdt = max(2.0, (256 - yc * yc) ** .5)
                if side == 'left':                       # seen from the street the neck is on the viewer's right = -x
                    els.append(el([0, y0, 0], [round(wdt, 2), y0 + 2, 16], uv=[0, 16 - y0 - 2, round(wdt, 2), 16 - y0]))
                else:
                    els.append(el([round(16 - wdt, 2), y0, 0], [16, y0 + 2, 16], uv=[round(16 - wdt, 2), 16 - y0 - 2, 16, 16 - y0]))
            kx = (12, 16) if side == 'left' else (0, 4)
            els.append(el([kx[0], 0, -1], [kx[1], 4, 1]))                                       # the curl
            els.append(el([kx[0] + 1, 4, -.5], [kx[1] - 1, 5, .5]))
            write(f'models/block/{blk}_{side}.json', {'textures': {'t': tex, 'particle': tex}, 'elements': els})
        v = {}
        for side in ('left', 'right'):
            v.update(horiz_states(NS + f'{blk}_{side}', f',side={side}'))
        write(f'blockstates/{blk}.json', {'variants': v})
        write(f'models/item/{blk}.json', {'parent': NS + f'{blk}_left'})

    # hoisting beam with pulley, rope and hook, pointing out of the wall (facing north: wall to the south)
    write('models/block/hoist_beam.json', {
        'textures': {'w': 'minecraft:block/dark_oak_log', 'e': 'minecraft:block/dark_oak_log_top',
                     'i': 'minecraft:block/anvil', 'r': 'minecraft:block/chain', 'particle': 'minecraft:block/dark_oak_log'},
        'elements': [
            {'from': [6, 9, -2], 'to': [10, 13, 16], 'faces': {
                'north': {'texture': '#e'}, 'south': {'texture': '#e'}, 'east': {'texture': '#w'},
                'west': {'texture': '#w'}, 'up': {'texture': '#w'}, 'down': {'texture': '#w'}}},
            el([5, 6.5, -1], [11, 9, 1.5], tex='#i'),                                        # pulley block
            el([7.6, 0, -.2], [8.4, 6.5, .6], tex='#i'),                                     # rope
            el([6.5, -1.5, -1], [9.5, 0, 1.5], tex='#i'),                                    # hook
            el([6, 13, 14], [10, 14, 16], tex='#w')]})
    write('blockstates/hoist_beam.json', {'variants': horiz_states(NS + 'hoist_beam')})
    write('models/item/hoist_beam.json', {'parent': NS + 'hoist_beam'})

    # warehouse shutters: diagonal two-colour planks, flat against the wall
    for paint, (a, b) in {'green': ((34, 78, 52), (226, 222, 206)), 'red': ((132, 34, 30), (226, 222, 206)),
                          'black': ((26, 26, 28), (150, 40, 34))}.items():
        im = Image.new('RGB', (16, 16))
        px = im.load()
        for x in range(16):
            for y in range(16):
                band = ((x + y) // 4) % 2 if y < 8 else ((x - y) // 4) % 2      # hourglass chevrons
                c = a if band else b
                if x in (0, 15) or y in (0, 15) or y == 8:
                    c = shade(a, .75)
                px[x, y] = shade(c, 1 + rnd.uniform(-.04, .04))
        save_tex(im, f'shutter_{paint}')
        write(f'models/block/shutter_{paint}.json', {'textures': {'t': NS + f'shutter_{paint}', 'particle': NS + f'shutter_{paint}'},
                                                      'elements': [el([0, 0, 14], [16, 16, 16])]})
    v = {}
    for paint in ('green', 'red', 'black'):
        v.update(horiz_states(NS + f'shutter_{paint}', f',paint={paint}'))
    write('blockstates/shutter.json', {'variants': v})
    write('models/item/shutter.json', {'parent': NS + 'shutter_green'})

    # language
    lang_path = os.path.join(ASSETS, 'lang/en_us.json')
    with open(lang_path) as f:
        lang = json.load(f)
    lang.update(LANG)
    with open(lang_path, 'w') as f:
        json.dump(lang, f, indent=2)
        f.write('\n')
    print('amsterdam blocks written')


if __name__ == '__main__':
    main()
