"""Ground, water and streets: the city before any building goes up."""
from ams_layout import *  # noqa: F401,F403

ROAD = [('bricks', 6), ('granite', 1)]            # klinkers: red-brown brick paving
SIDEWALK = [('stone_bricks', 5), ('cracked_stone_bricks', 1)]
EDGE = 'polished_andesite'                        # hardstone coping along the canal
WALL = [('bricks', 5), ('mud_bricks', 1)]         # canal walls
WALL_WET = [('mossy_stone_bricks', 3), ('mossy_cobblestone', 1)]


def base(ctx):
    """Solid ground everywhere at street level, then cut the water out of it."""
    w = ctx['w']
    w.fill(0, 0, 0, SX - 1, 0, SZ - 1, 'bedrock')
    w.fill(0, 1, 0, SX - 1, 52, SZ - 1, 'stone')
    w.fill(0, 53, 0, SX - 1, STREET - 1, SZ - 1, 'dirt')
    w.fill(0, STREET, 0, SX - 1, STREET, SZ - 1, 'packed_mud')


def water_body(ctx, x0, z0, x1, z1, bed, walls=True):
    """A rectangle of water with brick walls on whichever sides meet land."""
    w, rng = ctx['w'], ctx['rng']
    w.clear(x0, bed + 1, z0, x1, STREET, z1)
    w.fill(x0, bed, z0, x1, bed, z1, 'mud')
    w.fill(x0, bed + 1, z0, x1, WATER, z1, 'water')
    if not walls:
        return
    # walls: one block into the land on each side that is not water
    for (ax0, az0, ax1, az1) in ((x0 - 1, z0, x0 - 1, z1), (x1 + 1, z0, x1 + 1, z1),
                                 (x0, z0 - 1, x1, z0 - 1), (x0, z1 + 1, x1, z1 + 1)):
        for x in range(max(ax0, 0), min(ax1, SX - 1) + 1):
            for z in range(max(az0, 0), min(az1, SZ - 1) + 1):
                if w.get(x, WATER, z) == w.b('water'):
                    continue
                for y in range(bed, STREET):
                    blk = rng.choices([c for c, _ in WALL_WET], [k for _, k in WALL_WET])[0] if y >= WATER - 1 and y <= WATER \
                        else rng.choices([c for c, _ in WALL], [k for _, k in WALL])[0]
                    w.set(x, y, z, blk)
                w.set(x, STREET, z, EDGE)


def waters(ctx):
    w = ctx['w']
    # the IJ: open harbour water across the whole width
    water_body(ctx, 0, IJ[0], SX - 1, IJ[1], IJ_BED)
    # canals
    water_body(ctx, WEST_CANAL[0], OUTER[0], EAST_CANAL[1], OUTER[1], CANAL_BED)
    water_body(ctx, WEST_CANAL[0], INNER[0], EAST_CANAL[1], INNER[1], CANAL_BED)
    # cross canals and the lock channel
    water_body(ctx, WEST_CANAL[0], IJ[1] + 1, WEST_CANAL[1], INNER[1], CANAL_BED)
    water_body(ctx, EAST_CANAL[0], IJ[1] + 1, EAST_CANAL[1], INNER[1], CANAL_BED)
    # re-run the walls so corners between joined bodies are tidy
    for (x0, z0, x1, z1) in ((WEST_CANAL[0], OUTER[0], EAST_CANAL[1], OUTER[1]),
                             (WEST_CANAL[0], INNER[0], EAST_CANAL[1], INNER[1]),
                             (WEST_CANAL[0], IJ[1] + 1, WEST_CANAL[1], INNER[1]),
                             (EAST_CANAL[0], IJ[1] + 1, EAST_CANAL[1], INNER[1])):
        _rewall(ctx, x0, z0, x1, z1)
    # the far shore: a low strip of land across the IJ
    w.fill(0, IJ_BED, FAR_SHORE[0], SX - 1, STREET, FAR_SHORE[1], 'stone')
    w.fill(0, STREET, FAR_SHORE[0], SX - 1, STREET, FAR_SHORE[1], 'packed_mud')


