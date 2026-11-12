"""Street furniture and life on the water: elms, lanterns, bollards, benches, houseboats, the flower barges."""
from ams_layout import *  # noqa: F401,F403
from ams_city import elm
from ams_water import houseboat, flower_barge


PAINTS = [('black', 9), ('navy', 3), ('red', 2), ('green', 2), ('cream', 2)]


def lantern(w, x, y, z):
    """Canal lantern on a dark green post."""
    for k in range(3):
        w.set(x, y + k, z, 'recrafted:lamp_post')
    w.set(x, y + 3, z, 'recrafted:canal_lamp')


def bikes(w, rng, x, y, z, n, along='x'):
    """A cluster of parked bikes, leaning together (along = direction of the quay)."""
    for k in range(n):
        paint = rng.choices([p for p, _ in PAINTS], [c for _, c in PAINTS])[0]
        if along == 'x':
            w.set(x + k * 2, y, z, f'recrafted:bicycle[facing={rng.choice(["north", "south"])},paint={paint}]')
        else:
            w.set(x, y, z + k * 2, f'recrafted:bicycle[facing={rng.choice(["east", "west"])},paint={paint}]')


def near_bridge(ctx, x, z, pad=6):
    for b in ctx.get('bridges', []):
        if b['x0'] - pad <= x <= b['x1'] + pad and b['z0'] - pad - 6 <= z <= b['z1'] + pad + 6:
            return True
    return False


def tree_strip(ctx, z_strip, z_side_sidewalk, x0, x1):
    """Elms, lanterns and bollards along an east-west quay. z_strip is the tree strip row,
    z_side_sidewalk the sidewalk row next to the road (bollards stand there)."""
    w, rng = ctx['w'], ctx['rng']
    x = x0 + rng.randint(2, 5)
    k = 0
    while x <= x1:
        if not near_bridge(ctx, x, z_strip):
            if k % 3 == 1:
                lantern(w, x, STREET + 1, z_strip)
            else:
                elm(w, x, STREET + 1, z_strip, rng)
            if rng.random() < .6:
                bikes(w, rng, x + 2, STREET + 1, z_strip, rng.randint(1, 3))
        x += rng.randint(8, 11)
        k += 1
    for x in range(x0, x1 + 1, 3):
        if not near_bridge(ctx, x, z_side_sidewalk, 2) and rng.random() < .8:
            w.set(x, STREET + 1, z_side_sidewalk, 'recrafted:bollard')


def tree_strip_z(ctx, x_strip, x_side, z0, z1):
    w, rng = ctx['w'], ctx['rng']
    z = z0 + rng.randint(2, 5)
    k = 0
    while z <= z1:
        if not near_bridge(ctx, x_strip, z):
            if k % 3 == 1:
                lantern(w, x_strip, STREET + 1, z)
            else:
                elm(w, x_strip, STREET + 1, z, rng)
        z += rng.randint(8, 11)
        k += 1
    for z in range(z0, z1 + 1, 3):
        if rng.random() < .8:
            w.set(x_side, STREET + 1, z, 'recrafted:bollard')


def quays(ctx):
    a, b = WEST_CANAL[1] + 1, EAST_CANAL[0] - 1
    # tree strip = 7th row from the houses (index 6), sidewalk edge = index 1
    tree_strip(ctx, OUTER_N_QUAY[1] - 1, OUTER_N_QUAY[0] + 1, a, b)
    tree_strip(ctx, OUTER_S_QUAY[0] + 1, OUTER_S_QUAY[1] - 1, a, b)
    tree_strip(ctx, INNER_N_QUAY[1] - 1, INNER_N_QUAY[0] + 1, a, b)
    tree_strip(ctx, INNER_S_QUAY[0] + 1, INNER_S_QUAY[1] - 1, WEST_HOUSES[0] + 2, BLOEMENPLEIN[0] - 2)
    tree_strip(ctx, INNER_S_QUAY[0] + 1, INNER_S_QUAY[1] - 1, BLOEMENPLEIN[1] + 2, EAST_HOUSES[1] - 2)
    tree_strip_z(ctx, WEST_QUAY[1] - 1, WEST_QUAY[0] + 1, OUTER[0], INNER[1] - 2)
    tree_strip_z(ctx, EAST_E_QUAY[0] + 1, EAST_E_QUAY[1] - 1, OUTER[0], INNER[1] - 2)
    # harbour front: lanterns along the water and bollards for the boats
    w = ctx['w']
    rng_h = ctx['rng']
    for x in range(30, SX - 4, 14):
        if not (FERRY_PIER[0] - 2 <= x <= FERRY_PIER[1] + 2) and not (EAST_CANAL[0] - 3 <= x <= EAST_CANAL[1] + 3) \
                and not (WEST_CANAL[0] - 1 <= x <= WEST_CANAL[1] + 1):
            lantern(w, x, STREET + 1, ANKERKADE[0] + 1)
            if rng_h.random() < .5:
                bikes(w, rng_h, x + 2, STREET + 1, ANKERKADE[1] - 5, rng_h.randint(2, 5))
            w.set(x + 5, STREET + 1, ANKERKADE[0], 'polished_blackstone_wall')


def boats(ctx):
    rng = ctx['rng']
    # houseboats along the south side of the outer canal, clear of the bridges
    x = WEST_CANAL[1] + 6
    n = 0
    while x < EAST_CANAL[0] - 22:
        L = rng.choice([14, 16, 18, 20])
        if any(bx0 - 4 <= x + L and x <= bx1 + 4 for bx0, bx1 in OUTER_BRIDGES):
            x += 6
            continue
        name = 'kooistra_houseboat' if n == 7 else None
        houseboat(ctx, x, OUTER[1] - 5, L, 5, rng, name=name,
                  hull='black_concrete' if name else None, cabin='dark_oak_planks' if name else None)
        if name:
            ctx['anchors']['kooistra.houseboat'] = (x + 3, WATER + 2, OUTER[1] - 3)
        x += L + rng.randint(3, 8)
        n += 1
    # a few along the west cross canal
    z = OUTER_S_QUAY[0] + 4
    while z < INNER[0] - 18:
        ctx['w'].fill(WEST_CANAL[1] - 4, WATER - 1, z, WEST_CANAL[1], WATER + 1, z + 13, 'dark_oak_planks')
        ctx['w'].fill(WEST_CANAL[1] - 3, WATER + 2, z + 3, WEST_CANAL[1] - 1, WATER + 4, z + 10, rng.choice(['spruce_planks', 'white_terracotta']))
        z += 20
    # flower barges along the square
    x = BLOEMENPLEIN[0] + 1
    while x + 13 <= BLOEMENPLEIN[1]:
        flower_barge(ctx, x, INNER[1] - 5, 13, rng)
        x += 16


def build(ctx):
    quays(ctx)
    boats(ctx)
