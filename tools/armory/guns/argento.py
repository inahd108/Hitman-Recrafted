"""Argento .45 — the agency's signature pistol.

A long-slide stainless .45: octagonal slide with a flat sighting rib, cut serrations and a real
ejection port, scroll engraving with a gold inlay line, layered ivory grips with gold medallions,
a rounded trigger guard, a curved beavertail, a skeletonised hammer and a threaded barrel.

Built the way Blockbench gun modellers build: chamfered bars (45-degree corner pieces), round parts
as 8/16-sided prisms, curves as chains of short angled segments, and thin layered trims.
"""
import numpy as np

import materials as M
from geomodel import Model, arc_pts, chamfer_bar, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'argento'
K = 16                       # texels per model unit
GRIP_ROT = [16, 0, 0]
GRIP_PIV = [0, 2.9, 2.45]

# Bedrock units. Muzzle towards -z, shooter's right is -x.
SX = 0.68
SLIDE_Z0, SLIDE_Z1 = -9.0, 3.2
SLIDE_Y0, SLIDE_MID, SLIDE_Y1 = 3.55, 4.62, 6.1
BORE_Y = 5.15
MUZZLE_Z = -9.62
PORT = (-2.45, 0.2, 4.62, 5.62)          # z0, z1, y0, y1 of the ejection port (right side)


def hands(m):
    """Arm anchors where TACZ draws the player's arms (the usual service-pistol hold)."""
    m.part('R', 'gun_and_righthand', [-0.975, 2.125, 1])
    m.part('righthand', 'R', [-0.975, 2.125, 1], [93.01689, 5.80774, -177.55323])
    rh = m.part('righthand_pos', 'righthand', [-6.975, -8.875, 1])
    rh.bar(-2.975, 0.025, -8.875, 3.125, -1, 3, 'arm', data={'k': 2})
    m.part('L', 'mag_and_lefthand', [8, -8.5, 6.2])
    m.part('lefthand', 'L', [8, -8.5, 6.2], [97.5, 0, -180])
    lh = m.part('lefthand_pos', 'lefthand', [14, -19.5, 6.2])
    lh.bar(7, 10, -19.5, -7.5, 4.2, 8.2, 'arm', data={'k': 2})


def round_x2(part, cy, cz, r, x0, x1, mat, sides=8, **kw):
    """The same boss on both sides of the gun."""
    disc_x(part, cy, cz, r, x0, x1, mat, sides=sides, **kw)
    disc_x(part, cy, cz, r, -x1, -x0, mat, sides=sides, **kw)


