"""Kievit — a two-shot over-under pocket derringer.

A bright nickel frame with scroll engraving, deep-blued over-under barrels on a hinge at the top
rear (a thumb latch on the top strap lets them tip up to load), a spur trigger, a spur hammer and a
small bird's-head grip with dark, green-and-violet iridescent panels like a lapwing's back, a
brass lanyard ring underneath. Two rounds of .357, very loud for something this small.

It uses the pistol rig (one-hand hold, left hand under the grip) with the break-action bones:
barrels (rotate about the hinge: negative x tips the muzzles up), lever, extractor, shell_1, shell_2.
"""
import numpy as np

import materials as M
from common import GRIP_PIV, GRIP_ROT, arm_colour, pistol_rig, pistol_views
from geomodel import arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'kievit'
K = 16
UB_Y, LB_Y = 5.0, 4.18            # upper and lower bores
BR = 0.37                          # barrel outer radius
BX = 0.0
MUZZLE_Z = -4.05
BREECH_Z = 0.3
HINGE = [0, 5.62, 0.12]
RIB_TOP = UB_Y + BR + 0.08
SIGHT_Y = RIB_TOP + 0.16
GB = 0.75                          # grip bottom (grip frame)


def build_barrels(m):
    b = m.part('barrels', ID, HINGE)
    for y in (UB_Y, LB_Y):
        octagon(b, 'z', (BX, y), BR, MUZZLE_Z + 0.1, BREECH_Z, 'barrel', sides=16, data={'decal': 'tube'})
        octagon(b, 'z', (BX, y), BR + 0.03, MUZZLE_Z, MUZZLE_Z + 0.22, 'barrel', sides=16, data={'decal': 'muzzle'})
    b.bar(-0.24, 0.24, LB_Y, UB_Y, MUZZLE_Z + 0.05, BREECH_Z, 'barrel', data={'decal': 'web'})
    # flat top rib with a blade front sight
    round_bar(b, 'z', (-0.2, UB_Y + 0.2, MUZZLE_Z + 0.08), (0.2, RIB_TOP, BREECH_Z - 0.05), 'barrel', r=0.05,
              corners=(1, 1, 0, 0), sides=8, data={'decal': 'rib'})
    round_bar(b, 'z', (-0.05, RIB_TOP - 0.02, MUZZLE_Z + 0.25), (0.05, SIGHT_Y, MUZZLE_Z + 0.65), 'barrel', r=0.025,
              sides=8)
    # hinge lug on top of the breech end, riding in the frame's top strap
    b.bar(-0.2, 0.2, UB_Y + 0.25, HINGE[1] + 0.12, BREECH_Z - 0.55, BREECH_Z, 'barrel')
    disc_x(b, HINGE[1], HINGE[2], 0.16, -0.21, 0.21, 'barrel', sides=8)
    m.part('muzzle_pos', 'barrels', [0, UB_Y, MUZZLE_Z])
    # extractor plate between the chambers and the two rounds
    ex = m.part('extractor', 'barrels', [0, (UB_Y + LB_Y) / 2, BREECH_Z])
    ex.bar(-0.13, 0.13, LB_Y + 0.22, UB_Y - 0.22, BREECH_Z - 0.3, BREECH_Z + 0.01, 'steel')
    for name, y in (('shell_1', UB_Y), ('shell_2', LB_Y)):
        sh = m.part(name, 'extractor', [0, y, BREECH_Z])
        octagon(sh, 'z', (0, y), 0.25, BREECH_Z - 0.06, BREECH_Z + 0.02, 'brass', sides=16, data={'decal': 'head'})
        octagon(sh, 'z', (0, y), 0.21, BREECH_Z - 1.3, BREECH_Z - 0.06, 'brass', sides=16)


