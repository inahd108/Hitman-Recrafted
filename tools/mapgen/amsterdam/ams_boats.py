"""Boats, the drawbridge and the lock as working machinery for Oil & Water.

Everything a boat needs is laid down here: Kooistra's houseboat on the Gildegracht, the goods crane where the
Zwaluw waits for the bridge, the bridge keeper's booth and the lock keeper's wheel, the gate definitions
(blocks a gate sets when it opens), the water routes with rounded corners, and the boat crews.

All boat traffic goes round the same way, so no two boats ever meet head on:
  Gildegracht eastbound -> east canal northbound -> (tour boats) Touwslagersgracht westbound -> west canal southbound
  (the Zwaluw goes on north from the east canal to the smuggler's dock and the IJ, then south through the lock).
"""
import math

from ams_layout import *  # noqa: F401,F403
import ams_water

Y_BOAT = WATER + .5                 # boat origin: the hull course straddles the surface, the deck is at WATER + 1
INNER_LANE = 202.5
OUTER_LANE = 103.5
W_LANE = 32.5
E_LANE = 350.5
IJ_LANE = 11.5
HOME = (158.5, 197.5)               # the Zwaluw tied up alongside Kooistra's houseboat
CRANE_X = 284                       # goods crane on the Gildegracht south quay, west of the drawbridge
DOCK = (349.5, 71.5)


# ---- structures ------------------------------------------------------------------------------------
def kooistra_houseboat(ctx):
    w = ctx['w']
    x, z0 = 152, INNER[0]
    ams_water.houseboat(ctx, x, z0, 14, 5, ctx['rng'], name='kooistra_houseboat', hull='black_concrete',
                        cabin='dark_oak_planks', quay='north')
    zc = z0 + 2
    A = ctx['anchors']
    A['kooistra.houseboat'] = (x + 3, WATER + 2, zc)
    w.set(x + 5, WATER + 2, zc, 'barrel[facing=up]')                          # his bottle of jenever
    w.set(x + 5, WATER + 3, zc, 'recrafted:drink[poison=none]')
    A['kooistra.landing'] = (x + 6, WATER + 2, z0 + 4)                       # the south rail, where the Zwaluw ties up


def crane(ctx):
    """A timber goods crane on the south quay; its crate hangs right over where the Zwaluw waits for the bridge."""
    w, A = ctx['w'], ctx['anchors']
    x, zq = CRANE_X, INNER[1] + 2
    zc = 208
    for y in range(STREET + 1, STREET + 10):
        w.set(x, y, zq, 'stripped_spruce_log[axis=y]')
    for z in range(zc, zq + 2):
        w.set(x, STREET + 10, z, 'stripped_spruce_log[axis=z]')
    w.set(x, STREET + 9, zq - 1, 'spruce_trapdoor[facing=south,half=top]')
    w.set(x, STREET + 9, zq + 1, 'spruce_trapdoor[facing=north,half=top]')
    for y in range(STREET + 4, STREET + 10):
        w.set(x, y, zc, 'chain')
    w.set(x, STREET + 3, zc, 'barrel[facing=up]')
    w.set(x + 1, STREET + 1, zq + 1, 'recrafted:winch')
    A['crane.crate'] = (x, STREET + 3, zc)
    A['crane.winch'] = (x + 1, STREET + 1, zq + 1)
    A['crane.wait'] = (x + .5, zc + .5)


def booth(ctx):
    """The bridge keeper's booth beside the drawbridge, with the lever that holds the bridge down."""
    w, A = ctx['w'], ctx['anchors']
    x0, z0 = DRAWBRIDGE[0] - 7, INNER_S_QUAY[0] + 4
    x1, z1 = x0 + 3, z0 + 3
    w.fill(x0, STREET + 1, z0, x1, STREET + 3, z1, 'white_concrete')
    w.fill(x0 + 1, STREET + 1, z0 + 1, x1 - 1, STREET + 3, z1 - 1, 'air')
    w.fill(x0, STREET + 4, z0, x1, STREET + 4, z1, 'dark_oak_slab')
    for x in (x0 + 1, x1 - 1):
        w.set(x, STREET + 2, z1, 'glass_pane')
    w.set(x0, STREET + 2, z0 + 1, 'glass_pane')
    w.set(x0, STREET + 2, z0 + 2, 'glass_pane')
    w.set(x0 + 1, STREET + 1, z0, 'birch_door[facing=north,half=lower,hinge=left]')
    w.set(x0 + 1, STREET + 2, z0, 'birch_door[facing=north,half=upper,hinge=left]')
    w.set(x0 + 2, STREET + 1, z1 - 1, 'recrafted:bridge_control')
    w.set(x0 + 2, STREET + 3, z0 + 1, 'light[level=12]')
    A['drawbridge.booth'] = (x0 + 1, STREET + 1, z0 + 2)
    A['drawbridge.lever'] = (x0 + 2, STREET + 1, z1 - 1)


