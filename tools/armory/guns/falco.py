"""Falco — a semi-automatic .308 marksman rifle.

Flat-dark-earth receivers and a round slotted free-float handguard, a long fluted barrel with a slim
three-port brake, a folded bipod under the handguard, folding sights on a full-length rail, a black
pistol grip, a straight ten-round magazine and a fixed precision stock with a black cheek riser.

Built on the same AR-pattern frame as the Bulwark (TACZ's hold, hands and camera anchors).
"""
import math

import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'falco'
K = 14
BORE_Y = 9.62
MUZZLE_Z = -19.6
SIGHT_Y = 12.62
MAG_DEG = -3.0                     # a straight box, leaning very slightly forward
MAG_PIV = [0, 6.9, 2.0]
GRIP_PIV = [0, 7.4, 7.6]
FP_CAM = ((-2.45, 12.9, 14.68), (-2.45, 11.6, -20), 60)       # preview only: TACZ's hip camera


def layered(part, lo, hi, r, corners, mat, step=0.12, **kw):
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    round_bar(part, 'x', (x0 + step, y0, z0), (x1 - step, y1, z1), mat, r=r, corners=corners, **kw)
    iy0 = y0 + (step if corners[1] or corners[2] else 0)
    iy1 = y1 - (step if corners[0] or corners[3] else 0)
    iz0 = z0 + (step if corners[2] or corners[3] else 0)
    iz1 = z1 - (step if corners[0] or corners[1] else 0)
    round_bar(part, 'x', (x0, iy0, iz0), (x1, iy1, iz1), mat, r=max(0.05, r - step), corners=corners, **kw)


def rig(m):
    m.part('root', None, [0, 7.1, 6.85])
    m.part('gun_and_righthand', 'root', [0, 7.1, 6.85])
    m.part('mag_and_lefthand', 'root', [0, 5, 2])
    g = m.part(ID, 'gun_and_righthand', [0, 7.1, 6.85])
    off = np.array([-6.875, -13.825, 6.8])
    m.part('righthand', 'gun_and_righthand', list(np.array([6, 19, 0]) + off), [91.51126, 6.99759, -179.81584])
    rh = m.part('righthand_pos', 'righthand', list(np.array([0, 8, 0]) + off))
    lo = np.array([4, 8, -2]) + off
    rh.box(list(lo), list(lo + [4, 12, 4]), 'arm', data={'k': 2})
    off = np.array([8.05, -11.75, -5])
    m.part('lefthand', 'mag_and_lefthand', list(np.array([-6, 19, 0]) + off), [96.3949, -30.74097, -137.03831])
    lh = m.part('lefthand_pos', 'lefthand', list(np.array([0, 8, 0]) + off))
    lo = np.array([-8, 8, -2]) + off
    lh.box(list(lo), list(lo + [4, 12, 4]), 'arm', data={'k': 2})
    m.part('scope_pos', ID, [0, 11.3, 5.95])                    # optics sit on the receiver rail
    m.part('muzzle_flash', ID, [0, BORE_Y, MUZZLE_Z - 0.4])
    m.part('shell', ID, [-0.2, 9.75, 2.2])
    m.part('constraint', ID, [0, 12.64, -1])
    return g


def views(m):
    m.part('camera', None, [2.45, 12.9, 13.68])
    m.part('view', None, [0, 0, 8])
    m.part('idle_view', 'view', [2.45, 12.9, 14.68])
    m.part('iron_view', 'view', [0, SIGHT_Y + 0.04, 10.47])
    m.part('refit_view', 'view', [23, 10, 2], [0, 89.9, 0])
    m.part('refit_muzzle_view', 'view', [10, 9, -18], [0, 120, 0])
    m.part('refit_extended_mag_view', 'view', [10.62, 5.15, -4.72], [0, 117.5, 0])
    m.part('refit_scope_view', 'view', [8, 12.93, 12.3], [0, 50, 0])
    m.part('positioning', None, [0, 0, 0])
    m.part('thirdperson_hand', 'positioning', [0, 7.03, 6.65])
    m.part('ground', 'positioning', [0, -0.9, 4.65])
    m.part('fixed', 'positioning', [0.88, 7, 5.04], [0, 90, 0])


