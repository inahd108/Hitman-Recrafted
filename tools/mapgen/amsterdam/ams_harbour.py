"""The harbour front: Ankerkade quay, the warehouse row, the smuggler's dock, the station, the ferry pier
and the far bank of the IJ."""
from ams_layout import *  # noqa: F401,F403
from ams_houses import Style, canal_house, split_lots, bays


def warehouse(ctx, x0, x1, name=None, brick=None):
    """A five- or six-storey warehouse between the harbour quay and the outer canal.
    Spout gable over the canal, loading doors stacked up the middle, green shutters on every window."""
    rng = ctx['rng']
    st = Style(rng, 'lane', gable='spout', hoist=True, lit=.25, door='dark_oak',
               brick=brick or rng.choice(['red', 'dark', 'black', 'plum', 'red']), trim='stone')
    floors = rng.choice([5, 5, 6])
    info = canal_house(ctx, x0, WAREHOUSES[0], x1, WAREHOUSES[1], 'south', floors, st, name=name)
    fr = info['frame']
    W = info['W']
    mid = (W - 1) // 2
    shutter = rng.choice(['green', 'green', 'red', 'black'])
    for side_v, face in ((0, '{F}'), (info['D'] - 1, '{B}')):
        out = -1 if side_v == 0 else info['D']
        for li, ly in enumerate(info['levels']):
            for u in bays(W):
                if li == 0 and side_v == 0:
                    continue
                rows = (ly + 1, ly + 2) if li else (ly + 2, ly + 3)
                if u == mid and li > 0:
                    # loading doors up the middle
                    for yy in rows:
                        fr.set(u, yy, side_v, 'air' if side_v == 0 else 'recrafted:canal_window[axis=z,lit=false]')
                    continue
                for du in (-1, 1):
                    if 0 <= u + du < W:
                        for yy in rows:
                            fr.set(u + du, yy, out, f'recrafted:shutter[facing={face},paint={shutter}]')
    # the quay side gets a big ground-floor cart door
    fr.set(mid, info['base'] + 1, info['D'] - 1, 'air')
    fr.set(mid, info['base'] + 2, info['D'] - 1, 'air')
    fr.set(mid, info['base'] + 3, info['D'] - 1, 'air')
    return info