def build_frame(m):
    f = m.part('gun', ID, [0, 0, 0])
    # standing breech and top strap, with the hinge yoke reaching forward over the barrels' lug
    round_bar(f, 'z', (-0.42, 3.4, BREECH_Z), (0.42, 5.55, 1.65), 'frame', r=0.18, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'frame'})
    round_bar(f, 'z', (-0.42, 5.45, -0.2), (0.42, 5.82, 1.25), 'frame', r=0.12, corners=(1, 1, 0, 0), sides=8)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.22, sgn * 0.42))
        f.bar(x0, x1, 5.2, 5.82, -0.42, 0.3, 'frame')
        xa, xb = sorted((sgn * 0.42, sgn * 0.46))
        disc_x(f, HINGE[1], HINGE[2], 0.12, xa, xb, 'steel')                  # hinge-pin head
    # bottom strap under the lower barrel, ending in a rounded nose
    round_bar(f, 'z', (-0.38, 3.32, -2.0), (0.38, LB_Y - BR - 0.02, BREECH_Z + 0.2), 'frame', r=0.15,
              corners=(0, 0, 1, 1), sides=8, data={'decal': 'strap'})
    round_bar(f, 'x', (-0.38, 3.32, -2.25), (0.38, LB_Y - BR - 0.02, -1.9), 'frame', r=0.22, corners=(0, 0, 1, 0),
              sides=8)
    # spur trigger in its sheath
    path_yz(f, [(3.4, -0.8), (3.0, -0.76)], 0.2, -0.2, 0.2, 'frame')
    t = m.part('trigger', 'gun', [0, 3.3, -0.25])
    path_yz(t, [(3.35, -0.3)] + arc_pts(2.9, 0.05, 0.5, 120, 200, 3), 0.15, -0.12, 0.12, 'gold', data={'decal': 'trigger'})
    # spur hammer, cocked
    h = m.part('hammer', 'gun', [0, 4.45, 1.85])
    seg_yz(h, (4.45, 1.85), (5.45, 2.0), 0.38, -0.17, 0.17, 'steel')
    path_yz(h, [(5.4, 1.98), (5.66, 2.24), (5.74, 2.58), (5.66, 2.84)], 0.24, -0.21, 0.21, 'steel', data={'decal': 'spur'})
    # thumb latch on the top strap: swings aside to free the barrels
    lv = m.part('lever', ID, [0, 5.85, 0.95])
    lv.bar(-0.1, 0.1, 5.8, 5.95, 0.15, 1.15, 'steel')
    lv.box((-0.48, 5.8, 0.85), (0.02, 5.98, 1.15), 'steel', pivot=[-0.23, 5.89, 1.0], rotation=[0, -18, 0],
           data={'decal': 'knurl'})
    m.part('parts', 'gun', [0.42, 4.5, 1.0])
    # the frame runs back over the web of the hand into a rounded recoil shield
    round_bar(f, 'z', (-0.4, 3.05, 1.6), (0.4, 4.75, 3.55), 'frame', r=0.3, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'back'})
    round_bar(f, 'x', (-0.4, 3.05, 3.0), (0.4, 4.75, 3.85), 'frame', r=0.45, corners=(1, 0, 0, 1), sides=16)
    g = m.part('grip', 'gun', GRIP_PIV, GRIP_ROT)
    # bird's-head grip: short, the butt swelling back into a rounded hook
    round_bar(g, 'y', (-0.37, GB + 0.4, 1.3), (0.37, 3.75, 3.25), 'frame', r=0.28, data={'decal': 'gframe'})
    round_bar(g, 'x', (-0.37, GB, 1.3), (0.37, GB + 1.1, 3.6), 'frame', r=0.5, corners=(0, 1, 1, 0), sides=16)
    for sgn in (1, -1):
        corners = (1, 0, 0, 1) if sgn > 0 else (0, 1, 1, 0)
        x0, x1 = sorted((sgn * 0.28, sgn * 0.47))
        round_bar(g, 'y', (x0, GB + 0.38, 1.42), (x1, 3.45, 3.2), 'plume', r=0.16, corners=corners,
                  data={'decal': 'panel'})
        xa, xb = sorted((sgn * 0.47, sgn * 0.51))
        disc_x(g, 2.0, 2.3, 0.09, xa, xb, 'gold', sides=8)                    # grip screw
    disc_x(g, GB + 0.12, 3.15, 0.22, -0.08, 0.08, 'gold', sides=16)           # lanyard ring
    disc_x(g, GB + 0.12, 3.15, 0.12, -0.09, 0.09, 'black', sides=8)