def lock_wheel(ctx):
    w, A = ctx['w'], ctx['anchors']
    kx, ky, kz = A['lock.keeper']
    w.set(kx + 2, ky, kz, 'recrafted:lock_control')
    A['lock.wheel'] = (kx + 2, ky, kz)


# ---- gates -------------------------------------------------------------------------------------------------
def gates(ctx):
    w = ctx['w']
    out = []
    # drawbridge: the middle of the deck lifts (seven blocks), the raised leaves stand up at the portals
    x0, x1 = DRAWBRIDGE
    zc = (INNER[0] + INNER[1]) // 2
    deck = STREET + 1
    blocks = []
    for z in range(zc - 3, zc + 4):
        for x in range(x0 - 1, x1 + 2):
            for y in (deck, deck + 1):
                if not w.is_air(x, y, z):
                    blocks.append([x, y, z, 'minecraft:air'])
    for z in (zc - 4, zc + 4):
        for x in range(x0 + 1, x1):
            for y in range(deck + 1, deck + 4):
                blocks.append([x, y, z, 'minecraft:stripped_birch_wood'])
    out.append(dict(name='drawbridge', kind='drawbridge', open=blocks, clear=[x0, deck, zc - 3, x1, deck + 2, zc + 3]))
    # lock gates: the leaves swing back out of the lane, walkway and all
    gx0, gx1 = WEST_CANAL[0] + 3, WEST_CANAL[1] - 3
    for name, zg in (('lock.n', LOCK_GATES[0]), ('lock.s', LOCK_GATES[1])):
        blocks = []
        for x in range(gx0, gx1 + 1):
            for y in range(CANAL_BED, WATER + 1):
                blocks.append([x, y, zg, 'minecraft:water'])
            blocks.append([x, STREET, zg, 'minecraft:air'])
            if not w.is_air(x, STREET + 1, zg - 1):
                blocks.append([x, STREET + 1, zg - 1, 'minecraft:air'])
        out.append(dict(name=name, kind='lock', open=blocks, clear=[WEST_CANAL[0], CANAL_BED, zg - 1, WEST_CANAL[1], STREET + 2, zg + 1]))
    return out


# ---- routes --------------------------------------------------------------------------------------------------
def P(x, z, **kw):
    d = dict(pos=[round(x, 2), round(z, 2)])
    d.update(kw)
    return d


def rounded(points, r=6.0):
    """Replaces each plain corner (no stop, no gate) by a short arc so the boat turns instead of pivoting."""
    out = []
    n = len(points)
    for i, p in enumerate(points):
        if p.get('stop') or p.get('gate'):
            out.append(p)
            continue
        a, b = points[i - 1]['pos'], points[(i + 1) % n]['pos']
        x, z = p['pos']
        d1 = (x - a[0], z - a[1])
        d2 = (b[0] - x, b[1] - z)
        l1, l2 = math.hypot(*d1), math.hypot(*d2)
        if l1 < 1e-6 or l2 < 1e-6:
            out.append(p)
            continue
        u1 = (d1[0] / l1, d1[1] / l1)
        u2 = (d2[0] / l2, d2[1] / l2)
        turn = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        if turn < math.radians(20):
            out.append(p)
            continue
        rr = min(r, l1 / 2.2, l2 / 2.2)
        s = (x - u1[0] * rr, z - u1[1] * rr)
        e = (x + u2[0] * rr, z + u2[1] * rr)
        for k in range(5):                       # quadratic bezier through the corner
            t = k / 4
            bx = (1 - t) ** 2 * s[0] + 2 * (1 - t) * t * x + t * t * e[0]
            bz = (1 - t) ** 2 * s[1] + 2 * (1 - t) * t * z + t * t * e[1]
            out.append(P(bx, bz))
    return out