def build_upper(m):
    u = m.part('upper', ID, [0, 9.8, 4.0])
    # upper receiver
    round_bar(u, 'z', (-0.92, 8.75, -0.1), (0.92, 10.95, 9.3), 'fde', r=0.3, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'upper'})
    round_bar(u, 'z', (-0.5, 10.6, 8.5), (0.5, 11.05, 9.6), 'black', r=0.12, sides=8)                # charging handle
    # ejection port with the bolt carrier behind it, forward-assist boss
    u.bar(-0.95, -0.92, 9.15, 10.05, 1.6, 4.6, 'black')
    b = m.part('bolt', ID, [0, 9.6, 3.0])
    b.bar(-0.94, -0.88, 9.25, 9.95, 1.7, 4.5, 'steel', data={'decal': 'carrier'})
    octagon(u, 'x', (9.95, 5.2), 0.32, -1.45, -0.9, 'black', sides=8)
    # full-length top rail
    round_bar(u, 'z', (-0.5, 10.92, -12.1), (0.5, 11.3, 9.2), 'black', r=0.08, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'rail'})
    # round slotted handguard, with an end cap
    octagon(u, 'z', (0, 9.82), 1.02, -12.2, 0.15, 'fde', sides=16, data={'decal': 'guard'})
    octagon(u, 'z', (0, 9.82), 0.96, -12.45, -12.2, 'black', sides=16)
    # long fluted barrel and a slim three-port brake
    octagon(u, 'z', (0, BORE_Y), 0.32, -18.5, -12.2, 'black', sides=8, data={'decal': 'flutes'})
    octagon(u, 'z', (0, BORE_Y), 0.4, MUZZLE_Z, -18.4, 'black', sides=16, data={'decal': 'brake'})
    octagon(u, 'z', (0, BORE_Y), 0.18, MUZZLE_Z - 0.01, MUZZLE_Z + 0.02, 'bore', sides=8)
    m.part('muzzle_pos', 'upper', [0, BORE_Y, MUZZLE_Z])
    # bipod folded up under the front of the handguard
    bp = m.part('bipod', 'upper', [0, 8.6, -11.4])
    bp.bar(-0.45, 0.45, 8.45, 8.85, -11.9, -10.9, 'black')
    for sx in (-0.3, 0.3):
        octagon(bp, 'z', (sx, 8.45), 0.13, -10.9, -5.6, 'black', sides=8)
        bp.bar(sx - 0.17, sx + 0.17, 8.2, 8.5, -5.75, -5.45, 'rubber')
    # folding front sight on the rail
    fs = m.part('front_sight', 'upper', [0, 11.3, -11.2])
    seg_yz(fs, (11.3, -11.75), (12.0, -11.3), 0.32, -0.42, 0.42, 'black')
    fs.bar(-0.42, 0.42, 11.25, 11.9, -11.6, -10.8, 'black')
    for sx in (-0.38, 0.28):
        fs.bar(sx, sx + 0.1, 11.85, SIGHT_Y + 0.05, -11.45, -11.05, 'black')                  # protective ears
    fs.bar(-0.05, 0.05, 11.85, SIGHT_Y - 0.2, -11.3, -11.2, 'black')
    fs.bar(-0.05, 0.05, SIGHT_Y - 0.3, SIGHT_Y - 0.2, -11.31, -11.19, 'white')
    # folding rear sight with an aperture
    rs = m.part('rear_sight', 'upper', [0, 11.3, 6.6])
    rs.bar(-0.48, 0.48, 11.25, 11.75, 6.0, 7.2, 'black')
    seg_yz(rs, (11.6, 6.9), (12.3, 6.65), 0.3, -0.42, 0.42, 'black')
    for k in range(12):
        a = 2 * math.pi * k / 12
        cx, cy = math.cos(a) * 0.3, SIGHT_Y + math.sin(a) * 0.3
        rs.box((cx - 0.07, cy - 0.07, 6.5), (cx + 0.07, cy + 0.07, 6.75), 'black')


def build_lower(m):
    lw = m.part('lower', ID, [0, 7.8, 4.5])
    round_bar(lw, 'z', (-0.85, 7.0, -0.2), (0.85, 8.85, 9.1), 'fde', r=0.25, corners=(0, 0, 1, 1), sides=8,
              data={'decal': 'lower'})
    # flared magazine well
    layered(lw, (-0.95, 6.1, 0.35), (0.95, 7.2, 3.7), 0.3, (0, 1, 1, 0), 'fde', step=0.1)
    # trigger guard and trigger
    path_yz(lw, [(7.0, 4.1), (6.55, 4.3), (6.5, 6.3), (7.0, 6.6)], 0.22, -0.3, 0.3, 'black')
    t = m.part('trigger', ID, [0, 7.0, 5.3])
    path_yz(t, [(7.0, 5.3)] + arc_pts(6.35, 5.95, 0.7, 120, 200, 3), 0.17, -0.13, 0.13, 'steel')
    # selector and magazine catch, bolt release paddle (left)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.85, sgn * 0.93))
        disc_x(lw, 8.2, 6.9, 0.22, x0, x1, 'black', sides=8, data={'decal': 'selector'})
    disc_x(lw, 7.75, 3.95, 0.16, -0.93, -0.85, 'steel', sides=8)
    rel = m.part('release', ID, [0.9, 8.3, 4.2])
    rel.bar(0.86, 0.98, 7.9, 8.75, 3.9, 4.45, 'black', data={'decal': 'knurl'})
    # pistol grip, raked back
    g = m.part('grip', ID, GRIP_PIV, [18, 0, 0])
    layered(g, (-0.62, 2.4, 6.3), (0.62, 7.6, 8.9), 0.45, (0, 1, 1, 0), 'grip_black', data={'decal': 'grip'})
    for yc in (5.9, 4.8, 3.7):
        octagon(g, 'x', (yc, 6.3), 0.14, -0.5, 0.5, 'grip_black')
    g.bar(-0.5, 0.5, 2.25, 2.5, 6.5, 8.7, 'grip_black')
    # fixed precision stock: straight comb, black adjustable cheek riser, belly sloping to a monopod knob
    st = m.part('stock', ID, [0, 9.8, 12.0])
    layered(st, (-0.72, 8.0, 9.0), (0.72, 10.85, 17.6), 0.5, (1, 0, 0, 1), 'fde', step=0.1, data={'decal': 'stock'})
    seg_yz(st, (8.3, 10.6), (6.3, 17.4), 1.8, -0.7, 0.7, 'fde', data={'decal': 'stock'})
    disc_x(st, 7.95, 10.6, 0.85, -0.7, 0.7, 'fde', sides=16)
    round_bar(st, 'z', (-0.5, 10.8, 12.6), (0.5, 11.35, 16.8), 'black', r=0.15, corners=(1, 1, 0, 0), sides=8)
    for zp in (13.2, 16.0):
        octagon(st, 'y', (0, zp), 0.12, 10.5, 10.85, 'steel', sides=8)                        # riser posts
    octagon(st, 'y', (0, 16.6), 0.22, 4.9, 5.6, 'black', sides=8)                             # monopod knob
    st.bar(-0.7, 0.7, 5.4, 10.85, 17.55, 17.85, 'rubber')