def build():
    m = pistol_rig(ID, UB_Y, MUZZLE_Z)
    build_frame(m)
    build_barrels(m)
    pistol_views(m, SIGHT_Y - 0.05, MUZZLE_Z)
    return m


def plumage(p, n, seed=0):
    """Dark lapwing-back panels: near black with a green and violet sheen that shifts across the grain."""
    base = np.array([30, 34, 34], dtype=float)
    t = M.fbm(p, [3.0, 3.0, 3.0], 2, seed)
    green = np.array([40, 92, 70], dtype=float)
    violet = np.array([78, 52, 96], dtype=float)
    w = np.clip((t - 0.35) * 2.2, 0, 1)[:, None]
    sheen = green[None] * (1 - w) + violet[None] * w
    k = np.clip(0.35 + 0.65 * np.sin(p[:, 1] * 5.0 + p[:, 2] * 2.0 + t * 4.0) ** 2, 0, 1)[:, None]
    return base[None] * (1 - k * 0.7) + sheen * k * 0.75


BASE = {
    'frame': M.nickel, 'barrel': M.deep_blue, 'steel': M.blued, 'gold': M.gold, 'brass': M.brass,
    'black': M.matte_black, 'plume': plumage,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)
    if d == 'muzzle' and face == 'north':
        holes = M.disc(x, y, BX, UB_Y, 0.2) | M.disc(x, y, BX, LB_Y, 0.2)
        col = np.where(holes[:, None], np.array([[10, 10, 12]]), col)
    if d in ('frame', 'back', 'gframe') and side:
        cut = M.scrollwork(y, z, {'frame': 4.6, 'back': 4.0, 'gframe': 2.2}[d], seed=7 if n[0] > 0 else 9)
        col = np.where(cut[:, None], col * 0.6, col)
    if d == 'strap' and side:
        if n[0] > 0:
            t = M.text_mask(y, z, 'KIEVIT', -1.95, 3.74, 7.0 / K, reverse=True)
        else:
            t = M.text_mask(y, z, '357', -0.35, 3.74, 7.0 / K)
        col = np.where(t[:, None], M.gold(p, n) * 0.9, col)
    if d == 'tube':
        col = col * (1.0 + 0.1 * np.clip((np.abs(y - UB_Y) - 0.2) * 3, 0, 1))[:, None]
    if d == 'rib' and face == 'up':
        col = col * M.grooves(z, 0.1, 0.4, 0.72)[:, None]
    if d == 'panel' and side:
        inner = (z > 1.5) & (z < 3.1) & (y > GB + 0.6) & (y < 3.0)
        col = col * np.where(inner, M.checker(y, z, 0.16, 0.18, 0.78), 1.0)[:, None]
    if d == 'knurl':
        col = col * M.checker(z, x, 0.08, 0.3, 0.6)[:, None]
    if d == 'spur' and face in ('up', 'south'):
        col = col * M.grooves(z + y, 0.08, 0.4, 0.6)[:, None]
    if d == 'trigger' and face == 'north':
        col = col * M.grooves(y, 0.08, 0.35, 0.8)[:, None]
    if d == 'head' and face == 'south':
        primer = M.disc(x, y, 0, UB_Y, 0.09) | M.disc(x, y, 0, LB_Y, 0.09)
        col = np.where(primer[:, None], M.copper(p, n) * 1.1, col)
    metal = mat in ('frame', 'barrel', 'steel', 'gold', 'brass')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