def zwaluw_route(ctx):
    cw = ctx['anchors']['crane.wait']
    return rounded([
        P(*HOME, stop='home', wait=20 * 20, hold='kooistra'),
        P(HOME[0] + 16, HOME[1]), P(186, INNER_LANE), P(276, INNER_LANE),
        P(cw[0], cw[1], gate='drawbridge'),                       # waits under the crane for the bridge
        P(DRAWBRIDGE[0] - 7, INNER_LANE), P(DRAWBRIDGE[1] + 10, INNER_LANE),
        P(E_LANE, INNER_LANE),
        P(E_LANE, OUTER_LANE), P(E_LANE, WAREHOUSES[1] + 6),
        P(DOCK[0], DOCK[1], stop='dock', wait=20 * 20, hold='kooistra'),
        P(E_LANE, WAREHOUSES[0] - 6), P(E_LANE, IJ_LANE + 16), P(E_LANE - 14, IJ_LANE + 3), P(E_LANE - 30, IJ_LANE),
        P(W_LANE + 30, IJ_LANE), P(W_LANE + 14, IJ_LANE + 3), P(W_LANE, IJ_LANE + 16),
        P(W_LANE, LOCK_GATES[0] - 8, gate='lock.n'),
        P(W_LANE, (LOCK_GATES[0] + LOCK_GATES[1]) / 2 + 1, stop='lock.chamber', wait=20 * 8),
        P(W_LANE, (LOCK_GATES[0] + LOCK_GATES[1]) / 2 + 3, gate='lock.s'),
        P(W_LANE, OUTER_LANE), P(W_LANE, INNER_LANE),
        P(100, INNER_LANE), P(HOME[0] - 28, INNER_LANE), P(HOME[0] - 14, HOME[1]),
    ])


def tour_route():
    return rounded([
        P(60, INNER_LANE), P(DRAWBRIDGE[0] - 8, INNER_LANE, gate='drawbridge'),
        P(DRAWBRIDGE[1] + 10, INNER_LANE), P(E_LANE, INNER_LANE),
        P(E_LANE, OUTER_LANE), P(W_LANE, OUTER_LANE), P(W_LANE, INNER_LANE),
    ])


def rotate_to(route, x, z):
    """Starts a loop route at the point nearest (x, z)."""
    best = min(range(len(route)), key=lambda i: (route[i]['pos'][0] - x) ** 2 + (route[i]['pos'][1] - z) ** 2)
    return route[best:] + route[:best]


# ---- checking ----------------------------------------------------------------------------------------------
PASS = ('air', 'water', 'light', 'bulb_string', 'chain', 'cave_air')


def boatcheck(ctx, boats, gate_defs, design_len):
    """Sweeps each boat's footprint along its route and reports blocks it would sail through."""
    w = ctx['w']
    opened = {(b[0], b[1], b[2]) for g in gate_defs for b in g['open']}
    problems = []
    for bt in boats:
        L0, L1 = design_len[bt['design']]
        pts = [p['pos'] for p in bt['route']]
        seen = set()
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            if seg < 1e-6:
                continue
            fx, fz = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
            steps = max(1, int(seg / .5))
            for k in range(steps + 1):
                cx, cz = a[0] + fx * seg * k / steps, a[1] + fz * seg * k / steps
                for lz in range(L0, L1 + 1):
                    for lx in range(-2, 3):
                        # local x is across the boat (perpendicular to heading), local z along it
                        px = cx + lx * fz + lz * fx
                        pz = cz - lx * fx + lz * fz
                        bx, bz = math.floor(px), math.floor(pz)
                        checks = [WATER + 1] + ([WATER + 2] if abs(lx) <= 1 else [])
                        for y in checks:
                            if (bx, y, bz) in opened or (bx, y, bz) in seen:
                                continue
                            nm = w.name(w.get(bx, y, bz)).split(':')[-1].split('[')[0]
                            if nm not in PASS:
                                seen.add((bx, y, bz))
                                problems.append(f"{bt['name']}: {nm} at {(bx, y, bz)} near route point {i}")
    return problems


