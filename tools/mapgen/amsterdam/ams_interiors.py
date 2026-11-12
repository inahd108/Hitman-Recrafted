"""Hand-laid interiors for the buildings the contract happens in: the Gulden Hamer auction house,
the brown café on Zilversteeg and the forger's attic studio. Everything else uses the generic rooms
from ams_houses.interior()."""
from ams_layout import *  # noqa: F401,F403

CHECKER = ('quartz_bricks', 'polished_blackstone_bricks')


def chair(w, x, y, z, facing, wood='dark_oak'):
    """A seat facing the given way (the stair's back is behind the sitter)."""
    opp = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}[facing]
    w.set(x, y, z, f'{wood}_stairs[facing={opp}]')


def table(w, x, y, z, wood='dark_oak', top='white_carpet'):
    w.set(x, y, z, f'{wood}_fence')
    if top:
        w.set(x, y + 1, z, top if top.endswith('carpet') else f'{wood}_pressure_plate')


def lamp(w, x, y_ceiling, z, drop=1):
    """Hanging lantern under a ceiling block at y_ceiling."""
    for k in range(1, drop):
        w.set(x, y_ceiling - k, z, 'chain')
    w.set(x, y_ceiling - drop, z, 'lantern[hanging=true]')


def door(w, x, y, z, facing, wood='dark_oak', hinge='left'):
    w.set(x, y, z, f'{wood}_door[facing={facing},half=lower,hinge={hinge}]')
    w.set(x, y + 1, z, f'{wood}_door[facing={facing},half=upper,hinge={hinge}]')


def partition_x(w, x, y0, y1, z0, z1, mat, gaps=()):
    """A wall along z at x, with door gaps (z values)."""
    for z in range(z0, z1 + 1):
        for y in range(y0, y1 + 1):
            w.set(x, y, z, 'air' if z in gaps and y < y0 + 2 else mat)


def partition_z(w, z, y0, y1, x0, x1, mat, gaps=()):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            w.set(x, y, z, 'air' if x in gaps and y < y0 + 2 else mat)


