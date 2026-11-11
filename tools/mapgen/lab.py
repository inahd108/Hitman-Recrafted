"""Everything under Corvara: the sewer and cistern, the old salt mine, and the Halcyon lab."""
import math

from core import crate_stack, stairwell
from terrain import T0, T1, SEA
from estate import CELLAR, CELLAR_F

LF = 40                      # lab floor block y (walk at 41)
WALL, FLOOR, CEIL = 'white_concrete', 'light_gray_concrete', 'smooth_quartz'


def tunnel(ctx, pts, r=1.7, floor=(('gravel', .5), ('stone', .3), ('calcite', .2)), light=9, support=True):
    """Rough walkable gallery through a list of (x, y, z) floor-level points (y = feet level)."""
    w, rng = ctx['w'], ctx['rng']
    step = 0
    for (a, b) in zip(pts, pts[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[2] - a[2]), abs(b[1] - a[1]) * 2, 1) * 2)
        for i in range(n + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t
            y = int(round(a[1] + (b[1] - a[1]) * t))
            z = a[2] + (b[2] - a[2]) * t
            cx, cz = int(round(x)), int(round(z))
            R = int(math.ceil(r))
            for dx in range(-R, R + 1):
                for dz in range(-R, R + 1):
                    d = math.hypot(dx, dz)
                    if d > r + rng.random() * .5:
                        continue
                    px, pz = cx + dx, cz + dz
                    w.clear(px, y, pz, px, y + (2 if d > r - .8 else 3), pz)
                    if w.get(px, y - 1, pz) == 0 or 'water' in w.name(w.get(px, y - 1, pz)):
                        w.set(px, y - 1, pz, 'stone')
                    if rng.random() < .55:
                        w.set(px, y - 1, pz, rng.choices([f[0] for f in floor], [f[1] for f in floor])[0])
            step += 1
            if light and step % (light * 2) == 0:
                w.set(cx, y - 1, cz, 'ochre_froglight[axis=y]')
            if support and step % 14 == 7:
                for s in (-R, R):
                    pass


def room(ctx, x0, z0, x1, z1, f=LF, h=5, wall=WALL, floor=FLOOR, ceil=CEIL, lights=True, name=None):
    """Sealed room. (x0..x1, z0..z1) is the interior; f = floor block y; h = interior height."""
    w = ctx['w']
    w.fill(x0 - 1, f, z0 - 1, x1 + 1, f + h + 1, z1 + 1, wall)
    w.fill(x0, f, z0, x1, f, z1, floor)
    w.clear(x0, f + 1, z0, x1, f + h, z1)
    w.fill(x0, f + h + 1, z0, x1, f + h + 1, z1, ceil)
    if lights:
        for x in range(x0 + 2, x1 - 1, 5):
            for z in range(z0 + 2, z1 - 1, 5):
                w.set(x, f + h + 1, z, 'sea_lantern')
        w.set((x0 + x1) // 2, f + h + 1, (z0 + z1) // 2, 'sea_lantern')
    if name:
        ctx['anchors'][name] = ((x0 + x1) // 2, f + 1, (z0 + z1) // 2)


def doorway(ctx, x0, z0, x1, z1, f=LF, hgt=3, floor=FLOOR):
    w = ctx['w']
    w.fill(x0, f, z0, x1, f, z1, floor)
    w.clear(x0, f + 1, z0, x1, f + hgt, z1)


def secure_door(ctx, x, z, facing, reader_at, tier='lab', f=LF):
    """Single iron door at (x, z) + a card reader block."""
    w = ctx['w']
    w.set(x, f, z, FLOOR)
    w.set(x, f + 1, z, f'iron_door[facing={facing},half=lower,hinge=left,open=false]')
    w.set(x, f + 2, z, f'iron_door[facing={facing},half=upper,hinge=left,open=false]')
    w.set(x, f + 3, z, WALL)
    rx, rz = reader_at
    w.set(rx, f + 2, rz, f'recrafted:card_reader[tier={tier}]')


def sewer(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    # outlet in the quay wall -> north under the central stairs -> cistern under the fountain
    x0, x1 = 150, 151
    for z in range(160, 206):
        w.fill(x0 - 1, 61, z, x1 + 1, 66 if z < 204 else 65, z, 'stone_bricks') if z < 205 else None
        w.fill(x0, 62, z, x1, 62, z, 'mossy_stone_bricks' if rng.random() < .4 else 'stone_bricks')
        w.clear(x0, 63, z, x1, 64, z)
        if z % 8 == 0:
            w.set(x0, 62, z, 'ochre_froglight[axis=y]')
    w.set(x0, 64, 204, 'iron_bars')
    w.set(x1, 64, 204, 'iron_bars')
    w.set(x0, 63, 204, 'iron_bars')
    A['sewer.mouth'] = (151, 63, 203)
    A['sewer.mid'] = (151, 63, 180)
    # cistern
    cx0, cz0, cx1, cz1 = 154, 146, 170, 162
    w.fill(cx0 - 1, 63, cz0 - 1, cx1 + 1, 71, cz1 + 1, 'stone_bricks')
    w.fill_mix(cx0, 64, cz0, cx1, 64, cz1, rng, [('stone_bricks', .5), ('mossy_stone_bricks', .3), ('cobblestone', .2)])
    w.clear(cx0, 65, cz0, cx1, 69, cz1)
    for x in range(cx0 + 3, cx1 - 1, 5):
        for z in range(cz0 + 3, cz1 - 1, 5):
            w.fill(x, 65, z, x, 69, z, 'mossy_stone_bricks' if rng.random() < .4 else 'stone_bricks')
            w.set(x, 67, z, 'ochre_froglight[axis=y]')
    for x in range(cx0 + 5, cx1 - 3):
        for z in range(cz0 + 5, cz1 - 3):
            if w.get(x, 65, z) == 0:
                w.set(x, 64, z, 'water')
    # link sewer -> cistern (two steps up)
    w.fill(150, 62, 158, 153, 62, 161, 'stone_bricks')
    w.clear(150, 63, 158, 153, 65, 161)
    w.fill(152, 63, 158, 153, 63, 161, 'stone_brick_stairs[facing=east,half=bottom]')
    w.set(153, 63, 158, 'stone_bricks'); w.set(153, 63, 159, 'stone_bricks')
    w.set(153, 63, 160, 'stone_bricks'); w.set(153, 63, 161, 'stone_bricks')
    w.set(153, 64, 158, 'stone_brick_stairs[facing=east,half=bottom]'); w.set(153, 64, 159, 'stone_brick_stairs[facing=east,half=bottom]')
    w.set(153, 64, 160, 'stone_brick_stairs[facing=east,half=bottom]'); w.set(153, 64, 161, 'stone_brick_stairs[facing=east,half=bottom]')
    w.clear(153, 65, 158, 153, 67, 161)
    w.clear(152, 64, 158, 152, 66, 161)
    A['cistern'] = (156, 65, 150)
    # manhole into the piazza
    mx, mz = 156, 161
    for yy in range(65, T1):
        w.set(mx, yy, mz, 'ladder[facing=north]')
        w.set(mx, yy, mz + 1, 'stone_bricks')
    w.set(mx, T1, mz, 'spruce_trapdoor[facing=north,open=false,half=top]')
    A['manhole'] = (mx, T1 + 1, mz - 1)
    ctx['props'].append(('crowbar', 158, 65, 148))
    ctx['props'].append(('coin', 151, 63, 190))


def mine(ctx):
    """Old salt workings linking the cistern, the wine cellar and the lab's maintenance hatch."""
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    salt = (('calcite', .5), ('diorite', .2), ('gravel', .2), ('white_concrete_powder', .1))
    # big gallery
    gx, gy, gz = 152, 49, 100
    for dx in range(-15, 16):
        for dz in range(-11, 12):
            for dy in range(-1, 8):
                d = (dx / 15.0) ** 2 + (dz / 11.0) ** 2 + ((dy - 2) / 6.0) ** 2
                if d <= 1.0 + rng.random() * .08:
                    w.set(gx + dx, gy + dy, gz + dz, 'air')
            if (dx / 15.0) ** 2 + (dz / 11.0) ** 2 <= 1.05:
                w.set(gx + dx, gy - 2, gz + dz, rng.choices([s[0] for s in salt], [s[1] for s in salt])[0])
                if w.get(gx + dx, gy - 1, gz + dz) != 0:
                    w.set(gx + dx, gy - 1, gz + dz, rng.choices([s[0] for s in salt], [s[1] for s in salt])[0])
    for (px, pz) in ((146, 96), (158, 104), (150, 106), (160, 95)):
        w.fill(px, gy - 1, pz, px, gy + 7, pz, 'calcite')
        w.set(px, gy + 1, pz, 'ochre_froglight[axis=y]')
    for x in range(140, 165):
        w.set(x, gy - 1, 100, 'rail[shape=east_west]') if w.get(x, gy - 1, 100) == 0 and w.get(x, gy - 2, 100) != 0 else None
    crate_stack(w, 144, gy - 1, 103, rng, 3)
    A['mine.gallery'] = (152, gy - 1, 100)
    # galleries
    tunnel(ctx, [(194, LF + 1, 110), (182, 44, 108), (168, 48, 102)], floor=salt)            # to the lab hatch
    tunnel(ctx, [(138, 48, 97), (150, 61, 72), (128, 73, 53), (113, CELLAR_F + 1, 50)], floor=salt)   # up to the cellar
    tunnel(ctx, [(162, 65, 144), (160, 58, 124), (156, 50, 110)], floor=salt, r=1.4)         # down from the cistern
    # openings
    w.clear(111, CELLAR_F + 1, 49, 113, CELLAR_F + 2, 51)
    w.fill(111, CELLAR_F, 49, 113, CELLAR_F, 51, 'stone_bricks')
    w.set(111, CELLAR_F + 1, 49, 'barrel[facing=west]'); w.set(111, CELLAR_F + 2, 49, 'barrel[facing=west]')
    w.set(111, CELLAR_F + 2, 50, 'barrel[facing=west]')
    w.clear(162, 65, 145, 162, 66, 145)
    w.set(162, 66, 145, 'iron_bars')
    A['mine.cellar_end'] = (115, CELLAR_F + 1, 50)
    A['mine.lab_end'] = (192, LF + 1, 110)
    ctx['props'].append(('lead_pipe', 150, gy - 1, 98))
    ctx['props'].append(('lockpick', 146, gy - 1, 104))


def lab(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    f = LF
    sx0, sz0 = ctx['lab_stair']                      # stairwell interior min corner (281, 186)
    # --- lobby + service corridor -------------------------------------------------
    room(ctx, 268, 182, 279, 193, name='lab.lobby')
    doorway(ctx, 280, sz0 + 1, 280, sz0 + 2)
    w.fill(270, f + 1, 191, 274, f + 1, 191, 'smooth_quartz')
    w.set(272, f + 2, 191, 'recrafted:lab_console')
    w.set(270, f + 1, 183, 'recrafted:hiding_crate')
    A['lab.lobby.desk'] = (272, f + 1, 189)
    A['lab.stairs.bottom'] = (279, f + 1, sz0 + 1)
    room(ctx, 272, 150, 275, 180, name='lab.c1')                         # corridor C1
    doorway(ctx, 273, 181, 274, 181)
    room(ctx, 277, 168, 288, 178, name='lab.security')
    doorway(ctx, 276, 173, 276, 174)
    for z in (169, 171, 173, 175):
        w.set(288, f + 1, z, 'smooth_quartz'); w.set(288, f + 2, z, 'recrafted:lab_console')
    w.set(286, f + 1, 172, 'quartz_stairs[facing=east,half=bottom]')
    w.set(278, f + 1, 178, 'recrafted:fuse_box')
    A['lab.security.desk'] = (286, f + 1, 172)
    ctx['props'].append(('keycard_lab', 287, f + 2, 177))
    ctx['props'].append(('baton', 280, f + 1, 169))
    room(ctx, 277, 152, 290, 164, wall='light_gray_concrete', floor='smooth_stone', name='lab.generator')
    doorway(ctx, 276, 158, 276, 159)
    for (gx, gz) in ((281, 154), (281, 160), (287, 154), (287, 160)):
        w.fill(gx, f + 1, gz, gx + 1, f + 3, gz + 2, 'iron_block')
        w.set(gx, f + 2, gz + 1, 'redstone_block'); w.set(gx + 1, f + 4, gz + 1, 'iron_bars')
    w.set(278, f + 2, 152, 'recrafted:fuse_box')
    A['lab.generator.fuse'] = (278, f + 1, 153)
    ctx['props'].append(('wrench', 284, f + 1, 158))
    room(ctx, 258, 168, 270, 178, name='lab.lockers')
    doorway(ctx, 271, 173, 271, 174)
    for x in range(259, 270, 2):
        w.fill(x, f + 1, 168, x, f + 2, 168, 'iron_block')
    w.fill(260, f + 1, 174, 266, f + 1, 174, 'smooth_quartz_slab[type=bottom]')
    w.set(258, f + 1, 178, 'recrafted:hiding_crate')
    A['lab.lockers.bench'] = (263, f + 1, 175)
    ctx['props'].append(('outfit_hazmat', 261, f + 1, 170))
    ctx['props'].append(('outfit_scientist', 265, f + 1, 170))
    room(ctx, 256, 152, 270, 164, floor='smooth_stone', name='lab.canteen')
    doorway(ctx, 271, 158, 271, 159)
    for (tx, tz) in ((259, 155), (265, 155), (259, 161), (265, 161)):
        w.set(tx, f + 1, tz, 'smooth_quartz')
        w.set(tx - 1, f + 1, tz, 'quartz_stairs[facing=west,half=bottom]')
        w.set(tx + 1, f + 1, tz, 'quartz_stairs[facing=east,half=bottom]')
    w.set(259, f + 2, 155, 'recrafted:meal[poison=none]'); w.set(265, f + 2, 155, 'recrafted:drink[poison=none]')
    w.set(259, f + 2, 161, 'recrafted:drink[poison=none]'); w.set(265, f + 2, 161, 'recrafted:meal[poison=none]')
    w.fill(256, f + 1, 152, 262, f + 1, 152, 'smooth_stone')
    w.set(257, f + 2, 152, 'brewing_stand'); w.set(260, f + 1, 152, 'smoker[facing=south]')
    A['lab.canteen.seat0'] = (258, f + 1, 155)
    A['lab.canteen.seat1'] = (266, f + 1, 155)
    A['lab.canteen.seat2'] = (258, f + 1, 161)
    A['lab.canteen.coffee'] = (258, f + 1, 153)
    ctx['props'].append(('sedative', 262, f + 2, 152))
    # --- airlock -> clean corridor ---------------------------------------------------
    room(ctx, 272, 143, 275, 148, wall='cyan_stained_glass', ceil='smooth_quartz', name='lab.airlock')
    w.fill(271, f, 142, 276, f + 6, 142, WALL); w.fill(271, f, 149, 276, f + 6, 149, WALL)
    secure_door(ctx, 273, 149, 'south', (275, 149))
    w.set(274, f + 1, 149, WALL); w.set(274, f + 2, 149, WALL)
    secure_door(ctx, 273, 142, 'south', (275, 142))
    w.set(274, f + 1, 142, WALL); w.set(274, f + 2, 142, WALL)
    for z in (144, 147):
        w.set(272, f + 3, z, 'end_rod[facing=east]'); w.set(275, f + 3, z, 'end_rod[facing=west]')
    A['lab.airlock.s'] = (273, f + 1, 151)
    A['lab.airlock.n'] = (273, f + 1, 140)
    room(ctx, 200, 137, 276, 140, name='lab.c2')                          # corridor C2
    doorway(ctx, 273, 141, 273, 141)
    for i, x in enumerate(range(206, 276, 14)):
        A[f'lab.c2.{i}'] = (x, f + 1, 138)
    for x in range(204, 272, 8):
        w.set(x, f, 137, 'yellow_concrete'); w.set(x, f, 140, 'yellow_concrete')

    # --- core hall ---------------------------------------------------------------------
    hx0, hz0, hx1, hz1 = 214, 104, 254, 132
    room(ctx, hx0, hz0, hx1, hz1, h=9, name='lab.hall')
    doorway(ctx, 233, 133, 236, 136, hgt=4)
    for x in range(hx0, hx1 + 1):
        for z in range(hz0, hz1 + 1):
            if (x - hx0) % 8 == 0 or (z - hz0) % 7 == 0:
                w.set(x, f, z, 'smooth_stone')
    for (px, pz) in ((hx0 + 5, hz0 + 5), (hx1 - 5, hz0 + 5), (hx0 + 5, hz1 - 5), (hx1 - 5, hz1 - 5)):
        w.fill(px, f + 1, pz, px, f + 9, pz, 'quartz_pillar')
        w.set(px, f + 5, pz, 'pearlescent_froglight[axis=y]')
    # containment chamber
    kx0, kz0, kx1, kz1 = 229, 113, 239, 123
    for x in range(kx0 - 2, kx1 + 3):
        for z in range(kz0 - 2, kz1 + 3):
            if x in (kx0 - 2, kx1 + 2) or z in (kz0 - 2, kz1 + 2):
                w.set(x, f, z, 'yellow_concrete' if (x + z) % 2 else 'black_concrete')
    for yy in range(f + 1, f + 7):
        for x in range(kx0, kx1 + 1):
            for z in range(kz0, kz1 + 1):
                edge = x in (kx0, kx1) or z in (kz0, kz1)
                corner = x in (kx0, kx1) and z in (kz0, kz1)
                if corner:
                    w.set(x, yy, z, 'smooth_quartz')
                elif edge:
                    w.set(x, yy, z, 'cyan_stained_glass' if yy in (f + 1, f + 6) else 'glass')
    w.fill(kx0, f + 7, kz0, kx1, f + 7, kz1, 'smooth_quartz')
    w.fill(kx0 + 1, f, kz0 + 1, kx1 - 1, f, kz1 - 1, 'white_concrete')
    cxm, czm = (kx0 + kx1) // 2, (kz0 + kz1) // 2
    w.fill(cxm - 1, f + 1, czm - 1, cxm + 1, f + 1, czm + 1, 'smooth_quartz_slab[type=bottom]')
    w.set(cxm, f + 1, czm, 'smooth_quartz')
    w.set(cxm, f + 2, czm, 'recrafted:pathogen_core')
    w.fill(cxm, f + 4, czm, cxm, f + 6, czm, 'iron_bars')
    w.set(cxm, f + 7, czm, 'sea_lantern')
    for (dx, dz) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        w.set(cxm + dx, f + 1, czm + dz, 'verdant_froglight[axis=y]')
        w.set(cxm + dx, f + 2, czm + dz, 'lime_stained_glass')
    w.fill(cxm, f + 8, czm, cxm, f + 9, czm, 'iron_block')
    secure_door(ctx, cxm, kz1, 'south', (cxm + 1, kz1))
    w.set(cxm + 1, f + 2, kz1, 'recrafted:card_reader[tier=lab]')
    A['lab.core'] = (cxm, f + 1, czm + 2)
    A['lab.core.door'] = (cxm, f + 1, kz1 + 2)
    # consoles facing the chamber
    for i, (px, pz) in enumerate(((224, 127), (228, 128), (240, 128), (244, 127))):
        w.set(px, f + 1, pz, 'smooth_quartz'); w.set(px, f + 2, pz, 'recrafted:lab_console')
        A[f'lab.console{i}'] = (px, f + 1, pz + 1)
    w.set(234, f + 1, 128, 'smooth_quartz'); w.set(234, f + 2, 128, 'recrafted:purge_console')
    A['lab.purge'] = (234, f + 1, 129)
    # culture tanks along the north wall
    for i, tx in enumerate(range(hx0 + 3, hx1 - 2, 6)):
        w.fill(tx, f + 1, hz0, tx + 1, f + 5, hz0 + 1, 'lime_stained_glass')
        w.fill(tx, f + 2, hz0, tx + 1, f + 4, hz0, 'verdant_froglight[axis=y]')
        w.fill(tx, f + 6, hz0, tx + 1, f + 6, hz0 + 1, 'iron_block')
        A[f'lab.tank{i}'] = (tx, f + 1, hz0 + 3)
    for (bx, bz) in ((218, 118), (218, 124), (250, 118), (250, 124), (222, 109), (246, 109)):
        w.fill(bx, f + 1, bz, bx, f + 1, bz + 2, 'smooth_quartz')
        w.set(bx, f + 2, bz, rng.choice(['brewing_stand', 'candle[candles=1,lit=false]', 'water_cauldron[level=3]']))
        w.set(bx, f + 2, bz + 2, rng.choice(['brewing_stand', 'flower_pot', 'lantern[hanging=false]']))
    A['lab.bench.w'] = (219, f + 1, 120)
    A['lab.bench.e'] = (249, f + 1, 120)
    A['lab.hall.s'] = (234, f + 1, 131)
    A['lab.hall.nw'] = (220, f + 1, 108)
    A['lab.hall.ne'] = (248, f + 1, 108)
    A['lab.hall.w'] = (217, f + 1, 114)
    A['lab.hall.e'] = (251, f + 1, 114)
    w.set(hx1, f + 1, hz1, 'recrafted:hiding_crate')
    w.set(hx0, f + 1, hz1, 'recrafted:hiding_crate')
    ctx['props'].append(('fire_extinguisher', 216, f + 1, 131))
    ctx['props'].append(('syringe', 218, f + 2, 119))
    ctx['props'].append(('scalpel', 250, f + 2, 119))

    # --- side rooms ------------------------------------------------------------------------
    room(ctx, 196, 104, 210, 118, name='lab.wetlab')
    doorway(ctx, 211, 110, 213, 111)
    for z in range(105, 118, 3):
        w.fill(198, f + 1, z, 203, f + 1, z, 'smooth_quartz')
        w.set(199, f + 2, z, 'brewing_stand'); w.set(202, f + 2, z, rng.choice(['water_cauldron[level=3]', 'flower_pot']))
    A['lab.wetlab.bench'] = (201, f + 1, 109)
    ctx['props'].append(('lethal_poison', 200, f + 2, 108))
    ctx['props'].append(('emetic_poison', 201, f + 2, 114))
    room(ctx, 196, 121, 210, 132, wall='light_blue_concrete', floor='packed_ice', ceil='blue_ice', name='lab.cold')
    doorway(ctx, 211, 126, 213, 127)
    for x in range(197, 210, 3):
        w.fill(x, f + 1, 122, x, f + 3, 123, 'iron_block')
        w.fill(x, f + 1, 131, x, f + 3, 132, 'snow_block')
    room(ctx, 258, 104, 272, 116, floor='spruce_planks', name='lab.varga')
    doorway(ctx, 255, 110, 257, 111)
    w.fill(264, f + 1, 106, 268, f + 1, 106, 'dark_oak_planks')
    w.set(266, f + 1, 105, 'dark_oak_stairs[facing=north,half=bottom]')
    w.set(264, f + 2, 106, 'recrafted:drink[poison=none]')
    w.set(268, f + 2, 106, 'lantern[hanging=false]')
    w.fill(259, f + 1, 116, 263, f + 2, 116, 'bookshelf')
    w.set(271, f + 1, 105, 'white_bed[facing=north,part=foot]'); w.set(271, f + 1, 104, 'white_bed[facing=north,part=head]')
    w.set(259, f + 1, 105, 'recrafted:hiding_crate')
    A['lab.varga.desk'] = (266, f + 1, 105)
    A['lab.varga.sofa'] = (270, f + 1, 107)
    ctx['props'].append(('letter_opener', 266, f + 2, 106))
    room(ctx, 258, 120, 272, 132, wall='gray_concrete', floor='polished_deepslate', ceil='gray_concrete', name='lab.server')
    doorway(ctx, 255, 126, 257, 127)
    for x in range(260, 272, 3):
        for z in range(121, 132, 4):
            w.fill(x, f + 1, z, x, f + 3, z + 1, 'observer[facing=west]' if (x + z) % 2 else 'redstone_lamp[lit=true]')
    w.set(258, f + 2, 126, 'recrafted:fuse_box')
    A['lab.server.rack'] = (263, f + 1, 124)
    room(ctx, 222, 88, 246, 100, floor='rooted_dirt', wall='white_concrete', ceil='glowstone', lights=False,
         name='lab.greenhouse')
    doorway(ctx, 233, 101, 235, 103)
    for x in range(223, 246):
        for z in range(89, 100):
            if x % 3 and w.get(x, f + 1, z) == 0 and 232 > x or x > 236:
                w.set(x, f, z, 'coarse_dirt')
                w.set(x, f + 1, z, rng.choice(['dead_bush', 'wither_rose', 'fern', 'dead_bush', 'air', 'brown_mushroom']))
    A['lab.greenhouse.w'] = (228, f + 1, 96)
    ctx['props'].append(('garden_shears', 240, f + 1, 99))

    # --- maintenance hatch to the mine (west) ---------------------------------------------------
    doorway(ctx, 193, 110, 195, 110)
    secure_door(ctx, 195, 110, 'east', (195, 111))
    w.set(195, f + 2, 109, WALL)
    # --- sea cave + back stair (east) --------------------------------------------------------------
    cx0, cz0 = 276, 109
    stairwell(w, cx0, cz0, SEA + 1, f, 'stone_bricks', step='stone_brick', n=4)
    doorway(ctx, 273, 110, 275, 110)
    secure_door(ctx, 274, 110, 'east', (274, 111))
    w.set(273, f + 2, 109, WALL)
    A['lab.backstair.bottom'] = (277, f + 1, 110)
    # cavern with a dock
    dy = SEA + 1                                         # dock floor block
    for x in range(274, 318):
        for z in range(94, 108):
            for yy in range(56, 71):
                d = ((z - 100.5) / 7.0) ** 2 + ((yy - 62) / 8.5) ** 2
                if d <= 1.0 + rng.random() * .1 and x >= 276:
                    if yy <= SEA:
                        w.set(x, yy, z, 'water' if (x >= 285 and 97 <= z <= 104) else 'stone')
                    else:
                        w.set(x, yy, z, 'air')
    for x in range(276, 285):
        for z in range(95, 107):
            if w.get(x, dy + 1, z) == 0:
                w.set(x, dy, z, 'stone_bricks' if rng.random() < .7 else 'mossy_stone_bricks')
    for x in range(285, 296):
        for z in (96, 105):
            if w.get(x, dy + 1, z) == 0:
                w.set(x, dy, z, 'spruce_planks')
    w.clear(276, dy + 1, 107, 277, dy + 2, 108)
    w.fill(276, dy, 107, 277, dy, 108, 'stone_bricks')
    for (lx, lz) in ((278, 97), (283, 104), (290, 96), (294, 105)):
        if w.get(lx, dy + 1, lz) == 0:
            w.set(lx, dy + 1, lz, 'lantern[hanging=false]')
    from landmarks import boat
    boat(ctx, 287, 101, 9, 'x', beam=1, hull='dark_oak', stripe='gray', name='cave.boat')
    w.set(286, dy, 99, 'spruce_planks'); w.set(286, dy, 98, 'spruce_planks'); w.set(286, dy, 97, 'spruce_planks')
    w.set(287, dy + 1, 96, 'recrafted:exit_point')
    crate_stack(w, 279, dy + 1, 103, rng, 3)
    A['cave.dock'] = (281, dy + 1, 100)
    A['cave.stairs.top'] = (277, dy + 1, 110)
    ctx['props'].append(('outfit_security', 280, dy + 1, 96))
    ctx['zones'].append(dict(name='lab_service', box=[254, 36, 148, 294, 52, 196],
                             allow=['security', 'lab_guard', 'scientist', 'hazmat'], label='Halcyon facility — restricted'))
    ctx['zones'].append(dict(name='lab_clean', box=[192, 36, 84, 290, 52, 147],
                             allow=['lab_guard', 'hazmat', 'scientist'], label='Clean zone — protective suit required'))
    ctx['zones'].append(dict(name='sea_cave', box=[272, 56, 92, 300, 72, 114],
                             allow=['security', 'lab_guard', 'scientist', 'hazmat'], label='Private dock'))


def build(ctx):
    sewer(ctx)
    mine(ctx)
    lab(ctx)
    A, w = ctx['anchors'], ctx['w']
    # exit points on the surface
    fx, fy, fz = A['ferry.deck']
    w.set(fx, fy, fz + 4, 'recrafted:exit_point')
    px, py, pz = A['boat.patrol']
    w.set(px, py, pz + 5, 'recrafted:exit_point')
