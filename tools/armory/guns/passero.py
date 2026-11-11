"""Passero .22 — the quiet one.

A compact satin-black .22 with an integral suppressor: one long fluted can built onto the
barrel, sights on the slide and on the can, walnut grips with a brass sparrow medallion and
a brass trigger. Striker fired, so no hammer.
"""
import numpy as np

import materials as M
from common import GRIP_PIV, GRIP_ROT, arm_colour, pistol_rig, pistol_views
from geomodel import arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'passero'
K = 16
GB = -0.9                          # grip bottom (grip frame)
SX = 0.55                          # slide half width
SLIDE_Z0, SLIDE_Z1 = -4.3, 2.9
SLIDE_Y0, SLIDE_MID, SLIDE_Y1 = 3.55, 4.4, 5.55
BORE_Y = 4.75
CAN_R = 0.62
CAN_Z0, CAN_Z1 = -11.2, -4.42      # integral suppressor
MUZZLE_Z = CAN_Z0 - 0.02
PORT = (-1.65, -0.25, 4.32, 5.15)
SIGHT_Y = 5.9                      # line of sight


def build_slide(m):
    s = m.part('slide', ID, [0, 4.6, -0.7])
    pz0, pz1, py0, py1 = PORT
    CORE = -0.25
    round_bar(s, 'z', (CORE, SLIDE_MID, SLIDE_Z0), (SX, SLIDE_Y1, SLIDE_Z1), 'slide', r=0.36,
              corners=(1, 0, 0, 0), data={'decal': 'upper'})
    for z0, z1 in ((SLIDE_Z0, pz0), (pz1, SLIDE_Z1)):
        round_bar(s, 'z', (-SX, SLIDE_MID, z0), (CORE, SLIDE_Y1, z1), 'slide', r=0.3, corners=(0, 1, 0, 0),
                  data={'decal': 'upper'})
    round_bar(s, 'z', (-SX, py1, pz0), (CORE, SLIDE_Y1, pz1), 'slide', r=0.3, corners=(0, 1, 0, 0),
              data={'decal': 'upper'})
    s.bar(-0.42, CORE, SLIDE_MID - 0.1, py1, pz0, pz1, 'port')
    octagon(s, 'z', (-0.05, BORE_Y), 0.26, pz0 + 0.08, pz1 - 0.05, 'brass')
    round_bar(s, 'z', (-SX + 0.02, SLIDE_Y0, SLIDE_Z0), (SX - 0.02, SLIDE_MID, SLIDE_Z1), 'slide', r=0.1,
              corners=(0, 0, 1, 1), sides=8, data={'decal': 'lower'})
    round_bar(s, 'x', (-SX + 0.04, SLIDE_MID, SLIDE_Z0 - 0.05), (SX - 0.04, SLIDE_Y1 - 0.06, SLIDE_Z0 + 0.25),
              'slide', r=0.2, corners=(1, 0, 0, 0), sides=8)
    # rear cocking serrations only (front of the slide is hidden by the can)
    z = 1.55
    while z + 0.05 <= 2.75:
        for sgn in (1, -1):
            x0, x1 = sorted((sgn * (SX - 0.02), sgn * (SX + 0.006)))
            s.bar(x0, x1, SLIDE_Y0 + 0.25, SLIDE_Y1 - 0.35, z, z + 0.05, 'groove')
        z += 0.15
    # striker indicator at the back
    octagon(s, 'z', (0, BORE_Y + 0.15), 0.09, SLIDE_Z1, SLIDE_Z1 + 0.04, 'brass', sides=8)
    # three-dot sights: rear on the slide, front on top of the can
    sights = m.part('sight', 'slide', [0, SLIDE_Y1, 2.3])
    for sgn in (1, -1):
        x0, x1 = (0.09, 0.36) if sgn > 0 else (-0.36, -0.09)
        round_bar(sights, 'z', (x0, SLIDE_Y1 - 0.04, 2.15), (x1, SIGHT_Y + 0.08, 2.65), 'black', r=0.06,
                  corners=(1, 0, 0, 0) if sgn > 0 else (0, 1, 0, 0), sides=8)
        d0, d1 = sorted((sgn * 0.17, sgn * 0.27))
        sights.bar(d0, d1, SIGHT_Y - 0.12, SIGHT_Y - 0.02, 2.65, 2.662, 'white')
    round_bar(sights, 'z', (-0.36, SLIDE_Y1 - 0.04, 2.0), (0.36, SLIDE_Y1 + 0.1, 2.65), 'black', r=0.05,
              corners=(1, 1, 0, 0), sides=8)
    m.part('bullet_in_barrel', 'slide', [0, BORE_Y, -0.8])
    octagon(m['bullet_in_barrel'], 'z', (0, BORE_Y), 0.12, -1.2, -0.4, 'brass')


