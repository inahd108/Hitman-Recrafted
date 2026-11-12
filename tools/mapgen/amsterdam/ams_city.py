"""House rows along every canal, the gardens behind them, the landmark buildings on the south side
and the backdrop rows that close the map's edges."""
from ams_layout import *  # noqa: F401,F403
from ams_houses import Style, canal_house, row_x, row_z, TRIM
import ams_interiors


def gardens(ctx, x0, z0, x1, z1, split_x=None):
    """Back gardens: grass, gravel paths, plot walls and a few trees."""
    w, rng = ctx['w'], ctx['rng']
    w.fill_mix(x0, STREET, z0, x1, STREET, z1, rng, [('grass_block', 6), ('moss_block', 1), ('coarse_dirt', 1)])
    xs = split_x or list(range(x0, x1 + 1, rng.randint(8, 11)))
    for x in xs:
        w.fill(x, STREET + 1, z0, x, STREET + 2, z1, 'bricks')
    zm = (z0 + z1) // 2
    w.fill(x0, STREET + 1, zm, x1, STREET + 2, zm, 'bricks')
    for x in range(x0 + 4, x1, rng.randint(9, 13)):
        for z in (z0 + 5, z1 - 5):
            if rng.random() < .55:
                small_tree(w, x, STREET + 1, z, rng)


def small_tree(w, x, y, z, rng):
    h = rng.randint(4, 6)
    for k in range(h):
        w.set(x, y + k, z, 'oak_log')
    leaf = 'oak_leaves[persistent=true]' if rng.random() < .6 else 'birch_leaves[persistent=true]'
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            for dy in range(-1, 2):
                if abs(dx) + abs(dz) + abs(dy) <= 3 and rng.random() < .85:
                    w.set_if_air(x + dx, y + h + dy, z + dz, leaf)


def middle_block(ctx):
    a, b = MID_X
    zs = ZILVERSTEEG
    houses = []
    houses += row_x(ctx, a, zs[0] - 1, MID_N[0], MID_N[1], 'north', 'canal', floors=(3, 5))
    houses += row_x(ctx, zs[1] + 1, b, MID_N[0], MID_N[1], 'north', 'canal', floors=(3, 5))
    houses += row_x(ctx, a, zs[0] - 1, MID_S[0], MID_S[1], 'south', 'grand', floors=(4, 5), big=(.18, (13, 15, 17)))
    houses += row_x(ctx, zs[1] + 1, b, MID_S[0], MID_S[1], 'south', 'grand', floors=(4, 5), big=(.18, (13, 15, 17)))
    # Zilversteeg: shops facing the alley across the garden band
    shop_colors = ['red', 'green', 'blue', 'orange', 'black', 'brown', 'cyan', 'yellow']
    rng = ctx['rng']
    houses += row_z(ctx, MID_GARDENS[0], MID_GARDENS[1], zs[0] - 11, zs[0] - 1, 'east', 'lane', floors=(2, 4),
                    shop=None)
    houses += row_z(ctx, MID_GARDENS[0], MID_GARDENS[1], zs[1] + 1, zs[1] + 11, 'west', 'lane', floors=(2, 4))
    # the brown café: the alley shop nearest the middle of the east side
    east_side = [h for h in houses if h['frame'].front == 'west']
    if east_side:
        cafe = min(east_side, key=lambda h: abs((h['frame'].z0 + h['frame'].z1) / 2 - (MID_GARDENS[0] + MID_GARDENS[1]) / 2))
        cafe['name'] = 'cafe'
        ams_interiors.cafe(ctx, cafe)
    gardens(ctx, a, MID_GARDENS[0], zs[0] - 12, MID_GARDENS[1])
    gardens(ctx, zs[1] + 12, MID_GARDENS[0], b, MID_GARDENS[1])
    # awnings on the alley shops
    for h in houses:
        fr = h['frame']
        if fr.front in ('east', 'west'):
            c = rng.choice(shop_colors)
            for u in range(fr.W):
                fr.set(u, h['base'] + 4, -1, f'{c}_wool' if u % 2 == 0 else 'white_wool')
    return houses


