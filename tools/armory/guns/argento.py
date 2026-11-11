"""Argento .45 — the agency's signature pistol.

A long-slide stainless .45 with a flat sighting rib, scroll engraving, ivory grips with
gold medallions, a squared trigger guard and a threaded barrel for its suppressor.
"""
import numpy as np

import materials as M
from geomodel import Model

ID = 'argento'
GRIP_ROT = [16, 0, 0]
K = 17                      # texels per model unit
GRIP_PIV = [0, 2.9, 2.45]

# slide extents (Bedrock units). Shooter's right is -x.
SX = 0.78
SLIDE_Z0, SLIDE_Z1 = -9.0, 3.2
SLIDE_Y0, SLIDE_Y1 = 3.55, 6.15
BORE_Y = 5.15
MUZZLE_Z = -9.62


def hands(m):
    """Arm anchors where TACZ draws the player's arms. Same hold as a classic service pistol."""
    m.part('R', 'gun_and_righthand', [-0.975, 2.125, 1])
    m.part('righthand', 'R', [-0.975, 2.125, 1], [93.01689, 5.80774, -177.55323])
    rh = m.part('righthand_pos', 'righthand', [-6.975, -8.875, 1])
    rh.bar(-2.975, 0.025, -8.875, 3.125, -1, 3, 'arm', data={'k': 2})
    m.part('L', 'mag_and_lefthand', [8, -8.5, 6.2])
    m.part('lefthand', 'L', [8, -8.5, 6.2], [97.5, 0, -180])
    lh = m.part('lefthand_pos', 'lefthand', [14, -19.5, 6.2])
    lh.bar(7, 10, -19.5, -7.5, 4.2, 8.2, 'arm', data={'k': 2})


