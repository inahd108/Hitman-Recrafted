"""Offline walkability check: can a mob get from one waypoint to the next?

A coarse model of vanilla ground pathfinding on the voxel canvas: cells are either
passable or solid, a mob needs two passable cells over a solid one, may step up one
block and drop up to three. Good enough to catch routes that cross walls, missing
stairs, tables or water before anything runs in the game.
"""
from collections import deque

import numpy as np

SOFT = {'air', 'grass', 'tall_grass', 'fern', 'poppy', 'dandelion', 'azure_bluet', 'oxeye_daisy', 'cornflower',
        'white_tulip', 'pink_tulip', 'orange_tulip', 'red_tulip', 'allium', 'dead_bush', 'wither_rose',
        'brown_mushroom', 'rail', 'vine', 'ladder', 'rose_bush', 'peony', 'lilac', 'snow',
        'metal_detector', 'bicycle', 'bulb_string', 'light'}


def classify(w):
    """Per palette id: 0 passable, 1 solid, 2 tall solid (fence / wall), 3 liquid."""
    out = np.ones(len(w.palette), dtype=np.uint8)
    for i, full in enumerate(w.palette):
        name = full.split(':')[1].split('[')[0]
        props = full.split('[')[1] if '[' in full else ''
        if name in SOFT or name.endswith('_carpet') or name.endswith('_pressure_plate'):
            out[i] = 0
        elif name.endswith('_door'):
            out[i] = 0                      # wooden doors are opened; iron doors by cleared staff
        elif name.endswith('_trapdoor') and 'open=true' in props:
            out[i] = 0
        elif name.endswith('_fence') or name.endswith('_wall'):
            out[i] = 2
        elif name == 'water':
            out[i] = 3
    return out


class Walker:
    def __init__(self, w):
        self.w = w
        cls = classify(w)
        C = cls[w.G]                                   # [y, z, x]
        passable = C == 0
        solid = (C == 1) | (C == 2)
        tall_below = np.zeros_like(passable)
        tall_below[1:] = C[:-1] == 2
        floor = np.zeros_like(passable)
        floor[1:] = solid[:-1]
        head = np.zeros_like(passable)
        head[:-1] = passable[1:]
        self.passable = passable
        self.stand = passable & head & floor & ~tall_below
        self.sy, self.sz, self.sx = passable.shape

    def ok(self, x, y, z):
        return 0 <= x < self.sx and 0 <= z < self.sz and 1 <= y < self.sy - 2 and self.stand[y, z, x]

    def snap(self, x, y, z):
        """Nearest standable cell to a waypoint (same column first)."""
        for dy in (0, 1, -1):
            if self.ok(x, y + dy, z):
                return (x, y + dy, z)
        for r in (1, 2):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    for dy in (0, 1, -1):
                        if self.ok(x + dx, y + dy, z + dz):
                            return (x + dx, y + dy, z + dz)
        return None

    def reachable(self, a, b, limit=60000):
        a, b = self.snap(*a), self.snap(*b)
        if a is None or b is None:
            return False
        if a == b:
            return True
        seen = {a}
        q = deque([a])
        P = self.passable
        while q and len(seen) < limit:
            x, y, z = q.popleft()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if not (0 <= nx < self.sx and 0 <= nz < self.sz):
                    continue
                for ny in (y, y + 1, y - 1, y - 2, y - 3):
                    if not self.ok(nx, ny, nz):
                        continue
                    if ny > y and not P[y + 2, z, x]:
                        continue                     # no headroom to hop up
                    if ny < y and not (P[y, nz, nx] and P[y + 1, nz, nx]):
                        continue                     # cannot walk off the ledge
                    n = (nx, ny, nz)
                    if n in seen:
                        break
                    if n == b:
                        return True
                    seen.add(n)
                    q.append(n)
                    break
        return False


def find_path(wk, a, b, limit=80000):
    """Shortest walk (list of cells) between two waypoints, or None."""
    a, b = wk.snap(*a), wk.snap(*b)
    if a is None or b is None:
        return None
    if a == b:
        return [a]
    prev = {a: None}
    q = deque([a])
    P = wk.passable
    while q and len(prev) < limit:
        cur = q.popleft()
        x, y, z = cur
        for dx, dz in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nx, nz = x + dx, z + dz
            if not (0 <= nx < wk.sx and 0 <= nz < wk.sz):
                continue
            for ny in (y, y + 1, y - 1, y - 2, y - 3):
                if not wk.ok(nx, ny, nz):
                    continue
                if ny > y and not P[y + 2, z, x]:
                    continue
                if ny < y and not (P[y, nz, nx] and P[y + 1, nz, nx]):
                    continue
                n = (nx, ny, nz)
                if n in prev:
                    break
                prev[n] = cur
                if n == b:
                    out = [n]
                    while prev[out[-1]] is not None:
                        out.append(prev[out[-1]])
                    return out[::-1]
                q.append(n)
                break
    return None


def split_long_legs(w, npcs, max_leg=14, spacing=9):
    """Inserts pass-through stops along long legs so the in-game pathfinder only solves short hops."""
    wk = Walker(w)
    added = 0
    for n in npcs:
        pts = n['route']['points']
        if len(pts) < 2:
            continue
        out = []
        pairs = list(zip(pts, pts[1:]))
        closing = n['route'].get('mode') == 'loop' and len(pts) > 2
        if closing:
            pairs.append((pts[-1], pts[0]))
        for k, (pa, pb) in enumerate(pairs):
            out.append(pa)
            a = (int(pa['pos'][0] // 1), int(pa['pos'][1]), int(pa['pos'][2] // 1))
            b = (int(pb['pos'][0] // 1), int(pb['pos'][1]), int(pb['pos'][2] // 1))
            if abs(a[0] - b[0]) + abs(a[2] - b[2]) + abs(a[1] - b[1]) <= max_leg:
                continue
            path = find_path(wk, a, b)
            if not path or len(path) <= max_leg:
                continue
            steps = len(path) - 1
            count = steps // spacing
            for j in range(1, count + 1):
                idx = round(j * steps / (count + 1))
                c = path[idx]
                if abs(c[0] - b[0]) + abs(c[2] - b[2]) < 3:
                    continue
                mid = dict(pos=[c[0] + .5, c[1], c[2] + .5], wait=0, pose='stand')
                if pb.get('run'):
                    mid['run'] = True
                out.append(mid)
                added += 1
        if not closing:
            out.append(pts[-1])
        n['route']['points'] = out
    return added


def check_routes(w, npcs):
    """Returns a list of human-readable problems for every unreachable route leg."""
    wk = Walker(w)
    problems = []
    for n in npcs:
        pts = n['route']['points']
        cells = [(int(p['pos'][0] // 1), int(p['pos'][1]), int(p['pos'][2] // 1)) for p in pts]
        for i, c in enumerate(cells):
            if wk.snap(*c) is None:
                problems.append(f"{n['name']}: stop #{i + 1} {c} is not standable")
        legs = list(zip(range(len(cells)), range(1, len(cells))))
        if n['route'].get('mode') == 'loop' and len(cells) > 2:
            legs.append((len(cells) - 1, 0))
        for i, j in legs:
            if wk.snap(*cells[i]) is None or wk.snap(*cells[j]) is None:
                continue
            if not wk.reachable(cells[i], cells[j]):
                problems.append(f"{n['name']}: no way from stop #{i + 1} {cells[i]} to #{j + 1} {cells[j]}")
    return problems
