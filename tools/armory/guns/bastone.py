"""Bastone 9 — the guards' sidearm.

A full-size 9 mm service pistol: parkerized grey slide on a black polymer frame, an accessory
rail, a squared trigger guard, stippled grip with finger grooves and the Corvara police shield,
a bobbed hammer, slide-mounted decockers and green tritium night sights.
"""
import numpy as np

import materials as M
from common import GRIP_PIV, GRIP_ROT, arm_colour, pistol_rig, pistol_views
from geomodel import arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'bastone'
K = 16
GB = -1.15
SX = 0.62
SLIDE_Z0, SLIDE_Z1 = -6.9, 3.0
SLIDE_Y0, SLIDE_MID, SLIDE_Y1 = 3.55, 4.55, 5.95
BORE_Y = 5.0
MUZZLE_Z = SLIDE_Z0 - 0.02
PORT = (-2.1, 0.1, 4.55, 5.5)
SIGHT_Y = 6.32


def build_slide(m):
    s = m.part('slide', ID, [0, 4.8, -0.7])
    pz0, pz1, py0, py1 = PORT
    CORE = -0.28
    round_bar(s, 'z', (CORE, SLIDE_MID, SLIDE_Z0 + 0.35), (SX, SLIDE_Y1, SLIDE_Z1), 'slide', r=0.3,
              corners=(1, 0, 0, 0), data={'decal': 'upper'})
    for z0, z1 in ((SLIDE_Z0 + 0.35, pz0), (pz1, SLIDE_Z1)):
        round_bar(s, 'z', (-SX, SLIDE_MID, z0), (CORE, SLIDE_Y1, z1), 'slide', r=0.3, corners=(0, 1, 0, 0),
                  data={'decal': 'upper'})
    round_bar(s, 'z', (-SX, py1, pz0), (CORE, SLIDE_Y1, pz1), 'slide', r=0.3, corners=(0, 1, 0, 0),
              data={'decal': 'upper'})
    s.bar(-0.45, CORE, SLIDE_MID - 0.1, py1, pz0, pz1, 'port')
    octagon(s, 'z', (-0.08, BORE_Y), 0.3, pz0 + 0.1, pz1 - 0.05, 'steel')
    round_bar(s, 'z', (-SX + 0.02, SLIDE_Y0, SLIDE_Z0), (SX - 0.02, SLIDE_MID, SLIDE_Z1), 'slide', r=0.1,
              corners=(0, 0, 1, 1), sides=8, data={'decal': 'lower'})
    # bevelled nose: the upper slide steps down at the front
    round_bar(s, 'z', (-SX + 0.06, SLIDE_MID, SLIDE_Z0), (SX - 0.06, SLIDE_Y1 - 0.28, SLIDE_Z0 + 0.4), 'slide',
              r=0.3, corners=(1, 1, 0, 0), sides=8)
    seg_yz(s, (SLIDE_Y1 - 0.3, SLIDE_Z0 + 0.1), (SLIDE_Y1 - 0.02, SLIDE_Z0 + 0.55), 0.18, -SX + 0.12, SX - 0.12, 'slide')
    # front and rear serrations
    for zs, ze in ((1.25, 2.8), (-6.2, -5.1)):
        z = zs
        while z + 0.06 <= ze:
            for sgn in (1, -1):
                x0, x1 = sorted((sgn * (SX - 0.02), sgn * (SX + 0.008)))
                s.bar(x0, x1, SLIDE_Y0 + 0.28, SLIDE_Y1 - 0.36, z, z + 0.07, 'groove')
            z += 0.19
    # slide-mounted decocker levers (both sides)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * (SX - 0.02), sgn * (SX + 0.12)))
        round_bar(s, 'z', (x0, 5.15, 1.55), (x1, 5.45, 2.45), 'steel', r=0.06, sides=8, data={'decal': 'lever'})
    # loaded-chamber indicator and extractor (right)
    round_bar(s, 'z', (-SX - 0.03, 5.25, pz1 + 0.12), (-SX + 0.02, 5.38, 1.0), 'steel', r=0.03, sides=8)
    s.bar(-0.08, 0.08, SLIDE_Y1 - 0.02, SLIDE_Y1 + 0.03, -0.9, -0.4, 'red')
    # bore and crown in the nose
    octagon(s, 'z', (0, BORE_Y), 0.3, SLIDE_Z0 - 0.01, SLIDE_Z0 + 0.4, 'steel', sides=16, data={'decal': 'crown'})
    octagon(s, 'z', (0, BORE_Y), 0.13, SLIDE_Z0 - 0.02, SLIDE_Z0 - 0.01, 'bore', sides=8)
    # night sights: square rear notch, post front, tritium dots
    sights = m.part('sight', 'slide', [0, SLIDE_Y1, 2.3])
    round_bar(sights, 'z', (-0.48, SLIDE_Y1 - 0.04, 2.15), (0.48, SLIDE_Y1 + 0.14, 2.85), 'black', r=0.06,
              corners=(1, 1, 0, 0), sides=8)
    for sgn in (1, -1):
        x0, x1 = (0.1, 0.48) if sgn > 0 else (-0.48, -0.1)
        round_bar(sights, 'z', (x0, SLIDE_Y1 + 0.1, 2.3), (x1, SIGHT_Y + 0.1, 2.85), 'black', r=0.07,
                  corners=(1, 0, 0, 0) if sgn > 0 else (0, 1, 0, 0), sides=8)
        d0, d1 = sorted((sgn * 0.21, sgn * 0.33))
        sights.bar(d0, d1, SIGHT_Y - 0.13, SIGHT_Y - 0.01, 2.85, 2.862, 'tritium')
    round_bar(sights, 'z', (-0.08, SLIDE_Y1 - 0.04, -6.35), (0.08, SIGHT_Y + 0.02, -5.95), 'black', r=0.035, sides=8)
    sights.bar(-0.055, 0.055, SIGHT_Y - 0.13, SIGHT_Y - 0.01, -5.95, -5.938, 'tritium')
    m.part('bullet_in_barrel', 'slide', [0, BORE_Y, -0.8])
    octagon(m['bullet_in_barrel'], 'z', (0, BORE_Y), 0.17, -1.4, -0.4, 'brass')


