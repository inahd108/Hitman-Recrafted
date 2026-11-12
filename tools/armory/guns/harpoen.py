"""Harpoen — a pneumatic speargun.

A long sea-blue anodized air chamber with a slim aluminium rail riding on top of it, a black polymer
muzzle head with a sighting hoop over the spear, a rubber sleeve where the left hand holds the tube, a
trigger housing with the spear latch and a notch rear sight, a pistol grip, and a brass charging valve
in the rear end cap. The stainless spear bolt lies along the top of the rail, its barbed head well out
past the muzzle head.

The loaded spear is the TACZ `bullet_in_mag` bone, so TACZ itself hides it when the gun is empty (first
person, third person, on the ground or in an item frame) and shows it again once a reload has fed one.
A second copy, `spear_reload`, rests hidden inside the air chamber; the reload animation brings it out
in the left hand and slides it home along the rail.

Coordinates follow TACZ's own AR-pattern rifle (as the Bulwark does) so its two-handed hold fits: right
hand on the pistol grip, left hand under the air chamber.
"""
import math

import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'harpoen'
AMMO_ID = 'spear_bolt'
K = 12
AIR_Y, AIR_R = 9.45, 0.86          # air chamber
AIR_Z0, AIR_Z1 = -16.7, 9.4
RAIL_Y0, RAIL_Y1 = 10.25, 10.85
SPEAR_Y = 11.02                    # spear shaft axis
SHAFT_R = 0.15
TAIL_Z = 3.35                      # back end of the spear, held by the latch
HEAD_Z = -18.6                     # where the shaft meets the head
TIP_Z = -20.95
MUZZLE_Z = -18.05                  # front face of the muzzle head
SIGHT_Y = 11.62
GRIP_PIV = [0, 7.4, 7.6]
HIDE = (0.0, AIR_Y - SPEAR_Y, 5.2)   # offset of the reload spear's resting place inside the air chamber
FP_CAM = ((-2.45, 12.9, 14.68), (-2.45, 11.6, -20), 60)       # preview only: TACZ's hip camera


def layered(part, lo, hi, r, corners, mat, step=0.12, **kw):
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    round_bar(part, 'x', (x0 + step, y0, z0), (x1 - step, y1, z1), mat, r=r, corners=corners, **kw)
    iy0 = y0 + (step if corners[1] or corners[2] else 0)
    iy1 = y1 - (step if corners[0] or corners[3] else 0)
    iz0 = z0 + (step if corners[2] or corners[3] else 0)
    iz1 = z1 - (step if corners[0] or corners[1] else 0)
    round_bar(part, 'x', (x0, iy0, iz0), (x1, iy1, iz1), mat, r=max(0.05, r - step), corners=corners, **kw)


def seg_xz(part, p0, p1, thick, y0, y1, mat, **kw):
    """A straight bar seen from above, from p0=(x, z) to p1=(x, z): barbs."""
    (x0, z0), (x1, z1) = p0, p1
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    ry = math.degrees(math.atan2(dx, dz))
    return part.box((cx - thick / 2, y0, cz - L / 2), (cx + thick / 2, y1, cz + L / 2), mat,
                    pivot=[cx, (y0 + y1) / 2, cz], rotation=[0, ry, 0], **kw)


def spear(part, off=(0.0, 0.0, 0.0), y=SPEAR_Y):
    """The spear bolt: stainless shaft, tail notch, ferrule, tri-cut point, two side barbs and a flopper."""
    ox, oy, oz = off
    Y = y + oy
    octagon(part, 'z', (ox, Y), SHAFT_R, HEAD_Z + oz, TAIL_Z - 0.35 + oz, 'shaft', sides=8, data={'decal': 'shaft'})
    octagon(part, 'z', (ox, Y), SHAFT_R + 0.04, TAIL_Z - 0.35 + oz, TAIL_Z + oz, 'tip', sides=8, data={'decal': 'tail'})
    octagon(part, 'z', (ox, Y), 0.2, HEAD_Z - 0.7 + oz, HEAD_Z + oz, 'tip', sides=8)                  # ferrule
    for r, z0, z1 in ((0.2, -19.3, -19.75), (0.15, -19.75, -20.2), (0.1, -20.2, -20.6), (0.05, -20.6, TIP_Z)):
        octagon(part, 'z', (ox, Y), r, z1 + oz, z0 + oz, 'tip', sides=8, data={'decal': 'point'})
    for sgn in (1, -1):
        seg_xz(part, (ox + sgn * 0.08, -19.55 + oz), (ox + sgn * 0.5, -18.65 + oz), 0.07, Y - 0.035, Y + 0.035, 'tip')
    seg_yz(part, (Y + 0.08, -19.45 + oz), (Y + 0.42, -18.7 + oz), 0.07, ox - 0.035, ox + 0.035, 'tip')