def build_magazine(m):
    m.part('magazine', 'mag_and_lefthand', [0, 5, 2])
    for name, extra in (('mag_standard', 0), ('mag_extended_1', 1), ('mag_extended_2', 2), ('mag_extended_3', 3)):
        mag = m.part(name, 'magazine', MAG_PIV)
        _curved_mag(mag, extra)


def _curved_mag(mag, extra):
    """A straight ten-round .308 box, leaning slightly forward; longer for the extended magazines."""
    y0 = 6.95
    length = 3.2 + 1.0 * extra
    a = math.radians(-MAG_DEG)
    y1, z1 = y0 - length * math.cos(a), 2.0 - length * math.sin(a)
    seg_yz(mag, (y0, 2.0), (y1, z1), 2.9, -0.58, 0.58, 'mag', data={'decal': 'mag'})
    seg_yz(mag, (y1 + 0.05, z1), (y1 - 0.3, z1 - 0.3 * math.sin(a)), 3.05, -0.64, 0.64, 'black', data={'decal': 'base'})


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_upper(m)
    build_lower(m)
    build_magazine(m)
    views(m)
    return m


BASE = {
    'fde': M.fde, 'black': M.anodized, 'grip_black': lambda p, n: M.polymer(p, n, stipple=True) * 0.7,
    'mag': lambda p, n: M.polymer(p, n, stipple=False) * 0.6, 'steel': M.parkerized, 'rubber': M.rubber,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[8, 8, 9]], (N, 1))))
    if mat == 'white':
        return M.finish(M.rgba(np.tile([[230, 230, 220]], (N, 1))))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)
    if d == 'guard':
        # long rounded slots along the sides and underneath
        zz = np.mod(z + 12.0, 2.1)
        slots = (zz > 0.35) & (zz < 1.75) & (z > -11.6) & (z < -0.8)
        band = (np.abs(y - 9.82) < 0.28) if side else (np.abs(x) < 0.28)
        col = np.where((slots & band)[:, None], np.array([[20, 20, 18]]), col)
    if d == 'flutes' and face not in ('north', 'south'):
        col = col * np.where(np.mod(z, 1.5) < 1.15, 0.72, 1.0)[:, None]
    if d == 'rail' and face == 'up':
        col = col * M.grooves(z, 0.28, 0.45, 0.6)[:, None]
    if d == 'brake' and (side or face == 'up'):
        ports = (np.mod(z - MUZZLE_Z, 0.38) < 0.18) & (z < -18.6)
        col = np.where(ports[:, None], np.array([[12, 12, 12]]), col)
    if d == 'upper' and side and n[0] > 0:
        t = M.text_mask(y, z, 'FALCO', 0.8, 10.45, 7.0 / K, reverse=True)
        col = np.where(t[:, None], np.array([[40, 38, 34]]), col)
    if d == 'selector':
        col = col * np.where(M.disc(z, y, 6.9, 8.2, 0.05) | (np.abs(y - 8.2) < 0.04) & (z > 6.9), 1.6, 1.0)[:, None]
    if d in ('grip', 'stock') and side:
        col = col * (0.94 + 0.1 * (M.vnoise(p, 46) > 0.55))[:, None]
    if d == 'stock' and side:
        slot = (z > 14.4) & (z < 15.6) & (y > 8.0) & (y < 8.5)
        col = np.where(slot[:, None], np.array([[20, 22, 18]]), col)
    if d == 'mag' and side:
        col = col * M.grooves(y, 0.5, 0.18, 0.8)[:, None]
    if d == 'knurl':
        col = col * M.checker(z, y, 0.1, 0.3, 0.7)[:, None]
    metal = mat in ('black', 'steel')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
