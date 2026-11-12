"""Reiger 9 — the Amsterdam police service pistol.

A slim 9 mm striker pistol: a dark graphite-nitride slide with chamfered top edges and slanted
serrations, a police-blue polymer frame with a short accessory rail, an undercut trigger guard
and a flat, light trigger with a safety blade. Orange fibre front sight, plain black rear,
a slim stippled grip with a small beavertail and the heron crest moulded into each side.
"""
import numpy as np

import materials as M
from common import GRIP_PIV, GRIP_ROT, arm_colour, pistol_rig, pistol_views
from geomodel import arc_pts, chamfer_bar, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'reiger'
K = 16
GB = -1.0                          # grip bottom (grip frame)
SX = 0.5                           # slide half width: slimmer than the Bastone
SLIDE_Z0, SLIDE_Z1 = -6.5, 2.95
SLIDE_Y0, SLIDE_MID, SLIDE_Y1 = 3.55, 4.4, 5.65
BORE_Y = 4.85
MUZZLE_Z = SLIDE_Z0 - 0.02
PORT = (-1.95, 0.05, 4.4, 5.35)    # z0, z1, y0, y1 of the ejection port (right side)
SIGHT_Y = 6.02


def build_slide(m):
    s = m.part('slide', ID, [0, 4.7, -0.7])
    pz0, pz1, py0, py1 = PORT
    CORE = -0.24
    C = 0.2                        # top-edge chamfer
    # upper slide: chamfered top edges, cut around the ejection port on the right
    chamfer_bar(s, 'z', (CORE, SLIDE_MID, SLIDE_Z0 + 0.45), (SX, SLIDE_Y1, SLIDE_Z1), 'slide', c=C,
                corners=(1, 0, 0, 0), data={'decal': 'upper'})
    for z0, z1 in ((SLIDE_Z0 + 0.45, pz0), (pz1, SLIDE_Z1)):
        chamfer_bar(s, 'z', (-SX, SLIDE_MID, z0), (CORE, SLIDE_Y1, z1), 'slide', c=C, corners=(0, 1, 0, 0),
                    data={'decal': 'upper'})
    chamfer_bar(s, 'z', (-SX, py1, pz0), (CORE, SLIDE_Y1, pz1), 'slide', c=C, corners=(0, 1, 0, 0),
                data={'decal': 'upper'})
    s.bar(-0.4, CORE, SLIDE_MID - 0.1, py1, pz0, pz1, 'port')
    octagon(s, 'z', (-0.06, BORE_Y), 0.27, pz0 + 0.1, pz1 - 0.05, 'steel')                # barrel hood
    round_bar(s, 'z', (-SX + 0.02, SLIDE_Y0, SLIDE_Z0 + 0.1), (SX - 0.02, SLIDE_MID, SLIDE_Z1), 'slide', r=0.08,
              corners=(0, 0, 1, 1), sides=8, data={'decal': 'lower'})
    # angled nose: the front of the slide is cut back at the top
    chamfer_bar(s, 'z', (-SX + 0.05, SLIDE_Y0 + 0.05, SLIDE_Z0), (SX - 0.05, SLIDE_Y1 - 0.4, SLIDE_Z0 + 0.5), 'slide',
                c=0.16, corners=(1, 1, 0, 0))
    seg_yz(s, (SLIDE_Y1 - 0.42, SLIDE_Z0 + 0.12), (SLIDE_Y1 - 0.02, SLIDE_Z0 + 0.62), 0.2, -SX + 0.14, SX - 0.14, 'slide')
    # slanted serrations at the rear, both sides (the front of the slide is kept clean)
    for zs, ze in ((1.35, 2.75),):
        z = zs
        while z + 0.06 <= ze:
            for sgn in (1, -1):
                x0, x1 = sorted((sgn * (SX - 0.02), sgn * (SX + 0.008)))
                cy = (SLIDE_Y0 + SLIDE_Y1) / 2 + 0.05
                s.box((x0, SLIDE_Y0 + 0.32, z), (x1, SLIDE_Y1 - 0.34, z + 0.07), 'groove',
                      pivot=[(x0 + x1) / 2, cy, z + 0.035], rotation=[-16, 0, 0])
            z += 0.2
    # loaded-chamber notch at the back of the port and a striker indicator at the rear
    s.bar(-SX - 0.01, -SX + 0.02, 5.2, 5.32, pz1 + 0.1, pz1 + 0.6, 'steel')
    s.bar(-0.07, 0.07, 4.95, 5.12, SLIDE_Z1, SLIDE_Z1 + 0.04, 'orange')
    # bore and crown in the nose
    octagon(s, 'z', (0, BORE_Y), 0.28, SLIDE_Z0 - 0.01, SLIDE_Z0 + 0.4, 'steel', sides=16, data={'decal': 'crown'})
    octagon(s, 'z', (0, BORE_Y), 0.13, SLIDE_Z0 - 0.02, SLIDE_Z0 - 0.01, 'bore', sides=8)
    # sights: plain black U-notch rear, orange fibre front post
    sights = m.part('sight', 'slide', [0, SLIDE_Y1, 2.3])
    round_bar(sights, 'z', (-0.42, SLIDE_Y1 - 0.04, 2.1), (0.42, SLIDE_Y1 + 0.12, 2.75), 'black', r=0.06,
              corners=(1, 1, 0, 0), sides=8)
    for sgn in (1, -1):
        x0, x1 = (0.11, 0.42) if sgn > 0 else (-0.42, -0.11)
        chamfer_bar(sights, 'z', (x0, SLIDE_Y1 + 0.08, 2.25), (x1, SIGHT_Y + 0.08, 2.75), 'black', c=0.08,
                    corners=(1, 0, 0, 0) if sgn > 0 else (0, 1, 0, 0))
    round_bar(sights, 'z', (-0.08, SLIDE_Y1 - 0.04, -6.05), (0.08, SIGHT_Y, -5.6), 'black', r=0.035, sides=8)
    sights.bar(-0.05, 0.05, SIGHT_Y - 0.14, SIGHT_Y - 0.02, -5.6, -5.585, 'fibre')
    sights.bar(-0.045, 0.045, SIGHT_Y - 0.13, SIGHT_Y - 0.03, -6.065, -5.6, 'orange')
    m.part('bullet_in_barrel', 'slide', [0, BORE_Y, -0.8])
    octagon(m['bullet_in_barrel'], 'z', (0, BORE_Y), 0.16, -1.4, -0.4, 'brass')