def build_can(m):
    """Integral suppressor, fixed to the frame (the slide runs behind it)."""
    b = m.part('barrel', 'gun', [0, BORE_Y, 0])
    octagon(b, 'z', (0, BORE_Y), CAN_R, CAN_Z0 + 0.3, CAN_Z1 - 0.3, 'can', sides=16, data={'decal': 'can'})
    octagon(b, 'z', (0, BORE_Y), CAN_R + 0.04, CAN_Z1 - 0.3, CAN_Z1, 'can', sides=16, data={'decal': 'cap'})
    octagon(b, 'z', (0, BORE_Y), CAN_R + 0.03, CAN_Z0, CAN_Z0 + 0.3, 'can', sides=16, data={'decal': 'cap'})
    octagon(b, 'z', (0, BORE_Y), CAN_R + 0.02, CAN_Z1 - 0.46, CAN_Z1 - 0.38, 'brass', sides=16)
    octagon(b, 'z', (0, BORE_Y), 0.14, CAN_Z0 - 0.02, CAN_Z0, 'bore', sides=8)
    # flutes: shallow dark channels running along the can
    for k in range(8):
        ang = 22.5 + 45 * k
        if 60 < ang < 120:
            continue                                   # keep the top clean under the front sight
        a = np.radians(ang)
        cx, cy = np.cos(a) * (CAN_R - 0.01), BORE_Y + np.sin(a) * (CAN_R - 0.01)
        b.box((cx - 0.05, cy - 0.05, CAN_Z0 + 0.6), (cx + 0.05, cy + 0.05, CAN_Z1 - 0.7), 'flute',
              pivot=[cx, cy, (CAN_Z0 + CAN_Z1) / 2], rotation=[0, 0, ang])
    # front sight blade on the can
    round_bar(b, 'z', (-0.07, BORE_Y + CAN_R - 0.05, CAN_Z0 + 0.45), (0.07, SIGHT_Y, CAN_Z0 + 0.85), 'black',
              r=0.03, sides=8)
    seg_yz(b, (BORE_Y + CAN_R - 0.02, CAN_Z0 + 0.35), (SIGHT_Y - 0.05, CAN_Z0 + 0.7), 0.1, -0.07, 0.07, 'black')
    b.bar(-0.045, 0.045, SIGHT_Y - 0.12, SIGHT_Y - 0.03, CAN_Z0 + 0.85, CAN_Z0 + 0.862, 'white')
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])