def build_slide(m):
    s = m.part('slide', ID, [0, 5.0, -0.7])
    pz0, pz1, py0, py1 = PORT
    CORE = -0.3
    # upper slide: rounded top edges. Left/core full length, right skin built around the port.
    round_bar(s, 'z', (CORE, SLIDE_MID, SLIDE_Z0), (SX, SLIDE_Y1, SLIDE_Z1), 'steel', r=0.44,
              corners=(1, 0, 0, 0), data={'decal': 'upper'})
    for z0, z1 in ((SLIDE_Z0, pz0), (pz1, SLIDE_Z1)):
        round_bar(s, 'z', (-SX, SLIDE_MID, z0), (CORE, SLIDE_Y1, z1), 'steel', r=0.38,
                  corners=(0, 1, 0, 0), data={'decal': 'upper'})
    round_bar(s, 'z', (-SX, py1, pz0), (CORE, SLIDE_Y1, pz1), 'steel', r=0.38, corners=(0, 1, 0, 0),
              data={'decal': 'upper'})
    s.bar(-0.5, CORE, SLIDE_MID, py1, pz0, pz1, 'port')                       # port walls
    octagon(s, 'z', (-0.1, BORE_Y), 0.36, pz0 + 0.12, pz1 - 0.06, 'blued', data={'decal': 'hood'})
    # lower slide (rails), a hair narrower so the seam reads
    round_bar(s, 'z', (-SX + 0.02, SLIDE_Y0, SLIDE_Z0), (SX - 0.02, SLIDE_MID, SLIDE_Z1), 'steel', r=0.12,
              corners=(0, 0, 1, 1), sides=8, data={'decal': 'lower'})
    # softened front end of the slide
    round_bar(s, 'x', (-SX + 0.04, SLIDE_MID, SLIDE_Z0 - 0.06), (SX - 0.04, SLIDE_Y1 - 0.08, SLIDE_Z0 + 0.3),
              'steel', r=0.22, corners=(1, 0, 0, 0), sides=8, data={'decal': 'upper'})
    # gold inlay line along both sides
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * (SX - 0.01), sgn * (SX + 0.012)))
        s.bar(x0, x1, SLIDE_MID - 0.025, SLIDE_MID + 0.025, SLIDE_Z0 + 0.4, SLIDE_Z1 - 0.3, 'gold')
    # cut serrations: fine dark grooves standing a hair proud of the flats
    for zs, ze in ((1.4, 2.95), (-8.5, -7.35)):
        z = zs
        while z + 0.05 <= ze:
            for sgn in (1, -1):
                if sgn < 0 and pz0 - 0.1 < z < pz1 + 0.1:
                    continue
                x0, x1 = sorted((sgn * (SX - 0.02), sgn * (SX + 0.006)))
                s.bar(x0, x1, SLIDE_Y0 + 0.3, SLIDE_Y1 - 0.42, z, z + 0.055, 'groove')
            z += 0.16
    # flat sighting rib on top
    round_bar(s, 'z', (-0.2, SLIDE_Y1 - 0.02, -8.0), (0.2, SLIDE_Y1 + 0.1, 2.0), 'steel', r=0.05,
              corners=(1, 1, 0, 0), sides=8, data={'decal': 'rib'})
    # nose: bushing and recoil-spring plug
    octagon(s, 'z', (0, BORE_Y), 0.52, SLIDE_Z0 - 0.12, SLIDE_Z0 + 0.02, 'steel', sides=16, data={'decal': 'bushing'})
    octagon(s, 'z', (0, 4.08), 0.3, SLIDE_Z0 - 0.07, SLIDE_Z0 + 0.02, 'steel', sides=16, data={'decal': 'plug'})
    # extractor (right), firing pin stop plate and pin (rear)
    round_bar(s, 'z', (-SX - 0.03, 5.25, pz1 + 0.15), (-SX + 0.02, 5.4, 2.3), 'steel', r=0.03, sides=8)
    round_bar(s, 'z', (-0.22, 4.55, SLIDE_Z1), (0.22, 5.45, SLIDE_Z1 + 0.02), 'steel', r=0.06, sides=8)
    octagon(s, 'z', (0, BORE_Y), 0.08, SLIDE_Z1 + 0.025, SLIDE_Z1 + 0.05, 'steel', sides=8)
    # low-profile sights: a sloped rear sight with a square notch, a slim ramped front blade
    sights = m.part('sight', 'slide', [0, 6.2, 2.4])
    round_bar(sights, 'z', (-0.46, SLIDE_Y1 - 0.04, 2.2), (0.46, 6.24, 2.8), 'black', r=0.08,
              corners=(1, 1, 0, 0), sides=8)
    for sgn in (1, -1):
        x0, x1 = (0.11, 0.42) if sgn > 0 else (-0.42, -0.11)
        round_bar(sights, 'z', (x0, 6.22, 2.36), (x1, 6.46, 2.8), 'black', r=0.07,
                  corners=(1, 0, 0, 0) if sgn > 0 else (0, 1, 0, 0), sides=8)
        d0, d1 = sorted((sgn * 0.21, sgn * 0.31))
        sights.bar(d0, d1, 6.31, 6.41, 2.8, 2.812, 'white')
    seg_yz(sights, (SLIDE_Y1 + 0.02, 2.0), (6.3, 2.42), 0.12, -0.44, 0.44, 'black')     # sloped front face
    round_bar(sights, 'z', (-0.07, SLIDE_Y1 + 0.05, -8.4), (0.07, 6.46, -8.08), 'black', r=0.035, sides=8)
    seg_yz(sights, (SLIDE_Y1 + 0.08, -8.66), (6.42, -8.3), 0.12, -0.07, 0.07, 'black')
    sights.bar(-0.05, 0.05, 6.34, 6.43, -8.08, -8.068, 'gold')
    m.part('bullet_in_barrel', 'slide', [0, BORE_Y, -0.8])
    octagon(m['bullet_in_barrel'], 'z', (0, BORE_Y), 0.2, -1.6, -0.4, 'brass')