def rig(m):
    """TACZ's rifle hold, exactly as the Bulwark has it."""
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
    m.part('muzzle_flash', ID, [0, SPEAR_Y, MUZZLE_Z - 0.4])
    m.part('constraint', ID, [0, SIGHT_Y, -1])
    return g


def views(m):
    m.part('camera', None, [2.45, 12.9, 13.68])
    m.part('view', None, [0, 0, 8])
    m.part('idle_view', 'view', [2.45, 12.9, 14.68])
    m.part('iron_view', 'view', [0, SIGHT_Y + 0.04, 10.47])
    m.part('refit_view', 'view', [23, 10, 2], [0, 89.9, 0])
    m.part('positioning', None, [0, 0, 0])
    m.part('thirdperson_hand', 'positioning', [0, 7.03, 6.65])
    m.part('ground', 'positioning', [0, -0.9, 4.65])
    m.part('fixed', 'positioning', [0.88, 7, 5.04], [0, 90, 0])


def build_body(m):
    b = m.part('body', ID, [0, AIR_Y, -4])
    # air chamber, with a bumper ring at the front and a rubber sleeve for the left hand
    octagon(b, 'z', (0, AIR_Y), AIR_R, AIR_Z0, AIR_Z1, 'air', sides=16, data={'decal': 'air'})
    octagon(b, 'z', (0, AIR_Y), AIR_R + 0.08, -8.6, -1.4, 'rubber', sides=16, data={'decal': 'sleeve'})
    for zc in (-8.6, -1.4):
        octagon(b, 'z', (0, AIR_Y), AIR_R + 0.1, zc - 0.15, zc + 0.15, 'rubber', sides=16)
    # end cap and the brass charging valve
    octagon(b, 'z', (0, AIR_Y), AIR_R + 0.06, AIR_Z1, AIR_Z1 + 0.55, 'poly', sides=16, data={'decal': 'cap'})
    octagon(b, 'z', (0, AIR_Y), 0.3, AIR_Z1 + 0.55, AIR_Z1 + 0.85, 'brass', sides=8)
    octagon(b, 'z', (0, AIR_Y), 0.18, AIR_Z1 + 0.85, AIR_Z1 + 1.0, 'brass', sides=8)
    # pressure gauge on the left side of the chamber, ahead of the handle
    disc_x(b, AIR_Y + 0.1, 0.6, 0.42, AIR_R - 0.25, AIR_R + 0.18, 'steel', sides=16)
    disc_x(b, AIR_Y + 0.1, 0.6, 0.34, AIR_R + 0.18, AIR_R + 0.2, 'gauge', sides=16, data={'decal': 'gauge'})
    # the rail: a slim aluminium beam on a web over the chamber, grooved on top for the spear
    r = m.part('rail', ID, [0, RAIL_Y0, -6])
    round_bar(r, 'z', (-0.3, RAIL_Y0, -17.4), (0.3, RAIL_Y1, 2.0), 'alu', r=0.08, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'rail'})
    r.bar(-0.14, 0.14, AIR_Y + AIR_R - 0.1, RAIL_Y0 + 0.05, -16.4, 1.6, 'alu')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.14, sgn * 0.3))
        r.bar(x0, x1, RAIL_Y1 - 0.01, RAIL_Y1 + 0.06, -17.4, 2.0, 'alu')                  # groove lips
    # muzzle head: a moulded block holding chamber and rail, with cheeks and a sighting hoop over the spear
    h = m.part('muzzle_head', ID, [0, AIR_Y, -17])
    layered(h, (-0.74, AIR_Y - AIR_R - 0.12, MUZZLE_Z), (0.74, RAIL_Y1 - 0.05, -16.25), 0.35, (1, 1, 1, 1), 'poly',
            step=0.1, data={'decal': 'head'})
    octagon(h, 'z', (0, AIR_Y), AIR_R + 0.12, -16.35, -15.9, 'rubber', sides=16)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.2, sgn * 0.42))
        round_bar(h, 'z', (x0, RAIL_Y1 - 0.1, MUZZLE_Z), (x1, SPEAR_Y + 0.2, -16.55), 'poly', r=0.08,
                  corners=(1, 0, 0, 0) if sgn > 0 else (0, 1, 0, 0), sides=8)
    for k in range(9):
        a = math.pi * k / 8
        cx, cy = math.cos(a) * 0.36, SPEAR_Y + 0.12 + math.sin(a) * 0.36
        h.box((cx - 0.07, cy - 0.07, -17.75), (cx + 0.07, cy + 0.07, -17.45), 'steel')
    h.bar(-0.05, 0.05, SIGHT_Y - 0.14, SIGHT_Y, -17.66, -17.54, 'bead')
    m.part('muzzle_pos', 'muzzle_head', [0, SPEAR_Y, MUZZLE_Z])


