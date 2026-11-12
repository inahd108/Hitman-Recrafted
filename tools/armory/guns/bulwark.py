"""Bulwark AR — a full-size 5.56 rifle.

Black anodized upper and lower, an octagonal vented free-float handguard with a full-length top rail,
folding front and rear sights, a bronze ported muzzle brake and bronze bolt carrier, olive-drab
pistol grip, curved magazine and adjustable stock with a cheek riser.

Coordinates follow TACZ's own AR-pattern rifle so its two-handed hold fits: right hand on the pistol
grip, left hand under the handguard; the magazine and left hand share a bone.
"""
import math

import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'bulwark'
K = 14
BORE_Y = 9.62
MUZZLE_Z = -14.6
SIGHT_Y = 12.62
MAG_DEG = -6.0                     # the magazine leans forward at the bottom (and curves on from there)
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
    m.part('positioning', None, [0, 0, 0])
    m.part('thirdperson_hand', 'positioning', [0, 7.03, 6.65])
    m.part('ground', 'positioning', [0, -0.9, 4.65])
    m.part('fixed', 'positioning', [0.88, 7, 5.04], [0, 90, 0])


def build_upper(m):
    u = m.part('upper', ID, [0, 9.8, 4.0])
    # upper receiver
    round_bar(u, 'z', (-0.92, 8.75, -0.1), (0.92, 10.95, 9.3), 'anod', r=0.3, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'upper'})
    round_bar(u, 'z', (-0.5, 10.6, 8.5), (0.5, 11.05, 9.6), 'anod', r=0.12, sides=8)                 # charging handle
    # ejection port with the bolt carrier behind it, forward-assist boss
    u.bar(-0.95, -0.92, 9.15, 10.05, 1.6, 4.6, 'black')
    b = m.part('bolt', ID, [0, 9.6, 3.0])
    b.bar(-0.94, -0.88, 9.25, 9.95, 1.7, 4.5, 'bronze', data={'decal': 'carrier'})
    octagon(u, 'x', (9.95, 5.2), 0.32, -1.45, -0.9, 'anod', sides=8)
    # full-length top rail
    round_bar(u, 'z', (-0.5, 10.92, -11.1), (0.5, 11.3, 9.2), 'anod', r=0.08, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'rail'})
    # octagonal vented handguard
    octagon(u, 'z', (0, 9.82), 1.08, -11.2, 0.15, 'anod', sides=8, data={'decal': 'guard'})
    octagon(u, 'z', (0, 9.82), 1.12, -11.35, -11.05, 'anod', sides=8)
    # barrel, gas block and bronze ported brake
    octagon(u, 'z', (0, BORE_Y), 0.3, -13.3, -11.2, 'black', sides=16)
    octagon(u, 'z', (0, BORE_Y), 0.46, MUZZLE_Z, -13.2, 'bronze', sides=16, data={'decal': 'brake'})
    octagon(u, 'z', (0, BORE_Y), 0.2, MUZZLE_Z - 0.01, MUZZLE_Z + 0.02, 'bore', sides=8)
    m.part('muzzle_pos', 'upper', [0, BORE_Y, MUZZLE_Z])
    # folding front sight on the rail
    fs = m.part('front_sight', 'upper', [0, 11.3, -10.2])
    seg_yz(fs, (11.3, -10.75), (12.0, -10.3), 0.32, -0.42, 0.42, 'anod')
    fs.bar(-0.42, 0.42, 11.25, 11.9, -10.6, -9.8, 'anod')
    for sx in (-0.38, 0.28):
        fs.bar(sx, sx + 0.1, 11.85, SIGHT_Y + 0.05, -10.45, -10.05, 'anod')                  # protective ears
    fs.bar(-0.05, 0.05, 11.85, SIGHT_Y - 0.2, -10.3, -10.2, 'anod')
    fs.bar(-0.05, 0.05, SIGHT_Y - 0.3, SIGHT_Y - 0.2, -10.31, -10.19, 'white')
    # folding rear sight with an aperture
    rs = m.part('rear_sight', 'upper', [0, 11.3, 6.6])
    rs.bar(-0.48, 0.48, 11.25, 11.75, 6.0, 7.2, 'anod')
    seg_yz(rs, (11.6, 6.9), (12.3, 6.65), 0.3, -0.42, 0.42, 'anod')
    for k in range(12):
        a = 2 * math.pi * k / 12
        cx, cy = math.cos(a) * 0.3, SIGHT_Y + math.sin(a) * 0.3
        rs.box((cx - 0.07, cy - 0.07, 6.5), (cx + 0.07, cy + 0.07, 6.75), 'anod')