def build_frame(m):
    f = m.part('gun', ID, [0, 0, 0])
    b = m.part('barrel', 'gun', [0, BORE_Y, 0])
    octagon(b, 'z', (0, BORE_Y), 0.3, MUZZLE_Z, SLIDE_Z0 - 0.1, 'blued', sides=16, data={'decal': 'thread'})
    octagon(b, 'z', (0, BORE_Y), 0.17, MUZZLE_Z - 0.01, MUZZLE_Z, 'bore', sides=8)
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])
    # dust cover and receiver, rounded underneath
    round_bar(f, 'z', (-0.62, 2.95, -5.7), (0.62, SLIDE_Y0, -1.4), 'steel', r=0.24, corners=(0, 0, 1, 1),
              data={'decal': 'frame'})
    round_bar(f, 'z', (-0.62, 2.65, -1.4), (0.62, SLIDE_Y0, 3.0), 'steel', r=0.14, corners=(0, 0, 1, 1),
              sides=8, data={'decal': 'frame'})
    round_bar(f, 'x', (-0.6, 2.97, -5.82), (0.6, SLIDE_Y0 - 0.02, -5.6), 'steel', r=0.18, corners=(0, 0, 1, 0),
              sides=8)
    f.bar(-0.632, 0.632, 3.45, SLIDE_Y0, -5.65, 3.0, 'steel', data={'decal': 'trim'})
    round_x2(f, 3.15, -1.15, 0.13, 0.62, 0.68, 'steel', data={'decal': 'pin'})
    round_x2(f, 3.12, 2.35, 0.1, 0.62, 0.67, 'steel', data={'decal': 'pin'})
    # rounded trigger guard with a finger hook, as a chain of short segments
    guard = [(2.7, -1.55)] + arc_pts(1.42, -1.55, 0.45, 170, 270, 4) + [(0.97, -0.7), (0.97, 0.25)] \
        + arc_pts(1.4, 0.25, 0.43, 270, 330, 2) + [(1.5, 1.28)]
    path_yz(f, guard, 0.24, -0.26, 0.26, 'steel')
    path_yz(f, [(1.66, -1.98), (1.44, -2.16), (1.26, -2.1)], 0.15, -0.23, 0.23, 'steel')
    t = m.part('trigger', 'gun', [0, 2.62, -0.55])
    path_yz(t, [(2.62, -0.5)] + arc_pts(2.05, 0.15, 0.75, 130, 205, 4), 0.14, -0.13, 0.13, 'gold',
            data={'decal': 'trigger'})
    # beavertail curving back over the web of the hand
    path_yz(f, [(2.92, 3.62), (3.12, 4.2), (3.3, 4.62), (3.44, 4.88)], 0.32, -0.38, 0.38, 'steel')
    round_bar(f, 'z', (-0.48, 3.25, 3.0), (0.48, SLIDE_Y0, 4.6), 'steel', r=0.16, corners=(1, 1, 0, 0), sides=8)
    # hammer: skeletonised ring on a short body
    h = m.part('hammer', 'gun', [0, 3.6, 3.55])
    seg_yz(h, (3.55, 3.55), (3.98, 3.66), 0.3, -0.17, 0.17, 'blued')
    path_yz(h, arc_pts(4.18, 3.82, 0.24, -90, 270, 10), 0.09, -0.16, 0.16, 'blued')
    seg_yz(h, (4.35, 3.95), (4.45, 4.26), 0.12, -0.16, 0.16, 'blued', data={'decal': 'spur'})
    # left-side controls
    parts = m.part('parts', 'gun', [0.7, 3.5, 0])
    rel = m.part('hold_release', 'parts', [0.7, 3.45, 0.1])
    round_bar(rel, 'z', (0.6, 3.26, -1.42), (0.74, 3.6, 0.12), 'blued', r=0.06, sides=8, data={'decal': 'lever'})
    disc_x(rel, 3.42, -1.42, 0.2, 0.6, 0.74, 'blued', sides=16)
    saf = m.part('safety', 'parts', [0.7, 3.5, 3.0])
    round_bar(saf, 'z', (0.6, 3.36, 2.4), (0.72, 3.6, 3.35), 'blued', r=0.05, sides=8)
    round_bar(saf, 'z', (0.72, 3.46, 2.3), (0.84, 3.6, 2.95), 'blued', r=0.05, sides=8, data={'decal': 'lever'})
    disc_x(parts, 2.38, 0.92, 0.17, 0.58, 0.7, 'blued', sides=16, data={'decal': 'button'})

    # grip assembly, built upright and tilted as a whole: a rounded block with ivory panels
    g = m.part('grip', 'gun', GRIP_PIV, GRIP_ROT)
    round_bar(g, 'y', (-0.5, -0.3, 1.1), (0.5, 3.1, 3.9), 'steel', r=0.32, data={'decal': 'grip_core'})
    g.bar(-0.3, 0.3, 0.0, 2.65, 1.095, 1.12, 'blued', data={'decal': 'strap'})
    round_bar(g, 'y', (-0.42, -0.3, 3.7), (0.42, 2.78, 4.12), 'blued', r=0.2, corners=(1, 1, 0, 0),
              data={'decal': 'mainspring'})
    for sgn in (1, -1):
        corners = (1, 0, 0, 1) if sgn > 0 else (0, 1, 1, 0)
        x0, x1 = sorted((sgn * 0.36, sgn * 0.68))
        round_bar(g, 'y', (x0, -0.02, 1.22), (x1, 2.82, 3.64), 'ivory', r=0.16, corners=corners,
                  data={'decal': 'panel'})
        x0, x1 = sorted((sgn * 0.68, sgn * 0.71))
        for sy in (0.3, 2.5):
            disc_x(g, sy, 2.43, 0.11, x0, x1, 'gold', data={'decal': 'screw'})
        x0, x1 = sorted((sgn * 0.68, sgn * 0.73))
        disc_x(g, 1.4, 2.43, 0.3, x0, x1, 'gold', sides=16, data={'decal': 'medallion'})
    round_bar(g, 'y', (-0.56, -0.34, 1.04), (0.56, -0.2, 3.98), 'steel', r=0.12, sides=8)      # magwell lip