def build_frame(m):
    f = m.part('gun', ID, [0, 0, 0])
    b = m.part('barrel', 'gun', [0, BORE_Y, 0])
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])
    m.part('laser_pos', 'gun', [0, 2.5, -4.1])
    # dust cover with an accessory rail underneath
    round_bar(f, 'z', (-0.56, 2.8, -6.1), (0.56, SLIDE_Y0, -1.45), 'poly', r=0.12, corners=(0, 0, 1, 1), sides=8)
    round_bar(f, 'z', (-0.4, 2.55, -6.05), (0.4, 2.85, -2.2), 'poly', r=0.06, corners=(0, 0, 1, 1), sides=8)
    z = -5.85
    while z < -2.4:
        f.bar(-0.43, 0.43, 2.5, 2.6, z, z + 0.16, 'poly')
        z += 0.42
    round_bar(f, 'z', (-0.56, 2.62, -1.45), (0.56, SLIDE_Y0, 2.8), 'poly', r=0.12, corners=(0, 0, 1, 1), sides=8)
    f.bar(-0.572, 0.572, 3.45, SLIDE_Y0, -6.0, 2.8, 'steel')                     # steel rail inserts
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.56, sgn * 0.62))
        disc_x(f, 3.12, -1.1, 0.11, x0, x1, 'steel')
    # squared trigger guard with a serrated, slightly hooked front
    guard = [(2.62, -1.75), (1.4, -2.05), (1.0, -1.95), (0.94, -1.2), (0.95, 0.2)] \
        + arc_pts(1.38, 0.2, 0.42, 270, 330, 2) + [(1.48, 1.25)]
    path_yz(f, guard, 0.24, -0.25, 0.25, 'poly', data={'decal': 'guard'})
    t = m.part('trigger', 'gun', [0, 2.62, -0.5])
    path_yz(t, [(2.62, -0.45)] + arc_pts(2.05, 0.2, 0.74, 128, 205, 4), 0.14, -0.13, 0.13, 'steel',
            data={'decal': 'trigger'})
    # tang and bobbed hammer
    path_yz(f, [(2.9, 3.55), (3.1, 4.08), (3.28, 4.42)], 0.3, -0.38, 0.38, 'poly')
    round_bar(f, 'z', (-0.46, 3.22, 2.8), (0.46, SLIDE_Y0, 3.9), 'poly', r=0.14, corners=(1, 1, 0, 0), sides=8)
    h = m.part('hammer', 'gun', [0, 3.6, 3.4])
    seg_yz(h, (3.5, 3.38), (4.02, 3.5), 0.3, -0.18, 0.18, 'steel')
    octagon(h, 'x', (4.02, 3.62), 0.2, -0.18, 0.18, 'steel', data={'decal': 'spur'})
    # controls (left side)
    parts = m.part('parts', 'gun', [0.6, 3.4, 0])
    rel = m.part('hold_release', 'parts', [0.6, 3.4, 0])
    round_bar(rel, 'z', (0.54, 3.22, -1.25), (0.66, 3.52, 0.25), 'steel', r=0.05, sides=8, data={'decal': 'lever'})
    disc_x(parts, 2.36, 0.95, 0.16, 0.5, 0.62, 'poly', sides=16, data={'decal': 'button'})
    disc_x(parts, 3.2, 2.0, 0.12, 0.5, 0.62, 'steel')

    g = m.part('grip', 'gun', GRIP_PIV, GRIP_ROT)
    round_bar(g, 'y', (-0.52, GB, 1.12), (0.52, 3.1, 3.86), 'poly', r=0.34, data={'decal': 'grip'})
    # finger grooves on the front strap
    for k_, yc in enumerate((1.9, 0.95, 0.0)):
        if yc - 0.4 < GB:
            continue
        octagon(g, 'x', (yc, 1.16), 0.17, -0.4, 0.4, 'poly', data={'decal': 'grip'})
    round_bar(g, 'y', (-0.44, GB, 3.7), (0.44, 2.7, 4.06), 'poly', r=0.2, corners=(1, 1, 0, 0),
              data={'decal': 'grip'})
    for sgn in (1, -1):
        corners = (1, 0, 0, 1) if sgn > 0 else (0, 1, 1, 0)
        x0, x1 = sorted((sgn * 0.4, sgn * 0.6))
        round_bar(g, 'y', (x0, GB + 0.4, 1.3), (x1, 2.6, 3.62), 'poly', r=0.12, corners=corners,
                  data={'decal': 'stipple'})
        x0, x1 = sorted((sgn * 0.6, sgn * 0.63))
        g.bar(x0, x1, 2.0, 2.5, 2.2, 2.66, 'poly', data={'decal': 'shield'})
    # flared magwell
    round_bar(g, 'y', (-0.6, GB - 0.05, 1.02), (0.6, GB + 0.22, 3.98), 'poly', r=0.16, sides=8)