def warehouses(ctx):
    rng = ctx['rng']
    out = []
    spans = [(EAST_OF_WEST_QUAY[1] + 3, FERRY_PIER[0] - 6), (FERRY_PIER[1] + 6, EAST_CANAL[0] - 3)]
    for a, b in spans:
        for (x0, x1) in split_lots(rng, a, b, widths=(11, 13, 13, 15)):
            if x1 - x0 + 1 < 9:
                continue
            out.append(warehouse(ctx, x0, x1, brick='dark' if x0 >= BREWERY[0] else None))
    # a little square in front of the ferry, between the two runs
    w = ctx['w']
    w.fill_mix(FERRY_PIER[0] - 5, STREET, WAREHOUSES[0], FERRY_PIER[1] + 5, STREET, OUTER_N_QUAY[1], rng,
               [('stone_bricks', 3), ('cobblestone', 2), ('bricks', 1)])
    ctx['anchors']['ferry.square'] = ((FERRY_PIER[0] + FERRY_PIER[1]) // 2, STREET + 1, WAREHOUSES[0] + 10)
    return out


def smuggler_dock(ctx):
    """A brick boathouse over the east canal where it passes through the warehouse row."""
    w = ctx['w']
    x0, x1 = EAST_CANAL[0] - 2, EAST_CANAL[1] + 2
    z0, z1 = WAREHOUSES
    top = STREET + 14
    for x in (x0, x0 + 1, x1 - 1, x1):
        w.fill(x, CANAL_BED, z0, x, top, z1, 'nether_bricks')
    for z in (z0, z1):
        w.fill(x0, WATER + 7, z, x1, top, z, 'nether_bricks')
        w.fill(x0 + 2, WATER + 1, z, x1 - 2, WATER + 6, z, 'air')          # boat arches
        w.fill(x0 + 2, WATER + 6, z, x1 - 2, WATER + 6, z, 'dark_oak_slab[type=top]')
    w.fill(x0, top + 1, z0, x1, top + 1, z1, 'deepslate_tiles')
    # jetty inside along the west wall, running out under both arches to the quays
    w.fill(x0 + 2, WATER + 1, z0 - 1, x0 + 3, WATER + 1, z1 + 1, 'spruce_slab')
    for z in range(z0 + 4, z1 - 2, 6):
        w.set(x0 + 4, WATER + 1, z, 'spruce_fence')
        w.set(x0 + 3, WATER + 4, z, 'light[level=10]')
    ctx['anchors']['dock.jetty'] = (x0 + 2, WATER + 2, (z0 + z1) // 2)
    ctx['anchors']['dock.berth'] = ((x0 + x1) // 2 + 1, WATER + 1, (z0 + z1) // 2)


def station(ctx):
    """Station Ankerkade: one platform under a glass roof and a train waiting at it."""
    w = ctx['w']
    x0, x1 = 0, STATION[1]
    z_track = (ANKERKADE[0] + 1, ANKERKADE[0] + 3)
    for z in range(z_track[0], z_track[1] + 1):
        w.fill(x0, STREET, z, x1, STREET, z, 'gravel')
    for z in (z_track[0], z_track[1]):
        w.fill(x0, STREET + 1, z, x1, STREET + 1, z, 'rail[shape=east_west]')
    plat = (z_track[1] + 1, z_track[1] + 5)
    w.fill(x0, STREET + 1, plat[0], x1, STREET + 1, plat[1], 'smooth_stone')
    w.fill(x0, STREET + 1, plat[0], x1, STREET + 1, plat[0], 'yellow_concrete')
    # roof on iron columns
    for x in range(x0 + 2, x1 + 1, 6):
        for z in (plat[0] + 1, plat[1]):
            for y in range(STREET + 2, STREET + 7):
                w.set(x, y, z, 'iron_bars' if y < STREET + 6 else 'polished_blackstone')
    w.fill(x0, STREET + 7, z_track[0] - 1, x1, STREET + 7, plat[1] + 1, 'glass')
    w.fill(x0, STREET + 7, plat[1] + 1, x1, STREET + 7, plat[1] + 1, 'polished_blackstone_slab')
    for x in range(x0 + 4, x1 + 1, 8):
        w.set(x, STREET + 6, plat[0] + 2, 'lantern[hanging=true]')
    # the train: two coaches in yellow with a blue band
    for cx0 in (x0, x0 + 13):
        cx1 = min(cx0 + 11, x1)
        w.fill(cx0, STREET + 2, z_track[0], cx1, STREET + 5, z_track[1], 'yellow_concrete')
        w.fill(cx0, STREET + 3, z_track[0], cx1, STREET + 3, z_track[1], 'blue_concrete')
        w.fill(cx0 + 1, STREET + 4, z_track[1], cx1 - 1, STREET + 4, z_track[1], 'glass_pane')
        w.fill(cx0 + 1, STREET + 4, z_track[0], cx1 - 1, STREET + 4, z_track[0], 'glass_pane')
        w.fill(cx0, STREET + 6, z_track[0], cx1, STREET + 6, z_track[1], 'light_gray_concrete')
        w.set(cx0 + 5, STREET + 2, z_track[1], 'air')
        w.set(cx0 + 5, STREET + 3, z_track[1], 'air')
        w.set(cx0 + 5, STREET + 4, z_track[1] - 1, 'light[level=12]')
    ctx['anchors']['station.platform'] = (x1 - 3, STREET + 2, plat[0] + 2)
    ctx['anchors']['exit.train'] = (5, STREET + 2, z_track[1])


def ferry(ctx):
    """Timber pier into the IJ and the free ferry moored at its end."""
    w = ctx['w']
    x0, x1 = FERRY_PIER
    zp0 = IJ[0] + 18
    w.fill(x0, STREET, zp0, x1, STREET, IJ[1], 'spruce_planks')
    for z in range(zp0, IJ[1] + 1, 5):
        for x in (x0, x1):
            for y in range(IJ_BED, STREET):
                w.set(x, y, z, 'stripped_spruce_log[axis=y]')
            w.set(x, STREET + 1, z, 'spruce_fence')
            w.set(x, STREET + 2, z, 'lantern') if z % 10 == 0 else None
    # the ferry: flat white hull, blue band, open deck with a wheelhouse
    fx0, fx1 = x0 - 8, x1 + 8
    fz0, fz1 = IJ[0] + 6, zp0 - 1
    w.fill(fx0, WATER - 1, fz0, fx1, WATER + 1, fz1, 'white_concrete')
    w.fill(fx0, WATER, fz0, fx1, WATER, fz1, 'blue_concrete')
    w.fill(fx0 + 1, WATER + 1, fz0 + 1, fx1 - 1, WATER + 1, fz1 - 1, 'gray_concrete')
    w.fill(fx0 + 2, WATER + 2, fz0 + 2, fx0 + 5, WATER + 4, fz0 + 5, 'white_concrete')
    w.fill(fx0 + 2, WATER + 3, fz0 + 2, fx0 + 5, WATER + 3, fz0 + 5, 'glass')
    w.fill(fx0 + 1, WATER + 2, fz0 + 1, fx1 - 1, WATER + 2, fz0 + 1, 'white_stained_glass_pane')
    w.fill(fx0 + 1, WATER + 2, fz1 - 1, fx1 - 1, WATER + 2, fz1 - 1, 'white_stained_glass_pane')
    w.set(fx0 + 3, WATER + 3, fz0 + 3, 'light[level=13]')
    ctx['anchors']['exit.ferry'] = ((fx0 + fx1) // 2, WATER + 2, (fz0 + fz1) // 2)


def far_shore(ctx):
    """Silhouettes across the IJ: sheds, a crane, a few lit windows. Only ever seen from a distance."""
    w, rng = ctx['w'], ctx['rng']
    x = 0
    while x < SX:
        wd = rng.randint(6, 18)
        h = rng.randint(5, 16)
        mat = rng.choice(['deepslate_bricks', 'polished_blackstone', 'gray_concrete', 'black_concrete', 'nether_bricks'])
        w.fill(x, STREET + 1, FAR_SHORE[0], min(x + wd - 1, SX - 1), STREET + h, FAR_SHORE[1] - 1, mat)
        for k in range(rng.randint(0, 4)):
            lx = rng.randint(x, min(x + wd - 1, SX - 1))
            ly = rng.randint(STREET + 2, STREET + h - 1)
            w.set(lx, ly, FAR_SHORE[1] - 1, 'glass')
            w.set(lx, ly, FAR_SHORE[1] - 2, 'light[level=10]')
        x += wd + rng.randint(1, 6)
    for cx in (rng.randint(40, 120), rng.randint(220, 330)):                   # cranes
        for y in range(STREET + 1, STREET + 26):
            w.set(cx, y, FAR_SHORE[0] + 2, 'iron_bars')
        for k in range(-6, 14):
            w.set(cx + k, STREET + 26, FAR_SHORE[0] + 2, 'polished_blackstone_slab')
        w.set(cx + 13, STREET + 25, FAR_SHORE[0] + 2, 'chain')
        w.set(cx, STREET + 27, FAR_SHORE[0] + 2, 'redstone_lamp[lit=true]')


def build(ctx):
    far_shore(ctx)
    station(ctx)
    ferry(ctx)
    ctx['warehouses'] = warehouses(ctx)
    smuggler_dock(ctx)