def build_lower(m):
    lw = m.part('lower', ID, [0, 7.8, 4.5])
    round_bar(lw, 'z', (-0.85, 7.0, -0.2), (0.85, 8.85, 9.1), 'anod', r=0.25, corners=(0, 0, 1, 1), sides=8,
              data={'decal': 'lower'})
    # flared magazine well
    layered(lw, (-0.95, 6.1, 0.35), (0.95, 7.2, 3.7), 0.3, (0, 1, 1, 0), 'anod', step=0.1)
    # trigger guard and trigger
    path_yz(lw, [(7.0, 4.1), (6.55, 4.3), (6.5, 6.3), (7.0, 6.6)], 0.22, -0.3, 0.3, 'anod')
    t = m.part('trigger', ID, [0, 7.0, 5.3])
    path_yz(t, [(7.0, 5.3)] + arc_pts(6.35, 5.95, 0.7, 120, 200, 3), 0.17, -0.13, 0.13, 'steel')
    # selector and magazine catch, bolt release paddle (left)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.85, sgn * 0.93))
        disc_x(lw, 8.2, 6.9, 0.22, x0, x1, 'anod', sides=8, data={'decal': 'selector'})
    disc_x(lw, 7.75, 3.95, 0.16, -0.93, -0.85, 'steel', sides=8)
    rel = m.part('release', ID, [0.9, 8.3, 4.2])
    rel.bar(0.86, 0.98, 7.9, 8.75, 3.9, 4.45, 'anod', data={'decal': 'knurl'})
    # pistol grip, raked back
    g = m.part('grip', ID, GRIP_PIV, [18, 0, 0])
    layered(g, (-0.62, 2.4, 6.3), (0.62, 7.6, 8.9), 0.45, (0, 1, 1, 0), 'olive', data={'decal': 'grip'})
    for yc in (5.9, 4.8, 3.7):
        octagon(g, 'x', (yc, 6.3), 0.14, -0.5, 0.5, 'olive')
    g.bar(-0.5, 0.5, 2.25, 2.5, 6.5, 8.7, 'olive')
    # buffer tube and adjustable stock: flat cheek line on top, belly sloping down to the toe
    st = m.part('stock', ID, [0, 9.8, 12.0])
    octagon(st, 'z', (0, 9.8), 0.58, 9.1, 15.6, 'anod', sides=8)
    layered(st, (-0.72, 8.3, 11.6), (0.72, 11.25, 16.6), 0.5, (1, 0, 0, 1), 'olive', step=0.1,
            data={'decal': 'stock'})
    seg_yz(st, (8.6, 12.2), (7.3, 16.45), 1.7, -0.7, 0.7, 'olive', data={'decal': 'stock'})
    disc_x(st, 8.55, 12.25, 0.82, -0.7, 0.7, 'olive', sides=16)
    st.bar(-0.7, 0.7, 6.75, 11.2, 16.55, 16.85, 'rubber')


def build_magazine(m):
    m.part('magazine', 'mag_and_lefthand', [0, 5, 2])
    for name, extra in (('mag_standard', 0), ('mag_extended_1', 1), ('mag_extended_2', 2), ('mag_extended_3', 3)):
        mag = m.part(name, 'magazine', MAG_PIV)
        _curved_mag(mag, extra)


def _curved_mag(mag, extra):
    """A curved box magazine: short straight sections chained along an arc, each tipped further forward."""
    y, z = 6.95, 2.0
    pts = [(y, z)]
    for i in range(3 + extra):
        th = math.radians(-MAG_DEG + 5.5 * i)
        y, z = y - 1.6 * math.cos(th), z - 1.6 * math.sin(th)
        pts.append((y, z))
    for a, b in zip(pts, pts[1:]):
        seg_yz(mag, a, b, 2.8, -0.55, 0.55, 'olive_mag', ext=0.08, data={'decal': 'mag'})
    (ay, az), (by, bz) = pts[-2], pts[-1]
    L = math.hypot(by - ay, bz - az)
    uy, uz = (by - ay) / L, (bz - az) / L
    seg_yz(mag, (by - uy * 0.1, bz - uz * 0.1), (by + uy * 0.3, bz + uz * 0.3), 3.05, -0.64, 0.64, 'olive',
           data={'decal': 'base'})


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_upper(m)
    build_lower(m)
    build_magazine(m)
    views(m)
    return m


BASE = {
    'anod': M.anodized, 'olive': M.olive, 'olive_mag': M.olive, 'bronze': M.bronze, 'black': M.matte_black,
    'steel': M.parkerized, 'rubber': M.rubber,
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
        # long vent slots along every face but the bottom
        slots = (np.mod(z + 11.0, 1.55) > 0.35) & (np.mod(z + 11.0, 1.55) < 1.2) & (z > -10.6) & (z < -0.6)
        mid = np.abs((y - 9.82) if side else x) < 0.22
        col = np.where((slots & mid)[:, None], np.array([[14, 14, 16]]), col)
    if d == 'rail' and face == 'up':
        col = col * M.grooves(z, 0.28, 0.45, 0.6)[:, None]
    if d == 'brake' and (side or face == 'up'):
        ports = (np.mod(z - MUZZLE_Z, 0.42) < 0.2) & (z < -13.4)
        col = np.where(ports[:, None], np.array([[18, 16, 14]]), col)
    if d == 'upper' and side and n[0] > 0:
        t = M.text_mask(y, z, 'BULWARK', 1.0, 10.45, 7.0 / K, reverse=True)
        col = np.where(t[:, None], np.array([[196, 196, 188]]), col)
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
    metal = mat in ('anod', 'black', 'steel', 'bronze')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