def build():
    m = Model(ID, tex_size=512, texels_per_unit=K)
    m.part('root', None, [0, 3.9, 0])
    m.part('gun_and_righthand', 'root', [0, 3.9, 0])
    m.part('mag_and_lefthand', 'root', [0, 1.995, 1.6])
    hands(m)
    gun = m.part(ID, 'gun_and_righthand', [0, 3.9, 0])
    m.part('muzzle_flash', ID, [0, BORE_Y, MUZZLE_Z - 0.3])
    m.part('shell', ID, [-0.4, 5.45, -0.9])
    m.part('constraint', ID, [0, 6.275, 1.175])

    # ---- slide ---------------------------------------------------------------------
    slide = m.part('slide', ID, [0, 5.0, -0.7])
    slide.bar(-SX, SX, SLIDE_Y0, 5.72, SLIDE_Z0, SLIDE_Z1, 'steel', data={'decal': 'slide'})
    slide.bar(-0.62, 0.62, 5.72, SLIDE_Y1, SLIDE_Z0 + 0.06, SLIDE_Z1, 'steel', data={'decal': 'slide_top'})
    slide.bar(-0.36, 0.36, SLIDE_Y1, 6.27, -8.1, 2.0, 'steel', data={'decal': 'rib'})
    # bevel strips along the top corners give the slide a rounded profile
    slide.sym(0.62, 0.7, 5.72, 6.02, SLIDE_Z0 + 0.06, SLIDE_Z1, 'steel', data={'decal': 'slide'})
    # nose: bushing, recoil plug
    slide.bar(-0.56, 0.56, 4.6, 5.7, SLIDE_Z0 - 0.12, SLIDE_Z0, 'steel', data={'decal': 'bushing'})
    slide.bar(-0.42, 0.42, 3.72, 4.42, SLIDE_Z0 - 0.08, SLIDE_Z0, 'steel')
    # ejection port hood (visible through the port, moves with the slide)
    slide.bar(-0.79, -0.6, 4.62, 5.58, -2.4, 0.15, 'port')
    # sights
    sights = m.part('sight', 'slide', [0, 6.2, 2.4])
    sights.bar(-0.64, 0.64, SLIDE_Y1, 6.33, 2.12, 2.8, 'black')
    sights.sym(0.15, 0.64, 6.33, 6.76, 2.12, 2.8, 'black', data={'decal': 'rear_post'})
    sights.bar(-0.12, 0.12, 6.27, 6.8, -8.5, -8.0, 'black', data={'decal': 'front_post'})
    sights.bar(-0.07, 0.07, 6.6, 6.74, -8.02, -7.98, 'gold')
    m.part('bullet_in_barrel', 'slide', [0, BORE_Y, -0.8]).bar(-0.2, 0.2, 4.95, 5.35, -1.6, -0.4, 'brass')

    # ---- frame -----------------------------------------------------------------------
    frame = m.part('gun', ID, [0, 0, 0])
    barrel = m.part('barrel', 'gun', [0, BORE_Y, 0])
    barrel.bar(-0.31, 0.31, BORE_Y - 0.31, BORE_Y + 0.31, MUZZLE_Z, SLIDE_Z0 - 0.12, 'blued', data={'decal': 'thread'})
    barrel.bar(-0.24, 0.24, BORE_Y - 0.24, BORE_Y + 0.24, MUZZLE_Z - 0.01, MUZZLE_Z, 'bore')
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])
    # dust cover + receiver
    frame.bar(-0.72, 0.72, 2.92, SLIDE_Y0, -5.7, 1.2, 'steel', data={'decal': 'frame'})
    frame.bar(-0.72, 0.72, 2.92, SLIDE_Y0, 1.2, 3.9, 'steel', data={'decal': 'frame'})
    frame.bar(-0.64, 0.64, 2.62, 2.92, -1.95, 1.4, 'steel', data={'decal': 'frame'})
    frame.bar(-0.66, 0.66, 3.05, 3.4, -5.85, -5.7, 'steel')
    # squared trigger guard with a hooked front
    frame.bar(-0.3, 0.3, 1.18, 2.62, -2.05, -1.72, 'steel', data={'decal': 'guard_front'})
    frame.bar(-0.3, 0.3, 0.92, 1.2, -2.05, 1.45, 'steel')
    frame.bar(-0.3, 0.3, 1.2, 1.5, -2.25, -2.05, 'steel')
    # grip core, strap and panels share the grip angle
    g = dict(pivot=GRIP_PIV, rotation=GRIP_ROT)
    frame.bar(-0.58, 0.58, -0.32, 3.3, 1.0, 3.85, 'steel', data={'decal': 'grip_core'}, **g)
    frame.bar(-0.5, 0.5, -0.32, 2.75, 3.85, 4.06, 'blued', data={'decal': 'mainspring'}, **g)
    frame.sym(0.58, 0.77, -0.05, 2.78, 1.14, 3.6, 'ivory', data={'decal': 'panel'}, **g)
    frame.sym(0.77, 0.81, 1.12, 1.68, 2.1, 2.66, 'gold', data={'decal': 'medallion'}, **g)
    for sy in (0.3, 2.45):
        frame.sym(0.77, 0.8, sy - 0.11, sy + 0.11, 2.25, 2.47, 'blued', data={'decal': 'screw'}, **g)
    # beavertail grip safety
    frame.bar(-0.5, 0.5, 2.72, 3.32, 3.75, 4.75, 'steel', data={'decal': 'frame'})
    frame.bar(-0.44, 0.44, 3.06, 3.4, 4.6, 5.12, 'steel', data={'decal': 'frame'})
    # hammer (rocks back and forward when firing)
    hammer = m.part('hammer', 'gun', [0, 3.55, 3.5])
    hammer.bar(-0.19, 0.19, 3.5, 4.2, 3.42, 3.72, 'blued')
    hammer.bar(-0.19, 0.19, 4.15, 4.5, 3.5, 4.3, 'blued', data={'decal': 'hammer'})
    hammer.bar(-0.19, 0.19, 3.85, 4.2, 4.0, 4.3, 'blued')
    # trigger
    trig = m.part('trigger', 'gun', [0, 2.62, -0.6])
    trig.bar(-0.16, 0.16, 1.62, 2.62, -0.78, -0.48, 'gold', data={'decal': 'trigger'})
    # controls on the left (+x) side
    parts = m.part('parts', 'gun', [0.8, 3.5, 0])
    rel = m.part('hold_release', 'parts', [0.85, 3.5, 0.1])
    rel.bar(0.72, 0.9, 3.28, 3.72, -1.5, 0.15, 'blued', data={'decal': 'lever'})
    rel.bar(0.72, 0.92, 2.98, 3.32, -1.32, -0.98, 'blued')
    saf = m.part('safety', 'parts', [0.85, 3.5, 3.0])
    saf.bar(0.72, 0.95, 3.34, 3.6, 2.3, 3.45, 'blued', data={'decal': 'lever'})
    parts.bar(0.64, 0.8, 2.18, 2.6, 0.7, 1.08, 'blued', data={'decal': 'button'})

    # ---- magazine --------------------------------------------------------------------
    mab = m.part('magazine_and_bullet', 'mag_and_lefthand', [0, 1.995, 1.6])
    mag = m.part('magazine', 'magazine_and_bullet', [0, 1.995, 1.6])
    std = m.part('mag_standard', 'magazine', [0, 1.995, 1.6])
    std.bar(-0.4, 0.4, -0.3, 3.0, 1.25, 3.55, 'blued', data={'decal': 'mag'}, **g)
    std.bar(-0.52, 0.52, -0.66, -0.3, 1.1, 3.8, 'rubber', data={'decal': 'basepad'}, **g)
    rnd = m.part('bullet_in_mag', 'magazine', [0, 3.05, 1.8])
    rnd.bar(-0.21, 0.21, 2.82, 3.24, 1.75, 2.75, 'brass', **g)
    rnd.bar(-0.17, 0.17, 2.86, 3.2, 1.35, 1.75, 'copper', **g)
    top = m.part('bullet', 'magazine_and_bullet', [0, 3.3, 1.8])
    top.bar(-0.21, 0.21, 3.08, 3.5, 1.7, 2.7, 'brass')
    top.bar(-0.17, 0.17, 3.12, 3.46, 1.3, 1.7, 'copper')

    # ---- views and anchors -------------------------------------------------------------
    m.part('camera', None, [2.35, 7.275, 13.375])
    m.part('view', None, [8, 0, 0])
    m.part('idle_view', 'view', [2.35, 7.275, 14.375])
    m.part('iron_view', 'view', [0, 6.62, 14.875])
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
def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        top = c.hi[1]
        skin = (y > top - 3.2)
        col = np.where(skin[:, None], np.array([[224, 172, 132]]), np.array([[38, 40, 48]]))
        col = col * (0.92 + 0.1 * M.vnoise(p, 3))[:, None]
        return M.finish(M.rgba(col))
    if mat == 'steel':
        col = M.stainless(p, n, grain=2 if not (abs(n[2]) > 0.5) else 1)
    elif mat == 'blued':
        col = M.blued(p, n)
    elif mat == 'black':
        col = M.matte_black(p, n)
    elif mat == 'ivory':
        col = M.ivory(p, n)
    elif mat == 'gold':
        col = M.gold(p, n)
    elif mat == 'brass':
        col = M.brass(p, n)
    elif mat == 'copper':
        col = M.copper(p, n)
    elif mat == 'rubber':
        col = M.rubber(p, n)
    elif mat == 'port':
        col = np.tile(np.array([[54, 56, 62]], dtype=float), (len(x), 1))
        col *= (0.75 + 0.35 * (y > 4.95))[:, None]
    elif mat == 'bore':
        col = np.tile(np.array([[8, 8, 9]], dtype=float), (len(x), 1))
    else:
        col = np.tile(np.array([[255, 0, 255]], dtype=float), (len(x), 1))

    # ---- decals ------------------------------------------------------------------------
    if d == 'slide' and side:
        rear = (z > 1.25) & (z < 3.0) & (y < 5.95)
        front = (z > -8.55) & (z < -7.05) & (y < 5.95)
        k = np.ones_like(z)
        k = np.where(rear, M.grooves(z, 0.2, 0.42, 0.5), k)
        k = np.where(front, M.grooves(z, 0.2, 0.42, 0.5), k)
        right = n[0] < 0
        panel = (z > -6.75) & (z < 0.95) & (y > 3.75) & (y < 5.55)
        if right:
            panel &= ~((z > -2.6) & (z < 0.35))
        frame_line = panel & ((np.abs(z + 6.75) < 0.035) | (np.abs(z - 0.95) < 0.035)
                              | (np.abs(y - 3.75) < 0.035) | (np.abs(y - 5.55) < 0.035))
        cut = panel & M.scrollwork(y, z, 4.65)
        k = np.where(cut | frame_line, 0.55, k)
        col = col * k[:, None]
        # gold inlay line under the engraving panel
        inlay = (np.abs(y - 3.66) < 0.035) & (z > -8.4) & (z < 2.9)
        col = np.where(inlay[:, None], M.gold(p, n), col)
        if right:
            port = (z > -2.45) & (z < 0.2) & (y > 4.58) & (y < 5.62)
            col = np.where(port[:, None], np.array([[20, 21, 24]]), col)
    if d in ('slide', 'slide_top') and face == 'south':
        plate = (np.abs(x) < 0.38) & (y > 4.3) & (y < 5.6)
        col = np.where(plate[:, None], col * 0.8, col)
        pin = M.disc(x, y, 0, 5.15, 0.09)
        col = np.where(pin[:, None], col * 0.45, col)
    if d == 'rib' and face == 'up':
        col = col * M.grooves(z, 0.11, 0.35, 0.72)[:, None]
    if d == 'bushing' and face == 'north':
        ring = M.disc(x, y, 0, BORE_Y, 0.52) & ~M.disc(x, y, 0, BORE_Y, 0.33)
        col = np.where(ring[:, None], col * 1.05, col * 0.8)
    if d == 'thread' and side:
        col = col * M.grooves(z, 0.07, 0.4, 0.6)[:, None]
    if d == 'rear_post' and face == 'south':
        dot = M.disc(np.abs(x), y, 0.39, 6.56, 0.07)
        col = np.where(dot[:, None], np.array([[238, 238, 228]]), col)
    if d == 'front_post' and face == 'south':
        dot = M.disc(x, y, 0, 6.6, 0.075)
        col = np.where(dot[:, None], np.array([[255, 214, 92]]), col)
    if d == 'frame' and side and c.lo[2] < -5:
        if n[0] > 0:        # left side: the name, inlaid in gold
            t = M.text_mask(y, z, 'ARGENTO .45', -1.55, 3.47, 7.0 / K)
            col = np.where(t[:, None], M.gold(p, n) * 1.05, col * 0.97)
        else:
            t = M.text_mask(y, z, 'CORVARA', -5.45, 3.47, 7.0 / K, reverse=True)
            col = np.where(t[:, None], col * 0.5, col)
    if d == 'grip_core' and face == 'north':
        col = col * M.checker(x, y, 0.13, 0.2, 0.6)[:, None]
    if d == 'mainspring' and face == 'south':
        col = col * M.checker(x, y, 0.11, 0.22, 0.55)[:, None]
    if d == 'panel' and side:
        # checkering inside a smooth border
        a, b = y, z
        inner = (b > 1.32) & (b < 3.42) & (a > 0.12) & (a < 2.6)
        k = np.where(inner, M.checker(a, b, 0.14, 0.2, 0.78), 1.0)
        col = col * k[:, None]
    if d == 'medallion' and side:
        cz, cy = 2.38, 1.4
        inside = M.disc(z, y, cz, cy, 0.27)
        rose = inside & ((np.abs(z - cz) < 0.035) | (np.abs(y - cy) < 0.035)
                         | (np.abs(np.abs(z - cz) - np.abs(y - cy)) < 0.03)) & ~M.disc(z, y, cz, cy, 0.05)
        rim = inside & ~M.disc(z, y, cz, cy, 0.23)
        col = np.where(inside[:, None], col, M.ivory(p, n))
        col = np.where((rose | rim)[:, None], col * 0.62, col)
    if d == 'screw' and side:
        cz = (c.lo[2] + c.hi[2]) / 2
        cy = (c.lo[1] + c.hi[1]) / 2
        head = M.disc(z, y, cz, cy, 0.1)
        slot = head & (np.abs(z - cz) < 0.02)
        col = np.where(head[:, None], col * 1.25, M.ivory(p, n))
        col = np.where(slot[:, None], col * 0.4, col)
    if d == 'hammer' and face in ('south', 'up'):
        col = col * M.grooves(z if face == 'up' else y, 0.08, 0.4, 0.6)[:, None]
    if d == 'trigger' and face == 'north':
        col = col * M.grooves(y, 0.09, 0.35, 0.7)[:, None]
    if d == 'lever' and side:
        col = col * M.grooves(z, 0.1, 0.35, 0.75)[:, None]
    if d == 'button' and side:
        col = col * M.checker(y, z, 0.08, 0.25, 0.6)[:, None]
    if d == 'mag' and side:
        holes = M.disc(np.zeros_like(z), y, 0, 0.0, 0) | False
        for hy in (0.6, 1.2, 1.8):
            holes = holes | M.disc(z, y, 2.4, hy, 0.07)
        col = np.where(holes[:, None], col * 0.3, col)
    if d == 'basepad' and side:
        t = M.text_mask(y, z, '45', 2.95, -0.36, 5.0 / K * 7 / 7)
        col = np.where(t[:, None], M.gold(p, n), col)

    if mat not in ('port', 'bore'):
        col = M.edge_bevel(col, uv, wh, width=0.05)
    return M.finish(M.rgba(col))