def build_frame(m):
    f = m.part('gun', ID, [0, 0, 0])
    b = m.part('barrel', 'gun', [0, BORE_Y, 0])
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])
    # dust cover with a short two-slot rail underneath
    round_bar(f, 'z', (-0.46, 2.85, -5.75), (0.46, SLIDE_Y0, -1.4), 'poly', r=0.14, corners=(0, 0, 1, 1), sides=8)
    round_bar(f, 'z', (-0.36, 2.6, -5.65), (0.36, 2.9, -3.1), 'poly', r=0.06, corners=(0, 0, 1, 1), sides=8)
    for z in (-5.35, -4.35):
        f.bar(-0.39, 0.39, 2.55, 2.65, z, z + 0.5, 'poly')
    round_bar(f, 'z', (-0.46, 2.66, -1.4), (0.46, SLIDE_Y0, 2.75), 'poly', r=0.12, corners=(0, 0, 1, 1), sides=8)
    f.bar(-0.472, 0.472, 3.45, SLIDE_Y0, -5.6, 2.75, 'steel')                     # steel rail inserts
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.46, sgn * 0.51))
        disc_x(f, 3.12, -1.05, 0.1, x0, x1, 'steel')
    # undercut trigger guard with a squared, slightly hooked front
    guard = [(2.66, -1.55), (1.35, -1.95), (1.0, -1.8), (0.98, -1.05), (1.02, 0.25)] \
        + arc_pts(1.42, 0.25, 0.4, 270, 330, 2) + [(1.58, 1.18)]
    path_yz(f, guard, 0.22, -0.23, 0.23, 'poly', data={'decal': 'guard'})
    # flat-faced trigger with a safety blade: the light pull
    t = m.part('trigger', 'gun', [0, 2.62, -0.5])
    path_yz(t, [(2.62, -0.42), (2.1, -0.36), (1.62, -0.38)], 0.16, -0.14, 0.14, 'steel', data={'decal': 'trigger'})
    seg_yz(t, (2.3, -0.5), (1.72, -0.5), 0.08, -0.04, 0.04, 'orange')
    # tang and beavertail over the web of the hand (no hammer: striker fired)
    path_yz(f, [(2.95, 3.5), (3.12, 4.0), (3.3, 4.4), (3.36, 4.62)], 0.28, -0.36, 0.36, 'poly')
    round_bar(f, 'z', (-0.42, 3.2, 2.75), (0.42, SLIDE_Y0, 3.85), 'poly', r=0.14, corners=(1, 1, 0, 0), sides=8)
    # controls (left side)
    parts = m.part('parts', 'gun', [0.5, 3.4, 0])
    rel = m.part('hold_release', 'parts', [0.5, 3.4, 0])
    round_bar(rel, 'z', (0.44, 3.22, -1.1), (0.56, 3.48, 0.2), 'steel', r=0.05, sides=8, data={'decal': 'lever'})
    disc_x(parts, 2.38, 0.92, 0.15, 0.42, 0.53, 'poly', sides=16, data={'decal': 'button'})
    disc_x(parts, 3.18, 1.95, 0.1, 0.42, 0.53, 'steel')                       # takedown pin

    g = m.part('grip', 'gun', GRIP_PIV, GRIP_ROT)
    round_bar(g, 'y', (-0.46, GB, 1.12), (0.46, 3.1, 3.8), 'poly', r=0.32, data={'decal': 'grip'})
    round_bar(g, 'y', (-0.4, GB, 3.62), (0.4, 2.75, 4.0), 'poly', r=0.2, corners=(1, 1, 0, 0),
              data={'decal': 'grip'})
    for sgn in (1, -1):
        corners = (1, 0, 0, 1) if sgn > 0 else (0, 1, 1, 0)
        x0, x1 = sorted((sgn * 0.36, sgn * 0.54))
        round_bar(g, 'y', (x0, GB + 0.35, 1.28), (x1, 2.65, 3.6), 'poly', r=0.12, corners=corners,
                  data={'decal': 'stipple'})
        x0, x1 = sorted((sgn * 0.54, sgn * 0.57))
        g.bar(x0, x1, 1.72, 2.48, 2.0, 2.86, 'poly', data={'decal': 'crest'})
    round_bar(g, 'y', (-0.52, GB - 0.04, 1.04), (0.52, GB + 0.18, 3.92), 'poly', r=0.12, sides=8)