# ---- crews ----------------------------------------------------------------------------------------------------
def crews(ctx, boats):
    """NPCs who live aboard: each boat's skipper, and seated tourists on the tour boats."""
    out = []
    names = iter(['Jos', 'Marloes', 'Pieter', 'Hanneke', 'Bram', 'Ineke', 'Thomas', 'Anouk', 'Gijs', 'Femke', 'Ruud', 'Sanne'])
    tour_names = iter(['Mr. Becker', 'Mrs. Becker', 'Ms. Kowalski', 'Mr. Silva', 'Mrs. Ito', 'Mr. Ito', 'Ms. Laurent', 'Mr. Owusu',
                       'Mrs. Novak', 'Mr. Hughes', 'Ms. Rossi', 'Mr. Andersen'])
    for bt in boats:
        x, z = bt['route'][0]['pos']
        pos = [x, WATER + 1, z]
        skipper = dict(name=f"Skipper {next(names)}", role='skipper', pos=pos, yaw=0, aboard=bt['name'],
                       skin=0 if bt['name'] == 'zwaluw' else 1,
                       route=dict(mode='once', points=[dict(pos=pos, wait=600, pose='stand')]))
        out.append(skipper)
        if bt['design'] == 'tour':
            for i in range(6):
                out.append(dict(name=next(tour_names), role='tourist', pos=pos, yaw=0, aboard=bt['name'], skin=3 + i % 3,
                                route=dict(mode='once', points=[dict(pos=pos, wait=600, pose=['look', 'phone', 'talk'][i % 3])])))
    return out


def canal_mouths(ctx):
    """Opens both cross canals through the Ankerkade into the IJ, with a humped brick bridge over each so the
    harbour quay stays one walk."""
    import ams_ground
    w = ctx['w']
    z0, z1 = ANKERKADE[0] - 1, ANKERKADE[1]
    for cx0, cx1 in (WEST_CANAL, EAST_CANAL):
        w.clear(cx0, CANAL_BED + 1, z0, cx1, STREET + 6, z1)
        w.fill(cx0, CANAL_BED, z0, cx1, CANAL_BED, z1, 'mud')
        w.fill(cx0, CANAL_BED + 1, z0, cx1, WATER, z1, 'water')
        ams_ground._rewall(ctx, cx0, z0, cx1, z1)
        ams_water.arch_bridge(ctx, cx0, cx1, ANKERKADE[0] + 3, ANKERKADE[1] - 3, 'x', wide=True)


def junction_bridges(ctx):
    """The quays along the cross canals ran over the ring canals at street level; boats need to get through,
    so each crossing becomes a humped bridge."""
    w = ctx['w']
    for qx0, qx1 in (EAST_OF_WEST_QUAY, EAST_W_QUAY):
        for cz0, cz1 in (OUTER, INNER):
            if all(w.is_air(x, STREET, z) for x in range(qx0, qx1 + 1) for z in range(cz0, cz1 + 1)):
                continue
            w.clear(qx0, STREET, cz0, qx1, STREET + 6, cz1)
            w.fill(qx0, CANAL_BED + 1, cz0, qx1, WATER, cz1, 'water')
            ams_water.arch_bridge(ctx, qx0, qx1, cz0, cz1, 'z', wide=True)


def build(ctx):
    canal_mouths(ctx)
    junction_bridges(ctx)
    x0 = EAST_CANAL[0] - 2
    ctx['anchors']['dock.landing'] = (x0 + 3, WATER + 2, int(DOCK[1]))
    kooistra_houseboat(ctx)
    crane(ctx)
    booth(ctx)
    lock_wheel(ctx)


def mission_data(ctx):
    gate_defs = gates(ctx)
    tour = tour_route()
    boats = [
        dict(name='zwaluw', design='zwaluw', y=Y_BOAT, route=zwaluw_route(ctx)),
        dict(name='tour1', design='tour', y=Y_BOAT, route=rotate_to(tour, 120, INNER_LANE)),
        dict(name='tour2', design='tour', y=Y_BOAT, route=rotate_to(tour, 200, OUTER_LANE)),
    ]
    problems = boatcheck(ctx, boats, gate_defs, {'zwaluw': (-5, 6), 'tour': (-7, 8)})
    print(f'  boats: {len(boats)} routes, {sum(len(b["route"]) for b in boats)} points, {len(problems)} clashes')
    for pr in problems[:25]:
        print('    ', pr)
    return boats, gate_defs
