"""Corvara landmarks: harbour works, lighthouse, fish market, town hall, chapel, beach."""
import math

from core import (Frame, DIRS, OPP, POTS, bench, cafe_table, chair, citrus, crate_stack, cypress, leaves,
                  olive, palm, planter, stone_pine, street_lamp, umbrella)
from terrain import T0, T1, T2, T3, SEA, QUAY_Z
from town import house, hip_roof, gable_roof, wall_mix, ring, ring_mix


# ----------------------------------------------------------------------
# boats
# ----------------------------------------------------------------------
def boat(ctx, x, z, length, axis='z', beam=2, hull='spruce', stripe='white', cabin=False, mast=False,
         name=None):
    """Moored boat. (x, z) = centre of the stern. Bow points +axis. Deck is walkable at SEA+1."""
    w = ctx['w']
    y = SEA

    def P(i, j):  # i along the keel, j across
        return (x + j, z + i) if axis == 'z' else (x + i, z + j)

    fwd = {'z': 'south', 'x': 'east'}[axis]
    left = {'z': 'east', 'x': 'south'}[axis]   # +j side
    for i in range(length):
        t = i / max(1, length - 1)
        hw = beam if t < .62 else max(0, int(round(beam * (1 - (t - .62) / .38))))
        for j in range(-hw, hw + 1):
            px, pz = P(i, j)
            w.set(px, y - 1, pz, f'{hull}_planks')
            w.set(px, y, pz, f'{hull}_planks')
            edge = abs(j) == hw or i == 0 or i == length - 1
            if edge and hw > 0:
                w.set(px, y + 1, pz, f'{stripe}_concrete' if (i == 0 or abs(j) == hw) else f'{hull}_planks')
                if abs(j) == hw and 0 < i < length - 1:
                    side = left if j > 0 else OPP[left]
                    w.set(px, y + 1, pz, f'{hull}_trapdoor[facing={OPP[side]},open=true,half=bottom]')
                    w.set(px, y, pz, f'{stripe}_concrete')
            else:
                w.set(px, y + 1, pz, 'air')
        if hw == 0:
            px, pz = P(i, 0)
            w.set(px, y + 1, pz, f'{hull}_slab[type=bottom]')
    if cabin:
        c0, c1 = max(2, length // 3), max(4, length // 3 + max(3, length // 4))
        for i in range(c0, c1 + 1):
            for j in range(-(beam - 1), beam):
                px, pz = P(i, j)
                wall = i in (c0, c1) or abs(j) == beam - 1
                w.set(px, y + 1, pz, 'white_concrete' if wall else 'air')
                w.set(px, y + 2, pz, ('glass_pane' if (i + j) % 2 else 'white_concrete') if wall else 'air')
                w.set(px, y + 3, pz, f'{stripe}_concrete' if stripe != 'white' else 'smooth_quartz')
        px, pz = P(c0, 0)
        w.set(px, y + 1, pz, 'air'); w.set(px, y + 2, pz, 'air')
    if mast:
        mi = length // 2
        px, pz = P(mi, 0)
        for k in range(1, 9):
            w.set(px, y + k, pz, 'spruce_fence')
        for k in range(3, 9):
            for s in range(1, 9 - k + 1):
                qx, qz = P(mi - s, 0)
                w.set_if_air(qx, y + k, qz, 'white_wool' if (k + s) % 4 else 'light_gray_wool')
    if name:
        ctx['anchors'][name] = P(max(1, length // 4), 0)[0], y + 1, P(max(1, length // 4), 0)[1]


def harbour(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    y = T0
    # --- breakwater (west) with lighthouse ----------------------------------
    mx0, mx1 = 84, 90
    for z in range(QUAY_Z + 1, 262):
        for x in range(mx0 - 3, mx1 + 1):
            rough = x < mx0
            if rough:
                top = y - 1 - (mx0 - x) - rng.randint(0, 1)
                w.fill_mix(x, 40, z, x, top, z, rng, [('stone', .4), ('andesite', .3), ('cobblestone', .2),
                                                      ('mossy_cobblestone', .1)])
            else:
                w.fill(x, 40, z, x, y - 1, z, 'stone')
                w.set(x, y, z, rng.choice(['stone_bricks', 'stone_bricks', 'cobblestone', 'smooth_stone',
                                           'cracked_stone_bricks']))
                w.clear(x, y + 1, z, x, y + 6, z)
        if z % 9 == 0:
            w.set(mx1, y + 1, z, 'polished_blackstone_wall')
        if z % 18 == 4:
            street_lamp(w, mx0, y + 1, z)
    for i, z in enumerate(range(212, 260, 12)):
        A[f'mole.{i}'] = (87, y + 1, z)
    crate_stack(w, 86, y + 1, 230, rng, 3)
    bench(w, 85, y + 1, 244, 'z', 'east')
    A['mole.bench'] = (86, y + 1, 244)
    # round head
    cx, cz, R = 87, 268, 8
    for dx in range(-R - 2, R + 3):
        for dz in range(-R - 2, R + 3):
            d = math.hypot(dx, dz)
            if d <= R:
                w.fill(cx + dx, 40, cz + dz, cx + dx, y - 1, cz + dz, 'stone')
                w.set(cx + dx, y, cz + dz, 'stone_bricks' if d < R - 1 else 'polished_andesite')
                w.clear(cx + dx, y + 1, cz + dz, cx + dx, y + 8, cz + dz)
            elif d <= R + 2.2:
                top = y - 1 - int((d - R) * 2) - rng.randint(0, 1)
                w.fill_mix(cx + dx, 40, cz + dz, cx + dx, top, cz + dz, rng,
                           [('stone', .4), ('andesite', .3), ('cobblestone', .3)])
    lighthouse(ctx, cx, cz, y)

    # --- ferry pier + ferry ---------------------------------------------------
    for z in range(QUAY_Z + 1, 240):
        for x in range(126, 130):
            w.set(x, y, z, 'spruce_planks' if (z % 4) else 'stripped_spruce_log[axis=x]')
            w.clear(x, y + 1, z, x, y + 5, z)
        if z % 5 == 0:
            for x in (126, 129):
                w.fill(x, 50, z, x, y - 1, z, 'spruce_log')
                if z % 10 == 0:
                    w.set(x, y + 1, z, 'lantern[hanging=false]') if x == 126 and z % 20 == 0 else None
    street_lamp(w, 126, y + 1, 238)
    A['pier.start'] = (127, y + 1, 208)
    A['pier.mid'] = (127, y + 1, 222)
    A['pier.end'] = (128, y + 1, 236)
    ferry(ctx, 134, 214)
    # --- moored boats ---------------------------------------------------------
    cols = [('spruce', 'blue'), ('birch', 'red'), ('spruce', 'white'), ('dark_oak', 'green'), ('birch', 'cyan'),
            ('spruce', 'yellow')]
    for i, bx in enumerate((98, 108, 150, 162, 176, 192)):
        h, s = cols[i % len(cols)]
        boat(ctx, bx, QUAY_Z + 3, rng.randint(7, 9), 'z', beam=1, hull=h, stripe=s, mast=(i % 3 == 0),
             name=f'boat.{i}')
    boat(ctx, 206, QUAY_Z + 3, 12, 'z', beam=2, hull='spruce', stripe='blue', cabin=True, name='boat.trawler')
    # patrol launch of the harbour office (exit option)
    boat(ctx, 221, QUAY_Z + 3, 11, 'z', beam=2, hull='birch', stripe='gray', cabin=True, name='boat.patrol')
    for lx in (102, 112, 154, 166, 180, 196, 211, 226, 236):
        for yy in range(SEA - 1, T0 + 1):
            w.set(lx, yy, QUAY_Z + 1, 'ladder[facing=south]')
    # boats at anchor
    boat(ctx, 172, 246, 8, 'x', beam=1, hull='spruce', stripe='red', mast=True)
    boat(ctx, 228, 252, 9, 'x', beam=1, hull='birch', stripe='blue', mast=True)
    boat(ctx, 150, 262, 7, 'x', beam=1, hull='dark_oak', stripe='white')
    # the Belmonte yacht
    yacht(ctx, 244, 214)


def ferry(ctx, x, z):
    """Small island ferry moored on the east side of the pier; bow to the south."""
    w, A = ctx['w'], ctx['anchors']
    y = T0 - 1                     # deck floor sits at y + 1, level with the pier
    L, hw = 22, 3
    for i in range(L):
        t = i / (L - 1)
        ww = hw if t < .75 else max(1, int(round(hw * (1 - (t - .75) / .3))))
        for j in range(-ww, ww + 1):
            px, pz = x + j, z + i
            w.fill(px, SEA - 2, pz, px, y, pz, 'white_concrete')
            w.set(px, SEA + 1, pz, 'red_concrete')
            w.set(px, y + 1, pz, 'smooth_stone')       # main deck (walk at y+2)
            w.clear(px, y + 2, pz, px, y + 8, pz)
            if abs(j) == ww or i in (0, L - 1):
                w.set(px, y + 2, pz, 'iron_bars' if not (j == -ww and 6 <= i <= 8) else 'air')
    # superstructure
    for i in range(3, 12):
        for j in range(-2, 3):
            px, pz = x + j, z + i
            wall = i in (3, 11) or abs(j) == 2
            if wall:
                w.fill(px, y + 2, pz, px, y + 4, pz, 'white_concrete')
                if (i + j) % 2 == 0 and 3 < i < 11:
                    w.set(px, y + 3, pz, 'glass_pane')
            w.set(px, y + 5, pz, 'smooth_quartz')
    w.fill(x, y + 2, z + 11, x, y + 3, z + 11, 'air')
    w.fill(x - 2, y + 2, z + 7, x - 2, y + 3, z + 7, 'air')
    for i in (5, 7, 9):
        for j in (-1, 1):
            w.set(x + j, y + 2, z + i, 'spruce_stairs[facing=north,half=bottom]')
    # bridge + funnel
    w.fill(x - 1, y + 6, z + 4, x + 1, y + 7, z + 6, 'white_concrete')
    w.fill(x - 1, y + 7, z + 6, x + 1, y + 7, z + 6, 'glass_pane')
    w.fill(x - 1, y + 8, z + 4, x + 1, y + 8, z + 6, 'red_concrete')
    w.fill(x, y + 6, z + 8, x, y + 9, z + 8, 'red_concrete')
    w.set(x, y + 10, z + 8, 'black_concrete')
    # gangway to the pier (pier deck is 2 above sea; ferry deck too)
    for px in range(130, x - 3 + 1):
        w.set(px, T0, z + 7, 'spruce_planks')
    A['ferry.deck'] = (x, y + 2, z + 15)
    A['ferry.gangway'] = (130, T0 + 1, z + 7)
    A['spawn'] = (x, y + 2, z + 14)


def yacht(ctx, x, z):
    w, A = ctx['w'], ctx['anchors']
    y = T0 - 1
    L, hw = 20, 3
    for i in range(L):
        t = i / (L - 1)
        ww = hw if t < .6 else max(0, int(round(hw * (1 - (t - .6) / .4))))
        for j in range(-ww, ww + 1):
            px, pz = x + j, z + i
            w.fill(px, SEA - 1, pz, px, y, pz, 'white_concrete')
            w.set(px, y + 1, pz, 'birch_planks')
            w.clear(px, y + 2, pz, px, y + 8, pz)
            if abs(j) == ww and ww > 0:
                w.set(px, y + 1, pz, 'white_concrete')
                w.set(px, y + 2, pz, 'smooth_quartz_slab[type=bottom]')
    for i in range(5, 13):
        for j in range(-2, 3):
            px, pz = x + j, z + i
            wall = i in (5, 12) or abs(j) == 2
            if wall:
                w.fill(px, y + 2, pz, px, y + 3, pz, 'white_concrete')
                if 5 < i < 12:
                    w.set(px, y + 3, pz, 'black_stained_glass_pane')
            w.set(px, y + 4, pz, 'smooth_quartz')
    w.fill(x, y + 2, z + 5, x, y + 3, z + 5, 'air')
    w.fill(x - 1, y + 5, z + 8, x + 1, y + 5, z + 11, 'white_concrete')
    w.fill(x - 1, y + 5, z + 11, x + 1, y + 5, z + 11, 'black_stained_glass_pane')
    w.fill(x - 1, y + 6, z + 8, x + 1, y + 6, z + 11, 'smooth_quartz_slab[type=bottom]')
    # sun deck at the stern
    w.set(x - 1, y + 2, z + 2, 'white_carpet'); w.set(x + 1, y + 2, z + 2, 'white_carpet')
    cafe_table(w, x, y + 2, z + 3, ctx['rng'], 'white_carpet')
    # gangway to the quay
    for pz in range(QUAY_Z + 1, z + 1):
        w.set(x, T0, pz, 'birch_planks')
    A['yacht.deck'] = (x, y + 2, z + 2)
    A['yacht.cabin'] = (x, y + 2, z + 8)
    A['yacht.gangway'] = (x, T0 + 1, QUAY_Z)


def lighthouse(ctx, cx, cz, base):
    w, A = ctx['w'], ctx['anchors']
    Hh = 30
    for i in range(Hh):
        y = base + 1 + i
        R = 4.4 if i < 10 else (3.7 if i < 22 else 3.2)
        band = 'red_concrete' if (i // 5) % 2 == 1 else 'white_concrete'
        if i < 2:
            band = 'stone_bricks'
        for dx in range(-5, 6):
            for dz in range(-5, 6):
                d = math.hypot(dx, dz)
                if d <= R:
                    w.set(cx + dx, y, cz + dz, band if d > R - 1.25 else 'air')
        if i % 6 == 5:
            for dx in range(-4, 5):
                for dz in range(-4, 5):
                    if math.hypot(dx, dz) <= R - 1.25:
                        w.set(cx + dx, y, cz + dz, 'spruce_planks')
            w.set(cx + 1, y, cz, 'air')
        if i % 6 == 2 and i > 2:
            w.set(cx, y, cz + int(R), 'glass_pane')
            w.set(cx, y, cz - int(R), 'glass_pane')
            w.set(cx - 1, y, cz, 'lantern[hanging=false]') if False else None
        if i % 6 == 0:
            w.set(cx - 2, y + 1, cz, 'lantern[hanging=false]') if i else None
    # ladder up the inside (east side of the core)
    for i in range(Hh):
        w.set(cx + 1, base + 1 + i, cz, 'ladder[facing=west]')
        w.set(cx + 2, base + 1 + i, cz, 'white_concrete')
    # door (north, towards the mole)
    w.fill(cx, base + 1, cz - 4, cx, base + 2, cz - 3, 'air')
    w.set(cx, base + 1, cz - 4, 'spruce_door[facing=south,half=lower,hinge=left,open=false]')
    w.set(cx, base + 2, cz - 4, 'spruce_door[facing=south,half=upper,hinge=left,open=false]')
    # gallery
    gy = base + 1 + Hh
    for dx in range(-6, 7):
        for dz in range(-6, 7):
            d = math.hypot(dx, dz)
            if d <= 5.3:
                w.set(cx + dx, gy, cz + dz, 'smooth_stone')
                if d > 4.3:
                    w.set(cx + dx, gy + 1, cz + dz, 'iron_bars')
    w.set(cx + 1, gy, cz, 'ladder[facing=west]')
    w.set(cx + 2, gy, cz, 'smooth_stone')
    # lantern room
    for i in range(1, 5):
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                d = math.hypot(dx, dz)
                if 1.9 < d <= 2.9:
                    w.set(cx + dx, gy + i, cz + dz, 'glass' if i < 4 else 'red_concrete')
                elif d <= 1.9 and i == 4:
                    w.set(cx + dx, gy + i, cz + dz, 'red_concrete')
    w.fill(cx, gy + 1, cz - 2, cx, gy + 2, cz - 2, 'air')        # lantern-room door (north)
    w.set(cx, gy + 1, cz, 'ochre_froglight[axis=y]')
    w.set(cx, gy + 2, cz, 'sea_lantern')
    w.set(cx, gy + 3, cz, 'ochre_froglight[axis=y]')
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if math.hypot(dx, dz) <= 1.6:
                w.set(cx + dx, gy + 5, cz + dz, 'red_concrete')
    w.set(cx, gy + 6, cz, 'lightning_rod')
    A['lighthouse.door'] = (cx, base + 1, cz - 6)
    A['lighthouse.gallery'] = (cx, gy + 1, cz + 4)
    A['lighthouse.gallery.n'] = (cx, gy + 1, cz - 4)
    A['lighthouse.inside'] = (cx - 1, base + 1, cz)


def fish_market(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    x0, x1, z0, z1, y = 166, 185, 177, 189, T0
    w.clear(x0 - 1, y + 1, z0 - 1, x1 + 1, y + 14, z1 + 1)
    w.fill(x0, y, z0, x1, y, z1, 'polished_andesite')
    for x in range(x0, x1 + 1, 1):
        for z in range(z0, z1 + 1):
            if (x + z) % 2:
                w.set(x, y, z, 'smooth_stone')
    for x in (x0, x0 + 6, x0 + 13, x1):
        for z in (z0, z0 + 6, z1):
            w.fill(x, y + 1, z, x, y + 4, z, 'stripped_spruce_log')
            w.set(x, y + 1, z, 'stone_bricks')
    w.fill(x0, y + 5, z0, x1, y + 5, z1, 'spruce_planks')
    w.fill(x0 + 1, y + 5, z0 + 1, x1 - 1, y + 5, z1 - 1, 'air')
    for x in range(x0, x1 + 1, 3):
        w.fill(x, y + 5, z0, x, y + 5, z1, 'spruce_planks')
    hip_roof(w, x0, z0, x1, z1, y + 6, 'brick')
    for lx in (x0 + 3, x0 + 10, x1 - 3):
        w.set(lx, y + 4, z0 + 6, 'lantern[hanging=true]')
        w.set(lx, y + 5, z0 + 6, 'spruce_planks')
    # stalls: ice tables with the catch
    k = 0
    for sx in (x0 + 2, x0 + 8, x0 + 14):
        for sz in (z0 + 2, z0 + 8):
            w.fill(sx, y + 1, sz, sx + 3, y + 1, sz + 1, 'spruce_planks')
            for dx in range(4):
                w.set(sx + dx, y + 2, sz, rng.choice(['snow[layers=5]', 'snow[layers=6]']))
                w.set(sx + dx, y + 2, sz + 1, rng.choice(['snow[layers=5]', 'snow[layers=6]', 'snow[layers=5]']))
            w.set(sx + 4, y + 1, sz, 'barrel[facing=up]')
            A[f'fishmarket.stall{k}'] = (sx + 1, y + 1, sz + 3)
            A[f'fishmarket.monger{k}'] = (sx + 2, y + 1, sz - 1)
            ctx['props'].append(('fish', sx + 1, y + 2, sz))
            k += 1
    w.set(x1 - 1, y + 1, z0 + 1, 'recrafted:hiding_crate')
    A['fishmarket.center'] = (x0 + 10, y + 1, z0 + 6)
    A['fishmarket.front'] = (x0 + 10, y + 1, z1 + 3)
    ctx['props'].append(('kitchen_knife', x0 + 15, y + 2, z0 + 9))
    ctx['props'].append(('fish', x0 + 9, y + 2, z0 + 3))


def harbour_office(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    x0, x1, z0, z1, y = 207, 225, 176, 189, T0
    info = house(ctx, x0, z0, x1, z1, y, 2, 'south', wall='white', roof='hip', roofmat='brick',
                 shutter='warped', trim='light_blue_terracotta' if False else 'smooth_quartz',
                 name='harbour_office', floor_mat='polished_andesite', balcony=True, interior=True)
    fr = info['frame']
    du = info['door'][0] - x0
    w.fill(info['door'][0], y + 1, z1, info['door'][0], y + 2, z1, 'air')     # open doorway
    w.set(x0 + 12, y + 1, z1, 'recrafted:card_reader[tier=harbour]') if False else None
    # ground floor: public counter; upstairs: the captain's office
    w.fill(x0 + 2, y + 1, z0 + 6, x1 - 2, y + 1, z0 + 6, 'dark_oak_planks')
    w.fill(x0 + 9, y + 1, z0 + 6, x0 + 10, y + 1, z0 + 6, 'air')
    for x in (x0 + 3, x0 + 6, x1 - 5):
        w.set(x, y + 2, z0 + 6, rng.choice(['lantern[hanging=false]', 'potted_fern', 'air']))
    f2 = y + 6
    w.fill(x1 - 6, f2, z0 + 2, x1 - 3, f2, z0 + 2, 'dark_oak_planks')          # desk
    w.set(x1 - 4, f2, z0 + 1, 'dark_oak_stairs[facing=north,half=bottom]')     # chair behind desk
    w.set(x1 - 6, f2 + 1, z0 + 2, 'lantern[hanging=false]')
    w.set(x1 - 3, f2 + 1, z0 + 2, 'recrafted:drink[poison=none]')
    w.fill(x1 - 1, f2, z0 + 5, x1 - 1, f2 + 1, z0 + 8, 'bookshelf')
    w.set(x0 + 1, f2, z1 - 1, 'recrafted:hiding_crate')
    A['office.desk'] = (x1 - 4, f2, z0 + 1)
    A['office.desk.front'] = (x1 - 4, f2, z0 + 4)
    A['office.window'] = (x1 - 8, f2, z1 - 1)
    A['office.counter'] = (x0 + 6, y + 1, z0 + 5)
    A['office.lobby'] = (x0 + 9, y + 1, z0 + 9)
    A['office.upstairs'] = (x0 + 7, f2, z0 + 5)
    ctx['props'].append(('keycard_harbour', x1 - 5, f2 + 1, z0 + 2))
    ctx['props'].append(('letter_opener', x1 - 4, f2 + 1, z0 + 2))
    # flag + mast on the roof ridge
    rt = w.column_top((x0 + x1) // 2, (z0 + z1) // 2)
    mx, mz = (x0 + x1) // 2, (z0 + z1) // 2
    for i in range(1, 8):
        w.set(mx, rt + i, mz, 'iron_bars')
    w.fill(mx + 1, rt + 6, mz, mx + 3, rt + 7, mz, 'blue_wool')
    w.fill(mx + 1, rt + 6, mz, mx + 3, rt + 6, mz, 'white_wool')
    ctx['zones'].append(dict(name='harbour_office_upstairs', box=[x0, f2 - 1, z0, x1, f2 + 4, z1],
                             allow=['harbour_guard'], label='Harbour Office — staff only'))


def town_hall(ctx):
    """Municipio with loggia and clock tower on the east side of the piazza."""
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    x0, x1, z0, z1, y = 195, 214, 136, 155, T1
    info = house(ctx, x0, z0, x1, z1, y, 3, 'west', wall='cream', roof='hip', roofmat='brick', shutter='dark_oak',
                 trim='smooth_quartz', name='town_hall', floor_mat='polished_diorite', balcony=False,
                 plinth='polished_andesite')
    # loggia: arches along the piazza front
    for z in range(z0 + 1, z1, 3):
        w.fill(x0, y + 1, z, x0, y + 3, z + 1, 'air')
        w.set(x0, y + 3, z, 'smooth_quartz_stairs[facing=south,half=top]')
        w.set(x0, y + 3, z + 1, 'smooth_quartz_stairs[facing=north,half=top]')
    w.fill(x0 + 4, y + 1, z0 + 1, x0 + 4, y + 4, z1 - 1, 'smooth_sandstone')
    for z in range(z0 + 3, z1 - 1, 5):
        w.fill(x0 + 4, y + 1, z, x0 + 4, y + 2, z, 'air')
    w.fill(x0 + 1, y + 3, z0 + 4, x0 + 1, y + 3, z1 - 4, 'air')
    for z in range(z0 + 3, z1, 5):
        w.set(x0 + 2, y + 4, z, 'lantern[hanging=true]') if False else None
        w.set(x0 + 2, y + 3, z, 'lantern[hanging=true]')
    # balcony over the loggia
    for z in range(z0 + 7, z1 - 6):
        w.set(x0 - 1, y + 5, z, 'smooth_quartz_slab[type=top]')
        w.set(x0 - 1, y + 6, z, 'iron_bars')
    w.fill(x0 + 8, y + 1, z0 + 8, x0 + 12, y + 1, z0 + 9, 'dark_oak_planks')
    w.set(x0 + 10, y + 2, z0 + 8, 'lantern[hanging=false]')
    A['town_hall.loggia'] = (x0 + 2, y + 1, z0 + 10)
    A['town_hall.hall'] = (x0 + 9, y + 1, z0 + 12)
    A['town_hall.front'] = (x0 - 3, y + 1, z0 + 10)
    # clock tower at the north-west corner
    tx0, tz0, tx1, tz1 = x0 - 1, z0 - 1, x0 + 5, z0 + 5
    top = y + 30
    mix = wall_mix('cream')
    for yy in range(y + 16, top):
        ring_mix(w, tx0, tz0, tx1, tz1, yy, yy, rng, mix)
        w.clear(tx0 + 1, yy, tz0 + 1, tx1 - 1, yy, tz1 - 1)
    ring(w, tx0, tz0, tx1, tz1, y + 21, y + 21, 'smooth_quartz')
    ring(w, tx0, tz0, tx1, tz1, top, top, 'smooth_quartz')
    w.fill(tx0 + 1, y + 21, tz0 + 1, tx1 - 1, y + 21, tz1 - 1, 'spruce_planks')
    # clock faces (west + south)
    for (fx, fz, ax) in ((tx0, tz0 + 3, 'z'), (tx0 + 3, tz1, 'x')):
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                px, pz = (fx, fz + a) if ax == 'z' else (fx + a, fz)
                w.set(px, y + 18 + b, pz, 'smooth_quartz' if (a or b) else 'polished_blackstone')
    # belfry openings
    for yy in (y + 24, y + 25, y + 26):
        for a in (2, 3, 4):
            w.set(tx0 + a, yy, tz0, 'air'); w.set(tx0 + a, yy, tz1, 'air')
            w.set(tx0, yy, tz0 + a, 'air'); w.set(tx1, yy, tz0 + a, 'air')
    for a in (2, 3, 4):
        w.set(tx0 + a, y + 24, tz0, 'iron_bars'); w.set(tx0 + a, y + 24, tz1, 'iron_bars')
        w.set(tx0, y + 24, tz0 + a, 'iron_bars'); w.set(tx1, y + 24, tz0 + a, 'iron_bars')
    w.fill(tx0 + 1, y + 23, tz0 + 1, tx1 - 1, y + 23, tz1 - 1, 'spruce_planks')
    w.set(tx0 + 3, y + 27, tz0 + 3, 'bell[attachment=ceiling,facing=north]')
    w.fill(tx0 + 1, y + 28, tz0 + 1, tx1 - 1, y + 28, tz1 - 1, 'spruce_planks')
    w.set(tx0 + 3, y + 28, tz0 + 3, 'dark_oak_fence')
    hip_roof(w, tx0, tz0, tx1, tz1, top + 1, 'brick')
    # ladder from the top floor into the tower
    for yy in range(y + 11, y + 24):
        w.set(tx0 + 2, yy, tz0 + 2, 'ladder[facing=south]')
        w.set(tx0 + 2, yy, tz0 + 1, 'smooth_sandstone')
    w.set(tx0 + 2, y + 21, tz0 + 2, 'ladder[facing=south]')
    w.set(tx0 + 2, y + 23, tz0 + 2, 'ladder[facing=south]')
    w.set(tx0 + 2, y + 15, tz0 + 2, 'ladder[facing=south]')
    A['town_hall.belfry'] = (tx0 + 4, y + 24, tz0 + 4)
    ctx['props'].append(('wrench', tx0 + 4, y + 24, tz0 + 2))


def chapel(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    x0, x1, z0, z1, y = 206, 220, 60, 84, T3
    w.clear(x0 - 2, y + 1, z0 - 2, x1 + 9, y + 40, z1 + 3)
    w.fill(x0 - 1, y - 4, z0 - 1, x1 + 8, y, z1 + 1, 'stone_bricks')
    mix = [('white_concrete', .95), ('calcite', .05)]
    hh = 9
    ring_mix(w, x0, z0, x1, z1, y + 1, y + hh, rng, mix)
    ring(w, x0, z0, x1, z1, y + 1, y + 1, 'stone_bricks')
    w.fill(x0 + 1, y, z0 + 1, x1 - 1, y, z1 - 1, 'polished_diorite')
    for z in range(z0 + 1, z1):
        w.set((x0 + x1) // 2, y, z, 'red_terracotta')
    gable_roof(w, x0, z0, x1, z1, y + hh + 1, 'brick', mix, rng, 'z')
    cxm = (x0 + x1) // 2
    # facade: door, rose window, cross
    w.fill(cxm - 1, y + 1, z1, cxm + 1, y + 3, z1, 'air')
    w.set(cxm - 1, y + 3, z1, 'smooth_quartz_stairs[facing=east,half=top]')
    w.set(cxm + 1, y + 3, z1, 'smooth_quartz_stairs[facing=west,half=top]')
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if math.hypot(dx, dy) <= 2.3:
                w.set(cxm + dx, y + 8 + dy, z1, rng.choice(['yellow_stained_glass', 'light_blue_stained_glass',
                                                           'red_stained_glass']))
    top = w.column_top(cxm, z1)
    w.fill(cxm, top + 1, z1, cxm, top + 3, z1, 'smooth_quartz_wall' if False else 'stone_brick_wall')
    w.set(cxm - 1, top + 2, z1, 'stone_brick_wall'); w.set(cxm + 1, top + 2, z1, 'stone_brick_wall')
    # side windows
    for z in range(z0 + 4, z1 - 2, 5):
        for xs in (x0, x1):
            w.fill(xs, y + 4, z, xs, y + 7, z, 'light_blue_stained_glass_pane' if (z // 5) % 2 else
                   'yellow_stained_glass_pane')
    # interior
    for z in range(z0 + 8, z1 - 3, 2):
        for x in list(range(x0 + 2, cxm - 1)) + list(range(cxm + 2, x1 - 1)):
            w.set(x, y + 1, z, 'spruce_stairs[facing=south,half=bottom]')
    w.fill(cxm - 2, y + 1, z0 + 2, cxm + 2, y + 1, z0 + 4, 'smooth_quartz')
    w.fill(cxm - 1, y + 2, z0 + 2, cxm + 1, y + 2, z0 + 2, 'smooth_quartz')
    w.set(cxm, y + 3, z0 + 2, 'gold_block')
    w.set(cxm - 2, y + 2, z0 + 3, 'candle[candles=3,lit=true]')
    w.set(cxm + 2, y + 2, z0 + 3, 'candle[candles=3,lit=true]')
    w.set(cxm, y + 2, z0 + 5, 'lectern[facing=south]')
    for z in range(z0 + 5, z1 - 2, 6):
        w.set(cxm, y + hh, z, 'lantern[hanging=true]')
        w.set(cxm, y + hh + 1, z, 'chain[axis=y]') if False else None
    w.set(x0 + 1, y + 1, z1 - 1, 'recrafted:hiding_crate')
    A['chapel.door'] = (cxm, y + 1, z1 + 2)
    A['chapel.aisle'] = (cxm, y + 1, z0 + 12)
    A['chapel.altar'] = (cxm, y + 1, z0 + 6)
    A['chapel.pew'] = (x0 + 3, y + 1, z0 + 13)
    ctx['props'].append(('candlestick', cxm + 1, y + 2, z0 + 4))
    # campanile
    tx0, tz0 = x1 + 2, z0 + 2
    tx1, tz1 = tx0 + 5, tz0 + 5
    th = 26
    for yy in range(y + 1, y + th + 1):
        ring_mix(w, tx0, tz0, tx1, tz1, yy, yy, rng, mix)
    ring(w, tx0, tz0, tx1, tz1, y + 1, y + 2, 'stone_bricks')
    ring(w, tx0, tz0, tx1, tz1, y + th - 6, y + th - 6, 'smooth_quartz')
    w.fill(tx0 + 1, y + th - 6, tz0 + 1, tx1 - 1, y + th - 6, tz1 - 1, 'spruce_planks')
    for yy in range(y + th - 5, y + th - 1):
        for a in (2, 3):
            w.set(tx0 + a, yy, tz0, 'air'); w.set(tx0 + a, yy, tz1, 'air')
            w.set(tx0, yy, tz0 + a, 'air'); w.set(tx1, yy, tz0 + a, 'air')
    for a in (2, 3):
        w.set(tx0 + a, y + th - 5, tz0, 'iron_bars'); w.set(tx0 + a, y + th - 5, tz1, 'iron_bars')
        w.set(tx0, y + th - 5, tz0 + a, 'iron_bars'); w.set(tx1, y + th - 5, tz0 + a, 'iron_bars')
    w.fill(tx0 + 1, y + th, tz0 + 1, tx1 - 1, y + th, tz1 - 1, 'spruce_planks')
    w.set(tx0 + 2, y + th - 1, tz0 + 2, 'bell[attachment=ceiling,facing=north]')
    w.set(tx0 + 3, y + th - 1, tz0 + 3, 'bell[attachment=ceiling,facing=north]')
    hip_roof(w, tx0, tz0, tx1, tz1, y + th + 1, 'brick')
    w.fill(tx0, y + 1, tz0 + 2, tx0, y + 2, tz0 + 2, 'air')                  # door to the west (from the nave side)
    w.fill(x1, y + 1, tz0 + 2, x1 + 1, y + 2, tz0 + 2, 'air')
    for yy in range(y + 1, y + th - 5):
        w.set(tx1 - 1, yy, tz1 - 1, 'ladder[facing=north]')
    w.set(tx1 - 1, y + th - 6, tz1 - 1, 'ladder[facing=north]')
    A['chapel.belfry'] = (tx0 + 2, y + th - 5, tz0 + 3)
    # forecourt + cemetery
    for x in range(x0 - 2, x1 + 9):
        for z in range(z1 + 1, z1 + 5):
            w.set(x, y, z, 'polished_andesite' if (x + z) % 2 else 'smooth_stone')
            w.clear(x, y + 1, z, x, y + 3, z)
    cypress(w, x0 - 3, y + 1, z1 + 2, 9, rng)
    cypress(w, x1 + 9, y + 1, z1 + 2, 10, rng)
    gx0, gx1, gz0, gz1 = 230, 248, 60, 84
    for x in range(gx0, gx1 + 1):
        for z in (gz0, gz1):
            if w.is_air(x, ctx['H'][z, x] + 1, z):
                w.set(x, ctx['H'][z, x] + 1, z, 'mossy_stone_brick_wall' if rng.random() < .3 else 'stone_brick_wall')
    for z in range(gz0, gz1 + 1):
        x = gx1
        if not (70 <= z <= 72) and w.is_air(x, ctx['H'][z, x] + 1, z):
            w.set(x, ctx['H'][z, x] + 1, z, 'stone_brick_wall')
    k = 0
    for gx in range(gx0 + 2, gx1 - 1, 4):
        for gz in range(gz0 + 3, gz1 - 2, 5):
            h = ctx['H'][gz, gx]
            w.set(gx, h + 1, gz, rng.choice(['stone_brick_wall', 'mossy_stone_brick_wall', 'andesite_wall']))
            if rng.random() < .5:
                w.set(gx, h + 2, gz, 'stone_brick_wall')
            w.set(gx, h, gz + 1, 'coarse_dirt'); w.set(gx, h, gz + 2, 'podzol')
            w.set(gx, h + 1, gz + 1, rng.choice(['air', 'poppy', 'white_tulip', 'candle[candles=1,lit=true]', 'air']))
            w.set(gx, h + 1, gz + 2, 'air')
            k += 1
    for (tx, tz) in ((gx0 + 1, gz0 + 1), (gx1 - 1, gz0 + 1), (gx0 + 8, gz1 - 1), (gx1 - 2, gz1 - 2)):
        cypress(w, tx, ctx['H'][tz, tx] + 1, tz, rng.randint(8, 11), rng)
    A['cemetery.gate'] = (gx0 - 1, y + 1, 72)
    A['cemetery.grave'] = (gx0 + 6, ctx['H'][gz0 + 9, gx0 + 6] + 1, gz0 + 9)
    A['cemetery.far'] = (gx1 - 4, ctx['H'][gz0 + 14, gx1 - 4] + 1, gz0 + 14)
    ctx['props'].append(('shovel', gx0 + 3, ctx['H'][gz1 - 2, gx0 + 3] + 1, gz1 - 2))


def grove_and_promenade(ctx):
    w, rng, A, H = ctx['w'], ctx['rng'], ctx['anchors'], ctx['H']
    y = T3
    # promenade along the T3 edge
    for x in range(36, 252):
        for z in range(88, 95):
            if H[z, x] == y:
                w.set(x, y, z, 'gravel' if rng.random() < .88 else rng.choice(['andesite', 'coarse_dirt']))
                w.clear(x, y + 1, z, x, y + 2, z)
    for x in range(44, 250, 14):
        if w.is_air(x, y + 1, 87) and H[87, x] == y:
            street_lamp(w, x, y + 1, 87)
    for i, x in enumerate(range(48, 250, 28)):
        A[f'promenade.{i}'] = (x, y + 1, 91)
    # olive grove
    for gx in range(136, 198, 7):
        for gz in range(62, 86, 7):
            ox, oz = gx + rng.randint(-1, 1), gz + rng.randint(-1, 1)
            if H[oz, ox] == y and w.is_air(ox, y + 1, oz) or True:
                olive(w, ox, H[oz, ox] + 1, oz, rng)
    A['grove.mid'] = (166, y + 1, 76)
    A['grove.w'] = (140, y + 1, 80)
    A['grove.e'] = (192, y + 1, 70)
    # viewpoint at the central stair head
    for bx in (150, 168):
        bench(w, bx, y + 1, 93, 'x', 'south')
    A['viewpoint'] = (152, y + 1, 93)
    w.set(172, y + 1, 94, 'spruce_fence'); w.set(172, y + 2, 94, 'lightning_rod[facing=south]')
    A['viewpoint.telescope'] = (172, y + 1, 93)
    # wild trees on the hill and outside town
    for _ in range(170):
        x, z = rng.randint(28, 296), rng.randint(18, 200)
        if ctx['K'][z, x] != 2:
            continue
        if 36 <= x <= 132 and 22 <= z <= 88:
            continue                                  # estate grounds are landscaped separately
        if 134 <= x <= 200 and 58 <= z <= 96:
            continue
        if 200 <= x <= 252 and 56 <= z <= 96:
            continue
        h = H[z, x]
        if not w.is_air(x, h + 3, z):
            continue
        r = rng.random()
        if r < .4:
            stone_pine(w, x, h + 1, z, rng)
        elif r < .7:
            cypress(w, x, h + 1, z, rng.randint(7, 11), rng)
        else:
            olive(w, x, h + 1, z, rng)


def beach(ctx):
    w, rng, A, H = ctx['w'], ctx['rng'], ctx['anchors'], ctx['H']
    cols = ['red', 'blue', 'yellow', 'orange', 'cyan', 'lime']
    k = 0
    for bx in range(36, 80, 9):
        for bz in (190, 198):
            h = H[bz, bx]
            if ctx['K'][bz, bx] != 1 or h < 63:
                continue
            umbrella(w, bx, h + 1, bz, cols[k % len(cols)])
            for dx in (-1, 1):
                w.set(bx + dx, h + 1, bz + 1, 'smooth_quartz_slab[type=bottom]')
                w.set(bx + dx, h + 1, bz + 2, 'smooth_quartz_slab[type=bottom]')
            A[f'beach.sunbed{k}'] = (bx + 1, h + 1, bz + 1)
            A[f'beach.spot{k}'] = (bx + 3, h + 1, bz + 1)
            k += 1
    # beach bar
    bx0, bz0 = 60, 181
    h = H[bz0 + 2, bx0 + 3]
    w.fill(bx0, h, bz0, bx0 + 7, h, bz0 + 4, 'spruce_planks')
    w.clear(bx0, h + 1, bz0, bx0 + 7, h + 6, bz0 + 4)
    for (px, pz) in ((bx0, bz0), (bx0 + 7, bz0), (bx0, bz0 + 4), (bx0 + 7, bz0 + 4)):
        w.fill(px, h + 1, pz, px, h + 3, pz, 'stripped_jungle_log')
    w.fill(bx0 - 1, h + 4, bz0 - 1, bx0 + 8, h + 4, bz0 + 5, 'hay_block')
    w.fill(bx0 + 1, h + 5, bz0, bx0 + 6, h + 5, bz0 + 4, 'hay_block')
    w.fill(bx0 + 1, h + 1, bz0 + 3, bx0 + 6, h + 1, bz0 + 3, 'jungle_planks')
    for x in range(bx0 + 1, bx0 + 7, 2):
        w.set(x, h + 1, bz0 + 5, 'jungle_stairs[facing=south,half=top]') if False else None
        w.set(x, h + 1, bz0 + 4, 'jungle_fence')
        w.set(x, h + 2, bz0 + 4, 'jungle_pressure_plate')
    w.set(bx0 + 2, h + 2, bz0 + 3, 'recrafted:drink[poison=none]')
    w.set(bx0 + 5, h + 1, bz0 + 1, 'barrel[facing=up]')
    w.set(bx0 + 4, h + 1, bz0 + 1, 'barrel[facing=up]')
    w.set(bx0 + 3, h + 3, bz0 + 2, 'lantern[hanging=true]')
    A['beach.bar'] = (bx0 + 3, h + 1, bz0 + 2)
    A['beach.bar.front'] = (bx0 + 3, h + 1, bz0 + 6)
    A['beach.shore'] = (56, H[204, 56] + 1, 204)
    A['beach.w'] = (36, H[196, 36] + 1, 196)
    for (px, pz) in ((46, 184), (72, 186), (30, 190)):
        if ctx['K'][pz, px] == 1:
            palm(w, px, H[pz, px] + 1, pz, rng)
    ctx['props'].append(('bottle', bx0 + 4, h + 2, bz0 + 3))
    ctx['props'].append(('coin', 50, H[200, 50] + 1, 200))


def build(ctx):
    harbour(ctx)
    fish_market(ctx)
    harbour_office(ctx)
    town_hall(ctx)
    chapel(ctx)
    grove_and_promenade(ctx)
    beach(ctx)