def _rewall(ctx, x0, z0, x1, z1):
    w, rng = ctx['w'], ctx['rng']
    wat = w.b('water')
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if not (0 <= x < SX and 0 <= z < SZ) or w.get(x, WATER, z) == wat:
                continue
            near = any(0 <= x + dx < SX and 0 <= z + dz < SZ and w.get(x + dx, WATER, z + dz) == wat
                       for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if near and w.get(x, STREET, z) != w.b(EDGE):
                for y in range(CANAL_BED, STREET):
                    w.set(x, y, z, 'mossy_stone_bricks' if y >= WATER - 1 and y <= WATER and rng.random() < .6 else 'bricks')
                w.set(x, STREET, z, EDGE)


def quay(ctx, x0, z0, x1, z1, houses_side):
    """An 8-wide quay between a row of houses and a canal.

    houses_side: which side the houses are on ('north', 'south', 'west', 'east').
    Layout from the houses outward: 2 sidewalk, 4 road, 1 tree strip, then the coping (already set
    by the canal wall)."""
    w, rng = ctx['w'], ctx['rng']
    horiz = houses_side in ('north', 'south')
    span = (z0, z1) if horiz else (x0, x1)
    order = list(range(span[0], span[1] + 1))
    if houses_side in ('south', 'east'):
        order = order[::-1]          # first entry is next to the houses
    for i, c in enumerate(order):
        if i >= 7:
            continue                 # the coping along the water is the canal wall's
        mix = SIDEWALK if i < 2 else ROAD if i < 6 else [('cobblestone', 3), ('mossy_cobblestone', 1)]
        if horiz:
            w.fill_mix(x0, STREET, c, x1, STREET, c, rng, mix)
        else:
            w.fill_mix(c, STREET, z0, c, STREET, z1, rng, mix)
    return order


def streets(ctx):
    """Quays along every canal, the harbour front and the back street."""
    Q = ctx.setdefault('quays', {})
    Q['outer_n'] = quay(ctx, WEST_CANAL[1] + 1, OUTER_N_QUAY[0], EAST_CANAL[0] - 1, OUTER_N_QUAY[1], 'north')
    Q['outer_s'] = quay(ctx, WEST_CANAL[1] + 1, OUTER_S_QUAY[0], EAST_CANAL[0] - 1, OUTER_S_QUAY[1], 'south')
    Q['inner_n'] = quay(ctx, WEST_CANAL[1] + 1, INNER_N_QUAY[0], EAST_CANAL[0] - 1, INNER_N_QUAY[1], 'north')
    Q['inner_s'] = quay(ctx, WEST_HOUSES[0], INNER_S_QUAY[0], EAST_HOUSES[1], INNER_S_QUAY[1], 'south')
    Q['west_w'] = quay(ctx, WEST_QUAY[0], ANKERKADE[1] + 1, WEST_QUAY[1], INNER[1], 'west')
    Q['west_e'] = quay(ctx, EAST_OF_WEST_QUAY[0], ANKERKADE[1] + 1, EAST_OF_WEST_QUAY[1], INNER[0] - 1, 'east')
    Q['east_w'] = quay(ctx, EAST_W_QUAY[0], OUTER_S_QUAY[1] + 1, EAST_W_QUAY[1], INNER[0] - 1, 'west')
    Q['east_e'] = quay(ctx, EAST_E_QUAY[0], ANKERKADE[1] + 1, EAST_E_QUAY[1] - 4, INNER[1], 'east')
    # harbour front: wide paving with a strip of old setts along the water
    w, rng = ctx['w'], ctx['rng']
    w.fill_mix(0, STREET, ANKERKADE[0], SX - 1, STREET, ANKERKADE[1], rng, [('cobblestone', 4), ('stone_bricks', 2), ('andesite', 1)])
    w.fill_mix(0, STREET, ANKERKADE[1] - 3, SX - 1, STREET, ANKERKADE[1], rng, ROAD)
    # back street behind the south district
    w.fill_mix(0, STREET, BACK_STREET[0], SX - 1, STREET, BACK_STREET[1], rng, ROAD)
    w.fill_mix(0, STREET, BACK_STREET[0], SX - 1, STREET, BACK_STREET[0] + 1, rng, SIDEWALK)
    w.fill_mix(0, STREET, BACK_STREET[1] - 1, SX - 1, STREET, BACK_STREET[1], rng, SIDEWALK)
    # Zilversteeg: narrow alley paved in brick, open from canal to canal
    w.fill_mix(ZILVERSTEEG[0], STREET, MID_N[0], ZILVERSTEEG[1], STREET, MID_S[1], rng, ROAD)
