"""Canal houses: a facade grammar for narrow brick houses with Amsterdam gables.

A house is built in a Frame (u along the facade, v into the lot, front = the street side):
    - the front wall is two blocks thick so windows sit in a recess, the rest one block;
    - ground floor 5 high, upper floors 4 high, then a gable over the attic;
    - gables: spout, step, neck, bell or cornice (the last with a roof parallel to the street);
    - a hoist beam and loading door at the top of every gabled house;
    - invisible light blocks behind most windows so the city glows at dusk.
"""
from core import Frame
from ams_layout import FLOOR0, STREET

# wall block, matching stair block
BRICK = {
    'red': ('bricks', 'brick_stairs'),
    'dark': ('nether_bricks', 'nether_brick_stairs'),
    'plum': ('red_nether_bricks', 'red_nether_brick_stairs'),
    'black': ('polished_blackstone_bricks', 'polished_blackstone_brick_stairs'),
    'tan': ('mud_bricks', 'mud_brick_stairs'),
    'white': ('smooth_quartz', 'smooth_quartz_stairs'),
}
BRICK_WEIGHTS = [('red', 30), ('dark', 18), ('plum', 14), ('black', 14), ('tan', 12), ('white', 6)]
TRIM = {
    'white': ('smooth_quartz', 'smooth_quartz_stairs', 'smooth_quartz_slab'),
    'stone': ('smooth_sandstone', 'smooth_sandstone_stairs', 'smooth_sandstone_slab'),
}
DOORS = ['dark_oak', 'warped', 'crimson', 'spruce', 'dark_oak', 'warped']
ROOFS = {'slate': ('deepslate_tile_stairs', 'deepslate_tile_slab', 'deepslate_tiles'),
         'tile': ('brick_stairs', 'brick_slab', 'bricks')}
FLOOR_MATS = ['spruce_planks', 'dark_oak_planks', 'oak_planks', 'polished_andesite']

GABLES_BY_STREET = {
    'grand': [('cornice', 34), ('neck', 24), ('bell', 26), ('step', 10), ('spout', 0)],
    'canal': [('bell', 30), ('neck', 26), ('step', 18), ('cornice', 16), ('spout', 10)],
    'lane': [('spout', 26), ('step', 22), ('bell', 22), ('neck', 18), ('cornice', 12)],
}


WINDOW = 'recrafted:canal_window'


def window(fr, rng, lit, side='front'):
    """Sash window block state for a facade of this frame. side: 'front' faces F/B, 'side' faces L/R."""
    along_z = fr.front in ('north', 'south')
    if side == 'side':
        along_z = not along_z
    return f'{WINDOW}[axis={"z" if along_z else "x"},lit={"true" if rng.random() < lit else "false"}]'


def pick(rng, weighted):
    return rng.choices([k for k, _ in weighted], [w for _, w in weighted])[0]


def bays(W):
    """Window columns across an odd-width facade: every other column, starting one in."""
    return list(range(1, W - 1, 2))


class Style:
    def __init__(self, rng, street='canal', **over):
        self.brick = pick(rng, BRICK_WEIGHTS)
        self.trim = 'stone' if self.brick in ('red', 'dark') and rng.random() < .35 else 'white'
        self.gable = pick(rng, GABLES_BY_STREET[street])
        self.door = rng.choice(DOORS)
        self.roof = 'slate' if rng.random() < .7 else 'tile'
        self.floor = rng.choice(FLOOR_MATS)
        self.lit = rng.uniform(.55, .9)
        self.hoist = True
        self.shop = None          # wool colour for a shop awning, or None
        self.__dict__.update(over)