def build_frame(m):
    f = m.part('gun', ID, [0, 0, 0])
    build_can(m)
    # dust cover and the mount that carries the can
    round_bar(f, 'z', (-0.5, 2.95, -4.2), (0.5, SLIDE_Y0, -1.3), 'frame', r=0.2, corners=(0, 0, 1, 1), sides=8)
    round_bar(f, 'z', (-0.5, 2.65, -1.3), (0.5, SLIDE_Y0, 2.7), 'frame', r=0.12, corners=(0, 0, 1, 1), sides=8)
    round_bar(f, 'z', (-0.36, 3.3, -4.75), (0.36, BORE_Y - 0.2, -4.2), 'frame', r=0.12, corners=(0, 0, 1, 1), sides=8)
    f.bar(-0.512, 0.512, 3.45, SLIDE_Y0, -4.15, 2.7, 'frame')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.5, sgn * 0.56))
        disc_x(f, 3.15, -1.0, 0.11, x0, x1, 'black')
    # rounded trigger guard
    guard = [(2.7, -1.45)] + arc_pts(1.38, -1.4, 0.42, 165, 270, 4) + [(0.96, -0.6), (0.98, 0.3)] \
        + arc_pts(1.4, 0.3, 0.42, 270, 330, 2) + [(1.5, 1.28)]
    path_yz(f, guard, 0.22, -0.24, 0.24, 'frame')
    t = m.part('trigger', 'gun', [0, 2.6, -0.5])
    path_yz(t, [(2.6, -0.45)] + arc_pts(2.05, 0.2, 0.72, 130, 205, 4), 0.13, -0.12, 0.12, 'brass',
            data={'decal': 'trigger'})
    # tang over the hand (no hammer: striker fired)
    path_yz(f, [(2.95, 3.55), (3.12, 4.05), (3.3, 4.4)], 0.28, -0.36, 0.36, 'frame')
    round_bar(f, 'z', (-0.44, 3.25, 2.7), (0.44, SLIDE_Y0, 4.1), 'frame', r=0.14, corners=(1, 1, 0, 0), sides=8)
    # left-side controls
    parts = m.part('parts', 'gun', [0.6, 3.4, 0])
    rel = m.part('hold_release', 'parts', [0.6, 3.4, 0])
    round_bar(rel, 'z', (0.5, 3.24, -1.1), (0.62, 3.52, 0.2), 'black', r=0.05, sides=8, data={'decal': 'lever'})
    disc_x(parts, 2.38, 0.9, 0.15, 0.46, 0.58, 'black', sides=16, data={'decal': 'button'})

    g = m.part('grip', 'gun', GRIP_PIV, GRIP_ROT)
    round_bar(g, 'y', (-0.44, GB, 1.12), (0.44, 3.1, 3.8), 'frame', r=0.3, data={'decal': 'grip_core'})
    g.bar(-0.26, 0.26, GB + 0.3, 2.6, 1.105, 1.125, 'black', data={'decal': 'strap'})
    round_bar(g, 'y', (-0.36, GB, 3.6), (0.36, 2.7, 4.0), 'black', r=0.18, corners=(1, 1, 0, 0),
              data={'decal': 'backstrap'})
    for sgn in (1, -1):
        corners = (1, 0, 0, 1) if sgn > 0 else (0, 1, 1, 0)
        x0, x1 = sorted((sgn * 0.3, sgn * 0.62))
        round_bar(g, 'y', (x0, GB + 0.25, 1.24), (x1, 2.8, 3.56), 'walnut', r=0.16, corners=corners,
                  data={'decal': 'panel'})
        x0, x1 = sorted((sgn * 0.62, sgn * 0.66))
        disc_x(g, (GB + 0.25 + 2.8) / 2 + 0.25, 2.4, 0.24, x0, x1, 'brass', sides=16, data={'decal': 'medallion'})
        for sy in (GB + 0.5, 2.55):
            disc_x(g, sy, 2.4, 0.09, x0, x1, 'black')
    round_bar(g, 'y', (-0.5, GB - 0.04, 1.06), (0.5, GB + 0.1, 3.86), 'frame', r=0.1, sides=8)


def build_magazine(m):
    m.part('magazine_and_bullet', 'mag_and_lefthand', [0, 1.995, 1.6])
    m.part('magazine', 'magazine_and_bullet', [0, 1.995, 1.6])
    std = m.part('mag_standard', 'magazine', GRIP_PIV, GRIP_ROT)
    std.bar(-0.26, 0.26, GB, 3.0, 1.35, 3.3, 'blued')
    round_bar(std, 'y', (-0.42, GB - 0.34, 1.16), (0.42, GB - 0.02, 3.7), 'rubber', r=0.14, sides=8)
    rnd = m.part('bullet_in_mag', 'magazine', GRIP_PIV, GRIP_ROT)
    octagon(rnd, 'z', (0, 3.08), 0.12, 1.8, 2.6, 'brass')
    octagon(rnd, 'z', (0, 3.08), 0.1, 1.55, 1.8, 'lead')
    top = m.part('bullet', 'magazine_and_bullet', [0, 3.3, 1.8])
    octagon(top, 'z', (0, 3.3), 0.12, 1.8, 2.6, 'brass')
    octagon(top, 'z', (0, 3.3), 0.1, 1.55, 1.8, 'lead')