def build_handle(m):
    hd = m.part('handle', ID, [0, 8.0, 5])
    # trigger housing: rides on the chamber and carries the spear latch on top
    round_bar(hd, 'z', (-0.72, 7.0, 1.4), (0.72, AIR_Y, 9.2), 'poly', r=0.3, corners=(0, 0, 1, 1), sides=8,
              data={'decal': 'housing'})
    round_bar(hd, 'z', (-0.5, RAIL_Y0 - 0.3, 1.8), (0.5, 11.35, 4.6), 'poly', r=0.22, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'latch'})
    hd.bar(-0.56, 0.56, AIR_Y - 0.2, RAIL_Y0 + 0.2, 1.8, 4.6, 'poly')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.5, sgn * 0.56))
        disc_x(hd, 10.75, 3.1, 0.12, x0, x1, 'steel')
    # notch rear sight on the back of the latch housing
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.09, sgn * 0.38))
        hd.bar(x0, x1, 11.3, SIGHT_Y + 0.06, 4.0, 4.4, 'steel')
    hd.bar(-0.38, 0.38, 11.3, SIGHT_Y - 0.2, 4.0, 4.4, 'steel')
    # line release lever on the left of the housing
    hd.bar(0.72, 0.8, 7.9, 8.4, 2.0, 3.6, 'steel', data={'decal': 'knurl'})
    # trigger guard and trigger
    path_yz(hd, [(7.0, 4.1), (6.55, 4.3), (6.5, 6.3), (7.0, 6.6)], 0.22, -0.28, 0.28, 'poly')
    t = m.part('trigger', ID, [0, 7.0, 5.3])
    path_yz(t, [(7.0, 5.3)] + arc_pts(6.35, 5.95, 0.7, 120, 200, 3), 0.17, -0.13, 0.13, 'steel')
    # pistol grip, raked back, with a palm swell
    g = m.part('grip', ID, GRIP_PIV, [18, 0, 0])
    layered(g, (-0.64, 2.4, 6.3), (0.64, 7.6, 8.9), 0.45, (0, 1, 1, 0), 'poly', data={'decal': 'grip'})
    for yc in (5.9, 4.8, 3.7):
        octagon(g, 'x', (yc, 6.3), 0.14, -0.5, 0.5, 'poly')
    g.bar(-0.52, 0.52, 2.25, 2.5, 6.5, 8.7, 'poly')


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_body(m)
    build_handle(m)
    loaded = m.part('bullet_in_mag', ID, [0, SPEAR_Y, TAIL_Z])
    spear(loaded)
    spare = m.part('spear_reload', ID, [0, SPEAR_Y + HIDE[1], TAIL_Z + HIDE[2]])
    spear(spare, HIDE)
    views(m)
    return m


