"""Voxel canvas + building primitives used by the Corvara map generator.

The canvas is a dense uint16 grid indexed [y, z, x] holding palette ids.
The palette is a list of block-state strings ("minecraft:oak_stairs[facing=north]").
The mod reads the saved file (see recrafted.world.MapData) and serves it from a
custom chunk generator, so nothing here needs the game to run.
"""
import gzip
import math
import random
import struct

import numpy as np

DIRS = {
    'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0),
}
OPP = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
CW = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}
CCW = {v: k for k, v in CW.items()}


class World:
    def __init__(self, sx, sy, sz):
        self.sx, self.sy, self.sz = sx, sy, sz
        self.G = np.zeros((sy, sz, sx), dtype=np.uint16)
        self.palette = ['minecraft:air']
        self.pid = {'minecraft:air': 0}

    # ---- palette -----------------------------------------------------
    def b(self, name):
        if isinstance(name, (int, np.integer)):
            return int(name)
        if ':' not in name.split('[')[0]:
            name = 'minecraft:' + name
        i = self.pid.get(name)
        if i is None:
            i = len(self.palette)
            self.palette.append(name)
            self.pid[name] = i
        return i

    def name(self, i):
        return self.palette[int(i)]

    # ---- single cells ------------------------------------------------
    def inb(self, x, y, z):
        return 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz

    def set(self, x, y, z, blk):
        if self.inb(x, y, z):
            self.G[y, z, x] = self.b(blk)

    def get(self, x, y, z):
        if self.inb(x, y, z):
            return int(self.G[y, z, x])
        return 0

    def is_air(self, x, y, z):
        return self.get(x, y, z) == 0

    def set_if_air(self, x, y, z, blk):
        if self.inb(x, y, z) and self.G[y, z, x] == 0:
            self.G[y, z, x] = self.b(blk)

    # ---- volumes -----------------------------------------------------
    def _clip(self, x0, y0, z0, x1, y1, z1):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        x0, y0, z0 = max(x0, 0), max(y0, 0), max(z0, 0)
        x1, y1, z1 = min(x1, self.sx - 1), min(y1, self.sy - 1), min(z1, self.sz - 1)
        return x0, y0, z0, x1, y1, z1

    def fill(self, x0, y0, z0, x1, y1, z1, blk):
        x0, y0, z0, x1, y1, z1 = self._clip(x0, y0, z0, x1, y1, z1)
        if x1 < x0 or y1 < y0 or z1 < z0:
            return
        self.G[y0:y1 + 1, z0:z1 + 1, x0:x1 + 1] = self.b(blk)

    def fill_mix(self, x0, y0, z0, x1, y1, z1, rng, choices):
        """choices: [(block, weight), ...]"""
        x0, y0, z0, x1, y1, z1 = self._clip(x0, y0, z0, x1, y1, z1)
        if x1 < x0 or y1 < y0 or z1 < z0:
            return
        ids = [self.b(c[0]) for c in choices]
        w = [c[1] for c in choices]
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                row = rng.choices(ids, w, k=x1 - x0 + 1)
                self.G[y, z, x0:x1 + 1] = row

    def fill_air_only(self, x0, y0, z0, x1, y1, z1, blk):
        x0, y0, z0, x1, y1, z1 = self._clip(x0, y0, z0, x1, y1, z1)
        if x1 < x0 or y1 < y0 or z1 < z0:
            return
        sub = self.G[y0:y1 + 1, z0:z1 + 1, x0:x1 + 1]
        sub[sub == 0] = self.b(blk)

    def clear(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, 0)

    def shell(self, x0, y0, z0, x1, y1, z1, blk, floor=None, ceil=None):
        """Hollow box: four walls of blk; optional floor / ceiling blocks."""
        self.fill(x0, y0, z0, x1, y1, z0, blk)
        self.fill(x0, y0, z1, x1, y1, z1, blk)
        self.fill(x0, y0, z0, x0, y1, z1, blk)
        self.fill(x1, y0, z0, x1, y1, z1, blk)
        if floor is not None:
            self.fill(x0, y0, z0, x1, y0, z1, floor)
        if ceil is not None:
            self.fill(x0, y1, z0, x1, y1, z1, ceil)

    def column_top(self, x, z, ymax=None):
        """Highest non-air y in a column (or -1)."""
        col = self.G[:ymax, z, x] if ymax else self.G[:, z, x]
        nz = np.nonzero(col)[0]
        return int(nz[-1]) if len(nz) else -1

    # ---- save --------------------------------------------------------
    def save(self, path):
        with gzip.open(path, 'wb', compresslevel=9) as f:
            f.write(b'RCMAP1')
            f.write(struct.pack('>iiii', self.sx, self.sy, self.sz, len(self.palette)))
            for p in self.palette:
                raw = p.encode('utf-8')
                f.write(struct.pack('>H', len(raw)))
                f.write(raw)
            f.write(self.G.astype('>u2').tobytes())