def build():
    m = pistol_rig(ID, BORE_Y, MUZZLE_Z)
    build_slide(m)
    build_frame(m)
    build_magazine(m)
    pistol_views(m, SIGHT_Y - 0.07, MUZZLE_Z)
    return m


BASE = {
    'slide': M.satin_black, 'frame': M.satin_black, 'can': lambda p, n: M.matte_black(p, n) * 1.35,
    'black': M.matte_black,
    'walnut': M.walnut, 'brass': M.brass, 'blued': M.blued, 'rubber': M.rubber,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    if mat == 'white':
        return M.finish(M.rgba(np.tile([[236, 236, 226]], (N, 1))))
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[6, 6, 7]], (N, 1))))
    if mat == 'port':
        return M.finish(M.rgba(M.blued(p, n) * 0.45))
    if mat in ('groove', 'flute'):
        return M.finish(M.rgba(M.bake(np.tile([[20, 21, 24]], (N, 1)).astype(float), c.data['wn'])))
    if mat == 'lead':
        return M.finish(M.rgba(M.bake(np.tile([[120, 122, 126]], (N, 1)).astype(float), c.data['wn'], metal=True)))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)

    if d == 'upper' and side and abs(x.mean()) > SX - 0.05 and n[0] > 0:
        # the name, lightly engraved on the left flat
        t = M.text_mask(y, z, 'PASSERO .22', -3.55, 5.0, 7.0 / K, reverse=True)
        col = np.where(t[:, None], col * 2.3, col)
    if d in ('upper', 'lower') and face == 'south':
        col = col * M.grooves(y, 0.1, 0.3, 0.75)[:, None]
    if d == 'can' and not (abs(n[2]) > 0.5):
        band = (np.abs(z - (CAN_Z1 - 1.2)) < 0.04) | (np.abs(z - (CAN_Z0 + 1.0)) < 0.04)
        col = np.where(band[:, None], col * 0.55, col)
    if d == 'cap' and face == 'north':
        ring = M.disc(x, y, 0, BORE_Y, 0.45) & ~M.disc(x, y, 0, BORE_Y, 0.3)
        col = np.where(ring[:, None], col * 0.6, col)
    if d == 'panel' and side:
        inner = (z > 1.42) & (z < 3.38) & (y > GB + 0.45) & (y < 2.6)
        col = col * np.where(inner, M.checker(y, z, 0.13, 0.22, 0.72), 1.0)[:, None]
    if d == 'medallion' and side:
        cy = (GB + 0.25 + 2.8) / 2 + 0.25
        dy, dz = y - cy, z - 2.4
        # a small bird in flight: two swept wings and a body
        wing = (np.abs(dy - 0.35 * np.abs(dz)) < 0.035) & (np.abs(dz) < 0.17)
        body = (np.abs(dz) < 0.03) & (dy > -0.12) & (dy < 0.04)
        rim = ~M.disc(z, y, 2.4, cy, 0.19)
        col = np.where((wing | body | rim)[:, None], col * 0.55, col)
    if d in ('strap', 'backstrap'):
        col = col * M.checker(x, y, 0.1, 0.24, 0.6)[:, None]
    if d == 'trigger' and face == 'north':
        col = col * M.grooves(y, 0.08, 0.35, 0.72)[:, None]
    if d == 'lever' and side:
        col = col * M.grooves(z, 0.08, 0.35, 0.75)[:, None]
    if d == 'button' and side:
        col = col * M.checker(y, z, 0.07, 0.25, 0.6)[:, None]
    metal = mat in ('slide', 'frame', 'brass', 'blued')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