def build_magazine(m):
    m.part('magazine_and_bullet', 'mag_and_lefthand', [0, 1.995, 1.6])
    m.part('magazine', 'magazine_and_bullet', [0, 1.995, 1.6])
    std = m.part('mag_standard', 'magazine', GRIP_PIV, GRIP_ROT)
    std.bar(-0.36, 0.36, GB, 3.0, 1.3, 3.45, 'blued', data={'decal': 'mag'})
    round_bar(std, 'y', (-0.5, GB - 0.3, 1.14), (0.5, GB - 0.03, 3.82), 'poly', r=0.15, sides=8)
    # extended magazines (TACZ shows the one matching the fitted attachment level)
    for lvl in (1, 2, 3):
        ext = m.part(f'mag_extended_{lvl}', 'magazine', GRIP_PIV, GRIP_ROT)
        drop = 0.42 * lvl
        ext.bar(-0.36, 0.36, GB - drop, 3.0, 1.3, 3.45, 'blued', data={'decal': 'mag'})
        round_bar(ext, 'y', (-0.5, GB - drop - 0.3, 1.14), (0.5, GB - drop - 0.03, 3.82), 'poly', r=0.15, sides=8)
        ext.bar(-0.42, 0.42, GB - drop - 0.05, GB + 0.02, 1.2, 3.75, 'poly')
    rnd = m.part('bullet_in_mag', 'magazine', GRIP_PIV, GRIP_ROT)
    octagon(rnd, 'z', (0, 3.1), 0.17, 1.8, 2.7, 'brass')
    octagon(rnd, 'z', (0, 3.1), 0.14, 1.48, 1.8, 'copper')
    top = m.part('bullet', 'magazine_and_bullet', [0, 3.3, 1.8])
    octagon(top, 'z', (0, 3.3), 0.17, 1.75, 2.65, 'brass')
    octagon(top, 'z', (0, 3.3), 0.14, 1.43, 1.75, 'copper')


