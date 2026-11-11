"""Corvara old town: terraced rows of stuccoed houses, stair alleys and the piazza."""
import numpy as np

from core import (Frame, DIRS, OPP, POTS, bench, cafe_table, chair, citrus, crate_stack, leaves,
                  market_stall, planter, stone_pine, street_lamp, umbrella)
from terrain import T0, T1, T2, T3, Z0, Z1, Z2, Z3, SX, SZ

# stucco: (main, [(weathered variant, weight)])
WALLS = {
    'cream':  ('smooth_sandstone', [('cut_sandstone', .06), ('sandstone', .04)]),
    'ochre':  ('yellow_terracotta', [('orange_terracotta', .04), ('smooth_sandstone', .03)]),
    'peach':  ('white_terracotta', [('terracotta', .04), ('pink_terracotta', .02)]),
    'rose':   ('pink_terracotta', [('red_terracotta', .05), ('terracotta', .04)]),
    'orange': ('orange_terracotta', [('terracotta', .07)]),
    'white':  ('white_concrete', [('calcite', .12), ('white_concrete_powder', .04)]),
    'clay':   ('terracotta', [('orange_terracotta', .06), ('brown_terracotta', .03)]),
    'stone':  ('stone_bricks', [('mossy_stone_bricks', .1), ('cracked_stone_bricks', .1), ('andesite', .08)]),
    'brick':  ('bricks', [('granite', .06), ('terracotta', .05)]),
}
TOWN_COLORS = ['cream', 'ochre', 'peach', 'rose', 'orange', 'white', 'clay', 'ochre', 'peach', 'cream']
SHUTTERS = ['spruce', 'dark_oak', 'warped', 'mangrove', 'spruce', 'warped', 'jungle']
ROOFS = ['brick', 'brick', 'waxed_cut_copper', 'brick', 'granite', 'waxed_cut_copper']
ROOF_FULL = {'brick': 'bricks', 'waxed_cut_copper': 'waxed_cut_copper', 'granite': 'granite',
             'mud_brick': 'mud_bricks', 'stone_brick': 'stone_bricks', 'deepslate_tile': 'deepslate_tiles',
             'spruce': 'spruce_planks', 'dark_oak': 'dark_oak_planks'}


def wall_mix(key):
    main, alts = WALLS[key]
    rest = 1.0 - sum(a[1] for a in alts)
    return [(main, rest)] + list(alts)


def ring_mix(w, x0, z0, x1, z1, ya, yb, rng, mix):
    w.fill_mix(x0, ya, z0, x1, yb, z0, rng, mix)
    w.fill_mix(x0, ya, z1, x1, yb, z1, rng, mix)
    w.fill_mix(x0, ya, z0, x0, yb, z1, rng, mix)
    w.fill_mix(x1, ya, z0, x1, yb, z1, rng, mix)


def ring(w, x0, z0, x1, z1, ya, yb, blk):
    w.fill(x0, ya, z0, x1, yb, z0, blk)
    w.fill(x0, ya, z1, x1, yb, z1, blk)
    w.fill(x0, ya, z0, x0, yb, z1, blk)
    w.fill(x1, ya, z0, x1, yb, z1, blk)