# ----------------------------------------------------------------------
# noise
# ----------------------------------------------------------------------
def value_noise(sx, sz, cell, seed, octaves=3):
    """Smooth 2D value noise in [-1, 1], shape [sz, sx]."""
    rng = np.random.default_rng(seed)
    out = np.zeros((sz, sx))
    amp, total = 1.0, 0.0
    for _ in range(octaves):
        gx, gz = sx // cell + 3, sz // cell + 3
        g = rng.uniform(-1, 1, (gz, gx))
        xs = np.arange(sx) / cell
        zs = np.arange(sz) / cell
        xi, zi = xs.astype(int), zs.astype(int)
        xf, zf = xs - xi, zs - zi
        xf = xf * xf * (3 - 2 * xf)
        zf = zf * zf * (3 - 2 * zf)
        a = g[np.ix_(zi, xi)]
        b = g[np.ix_(zi, xi + 1)]
        c = g[np.ix_(zi + 1, xi)]
        d = g[np.ix_(zi + 1, xi + 1)]
        top = a + (b - a) * xf[None, :]
        bot = c + (d - c) * xf[None, :]
        out += amp * (top + (bot - top) * zf[:, None])
        total += amp
        amp *= 0.5
        cell = max(2, cell // 2)
    return out / total


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------------
# oriented frame: lets one building routine face any direction
# ----------------------------------------------------------------------
class Frame:
    """Local coords (u, y, v): u runs along the front facade, v goes into the lot.

    front is the outward direction of the facade ('south' means the front wall
    is on the +z side). Block names may contain {F} {B} {L} {R} placeholders
    which are replaced by world directions.
    """

    def __init__(self, w, x0, z0, x1, z1, front):
        self.w = w
        self.x0, self.z0, self.x1, self.z1 = x0, z0, x1, z1
        self.front = front
        if front in ('south', 'north'):
            self.W, self.D = x1 - x0 + 1, z1 - z0 + 1
        else:
            self.W, self.D = z1 - z0 + 1, x1 - x0 + 1
        if front == 'south':
            self.dirs = dict(F='south', B='north', L='west', R='east')
        elif front == 'north':
            self.dirs = dict(F='north', B='south', L='east', R='west')
        elif front == 'east':
            self.dirs = dict(F='east', B='west', L='north', R='south')
        else:
            self.dirs = dict(F='west', B='east', L='south', R='north')

    def xz(self, u, v):
        f = self.front
        if f == 'south':
            return self.x0 + u, self.z1 - v
        if f == 'north':
            return self.x1 - u, self.z0 + v
        if f == 'east':
            return self.x1 - v, self.z0 + u
        return self.x0 + v, self.z1 - u

    def fmt(self, blk):
        if isinstance(blk, str) and '{' in blk:
            return blk.format(**self.dirs)
        return blk

    def set(self, u, y, v, blk):
        x, z = self.xz(u, v)
        self.w.set(x, y, z, self.fmt(blk))

    def set_if_air(self, u, y, v, blk):
        x, z = self.xz(u, v)
        self.w.set_if_air(x, y, z, self.fmt(blk))

    def get(self, u, y, v):
        x, z = self.xz(u, v)
        return self.w.get(x, y, z)

    def fill(self, u0, y0, v0, u1, y1, v1, blk):
        xa, za = self.xz(u0, v0)
        xb, zb = self.xz(u1, v1)
        self.w.fill(xa, y0, za, xb, y1, zb, self.fmt(blk))

    def fill_mix(self, u0, y0, v0, u1, y1, v1, rng, choices):
        xa, za = self.xz(u0, v0)
        xb, zb = self.xz(u1, v1)
        self.w.fill_mix(xa, y0, za, xb, y1, zb, rng, [(self.fmt(c), wt) for c, wt in choices])

    def pos(self, u, y, v):
        x, z = self.xz(u, v)
        return (x, y, z)


# ----------------------------------------------------------------------
# small props shared by every district
# ----------------------------------------------------------------------
def leaves(kind):
    return f'{kind}_leaves[persistent=true]'


def cypress(w, x, y, z, h, rng):
    """Tall narrow Mediterranean cypress. y = first trunk block."""
    lf = leaves('spruce')
    for i in range(h):
        w.set(x, y + i, z, 'spruce_log' if i < h - 2 else lf)
    for i in range(1, h):
        r = 1 if i < h - 3 else 0
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= (1 if (i > 2 and i < h - 3) or rng.random() < .5 else 1):
                    if abs(dx) + abs(dz) == 0:
                        continue
                    if abs(dx) + abs(dz) == 2 and (i < 3 or i > h - 5 or rng.random() < .6):
                        continue
                    w.set_if_air(x + dx, y + i, z + dz, lf)
    w.set_if_air(x, y + h, z, lf)


def olive(w, x, y, z, rng):
    """Low, wide, gnarled tree with grey-green canopy."""
    lf = leaves('azalea') if rng.random() < .8 else leaves('flowering_azalea')
    h = rng.randint(2, 3)
    for i in range(h):
        w.set(x, y + i, z, 'stripped_oak_wood' if i == 0 else 'oak_log')
    top = y + h
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            for dy in range(-1, 2):
                d = abs(dx) + abs(dz) + abs(dy) * 1.5
                if d <= 3.2 and rng.random() < .85:
                    w.set_if_air(x + dx, top + dy, z + dz, lf)
    w.set(x, top, z, 'oak_log')


def stone_pine(w, x, y, z, rng):
    """Umbrella pine: bare trunk, flat wide crown."""
    h = rng.randint(7, 10)
    lean = rng.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
    cx, cz = x, z
    for i in range(h):
        if i == h // 2:
            cx += lean[0]
            cz += lean[1]
        w.set(cx, y + i, cz, 'spruce_log')
    lf = leaves('dark_oak')
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            d = math.hypot(dx, dz)
            if d <= 4.3 and rng.random() < .93:
                w.set_if_air(cx + dx, y + h, cz + dz, lf)
            if d <= 3.0:
                w.set_if_air(cx + dx, y + h + 1, cz + dz, lf)
            if 1.5 < d <= 3.6 and rng.random() < .5:
                w.set_if_air(cx + dx, y + h - 1, cz + dz, lf)


def palm(w, x, y, z, rng):
    h = rng.randint(6, 9)
    for i in range(h):
        w.set(x, y + i, z, 'jungle_log')
    lf = leaves('jungle')
    top = y + h
    w.set(x, top, z, lf)
    for d, (dx, dz) in DIRS.items():
        for i in range(1, 5):
            w.set_if_air(x + dx * i, top - (0 if i < 3 else i - 2), z + dz * i, lf)
        w.set_if_air(x + dx + CW_VEC[d][0], top, z + dz + CW_VEC[d][1], lf)
    for dx, dz in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        w.set_if_air(x + dx * 2, top - 1, z + dz * 2, lf)


CW_VEC = {d: DIRS[CW[d]] for d in DIRS}


def citrus(w, x, y, z, rng):
    """Small round tree, used in courtyards and planters."""
    w.set(x, y, z, 'oak_log')
    w.set(x, y + 1, z, 'oak_log')
    lf = leaves('oak')
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            for dy in (2, 3):
                if dy == 3 and abs(dx) + abs(dz) == 2:
                    continue
                w.set_if_air(x + dx, y + dy, z + dz, lf)
    w.set(x, y + 2, z, 'oak_log')


def street_lamp(w, x, y, z):
    """Wrought-iron lamp. y = first block above ground."""
    w.set(x, y, z, 'polished_blackstone_wall')
    w.set(x, y + 1, z, 'iron_bars')
    w.set(x, y + 2, z, 'iron_bars')
    w.set(x, y + 3, z, 'lantern[hanging=false]')


def wall_lantern(w, x, y, z):
    w.set(x, y, z, 'lantern[hanging=true]')


def bench(w, x, y, z, axis, facing):
    """Two-wide bench. axis 'x' or 'z'; facing = direction the sitter looks."""
    dx, dz = (1, 0) if axis == 'x' else (0, 1)
    for i in range(2):
        w.set(x + dx * i, y, z + dz * i, f'spruce_stairs[facing={OPP[facing]},half=bottom]')


def planter(w, x, y, z, rng, plant=None):
    w.set(x, y, z, 'terracotta')
    plant = plant or rng.choice(['azalea', 'flowering_azalea', 'fern', 'rose_bush', 'peony', 'lilac'])
    if plant in ('rose_bush', 'peony', 'lilac'):
        w.set(x, y + 1, z, f'{plant}[half=lower]')
        w.set(x, y + 2, z, f'{plant}[half=upper]')
    else:
        w.set(x, y + 1, z, plant)


POTS = ['potted_red_tulip', 'potted_orange_tulip', 'potted_pink_tulip', 'potted_poppy',
        'potted_allium', 'potted_azure_bluet', 'potted_cornflower', 'potted_fern',
        'potted_dandelion', 'potted_blue_orchid', 'potted_oxeye_daisy', 'potted_cactus',
        'potted_azalea_bush', 'potted_flowering_azalea_bush']


def cafe_table(w, x, y, z, rng, cloth=None, top=None):
    """Pedestal table. Something always stands on it, which also keeps mobs from walking over it."""
    w.set(x, y, z, 'quartz_pillar[axis=y]')
    w.set(x, y + 1, z, top or rng.choice(['recrafted:drink[poison=none]', 'recrafted:meal[poison=none]',
                                          rng.choice(POTS), 'recrafted:drink[poison=none]']))


def chair(w, x, y, z, facing, wood='spruce'):
    """facing = direction the sitter looks."""
    w.set(x, y, z, f'{wood}_stairs[facing={OPP[facing]},half=bottom]')


def umbrella(w, x, y, z, color):
    for i in range(3):
        w.set(x, y + i, z, 'spruce_fence')
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if abs(dx) == 2 and abs(dz) == 2:
                continue
            c = color if (dx + dz) % 2 == 0 else 'white'
            w.set_if_air(x + dx, y + 3, z + dz, f'{c}_carpet' if max(abs(dx), abs(dz)) == 2 else f'{c}_wool')
    w.set(x, y + 3, z, f'{color}_wool')
    w.set(x, y + 4, z, f'{color}_carpet')


def market_stall(w, x, y, z, color, rng, goods=None, axis='x'):
    """3x2 stall with striped awning. (x, z) is the min corner."""
    L = 3
    for i in range(L):
        px, pz = (x + i, z) if axis == 'x' else (x, z + i)
        g = (goods or rng.choice([['barrel[facing=up]', 'composter', 'barrel[facing=up]'],
                                   ['hay_block', 'melon', 'pumpkin'],
                                   ['barrel[facing=up]', 'barrel[facing=up]', 'smoker']]))[i % 3]
        w.set(px, y, pz, g)
        w.set(px, y + 1, pz, rng.choice(POTS))          # produce on display; also blocks walking over the counter
    corners = [(x, z), (x + L - 1, z + 1)] if axis == 'x' else [(x, z), (x + 1, z + L - 1)]
    ex = [(x - 1, z - 1), (x + L, z - 1), (x - 1, z + 2), (x + L, z + 2)] if axis == 'x' else \
         [(x - 1, z - 1), (x + 2, z - 1), (x - 1, z + L), (x + 2, z + L)]
    for (px, pz) in ex:
        for i in range(3):
            w.set(px, y + i, pz, 'spruce_fence')
    x0, z0 = ex[0]
    x1, z1 = ex[3]
    for px in range(x0, x1 + 1):
        for pz in range(z0, z1 + 1):
            stripe = (px if axis == 'x' else pz) % 2 == 0
            w.set(px, y + 3, pz, f'{color}_wool' if stripe else 'white_wool')


def crate_stack(w, x, y, z, rng, n=3):
    opts = ['barrel[facing=up]', 'barrel[facing=north]', 'spruce_planks', 'composter', 'barrel[facing=east]']
    for i in range(n):
        dx, dz = rng.randint(-1, 1), rng.randint(-1, 1)
        hgt = rng.randint(1, 2)
        for j in range(hgt):
            w.set_if_air(x + dx, y + j, z + dz, rng.choice(opts))


def stairwell(w, x0, z0, f_top, f_bot, wall, step='stone_brick', n=4, shell=True):
    """Switchback stairwell. Interior is (n+4) x 4 cells with min corner (x0, z0).

    f_top / f_bot are the y of the *floor blocks* at the top and bottom.
    You enter on the west landing (x0..x0+1) at the top; the whole bottom
    level is floor, so a door can be cut anywhere in the shell down there.
    """
    L = n + 4
    full = step + 's' if step.endswith('brick') else step
    if step in ('stone', 'smooth_stone', 'quartz', 'smooth_quartz', 'polished_andesite',
                'polished_deepslate', 'cobblestone', 'spruce', 'oak', 'dark_oak'):
        full = {'spruce': 'spruce_planks', 'oak': 'oak_planks', 'dark_oak': 'dark_oak_planks',
                'quartz': 'quartz_block'}.get(step, step)
    if shell:
        w.fill(x0 - 1, f_bot - 1, z0 - 1, x0 + L, f_top + 5, z0 + 4, wall)
    w.clear(x0, f_bot + 1, z0, x0 + L - 1, f_top + 4, z0 + 3)
    w.fill(x0, f_bot, z0, x0 + L - 1, f_bot, z0 + 3, full)
    # top landing
    w.fill(x0, f_top, z0, x0 + 1, f_top, z0 + 3, full)
    for zz in (z0 + 2, z0 + 3):
        w.set(x0 + 2, f_top + 1, zz, 'iron_bars')
    f = f_top
    lane = 0  # 0: z0..z0+1 heading east, 1: z0+2..z0+3 heading west
    while f > f_bot:
        steps = min(n, f - f_bot)
        zs = (z0, z0 + 1) if lane == 0 else (z0 + 2, z0 + 3)
        for i in range(steps):
            x = x0 + 2 + i if lane == 0 else x0 + L - 3 - i
            face = 'west' if lane == 0 else 'east'
            for zz in zs:
                w.set(x, f - i, zz, f'{step}_stairs[facing={face},half=bottom]')
        f -= steps
        if f > f_bot:
            if lane == 0:
                w.fill(x0 + L - 2, f, z0, x0 + L - 1, f, z0 + 3, full)
            else:
                w.fill(x0, f, z0, x0 + 1, f, z0 + 3, full)
        lane ^= 1
    for yy in range(f_bot + 4, f_top + 4, 4):
        w.set(x0 + L // 2, yy, z0 - 1 if shell else z0, 'sea_lantern')
        w.set(x0 + L // 2, yy, z0 + 4 if shell else z0 + 3, 'sea_lantern')
    return L