def build_magazine(m):
    m.part('magazine_and_bullet', 'mag_and_lefthand', [0, 1.995, 1.6])
    m.part('magazine', 'magazine_and_bullet', [0, 1.995, 1.6])
    std = m.part('mag_standard', 'magazine', GRIP_PIV, GRIP_ROT)
    std.bar(-0.32, 0.32, GB, 3.0, 1.3, 3.4, 'blued', data={'decal': 'mag'})
    round_bar(std, 'y', (-0.44, GB - 0.28, 1.12), (0.44, GB - 0.02, 3.78), 'poly', r=0.13, sides=8)
    round_bar(std, 'y', (-0.3, GB - 0.36, 1.05), (0.3, GB - 0.2, 1.5), 'poly', r=0.08, sides=8)    # finger lip
    for lvl in (1, 2, 3):
        ext = m.part(f'mag_extended_{lvl}', 'magazine', GRIP_PIV, GRIP_ROT)
        drop = 0.38 * lvl
        ext.bar(-0.32, 0.32, GB - drop, 3.0, 1.3, 3.4, 'blued', data={'decal': 'mag'})
        round_bar(ext, 'y', (-0.44, GB - drop - 0.28, 1.12), (0.44, GB - drop - 0.02, 3.78), 'poly', r=0.13, sides=8)
        ext.bar(-0.38, 0.38, GB - drop - 0.05, GB + 0.02, 1.2, 3.7, 'poly')
    rnd = m.part('bullet_in_mag', 'magazine', GRIP_PIV, GRIP_ROT)
    octagon(rnd, 'z', (0, 3.1), 0.16, 1.8, 2.65, 'brass')
    octagon(rnd, 'z', (0, 3.1), 0.13, 1.5, 1.8, 'copper')
    top = m.part('bullet', 'magazine_and_bullet', [0, 3.3, 1.8])
    octagon(top, 'z', (0, 3.3), 0.16, 1.75, 2.6, 'brass')
    octagon(top, 'z', (0, 3.3), 0.13, 1.45, 1.75, 'copper')


