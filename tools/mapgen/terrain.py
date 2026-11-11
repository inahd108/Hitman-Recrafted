"""Island terrain for Corvara: a terraced harbour town on a limestone island.

Layout (x east, z south):
  T0  y=65  z>=170   harbour front and quay
  T1  y=73  z 132..  Piazza del Sale
  T2  y=81  z 96..   upper town
  T3  y=89  z 58..   Tenuta Belmonte (west), olive grove, chapel (east)
  hill      z<58     vineyard steps, then cliffs falling to the sea
"""
import random

import numpy as np

from core import value_noise, smoothstep

SX, SY, SZ = 320, 136, 288
SEA = 62
T0, T1, T2, T3 = 65, 73, 81, 89
Z0, Z1, Z2, Z3 = 170, 132, 96, 58      # first row (north edge) of each terrace band
CORE_W, CORE_E = 70, 250
QUAY_Z = 204                            # last land row of the harbour front
K_SEA, K_SAND, K_GRASS, K_ROCK, K_PAVED, K_YARD = range(6)


def build_terrain(w, seed=7):
    rng = random.Random(seed)
    X, Z = np.meshgrid(np.arange(SX), np.arange(SZ))
    n_big = value_noise(SX, SZ, 48, seed + 1)
    n_med = value_noise(SX, SZ, 16, seed + 2)
    n_sml = value_noise(SX, SZ, 6, seed + 3, octaves=2)

    # --- coastline --------------------------------------------------------
    nx = (X - 160) / 138.0
    nz = (Z - 150) / 136.0
    r = (np.abs(nx) ** 4 + np.abs(nz) ** 4) ** 0.25
    d_e = (1 - r) * 112 + n_big * 7 + n_med * 3
    beach_line = 206 + 6 * np.sin(np.clip((X - 24) / 60.0, 0, 1) * np.pi)
    d_s = np.where(X < 84, beach_line - Z, QUAY_Z + 0.5 - Z)
    d = np.minimum(d_e, d_s)
    land = d > 0

    # --- terrace target ---------------------------------------------------
    steps = T3 + 2 * np.floor((Z3 - Z) / 7.0)
    t_core = np.where(Z >= Z0, T0, np.where(Z >= Z1, T1, np.where(Z >= Z2, T2, np.where(Z >= Z3, T3, steps))))
    t_smooth = np.interp(Z, [18, 58, 96, 132, 168, 204], [101, 90, 82, 74, 67, 63.4]) + n_med * 1.6
    west_start = np.where(Z < Z2, 34, CORE_W)
    wgt_w = smoothstep((west_start - X) / 16.0)
    east_flat = (X > CORE_E) & (Z >= 148)            # cannery yard
    wgt_e = np.where(east_flat, 0.0, smoothstep((X - CORE_E) / 12.0))
    wgt = np.maximum(wgt_w, wgt_e)
    T = t_core * (1 - wgt) + t_smooth * wgt
    T = np.where(east_flat, T0, T)
    # chapel knoll: gentle rise in the north-east instead of vineyard steps
    knoll = (X > 172) & (Z < Z3)
    T = np.where(knoll & (wgt < 0.01), T3 + np.clip((Z3 - Z) * 0.22, 0, 7) + n_med * 0.8, T)

    # --- coast clamp --------------------------------------------------------
    cliff = 63.2 + np.maximum(d_e, 0) * 2.3 + n_sml * 1.8
    H = np.minimum(T, cliff)
    beach = (X < 84) & (Z > 170)
    bh = 62.7 + np.maximum(d_s, 0) * 0.2
    H = np.where(beach, np.minimum(H, bh), H)
    # sea floor
    depth = np.clip(1.5 + (-d) * 0.7 + n_med * 1.5, 1, 20)
    harbour = (X >= 84) & (Z > QUAY_Z)
    depth = np.where(harbour, np.maximum(depth, 6), depth)
    H = np.where(land, H, SEA - depth)
    H = np.floor(H).astype(int)
    H = np.where(land, np.maximum(H, SEA + 1), H)

    # --- surface kinds ------------------------------------------------------
    K = np.full((SZ, SX), K_GRASS, dtype=np.uint8)
    K[~land] = K_SEA
    gz, gx = np.gradient(H.astype(float))
    steep = (np.abs(gz) + np.abs(gx)) >= 1.6
    K[land & steep] = K_ROCK
    K[land & beach & (H <= 66)] = K_SAND
    K[land & (H <= 63) & (X < 100)] = K_SAND
    core = (X >= CORE_W) & (X <= CORE_E)
    K[land & core & (Z >= Z2)] = K_PAVED
    K[land & east_flat] = K_YARD

    # --- voxel fill ---------------------------------------------------------
    ys = np.arange(SY)[:, None, None]
    Hn = H[None]
    w.G[(ys <= Hn)] = w.b('stone')
    w.G[(ys > Hn) & (ys <= SEA)] = w.b('water')
    w.G[0] = w.b('bedrock')

    zs, xs = np.nonzero(np.ones_like(H, dtype=bool))
    hs = H[zs, xs]
    ks = K[zs, xs]

    def put(mask, dy, blocks, weights=None):
        ids = np.array([w.b(b) for b in blocks], dtype=np.uint16)
        n = int(mask.sum())
        if n == 0:
            return
        pick = ids[np.random.default_rng(seed + dy + len(blocks)).choice(len(ids), n, p=weights)]
        w.G[hs[mask] - dy, zs[mask], xs[mask]] = pick

    m = ks == K_SEA
    put(m, 0, ['sand', 'gravel', 'sand', 'clay'], [.6, .2, .15, .05])
    put(m, 1, ['sand', 'sandstone'], [.5, .5])
    m = ks == K_SAND
    put(m, 0, ['sand'])
    put(m, 1, ['sand'])
    put(m, 2, ['sandstone'])
    m = ks == K_GRASS
    put(m, 0, ['grass_block', 'coarse_dirt', 'podzol'], [.9, .07, .03])
    put(m, 1, ['dirt'])
    put(m, 2, ['dirt'])
    m = ks == K_ROCK
    for dy in range(0, 7):
        put(m, dy, ['calcite', 'diorite', 'stone', 'andesite', 'smooth_sandstone'], [.34, .22, .2, .12, .12])
    m = ks == K_PAVED
    put(m, 0, ['stone_bricks', 'cobblestone', 'andesite', 'cracked_stone_bricks', 'mossy_stone_bricks', 'gravel'],
        [.44, .26, .16, .07, .05, .02])
    put(m, 1, ['cobblestone'])
    m = ks == K_YARD
    put(m, 0, ['smooth_stone', 'stone', 'gravel', 'andesite', 'coarse_dirt'], [.4, .2, .15, .15, .1])

    # --- retaining walls: face every tall step inside the town with masonry --
    wall_ids = [w.b(b) for b in ('stone_bricks', 'mossy_stone_bricks', 'cracked_stone_bricks', 'cobblestone',
                                 'smooth_sandstone')]
    wall_w = [.6, .12, .1, .08, .1]
    for z in range(1, SZ - 1):
        for x in range(1, SX - 1):
            if K[z, x] not in (K_PAVED, K_YARD, K_GRASS):
                continue
            if not (60 <= x <= 300 and z >= 50):
                continue
            h = H[z, x]
            lo = min(H[z + 1, x], H[z - 1, x], H[z, x + 1], H[z, x - 1])
            if h - lo >= 3 and K[z, x] != K_GRASS or (h - lo >= 5 and CORE_W <= x <= CORE_E):
                col = rng.choices(wall_ids, wall_w, k=h - lo)
                w.G[lo + 1:h + 1, z, x] = col

    # tufts on the grass
    for z in range(SZ):
        for x in range(SX):
            if K[z, x] == K_GRASS:
                rr = rng.random()
                y = H[z, x] + 1
                if rr < .10:
                    w.set(x, y, z, 'grass')
                elif rr < .12:
                    w.set(x, y, z, 'fern')
                elif rr < .135:
                    w.set(x, y, z, rng.choice(['poppy', 'dandelion', 'azure_bluet', 'oxeye_daisy', 'cornflower']))
                elif rr < .14:
                    w.set(x, y, z, 'dead_bush') if False else None
    return H, K, land