def canal_house(ctx, x0, z0, x1, z1, front, floors, st, base=FLOOR0, side_windows=(), name=None):
    """Build one house. Returns an info dict with its frame and useful anchors."""
    w, rng = ctx['w'], ctx['rng']
    fr = Frame(w, x0, z0, x1, z1, front)
    W, D = fr.W, fr.D
    wall, wall_st = BRICK[st.brick]
    tb, tst, tsl = TRIM[st.trim]
    heights = [5] + [4] * (floors - 1)
    levels, y = [], base
    for h in heights:
        levels.append(y)
        y += h
    top = y                                      # attic floor / cornice line

    fr.fill(0, base, 0, W - 1, top + 18, D - 1, 'air')
    fr.fill(0, STREET - 3, 0, W - 1, base - 1, D - 1, 'stone_bricks')
    fr.fill(0, base, 0, W - 1, base, D - 1, st.floor)
    # walls
    fr.fill(0, base + 1, 0, W - 1, top, 1, wall)
    fr.fill(0, base + 1, D - 1, W - 1, top, D - 1, wall)
    fr.fill(0, base + 1, 0, 0, top, D - 1, wall)
    fr.fill(W - 1, base + 1, 0, W - 1, top, D - 1, wall)
    fr.fill(0, base, 0, W - 1, base, 0, 'polished_andesite')            # hardstone plinth
    for ly in levels[1:] + [top]:
        fr.fill(1, ly, 2, W - 2, ly, D - 2, 'spruce_planks')
    info = dict(name=name, frame=fr, base=base, top=top, levels=levels, W=W, D=D, style=st)

    # ---- front openings -------------------------------------------------------------
    B = bays(W)
    door_u = B[0] if W <= 7 and rng.random() < .5 else B[-1] if W <= 7 else B[len(B) // 2]
    info['door'] = fr.pos(door_u, base + 1, -1)
    for li, ly in enumerate(levels):
        for u in B:
            if li == 0 and u == door_u:
                fr.set(u, ly + 1, 0, 'air')
                fr.set(u, ly + 2, 0, 'air')
                fr.set(u, ly + 3, 0, 'air')
                fr.set(u, ly + 1, 1, f'{st.door}_door[facing={{F}},half=lower,hinge=left]')
                fr.set(u, ly + 2, 1, f'{st.door}_door[facing={{F}},half=upper,hinge=left]')
                fr.set(u, ly + 3, 0, window(fr, rng, 1.0))                   # fanlight over the door
                fr.set(u, ly, -1, f'stone_brick_stairs[facing={{B}}]')
                continue
            rows = (ly + 2, ly + 3) if li == 0 else (ly + 1, ly + 2)
            pane = window(fr, rng, st.lit)                                   # one state per window, both rows
            for yy in rows:
                fr.set(u, yy, 0, pane)                                       # flush: recesses hide them along a canal
                fr.set(u, yy, 1, 'air')
            if li > 0:
                fr.set(u, rows[-1] + 1, 0, f'{tsl}[type=top]')               # white lintel
            if st.shop and li == 0:
                fr.set(u, ly + 1, 0, pane)
                fr.set(u, ly + 1, 1, 'air')
    if st.shop:
        for u in range(0, W):
            fr.set(u, base + 4, -1, f'{st.shop}_wool' if u % 2 == 0 else 'white_wool')

    # ---- side windows where the house stands alone ------------------------------------
    for side in side_windows:
        uu = 0 if side == 'L' else W - 1
        for ly in levels:
            for v in range(3, D - 2, 3):
                pane = window(fr, rng, st.lit, 'side')
                fr.set(uu, ly + 1, v, pane)
                fr.set(uu, ly + 2, v, pane)

    # ---- back wall windows ------------------------------------------------------------
    for ly in levels:
        for u in B:
            if rng.random() < .7:
                pane = window(fr, rng, st.lit * .8)
                fr.set(u, ly + 1, D - 1, pane)
                fr.set(u, ly + 2, D - 1, pane)

    # ---- gable and roof ---------------------------------------------------------------
    if st.gable == 'cornice':
        roof_parallel(fr, W, D, top, st, wall)
        cornice(fr, W, top, st, wall, rng)
        info['apex'] = top + 4
    else:
        roof_perpendicular(fr, W, D, top, st, wall, wall_st)
        info['apex'] = GABLES[st.gable](fr, W, top, wall, wall_st, st, rng)
    if rng.random() < .5:                                                   # chimney
        cu = 0 if rng.random() < .5 else W - 1
        cv = D // 2 + rng.randint(-2, 2)
        h = top + (W - 1) // 2 + 2
        for yy in range(top + 1, h + 1):
            fr.set(cu, yy, cv, wall)
        fr.set(cu, h + 1, cv, 'stone_brick_slab')
    return info


# ---- roofs --------------------------------------------------------------------------------
def roof_perpendicular(fr, W, D, top, st, wall, wall_st):
    """Pitched roof whose ridge runs from the front gable to the back (the usual canal house)."""
    rst, rsl, rfull = ROOFS[st.roof]
    R = (W - 1) // 2
    for v in range(2, D - 1):
        for k in range(R):
            fr.set(k, top + 1 + k, v, f'{rst}[facing={{R}}]')
            fr.set(W - 1 - k, top + 1 + k, v, f'{rst}[facing={{L}}]')
        fr.set(R, top + 1 + R, v, rsl)
    # back gable: plain brick triangle
    for k in range(R + 1):
        fr.fill(k, top + 1 + k, D - 1, W - 1 - k, top + 1 + k, D - 1, wall)
        if k < R:
            fr.set(k, top + 1 + k, D - 1, f'{wall_st}[facing={{R}}]')
            fr.set(W - 1 - k, top + 1 + k, D - 1, f'{wall_st}[facing={{L}}]')


def roof_parallel(fr, W, D, top, st, wall):
    """Roof whose ridge runs along the street, behind a cornice."""
    rst, rsl, rfull = ROOFS[st.roof]
    rise = min((D - 2) // 2, 5)
    for k in range(rise):
        fr.fill(0, top + 1 + k, 2 + k, W - 1, top + 1 + k, 2 + k, f'{rst}[facing={{B}}]')
        fr.fill(0, top + 1 + k, D - 1 - k, W - 1, top + 1 + k, D - 1 - k, f'{rst}[facing={{F}}]')
        fr.set(0, top + 1 + k, 3 + k, wall)
    fr.fill(0, top + 1 + rise, 2 + rise, W - 1, top + 1 + rise, D - 1 - rise, rsl)
    for k in range(rise):                                                  # end walls
        fr.fill(0, top + 1 + k, 3 + k, 0, top + 1 + k, D - 2 - k, wall)
        fr.fill(W - 1, top + 1 + k, 3 + k, W - 1, top + 1 + k, D - 2 - k, wall)


# ---- gables (front facade above the cornice line); each returns the apex y -----------------
def _hoist(fr, u, y, st):
    """Loading door two high with the hoist beam and its chain above."""
    fr.set(u, y, 0, 'air')
    fr.set(u, y + 1, 0, 'air')
    fr.set(u, y, 1, 'dark_oak_door[facing={F},half=lower,hinge=left]')
    fr.set(u, y + 1, 1, 'dark_oak_door[facing={F},half=upper,hinge=left]')
    if st.hoist:
        fr.set(u, y + 2, -1, 'dark_oak_fence')
        fr.set(u, y + 1, -1, 'chain')


def gable_spout(fr, W, top, wall, wall_st, st, rng):
    tb, tst, tsl = TRIM[st.trim]
    R = (W - 1) // 2
    for k in range(R + 1):
        y = top + 1 + k
        fr.fill(k, y, 0, W - 1 - k, y, 1, wall)
        if k < R:
            fr.set(k, y, 0, f'{wall_st}[facing={{R}}]')
            fr.set(W - 1 - k, y, 0, f'{wall_st}[facing={{L}}]')
    fr.set(R, top + 2 + R, 0, tsl)
    if R >= 2:
        _hoist(fr, R, top + 1, st)
    return top + 2 + R


def gable_step(fr, W, top, wall, wall_st, st, rng):
    tb, tst, tsl = TRIM[st.trim]
    s, y = 0, top + 1
    while W - 2 * s >= 1:
        lo, hi = s, W - 1 - s
        for k in range(2):
            fr.fill(lo, y + k, 0, hi, y + k, 1, wall)
        if W - 2 * (s + 1) >= 1:
            fr.set(lo, y + 2, 0, f'{tsl}')                                   # coping on the step
            fr.set(hi, y + 2, 0, f'{tsl}')
        s, y = s + 1, y + 2
    fr.set((W - 1) // 2, y, 0, tb)
    fr.set((W - 1) // 2, y + 1, 0, f'{tsl}')
    _hoist(fr, (W - 1) // 2, top + 1, st)
    return y + 1


def gable_neck(fr, W, top, wall, wall_st, st, rng):
    tb, tst, tsl = TRIM[st.trim]
    mid = (W - 1) // 2
    nl, nr = (2, W - 3) if W >= 7 else (1, W - 2)
    for k in range(2):
        fr.fill(0, top + 1 + k, 0, W - 1, top + 1 + k, 1, wall)
    y = top + 3
    # shoulders with scrolls
    fr.set(nl - 1, y, 0, f'{tst}[facing={{R}}]')
    fr.set(nr + 1, y, 0, f'{tst}[facing={{L}}]')
    if nl >= 2:
        fr.set(0, y, 0, tsl)
        fr.set(W - 1, y, 0, tsl)
    neck_h = 4
    for k in range(neck_h):
        fr.fill(nl, y + k, 0, nr, y + k, 1, wall)
        fr.set(nl, y + k, 0, tb)
        fr.set(nr, y + k, 0, tb)
    y += neck_h
    # pediment
    fr.set(nl, y, 0, f'{tst}[facing={{R}}]')
    fr.set(nr, y, 0, f'{tst}[facing={{L}}]')
    for u in range(nl + 1, nr):
        fr.set(u, y, 0, tb)
    fr.set(mid, y + 1, 0, tsl)
    _hoist(fr, mid, top + 4, st)
    return y + 1


def gable_bell(fr, W, top, wall, wall_st, st, rng):
    tb, tst, tsl = TRIM[st.trim]
    mid = (W - 1) // 2
    widths = []
    half = mid
    while half >= 1:
        widths += [half, half]
        half -= 1
    widths += [1] if W >= 7 else []
    y = top + 1
    for i, hw in enumerate(widths):
        lo, hi = mid - hw, mid + hw
        fr.fill(lo, y, 0, hi, y, 1, wall)
        narrower = i + 1 < len(widths) and widths[i + 1] < hw
        fr.set(lo, y, 0, f'{tst}[facing={{R}}]' if narrower else tb)
        fr.set(hi, y, 0, f'{tst}[facing={{L}}]' if narrower else tb)
        y += 1
    fr.set(mid, y, 0, tb)
    fr.set(mid, y + 1, 0, f'{tst}[facing={{F}},half=top]')
    _hoist(fr, mid, top + 3, st)
    return y + 1


GABLES = {'spout': gable_spout, 'step': gable_step, 'neck': gable_neck, 'bell': gable_bell}


def cornice(fr, W, top, st, wall, rng):
    """Straight top with an overhanging white cornice and, on wider houses, a dormer with the hoist."""
    tb, tst, tsl = TRIM[st.trim]
    fr.fill(0, top, -1, W - 1, top, -1, f'{tst}[facing={{B}},half=top]')
    fr.fill(0, top + 1, 0, W - 1, top + 1, 1, wall)
    fr.fill(0, top + 2, 0, W - 1, top + 2, 0, tsl)
    mid = (W - 1) // 2
    if W >= 9:
        for k in range(3):
            fr.fill(mid - 1, top + 2 + k, 1, mid + 1, top + 2 + k, 1, wall)
        fr.set(mid - 1, top + 5, 1, f'{tst}[facing={{R}}]')
        fr.set(mid + 1, top + 5, 1, f'{tst}[facing={{L}}]')
        fr.set(mid, top + 5, 1, tb)
        fr.set(mid, top + 2, 0, 'air')
        fr.set(mid, top + 3, 0, 'air')
        fr.set(mid, top + 2, 1, 'dark_oak_door[facing={F},half=lower,hinge=left]')
        fr.set(mid, top + 3, 1, 'dark_oak_door[facing={F},half=upper,hinge=left]')
        if st.hoist:
            fr.set(mid, top + 4, 0, 'dark_oak_fence')
            fr.set(mid, top + 4, -1, 'dark_oak_fence')
            fr.set(mid, top + 3, -1, 'chain')


# ---- rows ---------------------------------------------------------------------------------
def split_lots(rng, a, b, widths=(5, 7, 7, 9, 9, 11), big=None):
    """Cut [a, b] into odd-width lots. big = (probability, widths) for double houses."""
    lots, x = [], a
    while x <= b:
        left = b - x + 1
        if big and rng.random() < big[0]:
            cand = [wd for wd in big[1] if wd <= left]
        else:
            cand = [wd for wd in widths if wd <= left]
        if not cand:
            cand = [left] if left >= 3 else []
            if not cand:
                break
        wd = rng.choice(cand)
        if left - wd in (1, 2, 3, 4) and left >= 5:
            wd = left if left % 2 == 1 and left <= 13 else wd
        lots.append((x, x + wd - 1))
        x += wd
    return lots


def row_x(ctx, a, b, z0, z1, front, street='canal', floors=(3, 5), big=None, skip=(), **style_over):
    """A row of houses along x. front 'north' or 'south'."""
    rng = ctx['rng']
    out = []
    for (x0, x1) in split_lots(rng, a, b, big=big):
        if any(not (x1 < s0 or x0 > s1) for s0, s1 in skip):
            continue
        st = Style(rng, street, **style_over)
        if x1 - x0 + 1 >= 13 and st.gable in ('step', 'spout'):
            st.gable = 'cornice'
        f = rng.randint(*floors) + (1 if x1 - x0 + 1 >= 13 else 0)
        out.append(canal_house(ctx, x0, z0, x1, z1, front, f, st))
    return out


def row_z(ctx, a, b, x0, x1, front, street='canal', floors=(3, 5), **style_over):
    """A row of houses along z. front 'east' or 'west'."""
    rng = ctx['rng']
    out = []
    for (z0, z1) in split_lots(rng, a, b):
        st = Style(rng, street, **style_over)
        f = rng.randint(*floors)
        out.append(canal_house(ctx, x0, z0, x1, z1, front, f, st))
    return out