def build_magazine(m):
    m.part('magazine_and_bullet', 'mag_and_lefthand', [0, 1.995, 1.6])
    m.part('magazine', 'magazine_and_bullet', [0, 1.995, 1.6])
    std = m.part('mag_standard', 'magazine', GRIP_PIV, GRIP_ROT)
    std.bar(-0.34, 0.34, -0.3, 3.0, 1.3, 3.5, 'blued', data={'decal': 'mag'})
    round_bar(std, 'y', (-0.5, -0.68, 1.12), (0.5, -0.32, 3.86), 'rubber', r=0.18, sides=8)
    rnd = m.part('bullet_in_mag', 'magazine', GRIP_PIV, GRIP_ROT)
    octagon(rnd, 'z', (0, 3.1), 0.2, 1.75, 2.75, 'brass')
    octagon(rnd, 'z', (0, 3.1), 0.16, 1.4, 1.75, 'copper')
    top = m.part('bullet', 'magazine_and_bullet', [0, 3.3, 1.8])
    octagon(top, 'z', (0, 3.32), 0.2, 1.7, 2.7, 'brass')
    octagon(top, 'z', (0, 3.32), 0.16, 1.32, 1.7, 'copper')


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    m.part('root', None, [0, 3.9, 0])
    m.part('gun_and_righthand', 'root', [0, 3.9, 0])
    m.part('mag_and_lefthand', 'root', [0, 1.995, 1.6])
    hands(m)
    m.part(ID, 'gun_and_righthand', [0, 3.9, 0])
    m.part('muzzle_flash', ID, [0, BORE_Y, MUZZLE_Z - 0.3])
    m.part('shell', ID, [-0.4, 5.45, -0.9])
    m.part('constraint', ID, [0, 6.275, 1.175])
    build_slide(m)
    build_frame(m)
    build_magazine(m)
    m.part('camera', None, [2.35, 7.275, 13.375])
    m.part('view', None, [8, 0, 0])
    m.part('idle_view', 'view', [2.35, 7.275, 14.375])
    m.part('iron_view', 'view', [0, 6.4, 14.875])
    m.part('refit_view', 'view', [14.1, 2.725, -1], [0, 89, 0])
    m.part('refit_muzzle_view', 'view', [5.6, 5.525, -13.0], [0, 120, 0])
    m.part('positioning', None, [8, -1, -1])
    m.part('thirdperson_hand', 'positioning', [0, 4.075, -0.15])
    m.part('ground', 'positioning', [0, -3.9, -1.1])
    m.part('fixed', 'positioning', [0.625, 4.009, -0.5375], [0, 90, 0])
    return m


