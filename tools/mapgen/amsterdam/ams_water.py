"""Things on and over the water: arched bridges, the drawbridge, the lock, houseboats, barges."""
from ams_layout import *  # noqa: F401,F403


def arch_bridge(ctx, x0, x1, z0, z1, axis='z', name=None):
    """Brick arch over a canal. axis = direction of travel across the bridge ('z' crosses an east-west canal).
    x0..x1 (axis z) is the width of the deck; z0..z1 the water it spans."""
    w, rng = ctx['w'], ctx['rng']
    span = (z0, z1) if axis == 'z' else (x0, x1)
    n = span[1] - span[0] + 1
    mid = (span[0] + span[1]) / 2
    cells = range(x0, x1 + 1) if axis == 'z' else range(z0, z1 + 1)

    def put(c, t, y, blk):
        if axis == 'z':
            w.set(c, y, t, blk)
        else:
            w.set(t, y, c, blk)

    # ramps on the quays: rise 2 over 4 blocks each side
    for side, sgn in ((span[0] - 1, -1), (span[1] + 1, 1)):
        for k in range(4):
            t = side + sgn * k
            h = STREET + (1 if k < 2 else 0)
            for c in cells:
                put(c, t, h, 'bricks' if k < 2 else 'stone_bricks')
                if k < 2:
                    put(c, t, h - 1, 'bricks')
    for t in range(span[0], span[1] + 1):
        d = abs(t - mid) / (n / 2)              # 0 at the crown, 1 at the abutments
        deck = STREET + 2 if d < .55 else STREET + 1
        arch_top = WATER + (3 if d < .35 else 2 if d < .7 else 1)
        for c in cells:
            put(c, t, deck, 'bricks')
            for y in range(arch_top + 1, deck):
                put(c, t, y, 'bricks')
            put(c, t, arch_top, 'stone_bricks' if d < .9 else 'bricks')
        for edge in (cells[0], cells[-1]):
            put(edge, t, deck + 1, 'stone_brick_wall')
        if d < .9:
            # bridge lights: outline the arch and the deck on both faces of the bridge
            if axis == 'z':
                for xx, f in ((cells[0] - 1, 'west'), (cells[-1] + 1, 'east')):
                    w.set(xx, arch_top, t, f'recrafted:bulb_string[facing={f}]')
                    w.set(xx, deck, t, f'recrafted:bulb_string[facing={f}]')
            else:
                for zz, f in ((cells[0] - 1, 'north'), (cells[-1] + 1, 'south')):
                    w.set(t, arch_top, zz, f'recrafted:bulb_string[facing={f}]')
                    w.set(t, deck, zz, f'recrafted:bulb_string[facing={f}]')
        if d >= .9:
            for c in cells:
                for y in range(CANAL_BED, WATER + 1):
                    put(c, t, y, 'bricks')
    ctx.setdefault('bridges', []).append(dict(name=name, x0=x0, x1=x1, z0=z0, z1=z1, axis=axis))


def drawbridge(ctx, x0, x1, z0, z1, name='drawbridge'):
    """White timber drawbridge in the spirit of the old Amstel bridges: two portals with lifting beams."""
    w = ctx['w']
    deck = STREET + 1
    for z in range(z0 - 2, z1 + 3):
        for x in range(x0, x1 + 1):
            w.set(x, deck, z, 'stripped_birch_log[axis=z]' if x in (x0, x1) else 'birch_planks')
        w.set(x0, deck + 1, z, 'birch_fence')
        w.set(x1, deck + 1, z, 'birch_fence')
        if z0 <= z <= z1:
            w.set(x0 - 1, deck, z, 'recrafted:bulb_string[facing=west]')
            w.set(x1 + 1, deck, z, 'recrafted:bulb_string[facing=east]')
    # piers in the water
    for zp in (z0 + 2, z1 - 2):
        for x in (x0 + 1, x1 - 1):
            for y in range(CANAL_BED, deck):
                w.set(x, y, zp, 'stripped_birch_log[axis=y]')
    # portals over the lifting span
    zc = (z0 + z1) // 2
    for zp in (zc - 4, zc + 4):
        for x in (x0, x1):
            for y in range(deck + 1, deck + 9):
                w.set(x, y, zp, 'stripped_birch_log[axis=y]')
        for x in range(x0, x1 + 1):
            w.set(x, deck + 9, zp, 'stripped_birch_log[axis=x]')
    for z in range(zc - 6, zc + 7):
        w.set(x0, deck + 10, z, 'stripped_birch_log[axis=z]')
        w.set(x1, deck + 10, z, 'stripped_birch_log[axis=z]')
        w.set(x0 - 1, deck + 10, z, 'recrafted:bulb_string[facing=west]')
        w.set(x1 + 1, deck + 10, z, 'recrafted:bulb_string[facing=east]')
    for zp in (zc - 4, zc + 4):
        for y in range(deck + 1, deck + 9):
            w.set(x0 - 1, y, zp, 'recrafted:bulb_string[facing=west]')
            w.set(x1 + 1, y, zp, 'recrafted:bulb_string[facing=east]')
    for z in (zc - 6, zc + 6):
        for x in (x0, x1):
            w.set(x, deck + 9, z, 'chain')
            w.set(x, deck + 8, z, 'chain')
    ctx.setdefault('bridges', []).append(dict(name=name, x0=x0, x1=x1, z0=z0, z1=z1, axis='z', draw=True))
    ctx['anchors']['drawbridge.n'] = (x0 + 2, deck + 1, z0 - 3)
    ctx['anchors']['drawbridge.s'] = (x0 + 2, deck + 1, z1 + 3)