def build():
    m = pistol_rig(ID, BORE_Y, MUZZLE_Z)
    build_slide(m)
    build_frame(m)
    build_magazine(m)
    pistol_views(m, SIGHT_Y - 0.07, MUZZLE_Z)
    m.part('refit_extended_mag_view', 'view', [9.075, -1.6, 2.35], [0, 90, 0])
    return m


def navy(p, n):
    """Police-blue moulded polymer."""
    return M.polymer(p, n) * np.array([[0.95, 1.08, 1.55]])


BASE = {
    'slide': lambda p, n: M.anodized(p, n) * 0.92, 'poly': navy, 'black': M.matte_black, 'steel': M.blued,
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
    if mat == 'orange':
        return M.finish(M.rgba(M.bake(np.tile([[232, 112, 30]], (N, 1)).astype(float), c.data['wn'])))
    if mat == 'fibre':
        return M.finish(M.rgba(np.tile([[255, 168, 60]], (N, 1))))
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[6, 6, 7]], (N, 1))))
    if mat == 'port':
        return M.finish(M.rgba(M.blued(p, n) * 0.45))
    if mat == 'groove':
        return M.finish(M.rgba(M.bake(np.tile([[34, 35, 40]], (N, 1)).astype(float), c.data['wn'])))
    if mat == 'poly' and d in ('stipple', 'grip'):
        col = navy(p, n) * (0.9 + 0.16 * (M.vnoise(p, 46) > 0.55))[:, None] if d == 'stipple' else navy(p, n)
    else:
        col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)

    if d == 'upper' and side and abs(x.mean()) > SX - 0.05:
        if n[0] > 0:
            t = M.text_mask(y, z, 'REIGER 9', -4.4, 5.18, 7.0 / K, reverse=True)
        else:
            t = M.text_mask(y, z, 'AMSTERDAM', -2.15, 5.18, 7.0 / K)
        col = np.where(t[:, None], col * 1.9, col)
    if d in ('upper', 'lower') and face == 'south':
        col = col * M.grooves(y, 0.1, 0.3, 0.78)[:, None]
    if d == 'crown' and face == 'north':
        col = col * 0.7
    if d == 'guard' and face == 'north':
        col = col * M.grooves(y, 0.09, 0.4, 0.7)[:, None]
    if d == 'crest' and side:
        # the heron crest: a ring with the bird standing in it, neck folded, beak forward
        cy, cz = 2.1, 2.43
        dy, dz = y - cy, z - cz
        r = np.sqrt(dy * dy + dz * dz)
        ring = (r < 0.36) & (r > 0.29)
        body = ((dz - 0.06) / 0.15) ** 2 + ((dy + 0.02) / 0.08) ** 2 < 1
        neck = (np.abs(dz + 0.08 + 0.05 * np.sin(dy * 14)) < 0.03) & (dy > 0) & (dy < 0.2)
        beak = (np.abs(dy - 0.2) < 0.022) & (dz < -0.06) & (dz > -0.24)
        legs = (np.abs(dz - 0.04) < 0.018) & (dy < -0.08) & (dy > -0.28)
        col = np.where((ring | body | neck | beak | legs)[:, None], np.array([[150, 158, 178]]), col * 0.85)
    if d == 'trigger' and face == 'north':
        col = col * M.grooves(y, 0.08, 0.35, 0.8)[:, None]
    if d == 'lever' and side:
        col = col * M.grooves(z, 0.08, 0.35, 0.75)[:, None]
    if d == 'button' and side:
        col = col * M.checker(y, z, 0.07, 0.25, 0.6)[:, None]
    if d == 'mag' and side:
        holes = np.zeros(N, dtype=bool)
        for hy in np.arange(GB + 0.4, 2.7, 0.45):
            holes |= M.disc(z, y, 2.35, hy, 0.055)
        col = np.where(holes[:, None], col * 0.3, col)
    metal = mat in ('slide', 'steel', 'brass', 'copper', 'blued')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