# ------------------------------------------------------------------------------------
# suppressor (separate TACZ attachment model, origin at the muzzle, extends to -z)
# ------------------------------------------------------------------------------------
SUPP_ID = 'argento_suppressor'


def build_suppressor():
    m = Model(SUPP_ID, tex_size=256, texels_per_unit=12)
    s = m.part('silencer', None, [0, 0, 0])
    L = 7.2
    r = 0.62
    oct_rot = dict(pivot=[0, 0, 0], rotation=[0, 0, 45])
    s.bar(-r, r, -r, r, -L, -0.35, 'black', data={'decal': 'tube'})
    s.bar(-r, r, -r, r, -L, -0.35, 'black', data={'decal': 'tube'}, **oct_rot)
    # end caps a touch wider, with a gold ring at the back
    for z0, z1, mat in ((-0.45, 0.0, 'gold'), (-L - 0.1, -L + 0.45, 'black')):
        s.bar(-0.66, 0.66, -0.66, 0.66, z0, z1, mat, data={'decal': 'cap'})
        s.bar(-0.66, 0.66, -0.66, 0.66, z0, z1, mat, data={'decal': 'cap'}, **oct_rot)
    s.bar(-0.2, 0.2, -0.2, 0.2, -L - 0.11, -L - 0.1, 'bore')
    return m


def suppressor_shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    if c.mat == 'bore':
        return M.finish(M.rgba(np.tile([[6, 6, 7]], (len(x), 1))))
    col = M.gold(p, n) if c.mat == 'gold' else M.matte_black(p, n) * 1.15
    d = c.data.get('decal')
    if d == 'tube' and face not in ('north', 'south'):
        knurl = (z < -1.0) & (z > -2.6)
        col = np.where(knurl[:, None], col * M.checker(z, (x + y), 0.09, 0.3, 0.55)[:, None], col)
        ring = (np.abs(z + 5.6) < 0.04)
        col = np.where(ring[:, None], M.gold(p, n), col)
        t = M.text_mask(x + y, z, 'CORVARA', -3.0, 0.18, 0.3)
        col = np.where(t[:, None], col * 2.4, col)
    if face == 'north' and d == 'cap':
        ring = M.disc(x, y, 0, 0, 0.5) & ~M.disc(x, y, 0, 0, 0.36)
        col = np.where(ring[:, None], col * 0.6, col)
    col = M.edge_bevel(col, uv, wh, width=0.05)
    return M.finish(M.rgba(col))