# ------------------------------------------------------------------------------------
# texture
# ------------------------------------------------------------------------------------
BASE = {
    'steel': lambda p, n: M.stainless(p, n, grain=1 if abs(n[2]) > 0.5 else 2),
    'blued': M.blued, 'black': M.matte_black, 'ivory': M.ivory, 'gold': M.gold, 'brass': M.brass,
    'copper': M.copper, 'rubber': M.rubber,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    N = len(x)
    if mat == 'arm':
        skin = (y > c.hi[1] - 3.2)
        col = np.where(skin[:, None], np.array([[224, 172, 132]]), np.array([[38, 40, 48]]))
        return M.finish(M.rgba(col * (0.92 + 0.1 * M.vnoise(p, 3))[:, None]))
    if mat == 'groove':
        col = np.tile([[92, 95, 102]], (N, 1)).astype(float)
        return M.finish(M.rgba(M.bake(col, c.data['wn'], metal=True)))
    if mat == 'port':
        return M.finish(M.rgba(M.blued(p, n) * 0.5))
    if mat == 'white':
        return M.finish(M.rgba(np.tile([[242, 242, 232]], (N, 1))))
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[8, 8, 9]], (N, 1))))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)

    if d == 'upper' and side and abs(x.mean()) > 0.6:
        right = n[0] < 0
        pz0, pz1, py0, py1 = PORT
        if True:
            panel = (z > -6.85) & (z < 0.95) & (y > 4.74) & (y < 5.86)
            if right:
                panel &= ~((z > pz0 - 0.2) & (z < pz1 + 0.2))
            border = panel & ((np.abs(z + 6.85) < 0.04) | (np.abs(z - 0.95) < 0.04)
                              | (np.abs(y - 4.74) < 0.04) | (np.abs(y - 5.86) < 0.04))
            cut = panel & M.scrollwork(y, z, 5.3)
            col = np.where((cut | border)[:, None], col * 0.5, col)
    if d in ('upper', 'lower') and face == 'south':
        col = col * 0.8 * M.grooves(y, 0.12, 0.3, 0.82)[:, None]
    if d == 'rib' and face == 'up':
        col = col * M.grooves(z, 0.11, 0.35, 0.72)[:, None]
    if d == 'thread' and not (abs(n[2]) > 0.5):
        col = col * M.grooves(z, 0.07, 0.4, 0.6)[:, None]
    if d == 'bushing' and face == 'north':
        col = col * 0.82
    if d == 'strap':
        col = col * M.checker(x, y, 0.12, 0.22, 0.6)[:, None]
    if d == 'mainspring' and face == 'south':
        col = col * M.checker(x, y, 0.11, 0.24, 0.55)[:, None]
    if d == 'panel' and side:
        inner = (z > 1.42) & (z < 3.44) & (y > 0.18) & (y < 2.62)
        col = col * np.where(inner, M.checker(y, z, 0.14, 0.2, 0.8), 1.0)[:, None]
    if d == 'medallion' and side:
        cz, cy = 2.43, 1.4
        rose = ((np.abs(z - cz) < 0.035) | (np.abs(y - cy) < 0.035)
                | (np.abs(np.abs(z - cz) - np.abs(y - cy)) < 0.03)) & ~M.disc(z, y, cz, cy, 0.05)
        rim = ~M.disc(z, y, cz, cy, 0.22)
        col = np.where((rose | rim)[:, None], col * 0.66, col)
    if d == 'screw' and side:
        col = np.where((np.abs(z - 2.43) < 0.025)[:, None], col * 0.45, col)
    if d == 'trigger' and face == 'north':
        col = col * M.grooves(y, 0.09, 0.35, 0.72)[:, None]
    if d == 'lever' and side:
        col = col * M.grooves(z, 0.09, 0.35, 0.75)[:, None]
    if d == 'button' and side:
        col = col * M.checker(y, z, 0.07, 0.25, 0.6)[:, None]
    if d == 'spur' and face in ('up', 'south'):
        col = col * M.grooves(z + y, 0.07, 0.4, 0.6)[:, None]
    if d == 'mag' and side:
        holes = np.zeros(N, dtype=bool)
        for hy in (0.5, 1.1, 1.7, 2.3):
            holes |= M.disc(z, y, 2.4, hy, 0.07)
        col = np.where(holes[:, None], col * 0.3, col)
    if d == 'hood' and side:
        col = col * 1.15

    col = M.bake(col, c.data['wn'], metal=mat in ('steel', 'gold', 'blued', 'brass', 'copper'))
    return M.finish(M.rgba(col))