# ---- the ammo: one spear bolt ---------------------------------------------------------------
def build_bolt_item():
    """Inventory / ground / item-frame model of the spear bolt ammo (TACZ ammo positioning bones)."""
    m = Model('spear_bolt', tex_size=512, texels_per_unit=K)
    root = m.part('root', None, [0, 0, 0])
    s = m.part('spear', 'root', [0, 0.25, 0])
    # lying on its side along z, centred on the origin
    spear(s, (0.0, 0.25 - SPEAR_Y, -(TAIL_Z + TIP_Z) / 2))
    m.part('positioning', None, [-3.025, -8.95, -11.225])
    m.part('ground', 'positioning', [0, 0, 0])
    m.part('fixed', 'positioning', [0, 0.25, 0])
    m.part('thirdperson_hand', 'positioning', [0, 0, 3])
    return m


def build_bolt_entity():
    """The spear in flight: points down -z like TACZ's rocket, trailing behind the bullet position."""
    m = Model('spear_bolt_entity', tex_size=512, texels_per_unit=20)
    s = m.part('spear', None, [0, 0, 0])
    spear(s, (0.0, -SPEAR_Y, -TIP_Z - 1.5))
    for c in s.cubes:                    # in flight it is drawn at full scale: shrink it to the in-hand size
        c.lo, c.hi = [v * 0.6 for v in c.lo], [v * 0.6 for v in c.hi]
        if c.pivot is not None:
            c.pivot = [v * 0.6 for v in c.pivot]
    return m


BASE = {
    'air': lambda p, n: M.anodized(p, n) * np.array([[0.86, 1.18, 1.42]]), 'alu': M.gunmetal,
    'poly': lambda p, n: M.polymer(p, n, stipple=False), 'rubber': M.rubber, 'steel': M.blued,
    'brass': M.brass, 'shaft': M.stainless, 'tip': lambda p, n: M.stainless(p, n) * 0.8,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    if mat == 'bead':
        return M.finish(M.rgba(np.tile([[250, 236, 120]], (N, 1))))
    if mat == 'gauge':
        col = np.tile([[226, 224, 214]], (N, 1)).astype(float)
        dz, dy = z - 0.6, y - (AIR_Y + 0.1)
        needle = (np.abs(dy - dz * 0.6) < 0.035) & (dz < 0.02) & (dz > -0.26)
        ticks = (np.abs(np.sqrt(dz * dz + dy * dy) - 0.28) < 0.03) & (np.mod(np.arctan2(dy, dz) * 3, 1.0) < 0.25)
        col = np.where(needle[:, None], np.array([[200, 40, 32]]), col)
        col = np.where(ticks[:, None], col * 0.3, col)
        return M.finish(M.rgba(col))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)
    if d == 'rail' and side and n[0] > 0:
        t = M.text_mask(y, z, 'HARPOEN', -15.6, RAIL_Y1 - 0.02, 7.0 / K, reverse=True)
        col = np.where(t[:, None], col * 0.45, col)
    if d == 'air' and not (abs(n[2]) > 0.5):
        # a pale wave line running down both sides of the chamber
        wave = (np.abs(y - AIR_Y - 0.12 * np.sin(z * 1.6)) < 0.05) & (z > -15.8) & (z < -9.2)
        col = np.where(wave[:, None], np.array([[196, 210, 222]]), col)
    if d == 'sleeve' and not (abs(n[2]) > 0.5):
        col = col * M.checker(z, y + x, 0.22, 0.2, 0.7)[:, None]
    if d == 'rail' and face == 'up':
        col = col * np.where(np.abs(x) < 0.15, 0.55, 1.0)[:, None]
    if d == 'shaft':
        col = col * (1.0 + 0.08 * np.sin(z * 0.9))[:, None]
    if d == 'tail' and face in ('up', 'down'):
        col = col * 0.5
    if d in ('grip', 'housing') and side:
        col = col * (0.93 + 0.12 * (M.vnoise(p, 46) > 0.55))[:, None]
    if d == 'cap' and face == 'south':
        col = col * M.grooves(np.arctan2(y - AIR_Y, x) * 2.0, 0.6, 0.3, 0.7)[:, None]
    if d == 'knurl':
        col = col * M.grooves(z, 0.12, 0.4, 0.7)[:, None]
    metal = mat in ('alu', 'steel', 'brass', 'shaft', 'tip', 'air')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