def window_cols(n):
    c = max(1, (n - 2) // 3)
    if n < 5:
        return []
    if c == 1:
        return [n // 2]
    return sorted({int(round(2 + j * (n - 5) / (c - 1))) for j in range(c)})


def side_cells(fr, side):
    """Returns (n, cell(i)->(u,v), out(i)->(u,v), outward key)."""
    W, D = fr.W, fr.D
    if side == 'F':
        return W, (lambda i: (i, 0)), (lambda i: (i, -1)), 'F'
    if side == 'B':
        return W, (lambda i: (i, D - 1)), (lambda i: (i, D)), 'B'
    if side == 'L':
        return D, (lambda i: (0, i)), (lambda i: (-1, i)), 'L'
    return D, (lambda i: (W - 1, i)), (lambda i: (W, i)), 'R'


def gable_roof(w, x0, z0, x1, z1, y, mat, mix, rng, axis):
    full = ROOF_FULL.get(mat, mat)

    def put(x, yy, z, blk):
        if x0 <= x <= x1 and z0 <= z <= z1:
            w.set(x, yy, z, blk)
        else:
            w.set_if_air(x, yy, z, blk)

    if axis == 'x':
        n = z1 - z0 + 3
        for i in range((n + 1) // 2):
            za, zb, yy = z0 - 1 + i, z1 + 1 - i, y + i
            for x in range(x0 - 1, x1 + 2):
                if za == zb:
                    put(x, yy, za, f'{mat}_slab[type=bottom]')
                else:
                    put(x, yy, za, f'{mat}_stairs[facing=south,half=bottom]')
                    put(x, yy, zb, f'{mat}_stairs[facing=north,half=bottom]')
            if i >= 1 and za + 1 <= zb - 1:
                w.fill_mix(x0, yy, za + 1, x0, yy, zb - 1, rng, mix)
                w.fill_mix(x1, yy, za + 1, x1, yy, zb - 1, rng, mix)
        return y + (n + 1) // 2
    n = x1 - x0 + 3
    for i in range((n + 1) // 2):
        xa, xb, yy = x0 - 1 + i, x1 + 1 - i, y + i
        for z in range(z0 - 1, z1 + 2):
            if xa == xb:
                put(xa, yy, z, f'{mat}_slab[type=bottom]')
            else:
                put(xa, yy, z, f'{mat}_stairs[facing=east,half=bottom]')
                put(xb, yy, z, f'{mat}_stairs[facing=west,half=bottom]')
        if i >= 1 and xa + 1 <= xb - 1:
            w.fill_mix(xa + 1, yy, z0, xb - 1, yy, z0, rng, mix)
            w.fill_mix(xa + 1, yy, z1, xb - 1, yy, z1, rng, mix)
    return y + (n + 1) // 2


def hip_roof(w, x0, z0, x1, z1, y, mat, overhang=1):
    full = ROOF_FULL.get(mat, mat)
    xa, za, xb, zb = x0 - overhang, z0 - overhang, x1 + overhang, z1 + overhang
    yy = y
    while xa <= xb and za <= zb:
        if xb - xa < 2 or zb - za < 2:
            w.fill(xa, yy, za, xb, yy, zb, f'{mat}_slab[type=bottom]')
            break
        for x in range(xa, xb + 1):
            w.set_if_air(x, yy, za, f'{mat}_stairs[facing=south,half=bottom]')
            w.set_if_air(x, yy, zb, f'{mat}_stairs[facing=north,half=bottom]')
        for z in range(za + 1, zb):
            w.set_if_air(xa, yy, z, f'{mat}_stairs[facing=east,half=bottom]')
            w.set_if_air(xb, yy, z, f'{mat}_stairs[facing=west,half=bottom]')
        xa += 1; za += 1; xb -= 1; zb -= 1; yy += 1
    return yy


def flat_roof(ctx, x0, z0, x1, z1, top, mix, deco=True):
    w, rng = ctx['w'], ctx['rng']
    ring_mix(w, x0, z0, x1, z1, top + 1, top + 1, rng, mix)
    w.fill(x0 + 1, top, z0 + 1, x1 - 1, top, z1 - 1, 'smooth_sandstone')
    if not deco or x1 - x0 < 6 or z1 - z0 < 6:
        return
    # pergola in one corner
    px, pz = x0 + 2, z0 + 2
    for (ax, az) in ((px, pz), (px + 3, pz), (px, pz + 3), (px + 3, pz + 3)):
        w.fill(ax, top + 1, az, ax, top + 2, az, 'spruce_fence')
    for ax in range(px, px + 4):
        for az in range(pz, pz + 4):
            w.set(ax, top + 3, az, leaves('azalea') if rng.random() < .7 else leaves('flowering_azalea'))
    w.set(px + 1, top + 1, pz + 1, 'spruce_fence')
    w.set(px + 1, top + 2, pz + 1, 'white_carpet')
    w.set(px + 2, top + 1, pz + 1, 'spruce_stairs[facing=east,half=bottom]')
    for _ in range(4):
        ax, az = rng.randint(x0 + 1, x1 - 1), rng.randint(z0 + 1, z1 - 1)
        if w.is_air(ax, top + 1, az) and (ax in (x0 + 1, x1 - 1) or az in (z0 + 1, z1 - 1)):
            planter(w, ax, top + 1, az, rng)


FURN = ['bookshelf', 'crafting_table', 'barrel[facing=up]', 'chest[facing={F}]', 'loom', 'cartography_table',
        'smoker[facing={F}]', 'furnace[facing={F}]', 'composter', 'decorated_pot', 'fletching_table',
        'water_cauldron[level=3]', 'bookshelf', 'bookshelf']


def furnish(ctx, fr, y, stairs_cells, rng):
    """Scatter furniture along the side walls of one storey. y = feet level."""
    W, D = fr.W, fr.D
    spots = [(1, v) for v in range(2, D - 3)] + [(W - 2, v) for v in range(2, D - 3)]
    rng.shuffle(spots)
    used = 0
    for (u, v) in spots:
        if used >= 4 or (u, v) in stairs_cells:
            continue
        if fr.get(u, y, v) != 0:
            continue
        r = rng.random()
        if r < .25 and (u, v + 1) not in stairs_cells and fr.get(u, y, v + 1) == 0:
            col = rng.choice(['red', 'white', 'light_blue', 'yellow', 'green'])
            fr.set(u, y, v + 1, f'{col}_bed[facing={{B}},part=foot]'.replace('{{B}}', '{B}'))
            fr.set(u, y, v, f'{col}_bed[facing={{B}},part=head]'.replace('{{B}}', '{B}'))
            # bed head points to the back wall side: head at larger v
            fr.set(u, y, v + 1, f'{col}_bed[facing={{B}},part=head]'.replace('{{B}}', '{B}'))
            fr.set(u, y, v, f'{col}_bed[facing={{B}},part=foot]'.replace('{{B}}', '{B}'))
        elif r < .45:
            fr.set(u, y, v, 'spruce_fence')
            fr.set(u, y + 1, v, 'spruce_pressure_plate')
        else:
            fr.set(u, y, v, rng.choice(FURN))
            if rng.random() < .3:
                fr.set_if_air(u, y + 1, v, rng.choice(POTS))
        used += 1


def house(ctx, x0, z0, x1, z1, base, floors, front, wall='cream', roof='gable', roofmat='brick',
          shutter='spruce', trim='smooth_quartz', blind=(), shop=None, name=None, balcony=True,
          interior=True, plinth='stone_bricks', door_u=None, floor_mat=None, back_door=False):
    """Stuccoed townhouse. base = y of the ground-floor floor block. Returns info dict."""
    w, rng = ctx['w'], ctx['rng']
    fr = Frame(w, x0, z0, x1, z1, front)
    W, D = fr.W, fr.D
    top = base + 5 * floors
    mix = wall_mix(wall)
    w.clear(x0, base + 1, z0, x1, top + 14, z1)
    w.fill(x0, base - 3, z0, x1, base, z1, 'cobblestone')
    floor_mat = floor_mat or rng.choice(['spruce_planks', 'polished_andesite', 'terracotta', 'smooth_stone'])
    w.fill(x0 + 1, base, z0 + 1, x1 - 1, base, z1 - 1, floor_mat)
    for k in range(floors):
        y0 = base + 1 + 5 * k
        ring_mix(w, x0, z0, x1, z1, y0, y0 + 3, rng, mix)
        ring(w, x0, z0, x1, z1, y0 + 4, y0 + 4, trim)
        w.fill(x0 + 1, y0 + 4, z0 + 1, x1 - 1, y0 + 4, z1 - 1, 'spruce_planks' if k < floors - 1 else 'oak_planks')
    ring(w, x0, z0, x1, z1, base + 1, base + 1, plinth)

    info = dict(name=name, x0=x0, z0=z0, x1=x1, z1=z1, base=base, top=top, frame=fr)
    cols_f = window_cols(W)
    if door_u is None:
        door_u = cols_f[len(cols_f) // 2] if cols_f else W // 2
        if len(cols_f) >= 2 and not shop and rng.random() < .6:
            door_u = rng.choice(cols_f)

    # --- openings ----------------------------------------------------------
    shop_span = None
    if shop:
        half = 2 if W >= 11 else 1
        cu = W // 2
        shop_span = (cu - half, cu + half)
    for side in ('F', 'B', 'L', 'R'):
        if side in blind:
            continue
        n, cell, out, key = side_cells(fr, side)
        cols = window_cols(n)
        for k in range(floors):
            y0 = base + 1 + 5 * k
            for c in cols:
                u, v = cell(c)
                if side == 'F' and k == 0:
                    if shop_span and shop_span[0] - 1 <= c <= shop_span[1] + 1:
                        continue
                    if not shop and c == door_u:
                        continue
                fr.set(u, y0 + 1, v, 'glass_pane')
                fr.set(u, y0 + 2, v, 'glass_pane')
                if k == 0:
                    continue
                ou, ov = out(c)
                # shutters to both sides
                for dc in (-1, 1):
                    if (c + dc) in cols or not (0 <= c + dc < n):
                        continue
                    su, sv = out(c + dc)
                    for yy in (y0 + 1, y0 + 2):
                        fr.set_if_air(su, yy, sv, f'{shutter}_trapdoor[facing={{{key}}},open=true,half=bottom]')
                if rng.random() < .35:
                    fr.set_if_air(ou, y0, ov, f'{shutter}_trapdoor[facing={{{key}}},open=false,half=top]')
                    fr.set_if_air(ou, y0 + 1, ov, rng.choice(POTS))
        if side == 'F' and balcony and floors >= 2 and cols:
            c = cols[len(cols) // 2]
            k = rng.randint(1, floors - 1)
            y0 = base + 1 + 5 * k
            u, v = cell(c)
            for yy in (y0, y0 + 1, y0 + 2):
                fr.set(u, yy, v, 'glass_pane' if yy == y0 + 2 else 'air')
            fr.set(u, y0, v, f'{shutter}_door[facing={{F}},half=lower,hinge=left,open=true]')
            fr.set(u, y0 + 1, v, f'{shutter}_door[facing={{F}},half=upper,hinge=left,open=true]')
            for du in (-1, 0, 1):
                fr.set(u + du, y0 - 1, -1, 'smooth_stone_slab[type=top]')
                fr.set(u + du, y0, -1, 'iron_bars')
            fr.set(u - 1, y0 + 1, -1, 'air')
            fr.set(u + 1, y0 + 1, -1, 'air')

    y0 = base + 1
    if shop:
        a, b = shop_span
        fr.fill(a, y0, 0, b, y0 + 2, 0, 'air')
        col = shop if isinstance(shop, str) and shop in ('red', 'green', 'blue', 'yellow', 'orange', 'cyan') \
            else rng.choice(['red', 'green', 'blue', 'yellow', 'orange'])
        for u in range(a - 1, b + 2):
            for v in (-1, -2):
                fr.set_if_air(u, y0 + 2, v, 'spruce_trapdoor[facing={F},open=false,half=top]')
                fr.set_if_air(u, y0 + 3, v, f'{col}_carpet' if u % 2 == 0 else 'white_carpet')
        door_u = (a + b) // 2
        # counter + shelves
        if D >= 8:
            fr.fill(2, y0, 3, W - 3, y0, 3, 'spruce_planks')
            fr.set(W // 2, y0, 3, 'air')
            for u in range(1, W - 1):
                if rng.random() < .7:
                    fr.set(u, y0, D - 2, rng.choice(['barrel[facing=up]', 'bookshelf', 'barrel[facing={F}]']))
                    fr.set(u, y0 + 1, D - 2, rng.choice(['barrel[facing={F}]', 'bookshelf', 'air']))
    else:
        fr.set(door_u, y0, 0, f'{shutter}_door[facing={{B}},half=lower,hinge=left,open=false]')
        fr.set(door_u, y0 + 1, 0, f'{shutter}_door[facing={{B}},half=upper,hinge=left,open=false]')
        fr.set(door_u, y0 + 2, 0, trim)
    if back_door:
        bu = W // 2
        fr.fill(bu, y0, D - 1, bu, y0 + 1, D - 1, 'air')
        info['back'] = fr.pos(bu, y0, D)
    info['door'] = fr.pos(door_u, base + 1, -1)
    info['inside'] = fr.pos(door_u, base + 1, 2)
    fr.set(door_u + (1 if door_u + 1 < W - 1 else -1), y0 + 2, -1, 'lantern[hanging=false]') if False else None

    # --- interior ----------------------------------------------------------
    stairs_cells = set()
    if interior:
        for k in range(floors):
            y0 = base + 1 + 5 * k
            fr.set(W // 2, y0 + 3, D // 2, 'lantern[hanging=true]')
            if k < floors - 1:
                if W >= 9 and D >= 7:
                    if k % 2 == 0:
                        v = D - 2
                        for i in range(5):
                            fr.set(2 + i, y0 + i, v, 'spruce_stairs[facing={R},half=bottom]')
                            stairs_cells.add((2 + i, v))
                            if i >= 1:
                                fr.set(2 + i, y0 + 4, v, 'air')
                        stairs_cells.update({(1, v), (7, v)})
                    else:
                        v = D - 3
                        for i in range(5):
                            fr.set(6 - i, y0 + i, v, 'spruce_stairs[facing={L},half=bottom]')
                            stairs_cells.add((6 - i, v))
                            if i >= 1:
                                fr.set(6 - i, y0 + 4, v, 'air')
                        stairs_cells.update({(7, v), (1, v)})
                else:
                    for yy in range(y0, y0 + 5):
                        fr.set(1, yy, D - 2, 'ladder[facing={F}]')
                    stairs_cells.add((1, D - 2))
            furnish(ctx, fr, y0, stairs_cells, rng)

    # --- roof ----------------------------------------------------------------
    if roof == 'flat':
        flat_roof(ctx, x0, z0, x1, z1, top, mix)
        info['roof_top'] = top + 1
    elif roof == 'hip':
        info['roof_top'] = hip_roof(w, x0, z0, x1, z1, top, roofmat)
    else:
        xspan, zspan = x1 - x0, z1 - z0
        axis = 'x' if xspan >= zspan else 'z'
        if roof in ('gable_x', 'gable_z'):
            axis = roof[-1]
        info['roof_top'] = gable_roof(w, x0, z0, x1, z1, top, roofmat, mix, rng, axis)
        if rng.random() < .45:
            cx, cz = rng.randint(x0 + 1, x1 - 1), rng.randint(z0 + 1, z1 - 1)
            ct = w.column_top(cx, cz)
            w.fill(cx, ct, cz, cx, ct + 2, cz, 'bricks')
            w.set(cx, ct + 3, cz, 'brick_wall')
    if name:
        ctx['anchors'][name + '.door'] = info['door']
        ctx['anchors'][name + '.inside'] = info['inside']
    ctx.setdefault('houses', []).append(info)
    return info


def stairway(ctx, x0, x1, z_edge, y_top, y_bot, direction='south', mat='stone_brick'):
    """Steps descending from an upper terrace edge. z_edge = last row of the upper terrace."""
    w = ctx['w']
    n = y_top - y_bot
    dz = 1 if direction == 'south' else -1
    face = 'north' if direction == 'south' else 'south'
    for i in range(1, n + 1):
        z = z_edge + dz * i
        y = y_top - i + 1
        w.clear(x0, y + 1, z, x1, y_top + 6, z)
        w.fill(x0, y_bot + 1, z, x1, y - 1, z, 'stone_bricks')
        w.fill(x0, y, z, x1, y, z, f'{mat}_stairs[facing={face},half=bottom]')
    ctx['nowall'][z_edge, x0:x1 + 1] = True
    w.clear(x0, y_top + 1, z_edge, x1, y_top + 4, z_edge)
    # side walls so nobody walks off the flank
    for i in range(1, n + 1):
        z = z_edge + dz * i
        y = y_top - i + 1
        for xs in (x0 - 1, x1 + 1):
            if w.is_air(xs, y + 1, z) and w.get(xs, y, z) == 0:
                pass
    return dict(top=((x0 + x1) // 2, y_top + 1, z_edge), bottom=((x0 + x1) // 2, y_bot + 1, z_edge + dz * (n + 1)))


def lots_row(ctx, lots, z0, z1, base, front, floors=(2, 3), seed_colors=None, **kw):
    """lots: list of (xa, xb) or (xa, xb, opts). Adjacent lots get blind party walls."""
    rng = ctx['rng']
    out = []
    last_color = None
    for i, lot in enumerate(lots):
        xa, xb = lot[0], lot[1]
        opts = dict(kw)
        opts.update(lot[2] if len(lot) > 2 else {})
        blind = set(opts.pop('blind', ()))
        left_adj = i > 0 and lots[i - 1][1] + 1 >= xa
        right_adj = i + 1 < len(lots) and lots[i + 1][0] - 1 <= xb
        # frame L/R depend on facing: south front -> L=west ; north front -> L=east
        if front == 'south':
            if left_adj: blind.add('L')
            if right_adj: blind.add('R')
        else:
            if left_adj: blind.add('R')
            if right_adj: blind.add('L')
        color = opts.pop('wall', None)
        while color is None or color == last_color:
            color = rng.choice(TOWN_COLORS)
        last_color = color
        fl = opts.pop('floors', None) or rng.randint(*floors)
        roof = opts.pop('roof', None) or ('flat' if rng.random() < .22 else 'gable')
        za, zb = opts.pop('z0', z0), opts.pop('z1', z1)
        info = house(ctx, xa, za, xb, zb, base, fl, front, wall=color, roof=roof,
                     roofmat=opts.pop('roofmat', None) or rng.choice(ROOFS),
                     shutter=opts.pop('shutter', None) or rng.choice(SHUTTERS),
                     trim=opts.pop('trim', None) or rng.choice(['smooth_quartz', 'calcite', 'polished_diorite',
                                                                 'smooth_sandstone']),
                     blind=blind, **opts)
        out.append(info)
    return out


def yard(ctx, x0, z0, x1, z1, y, kind='garden'):
    """Small walled back court with greenery."""
    w, rng = ctx['w'], ctx['rng']
    if x1 - x0 < 2 or z1 - z0 < 1:
        return
    w.fill(x0, y, z0, x1, y, z1, 'grass_block')
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            r = rng.random()
            if r < .12:
                w.set(x, y + 1, z, rng.choice(['fern', 'grass', 'azalea', 'flowering_azalea']))
            elif r < .16:
                w.set(x, y + 1, z, rng.choice(['poppy', 'allium', 'pink_tulip', 'orange_tulip', 'cornflower']))
    if x1 - x0 >= 5:
        citrus(w, (x0 + x1) // 2, y + 1, (z0 + z1) // 2, rng)


def piazza(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    x0, x1, z0, z1, y = 132, 192, 138, 169, T1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            grid = (x - x0) % 6 == 0 or (z - z0) % 6 == 0
            blk = 'polished_diorite' if edge else ('polished_andesite' if grid else
                                                    ('stone_bricks' if rng.random() < .1 else 'smooth_stone'))
            w.set(x, y, z, blk)
            w.clear(x, y + 1, z, x, y + 3, z)
    cx, cz = 162, 154
    for dx in range(-9, 10):
        for dz in range(-9, 10):
            d = (dx * dx + dz * dz) ** .5
            if d <= 8.5:
                w.set(cx + dx, y, cz + dz, 'polished_diorite' if int(d) % 2 == 0 else 'polished_andesite')
    # fountain
    for dx in range(-5, 6):
        for dz in range(-5, 6):
            d = (dx * dx + dz * dz) ** .5
            if 3.6 < d <= 4.7:
                w.set(cx + dx, y + 1, cz + dz, 'smooth_quartz')
            elif d <= 3.6:
                w.set(cx + dx, y, cz + dz, 'prismarine_bricks' if rng.random() < .5 else 'dark_prismarine')
                w.set(cx + dx, y + 1, cz + dz, 'water')
    w.fill(cx, y + 1, cz, cx, y + 3, cz, 'quartz_pillar')
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.set(cx + dx, y + 3, cz + dz, 'smooth_quartz_slab[type=top]')
        w.set(cx + dx, y + 1, cz + dz, 'smooth_quartz')
    w.set(cx, y + 4, cz, 'sea_lantern')
    w.set(cx, y + 5, cz, 'smooth_quartz_slab[type=bottom]')
    A['piazza.fountain'] = (cx, y + 1, cz + 7)
    A['piazza.fountain.n'] = (cx, y + 1, cz - 7)
    A['piazza.fountain.e'] = (cx + 7, y + 1, cz)
    A['piazza.fountain.w'] = (cx - 7, y + 1, cz)
    # benches around the fountain
    for (bx, bz, ax, f) in ((cx - 1, cz + 6, 'x', 'south'), (cx - 1, cz - 6, 'x', 'north'),
                            (cx + 6, cz - 1, 'z', 'east'), (cx - 6, cz - 1, 'z', 'west')):
        bench(w, bx, y + 1, bz, ax, f)
    A['piazza.bench.s'] = (cx, y + 1, cz + 6)
    A['piazza.bench.e'] = (cx + 6, y + 1, cz)
    # corner trees in stone planters
    for (tx, tz) in ((x0 + 5, z0 + 4), (x1 - 5, z0 + 4), (x0 + 5, z1 - 5), (x1 - 5, z1 - 5)):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.set(tx + dx, y + 1, tz + dz, 'polished_diorite' if (dx or dz) else 'grass_block')
        stone_pine(w, tx, y + 2, tz, rng)
    # lamps
    for lx in range(x0 + 3, x1, 14):
        street_lamp(w, lx, y + 1, z1 - 1)
    for lz in (z0 + 10, z0 + 22):
        street_lamp(w, x0 + 1, y + 1, lz)
        street_lamp(w, x1 - 1, y + 1, lz)
    # belvedere benches looking at the sea
    for bx in (140, 148, 172, 180):
        bench(w, bx, y + 1, z1 - 2, 'x', 'south')
    A['belvedere.w'] = (144, y + 1, z1 - 3)
    A['belvedere.e'] = (176, y + 1, z1 - 3)
    A['belvedere.bench'] = (148, y + 1, z1 - 2)
    # cafe terrace (west side, in front of Caffe Aurora)
    seats = []
    for i, tz in enumerate((141, 145, 149)):
        for j, tx in enumerate((135, 139)):
            cafe_table(w, tx, y + 1, tz, rng)
            chair(w, tx - 1, y + 1, tz, 'east')
            chair(w, tx + 1, y + 1, tz, 'west')
            seats.append((tx - 1, y + 1, tz))
            seats.append((tx + 1, y + 1, tz))
            A[f'cafe.table{i * 2 + j}'] = (tx, y + 1, tz + 1)
    umbrella(w, 137, y + 1, 143, 'red')
    umbrella(w, 137, y + 1, 147, 'red')
    for i, s in enumerate(seats):
        A[f'cafe.seat{i}'] = s
    # market stalls (east half)
    cols = ['red', 'green', 'yellow', 'blue']
    for i, sx in enumerate((174, 181)):
        for j, sz in enumerate((141, 147)):
            market_stall(w, sx, y + 1, sz, cols[(i * 2 + j) % 4], rng)
            A[f'market.stall{i * 2 + j}'] = (sx + 1, y + 1, sz + 2)
            A[f'market.vendor{i * 2 + j}'] = (sx + 1, y + 1, sz + 1)
    crate_stack(w, 187, y + 1, 150, rng, 4)
    # newspaper kiosk
    w.fill(170, y + 1, 163, 172, y + 3, 165, 'dark_oak_planks')
    w.fill(170, y + 2, 163, 172, y + 2, 163, 'air')
    w.fill(170, y + 4, 162, 172, y + 4, 165, 'green_wool')
    w.set(171, y + 1, 163, 'bookshelf')
    A['piazza.kiosk'] = (171, y + 1, 161)


def quay(ctx):
    """Harbour promenade on T0: bollards, lamps, nets, crates, cafe tables."""
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    y = T0
    for x in range(84, 251):
        for z in range(201, 205):
            w.set(x, y, z, 'smooth_stone' if z < 204 else 'polished_andesite')
    for x in range(88, 250, 8):
        w.set(x, y + 1, 204, 'polished_blackstone_wall')
    for x in range(92, 250, 16):
        street_lamp(w, x, y + 1, 199)
    for x in (100, 112, 132, 146, 172, 190, 214, 232):
        bench(w, x, y + 1, 198, 'x', 'south')
        A[f'quay.bench{x}'] = (x, y + 1, 198)
    for x in (108, 128, 150, 186, 222, 240):
        palm_x = x
        w.set(palm_x, y, 196, 'grass_block')
        from core import palm
        palm(w, palm_x, y + 1, 196, rng)
    # fishing clutter
    for x in (96, 142, 178, 196, 228, 244):
        crate_stack(w, x, y + 1, 202, rng, rng.randint(2, 4))
    for x in (104, 136, 168, 210):
        w.set(x, y + 1, 203, 'white_wool')
        w.set(x + 1, y + 1, 203, 'cobweb') if False else None
        w.set(x + 1, y + 1, 203, 'spruce_trapdoor[facing=north,open=false,half=bottom]')
    for i, x in enumerate(range(90, 250, 20)):
        A[f'quay.walk{i}'] = (x, y + 1, 200)
    # trattoria terrace
    for i, tx in enumerate((125, 129, 133)):
        w.set(tx, y + 1, 192, 'barrel[facing=up]')
        w.set(tx, y + 2, 192, 'recrafted:meal[poison=none]' if i != 1 else 'recrafted:drink[poison=none]')
        chair(w, tx, y + 1, 191, 'south')
        chair(w, tx, y + 1, 193, 'north')
        A[f'trattoria.seat{i}'] = (tx, y + 1, 193)
        A[f'trattoria.seat{i}b'] = (tx, y + 1, 191)
        A[f'trattoria.table{i}'] = (tx + 1, y + 1, 192)
    umbrella(w, 127, y + 1, 192, 'red')
    umbrella(w, 131, y + 1, 192, 'red')
    A['trattoria.front'] = (130, y + 1, 195)
    A['quay.w'] = (88, y + 1, 196)
    A['quay.e'] = (246, y + 1, 196)
    A['quay.mid'] = (160, y + 1, 196)


def build(ctx):
    w, rng, H, A = ctx['w'], ctx['rng'], ctx['H'], ctx['anchors']
    ctx['nowall'] = np.zeros((SZ, SX), dtype=bool)

    # ---- stairways between terraces --------------------------------------
    st = {}
    st['h_w'] = stairway(ctx, 116, 121, Z0 - 1, T1, T0)
    st['h_c'] = stairway(ctx, 157, 164, Z0 - 1, T1, T0)
    st['h_e'] = stairway(ctx, 201, 206, Z0 - 1, T1, T0)
    st['p_w'] = stairway(ctx, 107, 111, Z1 - 1, T2, T1)
    st['p_c'] = stairway(ctx, 156, 165, Z1 - 1, T2, T1)
    st['p_e'] = stairway(ctx, 232, 236, Z1 - 1, T2, T1)
    st['u_w'] = stairway(ctx, 98, 102, Z2 - 1, T3, T2)
    st['u_c'] = stairway(ctx, 158, 163, Z2 - 1, T3, T2)
    st['u_e'] = stairway(ctx, 222, 226, Z2 - 1, T3, T2)
    for k, v in st.items():
        A[f'stairs.{k}.top'] = v['top']
        A[f'stairs.{k}.bottom'] = v['bottom']
    ctx['stairs'] = st

    # ---- T0: harbour-front row (faces the sea) -----------------------------
    hz0, hz1 = 176, 189
    lots_row(ctx, [
        (84, 93, dict(shop='blue', name='bait_shop', floors=2)),
        (94, 104, dict(floors=3)),
        (105, 115, dict(floors=3, name='pensione', wall='rose', roof='gable')),
    ], hz0, hz1, T0, 'south')
    lots_row(ctx, [
        (122, 138, dict(shop='red', name='trattoria', floors=2, wall='ochre', roof='flat', back_door=True,
                        floor_mat='polished_andesite')),
        (139, 147, dict(floors=3)),
        (148, 156, dict(floors=3)),
    ], hz0, hz1, T0, 'south')
    lots_row(ctx, [
        (187, 200, dict(floors=2, name='ice_house', wall='white', shop='cyan')),
    ], hz0, hz1, T0, 'south')
    lots_row(ctx, [
        (227, 237, dict(floors=3)),
        (238, 249, dict(floors=2, shop='green', name='chandlery')),
    ], hz0, hz1, T0, 'south')
    # back courts between the houses and the retaining wall
    for (xa, xb) in ((84, 115), (122, 156), (187, 200), (227, 249)):
        yard(ctx, xa, Z0, xb, hz0 - 1, T0)

    # ---- T1: Via Roma -------------------------------------------------------
    nz0, nz1 = 138, 150          # north row, faces south
    sz0, sz1 = 158, 168          # south row, faces north (backs onto the belvedere)
    lots_row(ctx, [(74, 84), (85, 95), (96, 105)], nz0, nz1, T1, 'south')
    lots_row(ctx, [(218, 230), (238, 248, dict(name='pharmacy', shop='green'))], nz0, nz1, T1, 'south')
    lots_row(ctx, [(74, 84), (85, 96), (97, 107), (108, 115, dict(floors=2))], sz0, sz1, T1, 'north')
    lots_row(ctx, [(122, 131, dict(name='gelateria', shop='yellow', floors=2))], sz0, sz1, T1, 'north')
    lots_row(ctx, [(193, 200, dict(floors=2)), ], sz0, sz1, T1, 'north')
    lots_row(ctx, [(207, 219), (220, 232), (233, 248)], sz0, sz1, T1, 'north')
    for (xa, xb) in ((74, 105), (218, 230), (238, 248)):
        yard(ctx, xa, Z1, xb, nz0 - 1, T1)
    # Caffe Aurora faces the piazza
    cafe = house(ctx, 114, 136, 130, 151, T1, 2, 'east', wall='peach', roof='hip', roofmat='brick',
                 shutter='warped', shop='red', name='cafe', floor_mat='polished_diorite', blind=('L',))
    A['cafe.counter'] = cafe['frame'].pos(cafe['frame'].W // 2, T1 + 1, 4)

    # ---- T2: Via Alta ---------------------------------------------------------
    uz0, uz1 = 108, 122
    lots_row(ctx, [(72, 82), (83, 96)], uz0, uz1, T2, 'south')
    lots_row(ctx, [
        (104, 114, dict(name='bakery', shop='orange', floors=2)),
        (115, 125), (126, 135),
        (136, 146, dict(name='tailor', shop='blue', floors=2)),
        (147, 155),
    ], uz0, uz1, T2, 'south')
    lots_row(ctx, [
        (166, 176, dict(name='doctor', floors=2, wall='white')),
        (177, 187), (188, 198), (199, 209), (210, 220),
    ], uz0, uz1, T2, 'south')
    lots_row(ctx, [(228, 238), (239, 248)], uz0, uz1, T2, 'south')
    for (xa, xb) in ((72, 96), (104, 155), (166, 220), (228, 248)):
        yard(ctx, xa, Z2 + 1, xb, uz0 - 1, T2)

    piazza(ctx)
    quay(ctx)

    # street lamps + planters along the streets
    for x in range(76, 250, 12):
        if w.is_air(x, T1 + 1, 154) and not (130 <= x <= 194):
            street_lamp(w, x, T1 + 1, 157 if (x // 12) % 2 else 151)
        if w.is_air(x, T2 + 1, 124):
            street_lamp(w, x, T2 + 1, 123 if w.is_air(x, T2 + 1, 123) else 124)
    for x in range(80, 248, 9):
        if w.is_air(x, T2 + 1, 130) and not ctx['nowall'][131, x]:
            planter(w, x, T2 + 1, 130, rng)
    for i, x in enumerate(range(76, 250, 24)):
        A[f'via_roma.{i}'] = (x, T1 + 1, 154)
        A[f'via_alta.{i}'] = (x, T2 + 1, 127)


def finish(ctx):
    """Balustrades on every exposed terrace edge that is still empty."""
    w, H, K = ctx['w'], ctx['H'], ctx['K']
    nowall = ctx['nowall']
    for z in range(40, SZ - 2):
        for x in range(60, SX - 2):
            h = H[z, x]
            if h < 64 or nowall[z, x]:
                continue
            drop = max(h - H[z + 1, x], h - H[z, x + 1], h - H[z, x - 1], h - H[z - 1, x])
            if drop >= 3 and w.get(x, h + 1, z) == 0 and w.get(x, h, z) != 0:
                nm = w.name(w.get(x, h, z))
                if 'water' in nm or 'stairs' in nm or 'slab' in nm:
                    continue
                w.set(x, h + 1, z, 'stone_brick_wall')