# ---- the Gulden Hamer -----------------------------------------------------------------------------
def gulden_hamer(ctx):
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    x0, x1 = GULDEN_HAMER                       # outer walls at x0 and x1
    zf, zb = SOUTH_HOUSES[0], SOUTH_HOUSES[0] + 29   # front wall (two thick) and back wall
    f0, f1, f2 = FLOOR0, FLOOR0 + 5, FLOOR0 + 9      # ground, first, second floor blocks
    feet0, feet1 = f0 + 1, f1 + 1
    ix0, ix1 = x0 + 1, x1 - 1
    iz0, iz1 = zf + 2, zb - 1
    wall = 'smooth_quartz'
    panel = 'stripped_dark_oak_wood'
    # clear the shell's insides on the two lower storeys and lay the floors
    w.clear(ix0, feet0, iz0, ix1, f2 - 1, iz1)
    for x in range(ix0, ix1 + 1):
        for z in range(iz0, iz1 + 1):
            w.set(x, f0, z, CHECKER[(x + z) % 2])
    w.fill(ix0, f1, iz0, ix1, f1, iz1, 'dark_oak_planks')

    # cross corridor and saleroom front wall
    zc = zf + 15                                    # corridor row
    zs0 = zc + 2                                    # saleroom from here to the back wall
    xm = (x0 + x1) // 2
    partition_z(w, zc + 1, feet0, f1 - 1, ix0, ix1, panel, gaps=(xm - 1, xm, xm + 1))
    # hall, with the cloakroom to the west and the catering kitchen to the east
    xw, xe = xm - 6, xm + 6
    partition_x(w, xw, feet0, f1 - 1, iz0, zc - 1, panel, gaps=(zf + 9,))
    partition_x(w, xe, feet0, f1 - 1, iz0, zc - 1, panel, gaps=(zf + 11,))
    # reception desk inside the door
    for z in range(zf + 4, zf + 8):
        w.set(xw + 2, feet0, z, 'dark_oak_planks')
        w.set(xw + 2, feet0 + 1, z, 'dark_oak_slab')
    w.set(xw + 2, feet0 + 1, zf + 5, 'lectern[facing=east]')
    # security line inside the doors: a brass railing across the vestibule with the metal detector in it
    for x in range(xw + 1, xe):
        if x != xm:
            w.set(x, feet0, zf + 3, 'dark_oak_fence')
    w.set(xm, feet0, zf + 3, 'recrafted:metal_detector[facing=north,alarm=false]')
    w.set(xm, feet0 + 1, zf + 3, 'air')
    A['hamer.gate'] = (xm, feet0, zf + 4)
    A['hamer.reception'] = (xw + 3, feet0, zf + 6)
    A['hamer.reception.desk'] = (xw + 1, feet0, zf + 6)
    A['hamer.hall'] = (xm, feet0, zf + 5)
    # grand stair from the back of the hall up to the first floor, rising towards the front
    for i in range(5):
        z = zc - 1 - i
        for x in range(xm - 2, xm + 3):
            w.set(x, feet0 + i, z, 'dark_oak_stairs[facing=north]')
            if feet0 + i != f1:
                w.set(x, f1, z, 'air')                                  # stairwell, keeping the top step
        for x in (xm - 3, xm + 3):
            w.set(x, feet0 + i, z, 'dark_oak_planks')
            w.set(x, feet0 + i + 1, z, 'dark_oak_fence')
    A['hamer.stairs.foot'] = (xm, feet0, zc)
    A['hamer.landing'] = (xm, feet1, zc - 6)
    # chandelier in the hall
    lamp(w, xm, f1, zf + 5, 2)

    # cloakroom / porters' room: rails of coats (fences with banners would be entities; use wool)
    for z in range(iz0 + 1, zc - 1, 2):
        w.set(ix0, feet0, z, 'dark_oak_fence')
        w.set(ix0, feet0 + 1, z, rng.choice(['black_wool', 'gray_wool', 'brown_wool']))
    # stair down to the vault from the cloakroom
    vx0, vx1 = ix0 + 2, xw - 1
    vz0, vz1 = iz0 + 1, zc - 1
    vfloor = f0 - 7
    for i in range(7):
        z = iz0 + 1 + i
        y = f0 - i
        w.set(ix0, y, z, 'polished_blackstone_brick_stairs[facing=north]')
        w.set(ix0 + 1, y, z, 'polished_blackstone_brick_stairs[facing=north]')
        for yy in range(y + 1, y + 4):
            w.set(ix0, yy, z, 'air')
            w.set(ix0 + 1, yy, z, 'air')
    A['hamer.vault.stairs'] = (ix0, feet0, iz0)
    # the vault itself
    w.fill(ix0 - 1, vfloor - 1, iz0 - 1, xw, f0 - 1, zc, 'polished_blackstone_bricks')
    w.clear(ix0, vfloor + 1, iz0 + 7, xw - 1, f0 - 2, zc - 1)
    w.clear(ix0, vfloor + 1, iz0 + 1, ix0 + 1, f0 - 1, iz0 + 7)
    for i in range(7):
        z = iz0 + 1 + i
        y = f0 - i
        w.set(ix0, y, z, 'polished_blackstone_brick_stairs[facing=north]')
        w.set(ix0 + 1, y, z, 'polished_blackstone_brick_stairs[facing=north]')
    w.fill(ix0, vfloor, iz0 + 7, xw - 1, vfloor, zc - 1, 'polished_deepslate')
    for x in range(ix0 + 2, xw - 1, 2):                                       # display cases
        w.set(x, vfloor + 1, zc - 2, 'polished_blackstone_bricks')
        w.set(x, vfloor + 2, zc - 2, 'glass')
    w.set((ix0 + xw) // 2, vfloor + 3, iz0 + 9, 'light[level=11]')
    w.set(xw - 2, vfloor + 1, iz0 + 8, 'barrel[facing=up]')                     # the ledger's strongbox
    A['hamer.vault'] = ((ix0 + xw) // 2, vfloor + 1, iz0 + 10)
    A['hamer.vault.case'] = (ix0 + 3, vfloor + 1, zc - 3)
    A['hamer.vault.ledger'] = (xw - 2, vfloor + 1, iz0 + 9)

    # catering kitchen
    for z in range(iz0 + 1, zc - 1):
        w.set(ix1, feet0, z, rng.choice(['smoker[facing=west,lit=true]', 'furnace[facing=west,lit=false]', 'crafting_table',
                                          'water_cauldron[level=3]', 'barrel[facing=up]']))
    for z in range(iz0 + 3, zc - 3):
        w.set(xe + 3, feet0, z, 'smooth_stone_slab[type=top]' if z % 2 else 'iron_block')
    lamp(w, xe + 4, f1, zf + 7)
    A['hamer.kitchen'] = (xe + 2, feet0, zf + 7)
    A['hamer.kitchen.counter'] = (xe + 2, feet0, iz0 + 4)
    A['hamer.kitchen.tray'] = (xe + 4, feet0, zc - 2)

    # saleroom: double height (no first floor over it), rows of chairs facing the podium
    w.clear(ix0, f1, zs0, ix1, f2 - 1, iz1)
    for z in range(zs0 + 2, zs0 + 8):
        for x in list(range(ix0 + 3, xm - 2)) + list(range(xm + 3, ix1 - 2)):
            if (x - ix0) % 1 == 0:
                chair(w, x, feet0, z, 'south', 'dark_oak')
    A['hamer.saleroom'] = (xm, feet0, zs0 + 1)
    A['hamer.saleroom.door'] = (xm, feet0, zc)
    for i, z in enumerate(range(zs0 + 2, zs0 + 8)):
        A[f'hamer.row{i}.w'] = (ix0 + 3, feet0, z)
        A[f'hamer.row{i}.e'] = (ix1 - 3, feet0, z)
    # podium against the back wall
    for x in range(xm - 4, xm + 5):
        for z in (iz1 - 1, iz1):
            w.set(x, feet0, z, 'dark_oak_slab[type=bottom]')
    w.set(xm, feet0 + 1, iz1 - 1, 'lectern[facing=north]')
    A['hamer.podium'] = (xm, feet0 + 1, iz1)
    for x in (xm - 4, xm + 4):                                               # easels for the lots
        w.set(x, feet0 + 1, iz1, 'dark_oak_fence')
        w.set(x, feet0 + 2, iz1, 'white_wool')
    # the chandelier over the podium: the auctioneer stands right under it. Its rope runs to a winch
    # on the press balcony; let it go and it comes down on whoever is at the lectern.
    for y in range(f2 - 1, f2 - 4, -1):
        w.set(xm, y, iz1, 'chain')
    w.set(xm, f2 - 4, iz1, 'recrafted:chandelier')
    A['hamer.chandelier'] = (xm, f2 - 4, iz1)
    # press balcony along the saleroom's front wall at first-floor level
    for x in range(ix0, ix1 + 1):
        w.set(x, f1, zs0, 'dark_oak_planks')
        w.set(x, f1, zs0 + 1, 'dark_oak_planks')
        w.set(x, feet1, zs0 + 1, 'dark_oak_fence')
    A['hamer.balcony'] = (xm - 6, feet1, zs0)
    w.set(xm + 3, feet1, zs0, 'recrafted:winch')
    A['hamer.winch'] = (xm + 3, feet1, zs0)
    for x in range(ix0 + 4, ix1 - 3, 6):
        w.set(x, f2 - 1, (zs0 + iz1) // 2, 'lantern[hanging=true]')
    # garden door in the back wall, west corner
    w.set(ix0 + 1, feet0, zb, 'air')
    w.set(ix0 + 1, feet0 + 1, zb, 'air')
    door(w, ix0 + 1, feet0, zb, 'south')
    A['hamer.garden.door'] = (ix0 + 1, feet0, zb - 1)
    A['hamer.corridor.w'] = (ix0 + 2, feet0, zc)
    A['hamer.corridor.e'] = (ix1 - 2, feet0, zc)

    # first floor over the front half: Ostendorp's office (west), viewing room (east), gallery between
    partition_x(w, xw, feet1, f2 - 1, iz0, zs0 - 1, panel, gaps=(zf + 8,))
    partition_x(w, xe, feet1, f2 - 1, iz0, zs0 - 1, panel, gaps=(zf + 8,))
    # office: desk, chair, bookshelves, safe
    w.fill(ix0, feet1, iz0 + 1, ix0, feet1 + 2, zs0 - 2, 'bookshelf')
    for x in range(ix0 + 3, ix0 + 6):
        w.set(x, feet1, zf + 6, 'dark_oak_planks')
        w.set(x, feet1 + 1, zf + 6, 'dark_oak_slab')
    chair(w, ix0 + 4, feet1, zf + 7, 'north')
    w.set(ix0 + 1, feet1, zs0 - 2, 'iron_block')
    w.set(ix0 + 1, feet1 + 1, zs0 - 2, 'iron_trapdoor[facing=east,half=top]')
    w.fill(ix0 + 2, feet1, iz0 + 1, xw - 2, feet1, zs0 - 3, 'red_carpet')
    lamp(w, ix0 + 4, f2, zf + 5)
    A['hamer.office'] = (ix0 + 4, feet1, zf + 9)
    A['hamer.office.desk'] = (ix0 + 4, feet1, zf + 7)
    A['hamer.office.safe'] = (ix0 + 2, feet1, zs0 - 2)
    # private viewing room: two sofas, an easel with tonight's lot
    for x in range(xe + 2, xe + 5):
        chair(w, x, feet1, iz0 + 2, 'south', 'spruce')
        chair(w, x, feet1, iz0 + 6, 'north', 'spruce')
    w.set(ix1 - 1, feet1, iz0 + 4, 'dark_oak_fence')
    w.set(ix1 - 1, feet1 + 1, iz0 + 4, 'white_wool')
    w.fill(xe + 1, feet1, iz0 + 1, ix1, feet1, zs0 - 2, 'blue_carpet')
    lamp(w, xe + 4, f2, iz0 + 4)
    table(w, xe + 5, feet1, iz0 + 4, 'dark_oak', top='')
    w.set(xe + 5, feet1 + 1, iz0 + 4, 'recrafted:drink[poison=none]')     # her champagne
    A['hamer.viewing'] = (xe + 3, feet1, iz0 + 4)
    A['hamer.viewing.easel'] = (ix1 - 2, feet1, iz0 + 4)
    # gallery between them: easels with paintings on show
    for z in range(iz0 + 1, zs0 - 1, 3):
        for x in (xw + 1, xe - 1):
            w.set(x, feet1, z, 'dark_oak_fence')
            w.set(x, feet1 + 1, z, rng.choice(['white_wool', 'light_gray_wool', 'yellow_wool']))
    lamp(w, xm, f2, zf + 6)
    A['hamer.gallery'] = (xm, feet1, zf + 6)
    # lights over the hall
    for x in (xm - 4, xm + 4):
        w.set(x, f1 - 1, zf + 4, 'lantern[hanging=true]')
    return A


# ---- the brown café on Zilversteeg -----------------------------------------------------------------
def cafe(ctx, info):
    """In de Gouden Ton: a dark panelled bar along one side, small tables, barrels over the bar."""
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    fr = info['frame']
    W, D = fr.W, fr.D
    y = info['base'] + 1
    top = info['levels'][1] if len(info['levels']) > 1 else info['top']
    # clear the generic ground floor, panel it
    fr.fill(1, y, 2, W - 2, top - 1, D - 2, 'air')
    fr.fill(1, info['base'], 2, W - 2, info['base'], D - 2, 'dark_oak_planks')
    for v in range(2, D - 1):
        fr.set(0, y, v, 'stripped_dark_oak_log[axis=y]')
        fr.set(W - 1, y, v, 'stripped_dark_oak_log[axis=y]')
    # bar counter along the right wall with stools; barrels stacked behind
    R = W - 2
    for v in range(4, D - 3):
        fr.set(R - 1, y, v, 'dark_oak_planks')
        fr.set(R - 1, y + 1, v, 'dark_oak_slab')
        fr.set(R, y + 1, v, 'barrel[facing=west]')
        fr.set(R, y + 2, v, 'barrel[facing=west]')
        if v % 2 == 0:
            fr.set(R - 2, y, v, 'dark_oak_fence')
    # tables by the windows
    for v in (3, 6, 9):
        if v < D - 3:
            fr.set(2, y, v, 'spruce_fence')
            fr.set(2, y + 1, v, 'brown_carpet')
            fr.set(1, y, v, 'spruce_stairs[facing={L}]')
    for v in range(3, D - 3, 3):
        fr.set(W // 2, top - 1, v, 'lantern[hanging=true]')
    # kitchen at the back
    fr.set(R, y, D - 2, 'smoker[facing=north,lit=true]')
    fr.set(R - 1, y, D - 2, 'barrel[facing=up]')
    A['cafe.door'] = info['door']
    A['cafe.bar'] = fr.pos(R - 2, y, (D - 1) // 2)
    A['cafe.behind_bar'] = fr.pos(R, y, 3)
    A['cafe.table1'] = fr.pos(2, y, 4)
    A['cafe.table2'] = fr.pos(2, y, 7)
    A['cafe.kitchen'] = fr.pos(R - 1, y, D - 3)
    A['cafe.stairs'] = fr.pos(2, y, D - 3)
    A['cafe.backroom'] = fr.pos(W // 2, info['levels'][1] + 1, D // 2) if len(info['levels']) > 1 else A['cafe.bar']
    bx, by, bz = A['cafe.backroom']
    for dx in (1, -1, 2, -2):                                    # the wage book on the manager's cabinet
        here = w.name(w.get(bx + dx, by, bz))
        if (here.endswith('air') or here.endswith('carpet')) and w.is_air(bx + dx, by + 1, bz):
            w.set(bx + dx, by, bz, 'recrafted:wage_book')
            A['cafe.wage_book'] = (bx + dx, by, bz)
            if w.name(w.get(bx + dx, by, bz + 1)).endswith(('air', 'carpet')):
                chair(w, bx + dx, by, bz + 1, 'north', 'spruce')
            break


# ---- the forger's attic studio --------------------------------------------------------------------
def studio(ctx, info):
    """Top two storeys of the forger's house: four easels, a stove, pigments, the hoist door to the quay."""
    w, rng, A = ctx['w'], ctx['rng'], ctx['anchors']
    fr = info['frame']
    W, D = fr.W, fr.D
    ly = info['levels'][-1]
    y = ly + 1
    # easels in a row facing the windows
    for i, v in enumerate((3, 5, 7, 9)):
        u = 2 + (i % 2)
        fr.set(u, y, v, 'dark_oak_fence')
        fr.set(u, y + 1, v, 'white_wool')
        A[f'studio.easel{i}'] = fr.pos(u, y, v + 1)
    fr.set(W - 2, y, D - 3, 'smoker[facing={L},lit=true]')
    for v in range(3, D - 4, 2):
        fr.set(W - 2, y, v, rng.choice(['brewing_stand', 'decorated_pot', 'flower_pot', 'cauldron']))
    for v in (4, 8, 12):
        fr.set(W // 2, y + 2, v, 'lantern[hanging=true]')
    fr.set(1, y + 2, 6, 'light[level=12]')
    A['studio.stove'] = fr.pos(W - 2, y, D - 4)
    A['studio'] = fr.pos(W // 2, y, D // 2)
    A['studio.window'] = fr.pos(W // 2, y, 2)
    fr.set(W // 2 + 1, y, 2, 'spruce_fence')
    fr.set(W // 2 + 1, y + 1, 2, 'recrafted:drink[poison=none]')            # his cup of tea, by the window
    fr.set(W - 2, y, 2, 'recrafted:winch')
    A['studio.winch'] = fr.pos(W - 2, y, 2)
    # a crate of "lead white" on the hoist rope, hanging over the quay in front of the door
    u = (W - 1) // 2
    hx, hy, hz = fr.pos(u, info['top'] + 2, -1)
    w.set(hx, hy, hz, 'chain')
    w.set(hx, hy - 1, hz, 'barrel[facing=up]')
    y0 = hy - 2
    while y0 > STREET and w.is_air(hx, y0, hz):
        y0 -= 1
    A['forger.crate'] = (hx, hy - 1, hz)
    A['forger.quay'] = (hx, y0 + 1, hz)
    A['studio.hoist'] = fr.pos((W - 1) // 2, info['top'] + 1, 2)