def lock(ctx):
    """Two timber gates across the west channel with a walkway on each, and the keeper's little house."""
    w = ctx['w']
    x0, x1 = WEST_CANAL
    for zg in LOCK_GATES:
        for x in range(x0, x1 + 1):
            for y in range(CANAL_BED, WATER + 1):
                w.set(x, y, zg, 'dark_oak_planks')
            w.set(x, STREET, zg, 'dark_oak_slab[type=top]')
            w.set(x, STREET + 1, zg - 1, 'dark_oak_fence')
        for x in (x0 + 4, x1 - 4):
            w.set(x, STREET + 1, zg + 1, 'dark_oak_fence')
            w.set(x, STREET + 2, zg + 1, 'dark_oak_fence')
            w.set(x, STREET + 3, zg + 1, 'dark_oak_trapdoor[facing=south,half=top]')
    # keeper's house: tiny, tall, leaning-looking, on the east bank
    hx0, hz0 = x1 + 2, LOCK_GATES[0] - 2
    w.fill(hx0, STREET + 1, hz0, hx0 + 5, STREET + 9, hz0 + 6, 'red_nether_bricks')
    w.fill(hx0 + 1, STREET + 1, hz0 + 1, hx0 + 4, STREET + 8, hz0 + 5, 'air')
    w.fill(hx0 + 1, STREET + 1, hz0 + 1, hx0 + 4, STREET + 1, hz0 + 5, 'spruce_planks')
    for k in range(4):
        w.fill(hx0 - 1 + k, STREET + 10 + k, hz0, hx0 - 1 + k, STREET + 10 + k, hz0 + 6, 'deepslate_tile_stairs[facing=east]')
        w.fill(hx0 + 6 - k, STREET + 10 + k, hz0, hx0 + 6 - k, STREET + 10 + k, hz0 + 6, 'deepslate_tile_stairs[facing=west]')
    for z in (hz0, hz0 + 6):
        for k in range(4):
            w.fill(hx0 + k, STREET + 10 + k, z, hx0 + 5 - k, STREET + 10 + k, z, 'red_nether_bricks')
    w.set(hx0, STREET + 2, hz0 + 3, 'air')
    w.set(hx0, STREET + 3, hz0 + 3, 'air')
    w.set(hx0, STREET + 2, hz0 + 3, 'warped_door[facing=west,half=lower,hinge=left]')
    w.set(hx0, STREET + 3, hz0 + 3, 'warped_door[facing=west,half=upper,hinge=left]')
    for y in (STREET + 3, STREET + 7):
        for z in (hz0 + 1, hz0 + 5):
            w.set(hx0, y, z, 'glass_pane')
            w.set(hx0, y + 1, z, 'glass_pane')
        w.set(hx0 + 2, y + 1, hz0 + 3, 'light[level=12]')
    ctx['anchors']['lock.keeper'] = (hx0 + 2, STREET + 2, hz0 + 3)
    ctx['anchors']['lock.n'] = ((x0 + x1) // 2, STREET + 1, LOCK_GATES[0])
    ctx['anchors']['lock.s'] = ((x0 + x1) // 2, STREET + 1, LOCK_GATES[1])


HULLS = ['black_concrete', 'green_terracotta', 'blue_terracotta', 'dark_oak_planks', 'cyan_terracotta', 'white_terracotta']
CABINS = ['spruce_planks', 'white_terracotta', 'dark_oak_planks', 'birch_planks', 'light_gray_terracotta']


def houseboat(ctx, x0, z0, length, beam, rng, name=None, hull=None, cabin=None):
    """Moored along x. z0 is the side against the quay."""
    w = ctx['w']
    x1, z1 = x0 + length - 1, z0 + beam - 1
    hull = hull or rng.choice(HULLS)
    cabin = cabin or rng.choice(CABINS)
    w.fill(x0, WATER - 1, z0, x1, WATER + 1, z1, hull)
    w.fill(x0 + 1, WATER - 1, z0 + 1, x1 - 1, WATER + 1, z1 - 1, 'air')
    w.fill(x0 + 1, WATER - 1, z0 + 1, x1 - 1, WATER - 1, z1 - 1, 'spruce_planks')
    w.fill(x0, WATER + 1, z0, x1, WATER + 1, z1, 'spruce_slab')
    # cabin
    cx0, cx1 = x0 + 2, x1 - 2
    w.fill(cx0, WATER + 2, z0 + 1, cx1, WATER + 4, z1 - 1, cabin)
    w.fill(cx0 + 1, WATER + 2, z0 + 2, cx1 - 1, WATER + 3, z1 - 2, 'air')
    w.fill(cx0, WATER + 5, z0 + 1, cx1, WATER + 5, z1 - 1, 'spruce_slab')
    for x in range(cx0 + 1, cx1, 2):
        lit = 'true' if rng.random() < .7 else 'false'
        w.set(x, WATER + 3, z0 + 1, f'recrafted:canal_window[axis=z,lit={lit}]')
        w.set(x, WATER + 3, z1 - 1, f'recrafted:canal_window[axis=z,lit={lit}]')
    w.set(cx0, WATER + 2, (z0 + z1) // 2, 'air')
    w.set(cx0, WATER + 3, (z0 + z1) // 2, 'air')
    # roof garden
    for x in range(cx0, cx1 + 1, 2):
        if rng.random() < .6:
            w.set(x, WATER + 6, z0 + 1 + rng.randint(0, max(0, beam - 3)), rng.choice(
                ['potted_fern', 'potted_azalea_bush', 'potted_red_tulip', 'potted_oak_sapling', 'potted_flowering_azalea_bush']))
    # gangplank to the quay
    gx = cx0 + 1
    w.set(gx, WATER + 1, z0 - 1, 'spruce_slab')
    ctx.setdefault('boats', []).append(dict(name=name, x0=x0, z0=z0, x1=x1, z1=z1))
    return (gx, WATER + 2, z0 + 1)


def flower_barge(ctx, x0, z0, length, rng):
    """A covered flower stall on a barge, moored along x on the inner canal's south side."""
    w = ctx['w']
    x1, z1 = x0 + length - 1, z0 + 5
    w.fill(x0, WATER - 1, z0, x1, WATER, z1, 'dark_oak_planks')
    w.fill(x0, WATER + 1, z0, x1, WATER + 1, z1, 'spruce_planks')
    for x in (x0, x1):
        for z in (z0, z1):
            for y in range(WATER + 2, WATER + 5):
                w.set(x, y, z, 'dark_oak_fence')
    w.fill(x0, WATER + 5, z0, x1, WATER + 5, z1, 'glass')
    w.fill(x0, WATER + 5, z1, x1, WATER + 5, z1, 'green_wool')
    flowers = ['potted_red_tulip', 'potted_orange_tulip', 'potted_white_tulip', 'potted_pink_tulip', 'potted_allium',
               'potted_cornflower', 'potted_poppy', 'potted_oxeye_daisy']
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1, 2):
            w.set(x, WATER + 2, z, 'barrel[facing=up]' if (x + z) % 3 else 'composter')
            w.set(x, WATER + 3, z, rng.choice(flowers))
    w.set((x0 + x1) // 2, WATER + 4, (z0 + z1) // 2, 'light[level=12]')