# ------------------------------------------------------------------------------------
# suppressor (separate TACZ attachment, origin at the muzzle, extends to -z)
# ------------------------------------------------------------------------------------
SUPP_ID = 'argento_suppressor'


def build_suppressor():
    m = Model(SUPP_ID, tex_size=256, texels_per_unit=12)
    s = m.part('silencer', None, [0, 0, 0])
    L = 7.2
    octagon(s, 'z', (0, 0), 0.64, -L + 0.4, -0.45, 'black', sides=16, data={'decal': 'tube'})
    octagon(s, 'z', (0, 0), 0.68, -0.45, 0.0, 'gold', sides=16, data={'decal': 'cap'})
    octagon(s, 'z', (0, 0), 0.68, -L, -L + 0.4, 'black', sides=16, data={'decal': 'cap'})
    octagon(s, 'z', (0, 0), 0.665, -5.66, -5.58, 'gold', sides=16)
    for z0 in (-1.2, -1.6, -2.0, -2.4):                    # grip rings
        octagon(s, 'z', (0, 0), 0.665, z0 - 0.14, z0, 'black', sides=8, data={'decal': 'ring'})
    octagon(s, 'z', (0, 0), 0.2, -L - 0.02, -L, 'bore')
    return m


def suppressor_shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    if c.mat == 'bore':
        return M.finish(M.rgba(np.tile([[6, 6, 7]], (len(x), 1))))
    col = M.gold(p, n) if c.mat == 'gold' else M.matte_black(p, n) * 1.2
    if c.data.get('decal') == 'ring':
        col = col * 0.8
    col = M.bake(col, c.data['wn'], metal=c.mat == 'gold')
    if face == 'north' and c.data.get('decal') == 'cap':
        ring = M.disc(x, y, 0, 0, 0.5) & ~M.disc(x, y, 0, 0, 0.34)
        col = np.where(ring[:, None], col * 0.6, col)
    return M.finish(M.rgba(col))