def build():
    m = pistol_rig(ID, BORE_Y, MUZZLE_Z)
    build_slide(m)
    build_frame(m)
    build_magazine(m)
    pistol_views(m, SIGHT_Y - 0.07, MUZZLE_Z)
    m.part('refit_laser_view', 'view', [12, 3.4, -9.5], [0, 90, 0])
    m.part('refit_extended_mag_view', 'view', [9.075, -1.6, 2.35], [0, 90, 0])
    return m


BASE = {
    'slide': M.parkerized, 'poly': M.polymer, 'black': M.matte_black, 'steel': M.blued,
    'brass': M.brass, 'copper': M.copper, 'blued': M.blued,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    if mat == 'tritium':
        col = np.tile([[150, 255, 140]], (N, 1)).astype(float)
        col[(np.abs(x) % 0.12) < 0.0] = 0
        return M.finish(M.rgba(col))
    if mat == 'red':
        return M.finish(M.rgba(np.tile([[190, 30, 28]], (N, 1))))
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[6, 6, 7]], (N, 1))))
    if mat == 'port':
        return M.finish(M.rgba(M.blued(p, n) * 0.45))
    if mat == 'groove':
        return M.finish(M.rgba(M.bake(np.tile([[52, 55, 54]], (N, 1)).astype(float), c.data['wn'])))
    if mat == 'poly' and d in ('stipple', 'grip'):
        col = M.polymer(p, n, stipple=(d == 'stipple'))
    else:
        col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)

    if d == 'upper' and side and abs(x.mean()) > SX - 0.05:
        if n[0] > 0:
            t = M.text_mask(y, z, 'BASTONE 9', -4.6, 5.25, 7.0 / K, reverse=True)
            col = np.where(t[:, None], col * 0.55, col)
        else:
            t = M.text_mask(y, z, 'CORVARA', -2.4, 5.25, 7.0 / K)
            col = np.where(t[:, None], col * 0.55, col)
    if d in ('upper', 'lower') and face == 'south':
        col = col * M.grooves(y, 0.1, 0.3, 0.78)[:, None]
    if d == 'crown' and face == 'north':
        col = col * 0.7
    if d == 'guard' and face == 'north':
        col = col * M.grooves(y, 0.09, 0.4, 0.7)[:, None]
    if d == 'shield' and side:
        # the Corvara police shield, moulded into the grip
        cy, cz = 2.27, 2.43
        dy, dz = y - cy, z - cz
        inside = (np.abs(dz) < 0.2 - np.clip(-dy, 0, 1) * 0.6) & (dy < 0.2) & (dy > -0.25)
        col = np.where(inside[:, None], col * 1.7, col * 0.9)
    if d == 'trigger' and face == 'north':
        col = col * M.grooves(y, 0.08, 0.35, 0.72)[:, None]
    if d == 'lever' and side:
        col = col * M.grooves(z, 0.08, 0.35, 0.75)[:, None]
    if d == 'button' and side:
        col = col * M.checker(y, z, 0.07, 0.25, 0.6)[:, None]
    if d == 'spur' and face in ('up', 'south'):
        col = col * M.grooves(z + y, 0.07, 0.4, 0.6)[:, None]
    if d == 'mag' and side:
        holes = np.zeros(N, dtype=bool)
        for hy in np.arange(GB + 0.4, 2.7, 0.45):
            holes |= M.disc(z, y, 2.4, hy, 0.06)
        col = np.where(holes[:, None], col * 0.3, col)
    metal = mat in ('slide', 'steel', 'brass', 'copper', 'blued')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