def side_strips(ctx):
    houses = []
    # west of the west cross canal, south of the outer canal: houses facing east
    houses += row_z(ctx, OUTER_S_QUAY[0], INNER[1], WEST_HOUSES[0], WEST_HOUSES[1], 'east', 'canal', floors=(3, 5))
    # east of the east cross canal: houses facing west
    houses += row_z(ctx, OUTER[0], INNER[1], EAST_HOUSES[0], EAST_HOUSES[1], 'west', 'canal', floors=(3, 5))
    # north of the outer canal: a short row west of the lock and one east of the smuggler's dock
    houses += row_z(ctx, WAREHOUSES[0], OUTER_N_QUAY[1], 0, WEST_QUAY[0] - 1, 'east', 'lane', floors=(3, 5))
    houses += row_z(ctx, WAREHOUSES[0], OUTER_N_QUAY[1], EAST_E_QUAY[1] - 3, SX - 1, 'west', 'lane', floors=(3, 5))
    return houses


# ---- landmarks on the south side -------------------------------------------------------------
def gulden_hamer(ctx):
    """The auction house: a double-wide 1670s house with a stone ground floor, a formal garden and a coach house."""
    w, rng = ctx['w'], ctx['rng']
    x0, x1 = GULDEN_HAMER
    z0, z1 = SOUTH_HOUSES[0], SOUTH_HOUSES[0] + 29
    st = Style(rng, 'grand', brick='dark', trim='white', gable='cornice', door='dark_oak', lit=.95, roof='slate', interior=False)
    info = canal_house(ctx, x0, z0, x1, z1, 'north', 4, st, name='gulden_hamer')
    fr, W = info['frame'], info['W']
    # stone ground floor and quoins
    for u in range(W):
        for y in range(info['base'] + 1, info['levels'][1]):
            if fr.get(u, y, 0) != 0:
                fr.set(u, y, 0, 'smooth_quartz')
    for y in range(info['base'] + 1, info['top'] + 1):
        fr.set(0, y, 0, 'quartz_bricks')
        fr.set(W - 1, y, 0, 'quartz_bricks')
    # double stair to a central door
    mid = (W - 1) // 2
    for du in (-1, 0, 1):
        fr.set(mid + du, info['base'] + 1, 0, 'air')
        fr.set(mid + du, info['base'] + 2, 0, 'air')
        fr.set(mid + du, info['base'] + 3, 0, 'air')
        fr.set(mid + du, info['base'] + 4, 0, 'smooth_quartz_slab[type=top]')
    fr.set(mid - 1, info['base'] + 1, 1, 'dark_oak_door[facing={F},half=lower,hinge=left]')
    fr.set(mid - 1, info['base'] + 2, 1, 'dark_oak_door[facing={F},half=upper,hinge=left]')
    fr.set(mid + 1, info['base'] + 1, 1, 'dark_oak_door[facing={F},half=lower,hinge=right]')
    fr.set(mid + 1, info['base'] + 2, 1, 'dark_oak_door[facing={F},half=upper,hinge=right]')
    fr.set(mid, info['base'] + 1, 1, 'air')
    fr.set(mid, info['base'] + 2, 1, 'air')
    for du in range(-3, 4):
        fr.set(mid + du, info['base'], -1, 'smooth_quartz_stairs[facing={B}]' if abs(du) <= 2 else 'smooth_quartz')
        fr.set(mid + du, info['base'] - 1, -2, 'smooth_quartz_stairs[facing={B}]' if abs(du) <= 2 else 'smooth_quartz')
    for du in (-4, 4):
        fr.set(mid + du, info['base'] + 1, -1, 'lantern')
        fr.set(mid + du, info['base'], -1, 'polished_andesite')
    # balustrade on the cornice
    for u in range(1, W - 1):
        fr.set(u, info['top'] + 3, 0, 'smooth_quartz_slab' if u % 2 else 'stone_brick_wall')
    # garden and coach house
    gz0, gz1 = z1 + 1, BACK_STREET[0] - 11
    w.fill(x0, STREET, gz0, x1, STREET, gz1, 'grass_block')
    w.fill(x0, STREET + 1, gz0, x0, STREET + 3, gz1, 'bricks')
    w.fill(x1, STREET + 1, gz0, x1, STREET + 3, gz1, 'bricks')
    cx = (x0 + x1) // 2
    w.fill(cx - 1, STREET, gz0, cx + 1, STREET, gz1, 'gravel')
    w.fill(x0 + 3, STREET, (gz0 + gz1) // 2, x1 - 3, STREET, (gz0 + gz1) // 2 + 1, 'gravel')
    for (hx0, hx1) in ((x0 + 3, cx - 3), (cx + 3, x1 - 3)):
        for hz0 in (gz0 + 2, (gz0 + gz1) // 2 + 3):
            w.fill(hx0, STREET + 1, hz0, hx1, STREET + 1, hz0 + 6, 'azalea_leaves[persistent=true]')
            w.fill(hx0 + 1, STREET + 1, hz0 + 1, hx1 - 1, STREET + 1, hz0 + 5, 'grass_block')
    w.set(cx, STREET + 1, (gz0 + gz1) // 2, 'water_cauldron[level=3]')
    st2 = Style(rng, 'lane', brick='dark', trim='white', gable='bell', door='dark_oak', lit=.6)
    coach = canal_house(ctx, x0 + 6, gz1 + 1, x1 - 6, BACK_STREET[0] - 1, 'south', 2, st2, name='coach_house')
    ctx['anchors'].update({'hamer.door': info['door'], 'hamer.garden': (cx, STREET + 1, (gz0 + gz1) // 2 + 2),
                           'hamer.coach': coach['door']})
    ams_interiors.gulden_hamer(ctx)
    return [info, coach]


def forger(ctx):
    """De Meester's house: narrow, seven floors, a step gable in sandstone, studio in the attic."""
    rng = ctx['rng']
    x0, x1 = FORGER
    st = Style(rng, 'canal', brick='red', trim='stone', gable='step', door='dark_oak', lit=.85, roof='tile')
    info = canal_house(ctx, x0, SOUTH_HOUSES[0], x1, SOUTH_HOUSES[1] + 2, 'north', 7, st, name='forger')
    back = canal_house(ctx, x0, SOUTH_HOUSES[1] + 9, x1, SOUTH_HOUSES[1] + 20, 'north', 4,
                       Style(rng, 'lane', brick='red', trim='stone', gable='spout', lit=.5), name='forger_back')
    ctx['anchors'].update({'forger.door': info['door'], 'forger.top': (x0 + 3, info['top'] + 1, SOUTH_HOUSES[0] + 4)})
    ams_interiors.studio(ctx, info)
    return [info, back]


def church(ctx):
    """Ankerkerk: brick nave with a steep slate roof and a tall tower with a copper spire on the quay."""
    w = ctx['w']
    x0, x1 = CHURCH
    nz0, nz1 = SOUTH_HOUSES[0] + 13, BACK_STREET[0] - 4
    wall_top = STREET + 16
    w.fill(x0 + 4, STREET + 1, nz0, x1 - 4, wall_top, nz1, 'bricks')
    w.fill(x0 + 5, STREET + 1, nz0 + 1, x1 - 5, wall_top, nz1 - 1, 'air')
    w.fill(x0 + 5, STREET, nz0 + 1, x1 - 5, STREET, nz1 - 1, 'polished_andesite')
    for z in range(nz0 + 3, nz1 - 2, 5):                                   # tall windows and buttresses
        for x in (x0 + 4, x1 - 4):
            for y in range(STREET + 4, wall_top - 2):
                w.set(x, y, z, 'glass_pane')
            w.set(x, wall_top - 2, z, 'stone_bricks')
        for x in (x0 + 3, x1 - 3):
            w.fill(x, STREET + 1, z + 2, x, wall_top - 4, z + 2, 'stone_bricks')
        w.set((x0 + x1) // 2, wall_top - 2, z, 'light[level=10]')
    half = (x1 - x0 - 8) // 2 + 1
    for k in range(half + 1):
        y = wall_top + 1 + k
        w.fill(x0 + 3 + k, y, nz0, x0 + 3 + k, y, nz1, 'deepslate_tile_stairs[facing=east]')
        w.fill(x1 - 3 - k, y, nz0, x1 - 3 - k, y, nz1, 'deepslate_tile_stairs[facing=west]')
        for z in (nz0, nz1):
            w.fill(x0 + 4 + k, y, z, x1 - 4 - k, y, z, 'bricks')
    # tower on the quay line
    cx = (x0 + x1) // 2
    tz0 = SOUTH_HOUSES[0]
    t0, t1 = cx - 6, cx + 6
    tz1 = tz0 + 12
    y_top = STREET + 34
    w.fill(t0, STREET + 1, tz0, t1, y_top, tz1, 'bricks')
    w.fill(t0 + 1, STREET + 1, tz0 + 1, t1 - 1, y_top, tz1 - 1, 'air')
    for y in range(STREET + 1, y_top + 1, 8):
        w.fill(t0, y, tz0, t1, y, tz0, 'smooth_sandstone')
    w.fill(cx - 1, STREET + 1, tz0, cx + 1, STREET + 4, tz0, 'air')        # door
    w.fill(cx - 1, STREET + 5, tz0, cx + 1, STREET + 5, tz0, 'smooth_sandstone_stairs[facing=south,half=top]')
    for side in range(4):                                                  # clock faces and belfry arches
        pass
    for x, z in ((cx, tz0), (cx, tz1), (t0, (tz0 + tz1) // 2), (t1, (tz0 + tz1) // 2)):
        w.set(x, y_top - 8, z, 'white_concrete')
        w.set(x, y_top - 9, z, 'black_concrete')
        for k in (-2, 2):
            if x in (t0, t1):
                w.fill(x, y_top - 4, z + k, x, y_top - 1, z + k, 'air')
            else:
                w.fill(x + k, y_top - 4, z, x + k, y_top - 1, z, 'air')
    # lantern stages and spire in copper
    lx0, lx1, lz0, lz1 = t0 + 2, t1 - 2, tz0 + 2, tz1 - 2
    w.fill(lx0, y_top + 1, lz0, lx1, y_top + 8, lz1, 'oxidized_cut_copper')
    w.fill(lx0 + 1, y_top + 2, lz0 + 1, lx1 - 1, y_top + 7, lz1 - 1, 'air')
    for z in range(lz0 + 2, lz1 - 1, 2):
        w.fill(lx0, y_top + 3, z, lx0, y_top + 6, z, 'air')
        w.fill(lx1, y_top + 3, z, lx1, y_top + 6, z, 'air')
    w.set(cx, y_top + 4, (lz0 + lz1) // 2, 'bell[attachment=ceiling,facing=north]')
    w.set(cx, y_top + 5, (lz0 + lz1) // 2, 'oxidized_cut_copper')
    r = (lx1 - lx0) // 2
    y = y_top + 9
    while r >= 0:
        for k in range(3):
            w.fill(cx - r, y, (lz0 + lz1) // 2 - r, cx + r, y, (lz0 + lz1) // 2 + r, 'oxidized_cut_copper')
            y += 1
        r -= 1
    for k in range(4):
        w.set(cx, y + k, (lz0 + lz1) // 2, 'lightning_rod')
    w.set(cx, y + 4, (lz0 + lz1) // 2, 'gold_block')
    ctx['anchors'].update({'church.door': (cx, STREET + 1, tz0 - 1), 'church.bell': (cx, y_top + 2, (lz0 + lz1) // 2 + 1),
                           'church.nave': (cx, STREET + 1, (nz0 + nz1) // 2)})


def hofje(ctx):
    """Hofje van de Zeven Zusters: a long plain front with one door, then a quiet garden ringed by tiny houses."""
    w, rng = ctx['w'], ctx['rng']
    x0, x1 = HOFJE
    st = Style(rng, 'lane', brick='plum', trim='white', gable='cornice', lit=.5)
    front = canal_house(ctx, x0, SOUTH_HOUSES[0], x1, SOUTH_HOUSES[0] + 9, 'north', 2, st, name='hofje_front')
    cx = (x0 + x1) // 2
    # gate passage straight through
    w.fill(cx - 1, STREET + 1, SOUTH_HOUSES[0], cx + 1, STREET + 4, SOUTH_HOUSES[0] + 9, 'air')
    w.fill(cx - 1, STREET + 1, SOUTH_HOUSES[0], cx + 1, STREET + 1, SOUTH_HOUSES[0] + 9, 'air')
    w.fill(cx - 1, STREET, SOUTH_HOUSES[0], cx + 1, STREET, SOUTH_HOUSES[0] + 9, 'stone_bricks')
    gz0, gz1 = SOUTH_HOUSES[0] + 10, BACK_STREET[0] - 2
    w.fill(x0, STREET, gz0, x1, STREET, gz1, 'grass_block')
    w.fill(x0 + 7, STREET, gz0 + 7, x1 - 7, STREET, gz0 + 7, 'gravel')
    w.fill(x0 + 7, STREET, gz1 - 7, x1 - 7, STREET, gz1 - 7, 'gravel')
    w.fill(x0 + 7, STREET, gz0 + 7, x0 + 7, STREET, gz1 - 7, 'gravel')
    w.fill(x1 - 7, STREET, gz0 + 7, x1 - 7, STREET, gz1 - 7, 'gravel')
    w.fill(cx, STREET, gz0, cx, STREET, gz0 + 7, 'gravel')
    houses = []
    # tiny houses along the east and west sides facing in, and along the back
    houses += row_z(ctx, gz0 + 1, gz1 - 1, x0, x0 + 6, 'east', 'lane', floors=(1, 2), gable='bell', brick='plum', trim='white')
    houses += row_z(ctx, gz0 + 1, gz1 - 1, x1 - 6, x1, 'west', 'lane', floors=(1, 2), gable='bell', brick='plum', trim='white')
    houses += row_x(ctx, x0 + 7, x1 - 7, gz1 - 6, gz1, 'north', 'lane', floors=(1, 2), gable='bell', brick='plum', trim='white')
    small_tree(w, cx, STREET + 1, (gz0 + gz1) // 2, rng)
    w.set(cx + 3, STREET + 1, (gz0 + gz1) // 2, 'cauldron')
    ctx['anchors'].update({'hofje.gate': (cx, STREET + 1, SOUTH_HOUSES[0] - 1), 'hofje.garden': (cx, STREET + 1, (gz0 + gz1) // 2 + 2)})
    return [front] + houses


def police(ctx):
    rng = ctx['rng']
    x0, x1 = POLICE
    st = Style(rng, 'canal', brick='black', trim='white', gable='cornice', door='dark_oak', lit=.95)
    info = canal_house(ctx, x0, SOUTH_HOUSES[0], x1, SOUTH_HOUSES[1], 'north', 3, st, name='police')
    fr = info['frame']
    fr.set(1, info['base'] + 4, -1, 'soul_lantern[hanging=true]')
    fr.set(info['W'] - 2, info['base'] + 4, -1, 'soul_lantern[hanging=true]')
    ctx['anchors']['police.door'] = info['door']
    return [info]


def bloemenplein(ctx):
    w, rng = ctx['w'], ctx['rng']
    x0, x1 = BLOEMENPLEIN
    z0, z1 = SOUTH_HOUSES[0], SOUTH_HOUSES[0] + 34
    w.fill_mix(x0, STREET, z0, x1, STREET, z1, rng, [('stone_bricks', 3), ('cobblestone', 2), ('andesite', 1), ('bricks', 1)])
    for x in range(x0 + 6, x1 - 3, 10):
        for z in (z0 + 8, z0 + 22):
            elm(w, x, STREET + 1, z, rng)
    # houses close the square on three sides
    houses = []
    houses += row_z(ctx, z0, z1, x0 - 11, x0 - 1, 'east', 'canal', floors=(3, 4))
    houses += row_x(ctx, x0, x1, z1 + 1, z1 + 16, 'north', 'canal', floors=(3, 5))
    ctx['anchors'].update({'square.centre': ((x0 + x1) // 2, STREET + 1, (z0 + z1) // 2),
                           'square.organ': (x0 + 6, STREET + 1, z0 + 3)})
    return houses


def elm(w, x, y, z, rng, h=None):
    """Canal elm: tall clean trunk, broad loose crown."""
    h = h or rng.randint(7, 9)
    for k in range(h):
        w.set(x, y + k, z, 'dark_oak_log')
    leaf = ['dark_oak_leaves[persistent=true]', 'oak_leaves[persistent=true]', 'jungle_leaves[persistent=true]']
    for dy in range(-2, 3):
        r = 4 if dy <= 0 else 3 if dy == 1 else 2
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + 1 and rng.random() < .78:
                    w.set_if_air(x + dx, y + h + dy, z + dz, rng.choice(leaf))
    for k in (1, 2):
        bx, bz = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        w.set(x + bx * k, y + h - 2 + k, z + bz * k, 'dark_oak_log')


def south_frontage(ctx):
    """Houses along the inner canal's south quay, between the landmarks; back houses on the back street."""
    out = []
    taken = [GULDEN_HAMER, FORGER, POLICE, BLOEMENPLEIN, CHURCH, HOFJE, (BLOEMENPLEIN[0] - 11, BLOEMENPLEIN[0] - 1)]
    a = WEST_HOUSES[0]
    free, x = [], a
    for (t0, t1) in sorted(taken):
        if t0 - 1 >= x:
            free.append((x, t0 - 1))
        x = max(x, t1 + 1)
    if x <= EAST_HOUSES[1]:
        free.append((x, EAST_HOUSES[1]))
    for (f0, f1) in free:
        if f1 - f0 + 1 >= 5:
            out += row_x(ctx, f0, f1, SOUTH_HOUSES[0], SOUTH_HOUSES[1], 'north', 'canal', floors=(3, 5))
    # back street: houses facing it from the north, behind gardens
    for (f0, f1) in free:
        if f1 - f0 + 1 >= 5 and not (f0 >= BLOEMENPLEIN[0] - 11 and f1 <= BLOEMENPLEIN[1]):
            out += row_x(ctx, f0, f1, BACK_STREET[0] - 16, BACK_STREET[0] - 1, 'south', 'lane', floors=(2, 4))
            gardens(ctx, f0, SOUTH_HOUSES[1] + 1, f1, BACK_STREET[0] - 17)
    return out


def backdrops(ctx):
    """Plain tall rows that close the map: south of the back street and down both edges."""
    rng = ctx['rng']
    out = []
    out += row_x(ctx, 0, SX - 1, BACKDROP_S[0], BACKDROP_S[0] + 15, 'north', 'canal', floors=(4, 6), lit=.4)
    out += row_z(ctx, OUTER[0], INNER[1], EDGE_W[0], EDGE_W[1], 'east', 'canal', floors=(4, 6), lit=.3)
    out += row_z(ctx, OUTER[0], INNER[1], EDGE_E[0], EDGE_E[1], 'west', 'canal', floors=(4, 6), lit=.3)
    return out


def build(ctx):
    ctx['houses'] = []
    ctx['houses'] += middle_block(ctx)
    ctx['houses'] += side_strips(ctx)
    ctx['houses'] += gulden_hamer(ctx)
    ctx['houses'] += forger(ctx)
    ctx['houses'] += police(ctx)
    church(ctx)
    ctx['houses'] += hofje(ctx)
    ctx['houses'] += bloemenplein(ctx)
    ctx['houses'] += south_frontage(ctx)
    ctx['houses'] += backdrops(ctx)
