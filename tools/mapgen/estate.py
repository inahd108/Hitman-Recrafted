"""Tenuta Belmonte (hilltop wine estate) and the Conservificio Corvara (cannery)."""
import math

from core import (POTS, bench, cafe_table, chair, citrus, crate_stack, cypress, leaves, planter, stairwell,
                  street_lamp, umbrella)
from terrain import T0, T3
from town import house, hip_roof, gable_roof, wall_mix, ring, ring_mix

# ---- estate geometry ----------------------------------------------------
EX0, EX1, EZ0, EZ1 = 37, 131, 24, 86          # perimeter wall
MX0, MZ0, MX1, MZ1 = 72, 42, 128, 58          # main block
CELLAR = (74, 44, 110, 56)                    # wine cellar interior (x0, z0, x1, z1); floor block y=82
CELLAR_F = 82


def vineyard(ctx, x0, z0, x1, z1):
    w, rng, H = ctx['w'], ctx['rng'], ctx['H']
    for z in range(z0, z1 + 1):
        if z % 3 != 1:
            continue
        for x in range(x0, x1 + 1):
            h = H[z, x]
            if ctx['K'][z, x] != 2 or not w.is_air(x, h + 2, z):
                continue
            nm = w.name(w.get(x, h, z))
            if 'grass_block' not in nm and 'dirt' not in nm and 'podzol' not in nm:
                continue
            w.set(x, h, z, 'coarse_dirt' if rng.random() < .5 else 'rooted_dirt')
            if x % 4 == 0:
                w.set(x, h + 1, z, 'oak_fence')
                w.set(x, h + 2, z, 'oak_fence')
            else:
                w.set(x, h + 1, z, leaves('oak') if rng.random() < .55 else 'air')
                w.set(x, h + 2, z, leaves('oak') if rng.random() < .85 else leaves('azalea'))


def estate(ctx):
    w, rng, A, H, K = ctx['w'], ctx['rng'], ctx['anchors'], ctx['H'], ctx['K']
    y = T3
    # --- cut the villa platform into the vineyard steps -----------------------
    for x in range(68, 132):
        for z in range(38, 58):
            if H[z, x] > y:
                w.clear(x, y + 1, z, x, H[z, x] + 3, z)
            w.set(x, y, z, 'grass_block')
            w.clear(x, y + 1, z, x, y + 2, z)
            H[z, x] = y
            K[z, x] = 2
    for x in range(67, 133):
        for z in (37,):
            h = H[z, x]
            if h > y:
                w.fill_mix(x, y, z, x, h, z, rng, [('stone_bricks', .7), ('mossy_stone_bricks', .2),
                                                   ('cobblestone', .1)])
    for z in range(37, 58):
        h = H[z, 67]
        if h > y:
            w.fill_mix(67, y, z, 67, h, z, rng, [('stone_bricks', .7), ('mossy_stone_bricks', .2),
                                                 ('cobblestone', .1)])

    vineyard(ctx, 40, 25, 129, 36)
    vineyard(ctx, 40, 37, 65, 57)
    A['vineyard.w'] = (52, H[46, 52] + 1, 45)
    A['vineyard.w2'] = (44, H[52, 44] + 1, 51)
    A['vineyard.n'] = (96, H[33, 96] + 1, 32)
    A['vineyard.n2'] = (116, H[30, 116] + 1, 29)

    # --- perimeter wall ---------------------------------------------------------
    mix = wall_mix('cream')

    def wall_at(x, z):
        h = H[z, x]
        if h < 70:
            return
        w.fill_mix(x, h + 1, z, x, h + 3, z, rng, mix)
        w.set(x, h + 4, z, 'brick_slab[type=bottom]')

    for x in range(EX0, EX1 + 1):
        if not (98 <= x <= 102):
            wall_at(x, EZ1)
        wall_at(x, EZ0)
    for z in range(EZ0, EZ1 + 1):
        wall_at(EX0, z)
        if not (74 <= z <= 76):
            wall_at(EX1, z)
    for gx in (97, 103):
        w.fill(gx, y + 1, EZ1, gx, y + 5, EZ1, 'smooth_sandstone')
        w.set(gx, y + 6, EZ1, 'lantern[hanging=false]')
    for gz in (73, 77):
        w.fill(EX1, y + 1, gz, EX1, y + 5, gz, 'smooth_sandstone')
    A['estate.gate.out'] = (100, y + 1, EZ1 + 3)
    A['estate.gate.in'] = (100, y + 1, EZ1 - 2)
    A['estate.gate.guard_l'] = (97, y + 1, EZ1 + 1)
    A['estate.gate.guard_r'] = (103, y + 1, EZ1 + 1)
    A['estate.service.out'] = (EX1 + 3, y + 1, 75)
    A['estate.service.in'] = (EX1 - 2, y + 1, 75)

    # --- villa: main block + two wings ------------------------------------------
    main = house(ctx, MX0, MZ0, MX1, MZ1, y, 2, 'south', wall='ochre', roof='hip', roofmat='brick',
                 shutter='dark_oak', trim='smooth_quartz', interior=False, balcony=False,
                 floor_mat='polished_diorite', door_u=28, plinth='polished_andesite')
    house(ctx, 72, 59, 84, 72, y, 2, 'east', wall='ochre', roof='hip', roofmat='brick', shutter='dark_oak',
          interior=False, balcony=False, floor_mat='polished_andesite', blind=('L',), plinth='polished_andesite')
    house(ctx, 116, 59, 128, 72, y, 2, 'west', wall='ochre', roof='hip', roofmat='brick', shutter='dark_oak',
          interior=False, balcony=False, floor_mat='spruce_planks', blind=('R',), plinth='polished_andesite')
    f1, f2 = y + 1, y + 6                           # feet levels of both storeys
    # wing <-> main block passages on both floors
    for (xa, xb) in ((76, 80), (120, 124)):
        for fy in (f1, f2):
            w.fill(xa, fy, 58, xb, fy + 2, 59, 'air')
        w.fill(xa, y + 5, 58, xb, y + 5, 59, 'spruce_planks')
        w.fill(xa, y, 58, xb, y, 59, 'polished_diorite')
    # main entrance from the court: three arches
    for ax in (96, 100, 104):
        w.fill(ax - 1, f1, MZ1, ax + 1, f1 + 2, MZ1, 'air')
        w.set(ax - 1, f1 + 2, MZ1, 'smooth_quartz_stairs[facing=east,half=top]')
        w.set(ax + 1, f1 + 2, MZ1, 'smooth_quartz_stairs[facing=west,half=top]')
    # wing doors onto the court
    w.fill(84, f1, 65, 84, f1 + 1, 66, 'air')
    w.fill(116, f1, 65, 116, f1 + 1, 66, 'air')

    # partitions (both floors)
    for px in (90, 110):
        for fy in (f1, f2):
            w.fill_mix(px, fy, MZ0 + 1, px, fy + 3, MZ1 - 1, rng, [('smooth_sandstone', .9), ('cut_sandstone', .1)])
            w.fill(px, fy, 50, px, fy + 2, 51, 'air')
    # --- hall + grand stair -------------------------------------------------------
    for i in range(5):
        for zz in (44, 45):
            w.set(94 + i, f1 + i, zz, 'dark_oak_stairs[facing=east,half=bottom]')
            if i >= 1:
                w.set(94 + i, y + 5, zz, 'air')
            w.fill(94 + i, f1, zz, 94 + i, f1 + i - 1, zz, 'dark_oak_planks') if i else None
    for x in range(92, 109):
        for z in range(47, 57):
            w.set(x, y, z, 'red_terracotta' if (x + z) % 2 else 'polished_diorite')
    w.set(100, f1 + 3, 52, 'lantern[hanging=true]')
    for lx in (93, 107):
        w.set(lx, f1, 56, 'decorated_pot')
    A['villa.hall'] = (100, f1, 53)
    A['villa.hall.stairs'] = (92, f1, 45)
    A['villa.landing'] = (101, f2, 45)
    A['villa.gallery'] = (100, f2, 53)
    # --- dining room (west) -------------------------------------------------------
    w.fill(77, f1, 49, 86, f1, 50, 'dark_oak_planks')
    for x in range(77, 87):
        w.set(x, f1, 48, 'dark_oak_stairs[facing=south,half=bottom]')
        w.set(x, f1, 51, 'dark_oak_stairs[facing=north,half=bottom]')
    for x in (78, 81, 84):
        w.set(x, f1 + 1, 49, 'recrafted:meal[poison=none]')
        w.set(x + 1, f1 + 1, 50, 'recrafted:drink[poison=none]')
    w.set(82, f1 + 3, 50, 'lantern[hanging=true]')
    w.fill(73, f1, 44, 73, f1 + 1, 47, 'bookshelf')
    w.set(88, f1, 44, 'recrafted:hiding_crate')
    A['villa.dining'] = (82, f1, 53)
    A['villa.dining.seat'] = (81, f1, 51)
    A['villa.dining.head'] = (79, f1, 48)
    A['villa.dining.serve'] = (84, f1, 53)
    # --- salon (east) ---------------------------------------------------------------
    w.fill(112, f1, 43, 119, f1 + 2, 43, 'bookshelf')
    w.fill(113, f1, 55, 116, f1, 55, 'white_wool')
    w.set(112, f1, 55, 'spruce_stairs[facing=east,half=bottom]')
    w.set(117, f1, 55, 'spruce_stairs[facing=west,half=bottom]')
    cafe_table(w, 115, f1, 52, rng, 'red_carpet')
    w.set(126, f1, 53, 'note_block'); w.set(126, f1, 54, 'note_block'); w.set(125, f1, 53, 'dark_oak_stairs[facing=east,half=bottom]')
    w.set(118, f1 + 3, 51, 'lantern[hanging=true]')
    A['villa.salon'] = (116, f1, 50)
    A['villa.salon.sofa'] = (114, f1, 54)
    A['villa.piano'] = (124, f1, 53)
    # --- upper floor: bedroom (west), office (east) ----------------------------------
    w.set(75, f2, 44, 'white_bed[facing=north,part=head]'); w.set(75, f2, 45, 'white_bed[facing=north,part=foot]')
    w.set(76, f2, 44, 'white_bed[facing=north,part=head]'); w.set(76, f2, 45, 'white_bed[facing=north,part=foot]')
    w.fill(73, f2, 52, 73, f2 + 2, 56, 'dark_oak_planks')
    w.set(88, f2, 44, 'recrafted:hiding_crate')
    w.set(82, f2 + 3, 50, 'lantern[hanging=true]')
    cafe_table(w, 85, f2, 55, rng, 'white_carpet')
    w.set(85, f2 + 1, 55, 'recrafted:drink[poison=none]')
    A['villa.bedroom'] = (80, f2, 50)
    A['villa.bedroom.bed'] = (77, f2, 45)
    A['villa.bedroom.table'] = (85, f2, 53)
    w.fill(114, f2, 46, 118, f2, 46, 'dark_oak_planks')                     # desk
    w.set(116, f2, 45, 'dark_oak_stairs[facing=north,half=bottom]')
    w.set(114, f2 + 1, 46, 'lantern[hanging=false]')
    w.set(118, f2 + 1, 46, 'recrafted:drink[poison=none]')
    w.fill(112, f2, 56, 119, f2 + 2, 56, 'bookshelf')
    w.set(118, f2 + 3, 51, 'lantern[hanging=true]')
    A['villa.office.desk'] = (116, f2, 45)
    A['villa.office'] = (116, f2, 50)
    A['villa.office.window'] = (116, f2, 56 - 1)
    ctx['props'].append(('keycard_estate', 115, f2 + 1, 46))
    ctx['props'].append(('letter_opener', 117, f2 + 1, 46))
    ctx['props'].append(('golf_club', 113, f2, 54))
    # upper floors of the passages / balcony doors
    for bx in (96, 100, 104):
        w.fill(bx, f2, MZ1, bx, f2 + 1, MZ1, 'air')
    # loggia + balcony over the court side
    for x in range(86, 115):
        w.set(x, y + 5, 59, 'smooth_quartz_slab[type=top]')
        w.set(x, y + 5, 60, 'smooth_quartz_slab[type=top]')
        w.set(x, y + 6, 60, 'iron_bars')
        if x % 4 == 2:
            w.fill(x, f1, 60, x, f1 + 3, 60, 'quartz_pillar')
    w.fill(85, y + 5, 59, 85, y + 5, 60, 'smooth_quartz_slab[type=top]')
    w.fill(115, y + 5, 59, 115, y + 5, 60, 'smooth_quartz_slab[type=top]')
    A['villa.balcony'] = (100, f2, 59)

    # --- tower (north-east corner) -----------------------------------------------------
    tx0, tz0, tx1, tz1 = 121, 42, 128, 49
    tmix = wall_mix('ochre')
    ttop = y + 22
    w.clear(tx0, y + 10, tz0, tx1, ttop + 10, tz1)
    for yy in range(y + 1, ttop + 1):
        ring_mix(w, tx0, tz0, tx1, tz1, yy, yy, rng, tmix)
    for fy in (y + 5, y + 10, y + 15, y + 20):
        w.fill(tx0 + 1, fy, tz0 + 1, tx1 - 1, fy, tz1 - 1, 'spruce_planks')
        ring(w, tx0, tz0, tx1, tz1, fy, fy, 'smooth_quartz')
    for fy in (y + 1, y + 6):                           # doors from the salon / office
        w.fill(tx0, fy, 46, tx0, fy + 1, 46, 'air')
    for fy in (y + 11, y + 16):
        for (px, pz) in ((tx0 + 3, tz0), (tx0 + 4, tz1), (tx0, tz0 + 3), (tx1, tz0 + 4)):
            w.fill(px, fy + 1, pz, px, fy + 2, pz, 'glass_pane')
    for a in range(2, 6):                               # open belvedere at the top
        for (px, pz) in ((tx0 + a, tz0), (tx0 + a, tz1), (tx0, tz0 + a), (tx1, tz0 + a)):
            w.fill(px, y + 22 - 0, pz, px, y + 22, pz, 'smooth_quartz')
            w.fill(px, y + 21, pz, px, y + 21, pz, 'iron_bars')
    ring(w, tx0, tz0, tx1, tz1, ttop + 1, ttop + 3, 'air')
    for (px, pz) in ((tx0, tz0), (tx1, tz0), (tx0, tz1), (tx1, tz1)):
        w.fill(px, y + 21, pz, px, ttop + 3, pz, 'smooth_sandstone')
    for a in range(1, 7):
        for (px, pz) in ((tx0 + a, tz0), (tx0 + a, tz1), (tx0, tz0 + a), (tx1, tz0 + a)):
            w.set(px, y + 22, pz, 'air')
            w.set(px, y + 23, pz, 'air')
    ring(w, tx0, tz0, tx1, tz1, ttop + 3, ttop + 3, 'smooth_quartz')
    hip_roof(w, tx0, tz0, tx1, tz1, ttop + 4, 'brick')
    for yy in range(y + 1, y + 21):
        w.set(tx1 - 1, yy, tz0 + 1, 'ladder[facing=south]')
    for fy in (y + 5, y + 10, y + 15, y + 20):
        w.set(tx1 - 1, fy, tz0 + 1, 'ladder[facing=south]')
    w.set(tx0 + 3, y + 21, tz1 - 1, 'spruce_fence'); w.set(tx0 + 3, y + 22, tz1 - 1, 'lightning_rod[facing=south]')
    w.set(tx0 + 2, y + 16, tz0 + 2, 'recrafted:hiding_crate')
    A['villa.tower.top'] = (tx0 + 3, y + 21, tz0 + 3)
    A['villa.tower.base'] = (tx0 + 2, f1, tz0 + 4)
    ctx['props'].append(('sniper_case', tx0 + 4, y + 21, tz0 + 2)) if False else None

    # --- west wing: kitchen (ground), staff room (upper) -------------------------------
    for z in range(61, 71):
        w.set(73, f1, z, rng.choice(['smoker[facing=east]', 'furnace[facing=east]', 'smooth_stone',
                                     'water_cauldron[level=3]', 'smooth_stone', 'barrel[facing=up]']))
    w.fill(77, f1, 63, 80, f1, 64, 'smooth_stone')
    w.set(78, f1 + 1, 63, 'recrafted:meal[poison=none]')
    w.set(79, f1 + 1, 64, 'recrafted:meal[poison=none]')
    w.set(78, f1 + 3, 66, 'lantern[hanging=true]')
    w.fill(72, f1, 68, 72, f1 + 1, 68, 'air')                                    # back door (west)
    w.set(82, f1, 71, 'recrafted:hiding_crate')
    A['kitchen.stove'] = (74, f1, 65)
    A['kitchen.prep'] = (79, f1, 65)
    A['kitchen.door'] = (70, f1, 68)
    A['kitchen.court_door'] = (86, f1, 65)
    ctx['props'].append(('kitchen_knife', 77, f1 + 1, 64))
    ctx['props'].append(('frying_pan', 73, f1 + 1, 66)) if False else ctx['props'].append(('frying_pan', 75, f1, 62))
    ctx['props'].append(('rat_poison', 82, f1, 61))
    ctx['props'].append(('rolling_pin', 80, f1 + 1, 63))
    for i in range(5):                                                            # stair to the staff floor
        w.set(77 + i, f1 + i, 71, 'spruce_stairs[facing=east,half=bottom]')
        if i >= 1:
            w.set(77 + i, y + 5, 71, 'air')
    for (bx, bz) in ((74, 61), (74, 64), (74, 67)):
        w.set(bx, f2, bz, 'red_bed[facing=west,part=head]' if False else 'red_bed[facing=east,part=foot]')
        w.set(bx - 1, f2, bz, 'red_bed[facing=east,part=head]') if False else None
        w.set(bx + 1, f2, bz, 'red_bed[facing=east,part=head]')
    w.set(78, f2 + 3, 66, 'lantern[hanging=true]')
    A['staff.room'] = (79, f2, 66)
    ctx['props'].append(('outfit_waiter', 80, f2, 62))
    # --- east wing: security room (ground), guest room (upper) --------------------------
    w.fill(126, f1, 61, 127, f1, 66, 'dark_oak_planks')
    for z in (61, 63, 65):
        w.set(127, f1 + 1, z, 'recrafted:lab_console')
    w.set(125, f1, 63, 'dark_oak_stairs[facing=west,half=bottom]')
    w.fill(118, f1, 71, 122, f1 + 1, 71, 'iron_block')
    w.set(122, f1 + 3, 66, 'lantern[hanging=true]')
    w.set(126, f1, 70, 'recrafted:fuse_box')
    A['security.desk'] = (125, f1, 63)
    A['security.room'] = (121, f1, 66)
    A['security.lockers'] = (120, f1, 70)
    ctx['props'].append(('outfit_estate_guard', 121, f1, 69))
    ctx['props'].append(('baton', 126, f1 + 1, 64))
    for i in range(5):
        w.set(123 - i, f1 + i, 60, 'spruce_stairs[facing=west,half=bottom]')
        if i >= 1:
            w.set(123 - i, y + 5, 60, 'air')
    w.set(126, f2, 62, 'blue_bed[facing=north,part=head]'); w.set(126, f2, 63, 'blue_bed[facing=north,part=foot]')
    w.set(122, f2 + 3, 66, 'lantern[hanging=true]')
    A['guest.room'] = (122, f2, 67)

    # --- court ---------------------------------------------------------------------------
    for x in range(85, 116):
        for z in range(59, 73):
            w.set(x, y, z, 'polished_diorite' if (x + z) % 2 else 'terracotta')
            if w.name(w.get(x, y + 1, z)).split(':')[1] in ('grass', 'fern', 'poppy', 'dandelion'):
                w.set(x, y + 1, z, 'air')
    cx, cz = 100, 66
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            d = max(abs(dx), abs(dz))
            if d == 2 and abs(dx) + abs(dz) < 4:
                w.set(cx + dx, y + 1, cz + dz, 'smooth_quartz')
            elif d < 2:
                w.set(cx + dx, y + 1, cz + dz, 'water')
                w.set(cx + dx, y, cz + dz, 'prismarine_bricks')
    w.fill(cx, y + 1, cz, cx, y + 2, cz, 'quartz_pillar')
    w.set(cx, y + 3, cz, 'sea_lantern')
    for (px, pz) in ((88, 62), (112, 62), (88, 70), (112, 70)):
        w.set(px, y + 1, pz, 'terracotta')
        citrus(w, px, y + 2, pz, rng)
    A['court.fountain'] = (100, y + 1, 70)
    A['court.w'] = (90, y + 1, 66)
    A['court.e'] = (110, y + 1, 66)
    A['court.arches'] = (100, y + 1, 61)

    # --- front garden + drive --------------------------------------------------------------
    for x in range(72, 129):
        for z in range(73, 86):
            if 98 <= x <= 102:
                w.set(x, y, z, 'gravel')
                w.set(x, y + 1, z, 'air')
            elif x in (97, 103) and z > 73:
                w.set(x, y, z, 'grass_block')
                w.set(x, y + 1, z, leaves('azalea') if z % 3 else leaves('flowering_azalea'))
    for z in (75, 79, 83):
        cypress(w, 95, y + 1, z, 9, rng)
        cypress(w, 105, y + 1, z, 9, rng)
    for (hx0, hx1) in ((76, 92), (108, 126)):
        for x in range(hx0, hx1 + 1):
            for z in (76, 82):
                w.set(x, y + 1, z, leaves('oak'))
        for x in range(hx0 + 2, hx1, 4):
            w.set(x, y + 1, 79, 'rose_bush[half=lower]'); w.set(x, y + 2, 79, 'rose_bush[half=upper]')
        bench(w, (hx0 + hx1) // 2, y + 1, 78, 'x', 'south')
    street_lamp(w, 97, y + 1, 73); street_lamp(w, 103, y + 1, 73)
    A['garden.w'] = (84, y + 1, 79)
    A['garden.e'] = (116, y + 1, 79)
    A['garden.bench'] = (84, y + 1, 78)
    A['drive.mid'] = (100, y + 1, 79)
    ctx['props'].append(('garden_shears', 90, y + 1, 80))

    # --- pool terrace (west) ------------------------------------------------------------------
    px0, px1, pz0, pz1 = 42, 68, 60, 84
    for x in range(px0, px1 + 1):
        for z in range(pz0, pz1 + 1):
            if H[z, x] != y:
                continue
            w.set(x, y, z, 'smooth_sandstone' if (x + z) % 5 else 'cut_sandstone')
            w.clear(x, y + 1, z, x, y + 3, z)
    for x in range(46, 61):
        for z in range(66, 75):
            edge = x in (46, 60) or z in (66, 74)
            if edge:
                w.set(x, y, z, 'smooth_quartz')
            else:
                w.set(x, y - 2, z, 'prismarine_bricks' if (x + z) % 2 else 'light_blue_concrete')
                w.set(x, y - 1, z, 'water'); w.set(x, y, z, 'water')
                w.fill(x, y - 3, z, x, y - 3, z, 'stone')
    for i, lz in enumerate((67, 70, 73)):
        w.set(63, y + 1, lz, 'smooth_quartz_slab[type=bottom]'); w.set(64, y + 1, lz, 'smooth_quartz_slab[type=bottom]')
        A[f'pool.lounger{i}'] = (64, y + 1, lz)
    umbrella(w, 65, y + 1, 68, 'white'); umbrella(w, 65, y + 1, 72, 'white')
    # pergola bar
    for (ax, az) in ((46, 60), (56, 60), (46, 63), (56, 63)):
        w.fill(ax, y + 1, az, ax, y + 3, az, 'stripped_oak_log')
    for x in range(45, 58):
        for z in range(59, 65):
            w.set(x, y + 4, z, leaves('flowering_azalea') if (x * 3 + z) % 4 == 0 else 'spruce_trapdoor[facing=north,open=false,half=bottom]')
    w.fill(48, y + 1, 61, 54, y + 1, 61, 'smooth_quartz')
    w.set(50, y + 2, 61, 'recrafted:drink[poison=none]')
    w.set(53, y + 2, 61, 'recrafted:drink[poison=none]')
    w.set(51, y + 3, 62, 'lantern[hanging=true]')
    A['pool.bar'] = (51, y + 1, 60)
    A['pool.bar.front'] = (50, y + 1, 63)
    A['pool.edge'] = (53, y + 1, 76)
    A['pool.south'] = (53, y + 1, 80)
    A['pool.path'] = (69, y + 1, 76)
    for (tx, tz) in ((43, 62), (43, 82), (67, 82)):
        planter(w, tx, y + 1, tz, rng)
    ctx['props'].append(('bottle', 49, y + 2, 61))
    ctx['props'].append(('coin', 62, y + 1, 78))

    # --- wine cellar under the main block --------------------------------------------------------
    cx0, cz0, cx1, cz1 = CELLAR
    f = CELLAR_F
    w.fill(cx0 - 1, f - 1, cz0 - 1, cx1 + 1, f + 6, cz1 + 1, 'stone_bricks')
    w.fill_mix(cx0, f, cz0, cx1, f, cz1, rng, [('stone_bricks', .5), ('cobblestone', .3), ('mossy_stone_bricks', .2)])
    w.clear(cx0, f + 1, cz0, cx1, f + 4, cz1)
    w.fill(cx0, f + 5, cz0, cx1, f + 5, cz1, 'bricks')
    for x in range(cx0 + 3, cx1 - 1, 4):
        for (zz, face) in ((cz0, 'south'), (cz1, 'north')):
            for dy in (1, 2):
                w.set(x, f + dy, zz, f'barrel[facing={face}]')
                w.set(x + 1, f + dy, zz, f'barrel[facing={face}]')
        w.set(x + 2, f + 4, (cz0 + cz1) // 2, 'lantern[hanging=true]') if x % 8 == 1 else None
    for x in range(cx0 + 6, cx1 - 4, 10):
        w.set(x, f + 4, (cz0 + cz1) // 2, 'lantern[hanging=true]')
    # tasting table
    tx, tz = 92, 50
    w.fill(tx, f + 1, tz, tx + 2, f + 1, tz, 'spruce_planks')
    w.set(tx + 1, f + 2, tz, 'recrafted:drink[poison=none]')
    w.set(tx, f + 2, tz, 'candle[candles=2,lit=true]')
    A['cellar.tasting'] = (tx + 1, f + 1, tz + 1)
    A['cellar.mid'] = (84, f + 1, 50)
    A['cellar.east'] = (107, f + 1, 50)
    # stairs from the kitchen wing
    for i in range(7):
        z = 61 - i
        for x in (74, 75):
            w.fill(x, 89 - i + 1, z, x, 89 - i + 3, z, 'air')
            w.set(x, 89 - i, z, 'stone_brick_stairs[facing=south,half=bottom]')
            w.fill(x, f, z, x, 89 - i - 1, z, 'stone_bricks') if 89 - i - 1 >= f else None
    w.fill(74, f + 1, 54, 75, f + 3, 54, 'air')
    A['cellar.stairs.top'] = (75, f1, 63)
    A['cellar.stairs.bottom'] = (75, f + 1, 53)
    ctx['props'].append(('corkscrew', tx + 2, f + 2, tz))
    ctx['props'].append(('bottle', 80, f + 1, 45))
    ctx['props'].append(('crowbar', 106, f + 1, 55))
    # big vats at the east end hide the old mine door
    for z in (cz0, cz0 + 1, cz1 - 1, cz1):
        w.fill(cx1 - 2, f + 1, z, cx1, f + 3, z, 'spruce_planks')
    ctx['zones'].append(dict(name='estate', box=[EX0, 80, EZ0, EX1, 130, EZ1],
                             allow=['estate_guard', 'bodyguard', 'waiter', 'cook', 'gardener', 'cleaner'],
                             label='Tenuta Belmonte — private property'))
    ctx['zones'].append(dict(name='villa_private', box=[MX0, y + 5, MZ0, MX1, y + 30, MZ1],
                             allow=['estate_guard', 'bodyguard', 'cleaner'],
                             label='Villa — private rooms'))


def cannery(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    y = T0
    x0, x1, z0, z1 = 258, 290, 158, 192
    w.clear(x0 - 1, y + 1, z0 - 1, x1 + 1, y + 30, z1 + 1)
    mix = wall_mix('brick')
    hh = 9
    ring_mix(w, x0, z0, x1, z1, y + 1, y + hh, rng, mix)
    ring(w, x0, z0, x1, z1, y + 1, y + 1, 'stone_bricks')
    ring(w, x0, z0, x1, z1, y + 8, y + 8, 'white_concrete')
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            w.set(x, y, z, 'polished_andesite' if (x % 6 == 0 or z % 6 == 0) else 'smooth_stone')
    # windows
    for z in range(z0 + 3, z1 - 2, 5):
        for xs in (x0, x1):
            w.fill(xs, y + 4, z, xs, y + 6, z + 1, 'glass_pane')
    for x in range(x0 + 3, x1 - 2, 5):
        for zs in (z0, z1):
            w.fill(x, y + 4, zs, x + 1, y + 6, zs, 'glass_pane')
    # three roof bays
    for (bx0, bx1) in ((x0, x0 + 10), (x0 + 11, x0 + 21), (x0 + 22, x1)):
        gable_roof(w, bx0, z0, bx1, z1, y + hh + 1, 'deepslate_tile', mix, rng, 'z')
        mx = (bx0 + bx1) // 2
        for z in range(z0 + 4, z1 - 2, 7):
            w.fill(mx, y + hh, z, mx, y + hh + 4, z, 'chain[axis=y]')
            w.set(mx, y + hh - 1, z, 'lantern[hanging=true]')
    # doors
    w.fill(x0, y + 1, 172, x0, y + 4, 176, 'air')
    w.fill(270, y + 1, z1, 274, y + 4, z1, 'air')
    A['cannery.door.out'] = (x0 - 3, y + 1, 174)
    A['cannery.door.in'] = (x0 + 3, y + 1, 174)
    A['cannery.dockdoor'] = (272, y + 1, z1 + 2)
    # production lines
    k = 0
    for lx in (264, 271):
        for z in range(164 + 6, 184):
            w.set(lx, y + 1, z, 'smooth_stone_slab[type=top]')
        for z in range(172, 184, 4):
            w.set(lx, y + 1, z, rng.choice(['blast_furnace[facing=west]', 'cauldron', 'grindstone[face=floor,facing=north]',
                                            'smithing_table']))
            w.set(lx, y + 2, z, rng.choice(['hopper[facing=down]', 'iron_bars', 'air']))
            A[f'cannery.line{k}'] = (lx - 1, y + 1, z + 1)
            k += 1
    for (bx, bz) in ((276, 172), (276, 176), (276, 180)):
        w.fill(bx, y + 1, bz, bx + 1, y + 3, bz + 1, 'waxed_copper_block')
        w.set(bx, y + 4, bz, 'iron_bars')
    A['cannery.boilers'] = (275, y + 1, 178)
    for z in range(z0 + 10, z1 - 8, 5):
        crate_stack(w, x1 - 3, y + 1, z, rng, 4)
    crate_stack(w, x0 + 3, y + 1, z1 - 4, rng, 5)
    w.set(x0 + 2, y + 1, z1 - 8, 'recrafted:hiding_crate')
    w.set(x0 + 1, y + 1, 180, 'recrafted:fuse_box')
    A['cannery.fuse'] = (x0 + 2, y + 1, 180)
    A['cannery.floor'] = (268, y + 1, 186)
    ctx['props'].append(('wrench', 266, y + 1, 185))
    ctx['props'].append(('lead_pipe', 277, y + 1, 183))
    ctx['props'].append(('hammer', x0 + 4, y + 1, 168))
    ctx['props'].append(('screwdriver', 272, y + 2, 176))
    # office mezzanine (north end)
    my = y + 5
    w.fill(x0 + 1, my, z0 + 1, x1 - 1, my, z0 + 7, 'spruce_planks')
    w.fill(x0 + 1, my, z0 + 8, x0 + 4, my, z0 + 9, 'spruce_planks')
    for x in range(x0 + 5, x1):
        w.set(x, my + 1, z0 + 7, 'iron_bars')
    for i in range(5):
        w.set(x0 + 9 - i, y + 1 + i, z0 + 9, 'spruce_stairs[facing=west,half=bottom]')
    w.set(x0 + 4, my + 1, z0 + 10, 'iron_bars') if False else None
    for x in range(x0 + 1, x0 + 5):
        w.set(x, my + 1, z0 + 10, 'iron_bars') if False else None
    # partition: Varga's surface office in the north-east
    w.fill(x1 - 13, my + 1, z0 + 1, x1 - 13, my + 3, z0 + 7, 'white_concrete')
    w.fill(x1 - 13, my + 1, z0 + 4, x1 - 13, my + 2, z0 + 4, 'air')
    w.fill(x1 - 12, my + 1, z0 + 7, x1 - 1, my + 3, z0 + 7, 'glass_pane')
    w.fill(x1 - 8, my + 1, z0 + 2, x1 - 5, my + 1, z0 + 2, 'dark_oak_planks')
    w.set(x1 - 6, my + 1, z0 + 1, 'dark_oak_stairs[facing=north,half=bottom]')
    w.set(x1 - 8, my + 2, z0 + 2, 'recrafted:drink[poison=none]')
    w.set(x1 - 5, my + 2, z0 + 2, 'lantern[hanging=false]')
    w.fill(x1 - 1, my + 1, z0 + 3, x1 - 1, my + 2, z0 + 6, 'bookshelf')
    w.set(x1 - 12, my + 1, z0 + 6, 'recrafted:hiding_crate')
    A['varga.office.desk'] = (x1 - 6, my + 1, z0 + 1)
    A['varga.office'] = (x1 - 8, my + 1, z0 + 5)
    A['varga.office.door'] = (x1 - 15, my + 1, z0 + 4)
    A['mezz.stairs.top'] = (x0 + 3, my + 1, z0 + 9)
    A['mezz.stairs.bottom'] = (x0 + 11, y + 1, z0 + 9)
    A['mezz.walk'] = (x0 + 10, my + 1, z0 + 4)
    w.fill(x0 + 6, my + 1, z0 + 1, x0 + 9, my + 1, z0 + 1, 'spruce_planks')
    w.set(x0 + 7, my + 2, z0 + 1, 'recrafted:meal[poison=none]')
    A['mezz.desk'] = (x0 + 8, my + 1, z0 + 2)
    ctx['props'].append(('keycard_lab', x1 - 7, my + 2, z0 + 2))
    ctx['props'].append(('scissors', x0 + 8, my + 2, z0 + 1))
    # stairwell to the lab (south-east corner)
    sx0, sz0 = 281, 186
    stairwell(w, sx0, sz0, y, 40, 'stone_bricks', step='stone_brick', n=4)
    w.fill(sx0 - 1, y + 1, sz0 + 1, sx0 - 1, y + 2, sz0 + 1, 'air')
    w.set(sx0 - 1, y + 1, sz0 + 1, 'iron_door[facing=east,half=lower,hinge=left,open=false]')
    w.set(sx0 - 1, y + 2, sz0 + 1, 'iron_door[facing=east,half=upper,hinge=left,open=false]')
    w.set(sx0 - 1, y + 2, sz0 + 2, 'recrafted:card_reader[tier=lab]')
    A['cannery.liftdoor'] = (sx0 - 3, y + 1, sz0 + 1)
    A['cannery.stairs.top'] = (sx0, y + 1, sz0 + 1)
    ctx['lab_stair'] = (sx0, sz0)
    # chimney
    for yy in range(y + 1, y + 34):
        r = 1
        ring_mix(w, 292 - r, 154 - r, 292 + r, 154 + r, yy, yy, rng, mix)
    ring(w, 291, 153, 293, 155, y + 31, y + 32, 'white_concrete')
    # yard wall, gate and dock
    for z in range(151, 205):
        if 193 <= z <= 198:
            continue
        w.set(253, y + 1, z, 'stone_bricks'); w.set(253, y + 2, z, 'iron_bars'); w.set(253, y + 3, z, 'iron_bars')
    for gz in (192, 199):
        w.fill(253, y + 1, gz, 253, y + 4, gz, 'bricks')
    w.fill(255, y + 1, 200, 257, y + 3, 202, 'white_concrete')
    w.fill(256, y + 1, 201, 256, y + 2, 201, 'air')
    w.fill(256, y + 1, 200, 256, y + 2, 200, 'air')
    w.set(255, y + 2, 201, 'glass_pane'); w.set(257, y + 2, 201, 'glass_pane')
    w.fill(255, y + 4, 200, 257, y + 4, 202, 'smooth_stone_slab[type=bottom]')
    A['cannery.gate.out'] = (250, y + 1, 196)
    A['cannery.gate.in'] = (256, y + 1, 196)
    A['cannery.gate.guard'] = (255, y + 1, 198)
    A['cannery.yard.n'] = (256, y + 1, 162)
    A['cannery.yard.s'] = (264, y + 1, 198)
    A['cannery.yard.e'] = (293, y + 1, 180)
    A['cannery.dock'] = (280, y + 1, 201)
    for x in range(262, 294, 7):
        crate_stack(w, x, y + 1, 200, rng, 3)
    # dock crane
    w.fill(288, y + 1, 201, 288, y + 7, 201, 'iron_bars')
    w.fill(288, y + 7, 201, 288, y + 7, 208, 'smooth_stone_slab[type=top]')
    w.fill(288, y + 4, 207, 288, y + 6, 207, 'chain[axis=y]')
    w.fill(287, y + 2, 206, 289, y + 3, 208, 'spruce_planks')
    w.set(294, y + 1, 160, 'recrafted:hiding_crate')
    ctx['props'].append(('outfit_worker', 259, y + 1, 190))
    ctx['props'].append(('brick', 257, y + 1, 170))
    ctx['zones'].append(dict(name='cannery', box=[254, 60, 152, 298, 110, 204],
                             allow=['worker', 'security', 'scientist'],
                             label='Conservificio Corvara — employees only'))


def build(ctx):
    estate(ctx)
    cannery(ctx)
