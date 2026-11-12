#!/usr/bin/env python3
"""Generates every texture, model, blockstate and the language file for the mod.

    python3 tools/assets/gen_assets.py

All art is drawn procedurally so the repository needs no binary sources.
"""
import json
import os
import random

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/recrafted')


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


def rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


# ----------------------------------------------------------------------
# 16x16 sprite canvas
# ----------------------------------------------------------------------
class Sprite:
    def __init__(self, n=16):
        self.n = n
        self.p = {}

    def px(self, x, y, c):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.p[(x, y)] = c if len(c) == 4 else c + (255,)

    def rect(self, x0, y0, x1, y1, c):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.px(x, y, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(t):
                self.px(x + a, y, c)
                if t > 1:
                    self.px(x, y + a, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            for y in range(int(cy - r - 1), int(cy + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + .3:
                    self.px(x, y, c)

    def finish(self, outline=True, light=True):
        im = Image.new('RGBA', (self.n, self.n), (0, 0, 0, 0))
        pts = dict(self.p)
        if light:
            for (x, y), c in list(pts.items()):
                # top-left highlight, bottom-right shadow
                if (x - 1, y - 1) not in pts and (x, y - 1) not in pts:
                    pts[(x, y)] = shade(c, 1.18)
                elif (x + 1, y + 1) not in pts and (x, y + 1) not in pts:
                    pts[(x, y)] = shade(c, 0.8)
        if outline:
            for (x, y), c in list(self.p.items()):
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q not in pts and 0 <= q[0] < self.n and 0 <= q[1] < self.n:
                        pts[q] = shade(c, 0.32)
        for (x, y), c in pts.items():
            im.putpixel((x, y), c)
        return im


STEEL, DARK, WOOD, RED, GOLD = rgb('b9c0c7'), rgb('3a3f46'), rgb('8a5a2b'), rgb('c0392b'), rgb('e3b341')
WHITE, BLACK, GREEN, BLUE, YELLOW = rgb('f2f2ee'), rgb('1c1d21'), rgb('3f9b4a'), rgb('3a6fd8'), rgb('f1c40f')


def item_sprites():
    S = {}

    def new(name):
        s = Sprite()
        S[name] = s
        return s

    s = new('wrench'); s.line(3, 13, 9, 7, STEEL, 2); s.rect(9, 3, 12, 6, STEEL); s.rect(10, 2, 11, 4, (0, 0, 0, 0)); s.p.pop((10, 2), None); s.p.pop((11, 2), None); s.p.pop((10, 3), None); s.p.pop((11, 3), None); s.px(13, 5, STEEL)
    s = new('crowbar'); s.line(3, 13, 11, 5, rgb('34495e'), 2); s.px(12, 4, rgb('34495e')); s.rect(12, 3, 13, 3, RED); s.px(13, 4, RED); s.px(2, 13, RED); s.px(2, 12, RED)
    s = new('hammer'); s.line(3, 13, 9, 7, WOOD, 2); s.line(8, 3, 12, 7, STEEL, 3)
    s = new('lead_pipe'); s.line(3, 12, 11, 4, rgb('7f8a93'), 3); s.rect(2, 12, 4, 14, rgb('5c666e')); s.rect(11, 3, 13, 5, rgb('5c666e'))
    s = new('brick'); s.rect(2, 6, 13, 11, rgb('a5482f')); s.line(2, 8, 13, 8, rgb('d8c9b8')); s.px(7, 6, rgb('d8c9b8')); s.px(7, 7, rgb('d8c9b8')); s.px(4, 9, rgb('d8c9b8')); s.px(4, 10, rgb('d8c9b8')); s.px(10, 9, rgb('d8c9b8')); s.px(10, 10, rgb('d8c9b8')); s.px(4, 11, rgb('d8c9b8')); s.px(10, 11, rgb('d8c9b8'))
    s = new('bottle'); s.rect(6, 7, 9, 13, rgb('2e7d4f')); s.rect(7, 3, 8, 6, rgb('2e7d4f')); s.rect(7, 2, 8, 2, rgb('caa472')); s.rect(6, 9, 9, 11, rgb('efe6cf')); s.px(7, 10, RED)
    s = new('frying_pan'); s.line(2, 14, 6, 10, rgb('5a3b1e'), 2); s.disc(10, 6, 4, rgb('2b2e33')); s.disc(10, 6, 2.6, rgb('4a4f57'))
    s = new('rolling_pin'); s.line(4, 11, 11, 4, rgb('d9b98a'), 3); s.px(3, 13, WOOD); s.px(2, 14, WOOD); s.px(13, 3, WOOD); s.px(14, 2, WOOD)
    s = new('fish'); s.disc(7, 8, 3.2, rgb('8fb3c9')); s.rect(4, 7, 11, 9, rgb('8fb3c9')); s.line(12, 8, 14, 5, rgb('6f93a9')); s.line(12, 8, 14, 11, rgb('6f93a9')); s.px(13, 8, rgb('6f93a9')); s.px(4, 7, BLACK); s.rect(5, 10, 9, 10, rgb('e6eef2'))
    s = new('oar'); s.line(2, 14, 9, 7, WOOD, 1); s.line(9, 6, 12, 3, rgb('b07a3f'), 3)
    s = new('shovel'); s.line(3, 13, 9, 7, WOOD, 1); s.rect(10, 3, 13, 6, STEEL); s.px(9, 6, STEEL); s.px(2, 14, WOOD); s.px(3, 14, WOOD); s.px(2, 13, WOOD)
    s = new('golf_club'); s.line(12, 2, 5, 11, STEEL, 1); s.rect(2, 11, 5, 13, rgb('2b2e33')); s.px(13, 1, BLACK); s.px(12, 2, BLACK)
    s = new('broom'); s.line(13, 2, 7, 8, WOOD, 1); s.rect(3, 9, 7, 13, rgb('d6b24a')); s.rect(4, 8, 7, 9, rgb('8a5a2b')); s.line(3, 13, 3, 14, rgb('b8962e')); s.line(5, 13, 5, 14, rgb('b8962e')); s.line(7, 13, 7, 14, rgb('b8962e'))
    s = new('baton'); s.line(4, 12, 12, 4, rgb('25272b'), 2); s.rect(3, 12, 5, 14, rgb('4a4f57')); s.line(7, 7, 9, 9, rgb('25272b'), 1)
    s = new('candlestick'); s.rect(5, 13, 10, 14, GOLD); s.rect(7, 7, 8, 12, GOLD); s.rect(6, 6, 9, 6, GOLD); s.rect(7, 2, 8, 5, WHITE); s.px(7, 9, shade(GOLD, 1.2)); s.rect(6, 10, 9, 10, GOLD)
    s = new('fire_extinguisher'); s.rect(5, 5, 10, 14, RED); s.rect(6, 3, 9, 4, BLACK); s.line(10, 3, 12, 3, BLACK); s.line(12, 3, 12, 8, BLACK); s.rect(6, 8, 9, 10, WHITE); s.px(7, 2, STEEL)
    s = new('newspaper'); s.rect(2, 4, 13, 12, rgb('e9e4d4')); [s.line(4, y, 11, y, rgb('8d8d86')) for y in (7, 9, 11)]; s.rect(4, 5, 9, 5, BLACK); s.line(8, 4, 8, 12, rgb('c9c4b4'))
    s = new('kitchen_knife'); s.line(3, 13, 6, 10, rgb('2b2e33'), 2); s.line(7, 8, 12, 3, STEEL, 2); s.px(13, 2, STEEL)
    s = new('cleaver'); s.line(3, 13, 6, 10, rgb('5a3b1e'), 2); s.rect(7, 3, 12, 9, STEEL); s.px(11, 4, DARK); s.rect(7, 9, 12, 9, shade(STEEL, 1.15))
    s = new('scissors'); s.line(5, 9, 12, 2, STEEL); s.line(7, 11, 14, 4, STEEL); s.disc(4, 11, 1.6, RED); s.disc(7, 13, 1.6, RED); s.px(4, 11, (0, 0, 0, 0)); s.p.pop((4, 11), None); s.p.pop((7, 13), None); s.px(8, 8, DARK)
    s = new('letter_opener'); s.line(3, 13, 6, 10, GOLD, 2); s.line(7, 9, 13, 3, STEEL, 1); s.px(6, 9, GOLD); s.px(7, 10, GOLD)
    s = new('screwdriver'); s.line(3, 12, 6, 9, YELLOW, 3); s.line(8, 8, 13, 3, STEEL, 1); s.px(4, 13, BLACK)
    s = new('garden_shears'); s.line(6, 8, 12, 2, STEEL, 2); s.line(8, 10, 14, 4, STEEL, 1); s.line(2, 12, 5, 9, GREEN, 2); s.line(5, 14, 8, 11, GREEN, 2); s.px(7, 9, DARK)
    s = new('fire_axe'); s.line(3, 13, 10, 6, rgb('c9a227'), 2); s.rect(9, 2, 13, 6, RED); s.rect(13, 2, 13, 6, STEEL); s.rect(12, 1, 13, 1, STEEL)
    s = new('fishing_gaff'); s.line(2, 14, 10, 6, WOOD, 1); s.line(11, 5, 13, 3, STEEL); s.line(13, 3, 14, 5, STEEL); s.line(14, 5, 12, 7, STEEL)
    s = new('corkscrew'); s.rect(4, 3, 11, 5, WOOD); s.line(7, 6, 8, 7, STEEL); s.line(8, 7, 6, 9, STEEL); s.line(6, 9, 9, 11, STEEL); s.line(9, 11, 7, 13, STEEL); s.px(7, 14, STEEL)
    s = new('scalpel'); s.line(3, 13, 9, 7, STEEL, 1); s.line(10, 6, 12, 4, rgb('e8eef2'), 2); s.px(13, 3, rgb('e8eef2'))
    s = new('fiber_wire'); s.rect(2, 10, 4, 13, WOOD); s.rect(11, 2, 13, 5, WOOD); [s.px(x, y, rgb('9aa3ab')) for (x, y) in ((5, 10), (6, 9), (7, 9), (8, 8), (8, 7), (9, 6), (10, 6), (10, 5))]
    s = new('coin'); s.disc(8, 8, 4, GOLD); s.disc(8, 8, 2.4, shade(GOLD, 0.82)); s.px(8, 7, shade(GOLD, 1.25)); s.px(8, 8, shade(GOLD, 1.25)); s.px(8, 9, shade(GOLD, 1.25))
    s = new('pocket_radio'); s.rect(3, 6, 12, 13, rgb('2a9d8f')); s.disc(6, 10, 2, rgb('1f2a30')); s.rect(9, 8, 11, 8, WHITE); s.rect(9, 10, 11, 11, rgb('e76f51')); s.line(11, 5, 13, 1, STEEL)

    def vial(name, liquid, cap):
        s = new(name); s.rect(6, 5, 9, 13, rgb('dfe9ee')); s.rect(6, 8, 9, 13, liquid); s.rect(6, 3, 9, 4, cap); s.px(7, 6, WHITE)
    vial('emetic_poison', rgb('8bc34a'), rgb('5d4037'))
    vial('lethal_poison', rgb('7b3fa0'), rgb('1c1d21'))
    s = new('rat_poison'); s.rect(4, 4, 11, 13, YELLOW); s.rect(4, 4, 11, 5, BLACK); s.disc(7.5, 9, 1.8, BLACK); s.px(7, 9, YELLOW); s.px(8, 9, YELLOW); s.rect(7, 11, 8, 11, BLACK)

    def syringe(name, liquid):
        s = new(name); s.line(4, 11, 9, 6, rgb('e6eef2'), 2); s.line(5, 10, 7, 8, liquid, 2); s.line(11, 4, 13, 2, STEEL); s.px(10, 5, STEEL); s.line(2, 12, 4, 14, DARK); s.px(3, 12, DARK)
    syringe('sedative', rgb('4aa3df'))
    syringe('syringe', rgb('c0392b'))
    s = new('lockpick'); s.line(3, 12, 11, 4, DARK, 1); s.px(12, 4, DARK); s.px(12, 3, DARK); s.line(4, 14, 12, 7, rgb('6b737b'), 1); s.px(13, 7, rgb('6b737b')); s.rect(2, 12, 3, 14, RED)

    def card(name, col):
        s = new(name); s.rect(2, 5, 13, 11, col); s.rect(2, 7, 13, 7, shade(col, 0.6)); s.rect(4, 9, 6, 10, GOLD); s.rect(9, 9, 12, 9, WHITE)
    card('keycard_lab', rgb('27b7c9'))
    card('keycard_estate', rgb('b8862b'))
    card('keycard_harbour', rgb('2f5fb3'))
    s = new('route_planner'); s.rect(3, 3, 12, 14, rgb('8a5a2b')); s.rect(4, 4, 11, 13, rgb('f2efe4')); s.rect(6, 2, 9, 3, STEEL)
    for (x, y) in ((5, 11), (6, 10), (7, 9), (8, 9), (9, 8), (10, 6)):
        s.px(x, y, rgb('2a7de1'))
    s.px(5, 12, RED); s.px(10, 5, GREEN); s.px(8, 8, YELLOW)
    s = new('casting_card'); s.rect(2, 4, 13, 12, rgb('f2efe4')); s.rect(2, 4, 13, 5, rgb('c0392b')); s.disc(5.5, 8, 1.5, rgb('30343a')); s.rect(4, 10, 7, 11, rgb('30343a')); s.rect(9, 7, 12, 7, rgb('8d8d86')); s.rect(9, 9, 12, 9, rgb('8d8d86')); s.rect(9, 11, 11, 11, rgb('8d8d86'))
    return S


OUTFIT_COLORS = {
    'fisherman': ('2f6f8f', 'e8d9a8'), 'waiter': ('f2f2ee', '1c1d21'), 'cook': ('f7f7f2', 'c9c9c2'),
    'cleaner': ('6fa8dc', 'f2f2ee'), 'gardener': ('4e7d3a', '8a5a2b'), 'priest': ('1c1d21', 'f2f2ee'),
    'worker': ('3b5b8c', 'e67e22'), 'harbour_guard': ('1f3a6e', 'e3b341'), 'estate_guard': ('2b2e33', 'c0392b'),
    'bodyguard': ('15161a', 'f2f2ee'), 'security': ('5a6570', 'f1c40f'), 'lab_guard': ('e2c400', '2b2e33'),
    'scientist': ('f4f6f7', '27b7c9'), 'hazmat': ('f1c40f', '5a6570'),
}


def outfit_sprite(main, accent):
    s = Sprite()
    m, a = rgb(main), rgb(accent)
    s.rect(3, 5, 12, 13, m)
    s.rect(1, 5, 2, 8, m); s.rect(13, 5, 14, 8, m)
    s.px(6, 5, a); s.px(9, 5, a); s.px(7, 6, a); s.px(8, 6, a)
    s.rect(7, 7, 8, 12, shade(m, 0.88))
    s.rect(3, 13, 12, 13, a)
    return s


# ----------------------------------------------------------------------
# block textures
# ----------------------------------------------------------------------
def noise_tex(base, rnd, amt=0.08, n=16):
    im = Image.new('RGBA', (n, n))
    for x in range(n):
        for y in range(n):
            im.putpixel((x, y), shade(base, 1 + rnd.uniform(-amt, amt)))
    return im


def frame(im, c, w=1):
    n = im.width
    for i in range(n):
        for k in range(w):
            for (x, y) in ((i, k), (i, n - 1 - k), (k, i), (n - 1 - k, i)):
                im.putpixel((x, y), c)


def block_textures(rnd):
    T = {}
    for tier, col in (('lab', '27b7c9'), ('estate', 'b8862b'), ('harbour', '2f5fb3')):
        im = noise_tex(rgb('c9ced3'), rnd, 0.04)
        frame(im, rgb('8d959c'))
        for x in range(4, 12):
            for y in range(3, 13):
                im.putpixel((x, y), rgb('2b2e33'))
        for x in range(5, 11):
            for y in range(4, 7):
                im.putpixel((x, y), rgb(col))
        for (x, y) in ((5, 8), (7, 8), (9, 8), (5, 10), (7, 10), (9, 10)):
            im.putpixel((x, y), rgb('8d959c')); im.putpixel((x + 1, y), rgb('8d959c'))
        im.putpixel((10, 12), rgb('e74c3c'))
        T[f'card_reader_{tier}'] = im
    im = noise_tex(rgb('3f6b4a'), rnd, 0.06)
    frame(im, rgb('24402c'))
    for x in range(2, 14):
        im.putpixel((x, 5), rgb('24402c')); im.putpixel((x, 10), rgb('24402c'))
    for y in range(6, 10):
        im.putpixel((7, y), rgb('8d959c')); im.putpixel((8, y), rgb('8d959c'))
    T['hiding_crate_side'] = im
    im = noise_tex(rgb('355a3f'), rnd, 0.06)
    frame(im, rgb('24402c'), 2)
    for x in range(6, 10):
        im.putpixel((x, 7), rgb('8d959c')); im.putpixel((x, 8), rgb('8d959c'))
    T['hiding_crate_top'] = im
    im = Image.new('RGBA', (16, 16))
    for x in range(16):
        for y in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** .5
            c = rgb('1d3b2a') if d > 7 else shade(rgb('7dff6a'), 1.15 - d * 0.085 + rnd.uniform(-.06, .06))
            im.putpixel((x, y), c)
    frame(im, rgb('c9ced3'))
    for (x, y) in ((5, 6), (9, 5), (7, 9), (10, 10), (4, 10)):
        im.putpixel((x, y), rgb('eaffd0'))
    T['pathogen_core'] = im

    def console(screen, text):
        im = noise_tex(rgb('aeb5bb'), rnd, 0.04)
        frame(im, rgb('7d858c'))
        for x in range(2, 14):
            for y in range(2, 10):
                im.putpixel((x, y), rgb(screen))
        for (x0, x1, y) in text:
            for x in range(x0, x1 + 1):
                im.putpixel((x, y), rgb('d8fff0'))
        for x in range(3, 13, 2):
            im.putpixel((x, 12), rgb('4a4f57')); im.putpixel((x, 13), rgb('4a4f57'))
        return im
    T['lab_console'] = console('0f3b3a', ((3, 8, 3), (3, 6, 5), (3, 10, 7)))
    im = console('4a0f0f', ((3, 12, 3), (5, 10, 5), (3, 12, 7)))
    for x in range(6, 10):
        for y in range(11, 14):
            im.putpixel((x, y), rgb('e74c3c'))
    T['purge_console'] = im
    T['console_side'] = (lambda i: (frame(i, rgb('7d858c')), i)[1])(noise_tex(rgb('aeb5bb'), rnd, 0.04))
    im = noise_tex(rgb('1f6f4a'), rnd, 0.05)
    frame(im, rgb('f2f2ee'))
    for (x, y) in ((4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (9, 6), (10, 7), (9, 10), (10, 9), (8, 5), (8, 11)):
        im.putpixel((x, y), rgb('f2f2ee'))
    T['exit_point'] = im
    for name, led in (('fuse_box', '2ecc71'), ('fuse_box_broken', 'e74c3c')):
        im = noise_tex(rgb('8f969c'), rnd, 0.05)
        frame(im, rgb('5c636a'))
        for x in range(3, 13):
            for y in range(3, 12):
                im.putpixel((x, y), rgb('6b737b') if (x in (3, 12) or y in (3, 11)) else rgb('a9b0b6'))
        for (x, y) in ((8, 5), (7, 6), (8, 7), (7, 8), (8, 9)):
            im.putpixel((x, y), rgb('f1c40f'))
        im.putpixel((11, 13), rgb(led)); im.putpixel((12, 13), rgb(led))
        if 'broken' in name:
            for (x, y) in ((5, 4), (6, 6), (5, 8), (10, 9), (9, 10)):
                im.putpixel((x, y), rgb('1c1d21'))
        T[name] = im
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for x in range(16):
        for y in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** .5
            if d <= 7.6:
                im.putpixel((x, y), rgb('f4f1e8') if d > 5 else rgb('e6e0d0'))
            if d <= 3.6:
                im.putpixel((x, y), shade(rgb('c8642e'), 1 + rnd.uniform(-.15, .15)))
    for (x, y) in ((6, 6), (9, 8), (7, 9)):
        im.putpixel((x, y), rgb('5e8f3a'))
    T['meal'] = im
    T['meal_side'] = noise_tex(rgb('f4f1e8'), rnd, 0.03)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for x in range(16):
        for y in range(16):
            im.putpixel((x, y), rgb('7a1f2b') if y > 5 else (214, 232, 238, 255))
            if x in (0, 15):
                im.putpixel((x, y), (240, 248, 250, 255))
    T['drink'] = im
    return T


# ----------------------------------------------------------------------
# NPC skins (64x64, classic arms)
# ----------------------------------------------------------------------
PARTS = {  # name -> (u, v, w, h, d) of the unwrapped box; overlay offset
    'head': (0, 0, 8, 8, 8), 'body': (16, 16, 8, 12, 4), 'rarm': (40, 16, 4, 12, 4), 'rleg': (0, 16, 4, 12, 4),
    'lleg': (16, 48, 4, 12, 4), 'larm': (32, 48, 4, 12, 4),
}
OVER = {'head': (32, 0), 'body': (16, 32), 'rarm': (40, 32), 'rleg': (0, 32), 'lleg': (0, 48), 'larm': (48, 48)}
SKIN_TONES = ['f1c9a5', 'e0ac7e', 'c68e5f', '9c6b43', '6f4a2e', 'f6d7bd']
HAIR = ['2b1d14', '4a2f1b', '7a5230', 'b8893f', '1a1a1c', '8c8c8c', 'd9d9d4', '6b2f1a']


class Skin:
    def __init__(self, rnd):
        self.im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        self.rnd = rnd

    def faces(self, part, over=False):
        u, v, w, h, d = PARTS[part]
        if over:
            u, v = OVER[part]
        return dict(top=(u + d, v, w, d), bottom=(u + d + w, v, w, d), right=(u, v + d, d, h), front=(u + d, v + d, w, h),
                    left=(u + d + w, v + d, d, h), back=(u + d + w + d, v + d, w, h))

    def fill(self, part, col, over=False, rows=None, sides=('top', 'bottom', 'right', 'front', 'left', 'back'), amt=0.06):
        """rows = (r0, r1) restricts vertical range on side faces (0 = top of the part)."""
        f = self.faces(part, over)
        for name in sides:
            x0, y0, w, h = f[name]
            for x in range(w):
                for y in range(h):
                    if rows and name not in ('top', 'bottom') and not (rows[0] <= y <= rows[1]):
                        continue
                    if rows and name == 'top' and rows[0] > 0:
                        continue
                    if rows and name == 'bottom' and rows[1] < h - 1 and name == 'bottom':
                        continue
                    k = 1 + self.rnd.uniform(-amt, amt)
                    if name in ('right', 'left'):
                        k *= 0.93
                    if name == 'back':
                        k *= 0.9
                    if name == 'bottom':
                        k *= 0.8
                    self.im.putpixel((x0 + x, y0 + y), shade(col, k))

    def px(self, part, face, x, y, col, over=False):
        x0, y0, w, h = self.faces(part, over)[face]
        if 0 <= x < w and 0 <= y < h:
            self.im.putpixel((x0 + x, y0 + y), col if len(col) == 4 else col + (255,))

    def hline(self, part, face, x0, x1, y, col, over=False):
        for x in range(x0, x1 + 1):
            self.px(part, face, x, y, col, over)

    def band(self, part, y0, y1, col, over=False, sides=('right', 'front', 'left', 'back')):
        self.fill(part, col, over, rows=(y0, y1), sides=sides)


def make_skin(spec, rnd):
    s = Skin(rnd)
    tone = rgb(SKIN_TONES[spec.get('tone', 0)])
    hair = rgb(HAIR[spec.get('hair', 0)])
    shirt, pants, shoes = rgb(spec['shirt']), rgb(spec['pants']), rgb(spec.get('shoes', '2b1d14'))
    # ---- head ----
    s.fill('head', tone)
    style = spec.get('hairstyle', 'short')
    if style != 'bald':
        s.fill('head', hair, sides=('top',))
        depth = {'short': 2, 'long': 7, 'bob': 5, 'crop': 1}.get(style, 2)
        s.band('head', 0, depth, hair, sides=('right', 'left', 'back'))
        s.band('head', 0, 7 if style == 'long' else max(depth, 3), hair, sides=('back',))
        s.hline('head', 'front', 0, 7, 0, hair)
        if style in ('long', 'bob'):
            s.hline('head', 'front', 0, 7, 1, hair)
            for y in range(2, 6 if style == 'long' else 4):
                s.px('head', 'front', 0, y, hair); s.px('head', 'front', 7, y, hair)
        else:
            s.px('head', 'front', 0, 1, hair); s.px('head', 'front', 7, 1, hair)
            if rnd.random() < .5:
                s.hline('head', 'front', 0, 3, 1, hair)
    eye = rgb(spec.get('eyes', rnd.choice(['3b2a1a', '2f4f6f', '3f6f3a', '1c1d21'])))
    for (ex, wx) in ((2, 1), (5, 6)):
        s.px('head', 'front', wx, 4, WHITE)
        s.px('head', 'front', ex, 4, eye)
    s.hline('head', 'front', 1, 2, 3, shade(hair, 0.9)); s.hline('head', 'front', 5, 6, 3, shade(hair, 0.9))
    s.hline('head', 'front', 3, 4, 6, shade(tone, 0.72))
    s.px('head', 'front', 3, 5, shade(tone, 0.9)); s.px('head', 'front', 4, 5, shade(tone, 0.9))
    if spec.get('beard'):
        for y in (5, 6, 7):
            for x in range(1, 7):
                if y == 5 and 2 <= x <= 5:
                    continue
                s.px('head', 'front', x, y, shade(hair, 0.95))
        s.hline('head', 'front', 3, 4, 6, shade(tone, 0.7))
        s.band('head', 5, 7, hair, sides=('right', 'left'))
    if spec.get('moustache'):
        s.hline('head', 'front', 2, 5, 5, shade(hair, 0.9))
    if spec.get('glasses'):
        g = rgb('1c1d21')
        for x in (1, 2, 3, 4, 5, 6):
            s.px('head', 'front', x, 4, g if x in (3, 4) else (40, 60, 80, 255) if spec['glasses'] == 'dark' else (190, 220, 235, 255))
        s.px('head', 'front', 0, 4, g); s.px('head', 'front', 7, 4, g)
    # ---- torso / arms / legs ----
    s.fill('body', shirt)
    sleeve = spec.get('sleeve', 12)
    for arm in ('rarm', 'larm'):
        s.fill(arm, tone)
        s.band(arm, 0, sleeve - 1, shirt)
        s.fill(arm, shirt, sides=('top',))
        if spec.get('gloves'):
            s.band(arm, 10, 11, rgb(spec['gloves']))
            s.fill(arm, rgb(spec['gloves']), sides=('bottom',))
    for leg in ('rleg', 'lleg'):
        s.fill(leg, pants)
        s.band(leg, 10, 11, shoes)
        s.fill(leg, shoes, sides=('bottom',))
        if spec.get('shorts'):
            s.band(leg, 5, 9, tone)
    if spec.get('belt'):
        s.band('body', 11, 11, rgb(spec['belt']))
        s.px('body', 'front', 3, 11, GOLD); s.px('body', 'front', 4, 11, GOLD)
    if spec.get('collar'):
        c = rgb(spec['collar'])
        s.px('body', 'front', 2, 0, c); s.px('body', 'front', 5, 0, c); s.px('body', 'front', 3, 1, c); s.px('body', 'front', 4, 1, c)
        s.px('body', 'front', 3, 0, tone); s.px('body', 'front', 4, 0, tone)
    if spec.get('tie'):
        t = rgb(spec['tie'])
        for y in range(1, 7):
            s.px('body', 'front', 3 + (y % 2 == 0), y, t) if False else s.px('body', 'front', 3, y, t)
        s.px('body', 'front', 4, 1, t)
    if spec.get('jacket'):
        j = rgb(spec['jacket'])
        s.fill('body', j, sides=('right', 'left', 'back', 'top'))
        for y in range(12):
            for x in (0, 1, 6, 7):
                s.px('body', 'front', x, y, shade(j, 1 + rnd.uniform(-.05, .05)))
            if y > 6:
                s.px('body', 'front', 2, y, j); s.px('body', 'front', 5, y, j)
        for arm in ('rarm', 'larm'):
            s.band(arm, 0, 10, j)
            s.fill(arm, j, sides=('top',))
    if spec.get('buttons'):
        for y in (2, 4, 6, 8):
            s.px('body', 'front', 4, y, rgb(spec['buttons']))
    if spec.get('apron'):
        a = rgb(spec['apron'])
        for y in range(3, 12):
            s.hline('body', 'front', 1, 6, y, shade(a, 1 + rnd.uniform(-.04, .04)))
        s.px('body', 'front', 1, 2, a); s.px('body', 'front', 6, 2, a)
        for leg in ('rleg', 'lleg'):
            for y in range(0, 5):
                s.hline(leg, 'front', 0, 3, y, a)
    if spec.get('vest'):
        v = rgb(spec['vest'])
        for y in range(1, 9):
            for x in (0, 1, 2, 5, 6, 7):
                s.px('body', 'front', x, y, v)
        s.band('body', 1, 8, v, sides=('back', 'right', 'left'))
    if spec.get('stripe'):
        st = rgb(spec['stripe'])
        s.band('body', 5, 5, st); s.band('body', 8, 8, st)
        for arm in ('rarm', 'larm'):
            s.band(arm, 4, 4, st)
        for leg in ('rleg', 'lleg'):
            s.band(leg, 7, 7, st)
    if spec.get('badge'):
        s.px('body', 'front', 5, 2, rgb(spec['badge'])); s.px('body', 'front', 6, 2, rgb(spec['badge']))
    if spec.get('epaulettes'):
        for arm in ('rarm', 'larm'):
            s.fill(arm, rgb(spec['epaulettes']), sides=('top',))
    if spec.get('cross'):
        s.px('body', 'front', 3, 3, GOLD); s.px('body', 'front', 4, 3, GOLD); s.px('body', 'front', 3, 4, GOLD)
        s.px('body', 'front', 3, 2, GOLD); s.px('body', 'front', 3, 5, GOLD); s.px('body', 'front', 2, 3, GOLD)
    if spec.get('robe'):
        r = rgb(spec['robe'])
        for leg in ('rleg', 'lleg'):
            s.band(leg, 0, 9, r)
    if spec.get('dress'):
        r = rgb(spec['dress'])
        for leg in ('rleg', 'lleg'):
            s.band(leg, 0, 5, r)
            s.band(leg, 6, 9, tone)
    # ---- headgear (overlay layer) ----
    hat = spec.get('hat')
    if hat:
        kind, col = hat
        c = rgb(col)
        if kind == 'cap':
            s.fill('head', c, over=True, sides=('top',))
            s.band('head', 0, 1, c, over=True)
            s.hline('head', 'front', 0, 7, 2, shade(c, 0.6), over=True)
            s.px('head', 'front', 3, 0, GOLD, over=True); s.px('head', 'front', 4, 0, GOLD, over=True)
        elif kind == 'toque':
            s.fill('head', c, over=True, sides=('top',))
            s.band('head', 0, 2, c, over=True)
        elif kind == 'beanie':
            s.fill('head', c, over=True, sides=('top',))
            s.band('head', 0, 2, c, over=True)
            s.band('head', 2, 2, shade(c, 0.75), over=True)
        elif kind == 'straw':
            s.fill('head', c, over=True, sides=('top',))
            s.band('head', 0, 1, c, over=True)
            s.band('head', 1, 1, shade(c, 0.7), over=True)
        elif kind == 'scarf':
            s.fill('head', c, over=True, sides=('top',))
            s.band('head', 0, 2, c, over=True, sides=('right', 'left', 'back'))
            s.band('head', 0, 6, c, over=True, sides=('back',))
            s.hline('head', 'front', 0, 7, 0, c, over=True)
        elif kind == 'hood':     # full hazmat hood with visor
            s.fill('head', c, over=True)
            for y in range(2, 6):
                for x in range(1, 7):
                    s.px('head', 'front', x, y, (20, 30, 40, 255) if y in (2, 5) or x in (1, 6) else (70, 110, 130, 255), over=True)
            s.hline('head', 'front', 3, 4, 6, rgb('5a6570'), over=True)
            s.hline('head', 'front', 3, 4, 7, rgb('5a6570'), over=True)
        elif kind == 'helmet':
            s.fill('head', c, over=True, sides=('top',))
            s.band('head', 0, 3, c, over=True, sides=('right', 'left', 'back'))
            s.band('head', 0, 1, c, over=True, sides=('front',))
            for x in range(1, 7):
                s.px('head', 'front', x, 4, (30, 40, 50, 255), over=True)
    return s.im


def agent_skin():
    """The operative from the title screen: hand-placed pixels rather than the generic outfit kit.
    Charcoal suit, white shirt, slate tie, black gloves, dark hair combed back with a side parting."""
    s = Skin(random.Random(47))
    tone, tone_d = rgb('e2b693'), rgb('c99a78')
    hair, hair_l = rgb('1d1916'), rgb('33291f')
    suit, lapel, seam = rgb('2c2f36'), rgb('1e2026'), rgb('17191d')
    shirt, tie, knot = rgb('ecebe6'), rgb('243244'), rgb('2f4058')
    glove, shoe, shine = rgb('141416'), rgb('0e0e10'), rgb('34363c')
    # ---- head ----
    s.fill('head', tone, amt=0.02)
    s.fill('head', hair, sides=('top',), amt=0.05)
    for x in range(8):                                   # parting on his right, combed back
        s.px('head', 'top', x, 2, hair_l if x > 0 else hair)
    s.band('head', 0, 3, hair, sides=('right', 'left'))
    s.band('head', 0, 6, hair, sides=('back',))
    s.px('head', 'right', 7, 4, hair); s.px('head', 'left', 0, 4, hair)      # sideburns
    s.px('head', 'right', 3, 4, tone_d); s.px('head', 'right', 3, 5, tone_d)  # ears
    s.px('head', 'left', 4, 4, tone_d); s.px('head', 'left', 4, 5, tone_d)
    s.hline('head', 'front', 0, 7, 0, hair)
    s.px('head', 'front', 0, 1, hair); s.px('head', 'front', 1, 1, hair_l); s.px('head', 'front', 7, 1, hair)
    s.hline('head', 'front', 1, 2, 3, rgb('2a221c')); s.hline('head', 'front', 5, 6, 3, rgb('2a221c'))   # brows
    for (wx, ix) in ((1, 2), (6, 5)):
        s.px('head', 'front', wx, 4, rgb('f4f2ee'))
        s.px('head', 'front', ix, 4, rgb('2c3a46'))
    s.px('head', 'front', 3, 5, tone_d); s.px('head', 'front', 4, 5, shade(tone, 0.94))                  # nose
    s.hline('head', 'front', 3, 4, 6, rgb('a9725c')); s.px('head', 'front', 2, 6, shade(tone, 0.9))     # mouth
    for x in range(1, 7):                                                                                 # jaw, a day's stubble
        s.px('head', 'front', x, 7, shade(tone, 0.88))
    for y in (5, 6, 7):
        s.px('head', 'front', 0, y, shade(tone, 0.86)); s.px('head', 'front', 7, y, shade(tone, 0.86))
    # ---- jacket ----
    s.fill('body', suit, amt=0.025)
    rows = [  # J jacket, L lapel, W shirt, T tie, K knot, P pocket square, B button
        'JLWKKWLJ',
        'JLWTTWLJ',
        'JJLTTLPJ',
        'JJLTTLJJ',
        'JJJLLJJJ',
        'JJJJBJJJ',
        'JJJJJJJJ',
        'JJJJBJJJ',
        'JJJSJJJJ',
        'JJJSJJJJ',
        'JJJSJJJJ',
        'JJJSJJJJ',
    ]
    col = {'L': lapel, 'W': shirt, 'T': tie, 'K': knot, 'P': shirt, 'B': rgb('3b3e46'), 'S': seam}
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c in col:
                s.px('body', 'front', x, y, col[c])
    for y in range(8, 12):
        s.px('body', 'back', 3, y, seam)                       # vent
    s.band('body', 11, 11, shade(suit, 0.9), sides=('right', 'left', 'back'))
    # ---- sleeves, cuffs, gloves ----
    for arm in ('rarm', 'larm'):
        s.fill(arm, suit, amt=0.025)
        s.band(arm, 9, 9, shirt)
        s.band(arm, 10, 11, glove)
        s.fill(arm, glove, sides=('bottom',))
    s.band('rarm', 0, 8, shade(suit, 0.9), sides=('left',))    # inner faces in shadow
    s.band('larm', 0, 8, shade(suit, 0.9), sides=('right',))
    # ---- trousers and shoes ----
    for leg in ('rleg', 'lleg'):
        s.fill(leg, suit, amt=0.025)
        for y in range(0, 10):
            s.px(leg, 'front', 1 if leg == 'rleg' else 2, y, shade(suit, 1.12))   # crease
        s.band(leg, 10, 11, shoe)
        s.fill(leg, shoe, sides=('bottom',))
        s.px(leg, 'front', 1, 10, shine); s.px(leg, 'front', 2, 10, shine)
    return s.im


def D(**k):
    return k


ROLE_SKINS = {
    'civilian': [
        D(tone=0, hair=1, shirt='c94f4f', pants='3b4a66', collar='f2f2ee'),
        D(tone=1, hair=4, hairstyle='long', shirt='e8d9a8', pants='7a5230', dress='e8d9a8', shoes='8a5a2b'),
        D(tone=2, hair=5, shirt='5b7a8c', pants='4a4038', jacket='6b5a48', moustache=True),
    ],
    'tourist': [
        D(tone=5, hair=3, shirt='f39c12', pants='e8dcc0', sleeve=4, shorts=True, glasses='dark', shoes='c9b28a'),
        D(tone=0, hair=7, hairstyle='bob', shirt='48c9b0', pants='f2f2ee', sleeve=4, shorts=True, hat=('straw', 'e8d9a8'), shoes='d98880'),
        D(tone=3, hair=4, shirt='ec7063', pants='5d6d7e', sleeve=4, stripe='f7dc6f', hat=('cap', '2e86c1'), shoes='f2f2ee'),
    ],
    'fisherman': [
        D(tone=1, hair=5, shirt='2f6f8f', pants='4a4038', beard=True, hat=('beanie', 'b03a2e'), stripe='f2f2ee', shoes='1c1d21'),
        D(tone=2, hair=4, shirt='e8d9a8', pants='3b4a66', sleeve=5, vest='d4ac0d', hat=('beanie', '34495e'), shoes='1c1d21'),
    ],
    'shopkeeper': [
        D(tone=0, hair=2, shirt='f2f2ee', pants='4a4038', apron='4e7d3a', sleeve=6, moustache=True),
        D(tone=1, hair=4, hairstyle='bob', shirt='d98880', pants='5d4037', apron='f2efe4', sleeve=6),
    ],
    'waiter': [
        D(tone=0, hair=4, shirt='f2f2ee', pants='1c1d21', vest='1c1d21', tie='1c1d21', shoes='1c1d21'),
        D(tone=2, hair=1, hairstyle='bob', shirt='f2f2ee', pants='1c1d21', vest='1c1d21', tie='7b241c', shoes='1c1d21'),
    ],
    'cook': [
        D(tone=1, hair=4, shirt='f7f7f2', pants='5d6d7e', buttons='c9c9c2', hat=('toque', 'f7f7f2'), apron='f7f7f2', moustache=True),
        D(tone=5, hair=7, shirt='f7f7f2', pants='2b2e33', buttons='c9c9c2', hat=('toque', 'f7f7f2'), apron='e6e6e0'),
    ],
    'cleaner': [
        D(tone=2, hair=4, hairstyle='bob', shirt='6fa8dc', pants='6fa8dc', apron='f2f2ee', hat=('scarf', 'f2f2ee'), shoes='f2f2ee'),
        D(tone=0, hair=5, shirt='7f8c8d', pants='5d6d7e', stripe='f1c40f', gloves='f1c40f'),
    ],
    'gardener': [
        D(tone=1, hair=2, shirt='4e7d3a', pants='6b5a48', apron='7a5230', hat=('straw', 'd9c27a'), gloves='8a5a2b', sleeve=6),
        D(tone=3, hair=4, shirt='7d9c5a', pants='4a4038', vest='5a6b3a', hat=('straw', 'c9b26a'), beard=True, sleeve=6),
    ],
    'priest': [D(tone=0, hair=6, hairstyle='crop', shirt='1c1d21', pants='1c1d21', robe='1c1d21', collar='f2f2ee', cross=True, glasses='clear')],
    'worker': [
        D(tone=1, hair=4, shirt='3b5b8c', pants='3b5b8c', stripe='e67e22', hat=('helmet', 'f1c40f'), gloves='5a6570', shoes='1c1d21'),
        D(tone=4, hair=4, hairstyle='crop', shirt='3b5b8c', pants='3b5b8c', vest='e67e22', hat=('helmet', 'f2f2ee'), shoes='1c1d21'),
    ],
    'harbour_guard': [
        D(tone=0, hair=1, shirt='1f3a6e', pants='16284d', belt='1c1d21', badge='e3b341', epaulettes='e3b341', hat=('cap', '16284d'), collar='f2f2ee', shoes='1c1d21'),
        D(tone=2, hair=4, shirt='1f3a6e', pants='16284d', belt='1c1d21', badge='e3b341', epaulettes='e3b341', hat=('cap', '16284d'), moustache=True, shoes='1c1d21'),
    ],
    'estate_guard': [
        D(tone=1, hair=4, hairstyle='crop', shirt='2b2e33', pants='1c1d21', belt='5a3b1e', badge='c0392b', tie='c0392b', glasses='dark', shoes='1c1d21'),
        D(tone=3, hair=4, hairstyle='bald', shirt='2b2e33', pants='1c1d21', belt='5a3b1e', badge='c0392b', beard=True, shoes='1c1d21'),
    ],
    'bodyguard': [D(tone=0, hair=4, hairstyle='crop', shirt='f2f2ee', pants='15161a', jacket='15161a', tie='15161a', glasses='dark', shoes='0d0d0f')],
    'security': [
        D(tone=0, hair=2, hairstyle='crop', shirt='5a6570', pants='3d454d', belt='1c1d21', vest='2b2e33', badge='f1c40f', hat=('cap', '3d454d'), shoes='1c1d21'),
        D(tone=4, hair=4, hairstyle='crop', shirt='5a6570', pants='3d454d', belt='1c1d21', vest='2b2e33', badge='f1c40f', shoes='1c1d21'),
    ],
    'lab_guard': [D(tone=0, hair=4, shirt='e2c400', pants='e2c400', belt='2b2e33', vest='2b2e33', stripe='2b2e33', gloves='2b2e33', hat=('hood', 'e2c400'), shoes='2b2e33')],
    'scientist': [
        D(tone=0, hair=1, shirt='7fb3d5', pants='5d6d7e', jacket='f4f6f7', glasses='clear', tie='2c3e50', shoes='2b1d14'),
        D(tone=3, hair=4, hairstyle='bob', shirt='a9dfbf', pants='34495e', jacket='f4f6f7', badge='27b7c9', shoes='2b1d14'),
    ],
    'hazmat': [D(tone=0, hair=4, shirt='f1c40f', pants='f1c40f', stripe='5a6570', gloves='5a6570', hat=('hood', 'f1c40f'), shoes='5a6570')],
    'belmonte': [D(tone=1, hair=5, shirt='f7f1e3', pants='e8dcc0', jacket='e8dcc0', collar='f7f1e3', beard=True, glasses='dark', shoes='7a5230', belt='7a5230')],
    'varga': [D(tone=5, hair=6, hairstyle='bob', shirt='2c3e50', pants='2c3e50', jacket='f4f6f7', glasses='clear', badge='c0392b', shoes='1c1d21')],
    'sordi': [D(tone=2, hair=4, shirt='f2f2ee', pants='16284d', jacket='16284d', buttons='e3b341', epaulettes='e3b341', badge='e3b341', hat=('cap', 'f2f2ee'), moustache=True, shoes='1c1d21')],
}

PROP_NAMES = {
    'wrench': 'Wrench', 'crowbar': 'Crowbar', 'hammer': 'Hammer', 'lead_pipe': 'Lead Pipe', 'brick': 'Brick',
    'bottle': 'Wine Bottle', 'frying_pan': 'Frying Pan', 'rolling_pin': 'Rolling Pin', 'fish': 'Fresh Fish', 'oar': 'Oar',
    'shovel': 'Shovel', 'golf_club': 'Golf Club', 'broom': 'Broom', 'baton': 'Baton', 'candlestick': 'Candlestick',
    'fire_extinguisher': 'Fire Extinguisher', 'newspaper': 'Newspaper', 'kitchen_knife': 'Kitchen Knife', 'cleaver': 'Cleaver',
    'scissors': 'Scissors', 'letter_opener': 'Letter Opener', 'screwdriver': 'Screwdriver', 'garden_shears': 'Garden Shears',
    'fire_axe': 'Fire Axe', 'fishing_gaff': 'Fishing Gaff', 'corkscrew': 'Corkscrew', 'scalpel': 'Scalpel',
    'fiber_wire': 'Fiber Wire', 'coin': 'Coin', 'pocket_radio': 'Pocket Radio', 'emetic_poison': 'Emetic Vial',
    'rat_poison': 'Rat Poison', 'lethal_poison': 'Lethal Poison Vial', 'sedative': 'Sedative Syringe',
    'syringe': 'Lethal Syringe', 'lockpick': 'Lockpick', 'keycard_lab': 'Lab Keycard', 'keycard_estate': 'Estate Keycard',
    'keycard_harbour': 'Harbour Keycard',
}
ROLE_TITLES = {
    'fisherman': 'Fisherman', 'waiter': 'Waiter', 'cook': 'Cook', 'cleaner': 'Cleaner', 'gardener': 'Gardener',
    'priest': 'Priest', 'worker': 'Cannery Worker', 'harbour_guard': 'Harbour Police', 'estate_guard': 'Estate Guard',
    'bodyguard': 'Bodyguard', 'security': 'Halcyon Security', 'lab_guard': 'Virus Lab Guard', 'scientist': 'Scientist',
    'hazmat': 'Hazmat',
}
HANDHELD = {'wrench', 'crowbar', 'hammer', 'lead_pipe', 'frying_pan', 'rolling_pin', 'oar', 'shovel', 'golf_club', 'broom',
            'baton', 'kitchen_knife', 'cleaver', 'letter_opener', 'screwdriver', 'garden_shears', 'fire_axe', 'fishing_gaff',
            'scalpel', 'candlestick', 'fish'}


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def save(im, *parts):
    path = os.path.join(ASSETS, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


def main():
    rnd = random.Random(11)
    lang = {
        'itemGroup.recrafted': 'Recrafted: Contracts',
        'key.recrafted.focus': 'Focus (highlight targets and guards)',
        'key.categories.recrafted': 'Recrafted: Contracts',
        'entity.recrafted.npc': 'Townsperson',
        'entity.recrafted.prop': 'Prop',
        'entity.recrafted.thrown_prop': 'Thrown Prop',
        'item.recrafted.route_planner': 'Route Planner',
        'item.recrafted.casting_card': 'Casting Card',
        'block.recrafted.card_reader': 'Card Reader',
        'block.recrafted.hiding_crate': 'Hiding Crate',
        'block.recrafted.pathogen_core': 'CINDER Sample',
        'block.recrafted.purge_console': 'Purge Console',
        'block.recrafted.lab_console': 'Lab Console',
        'block.recrafted.exit_point': 'Exit Point',
        'block.recrafted.fuse_box': 'Fuse Box',
        'block.recrafted.meal': 'Plate of Food',
        'block.recrafted.drink': 'Glass of Wine',
    }
    # ---- items ----
    sprites = item_sprites()
    missing = set(PROP_NAMES) - set(sprites)
    assert not missing, missing
    for name, sp in sprites.items():
        save(sp.finish(), 'textures', 'item', name + '.png')
        parent = 'minecraft:item/handheld' if name in HANDHELD else 'minecraft:item/generated'
        write_json(os.path.join(ASSETS, 'models/item', name + '.json'),
                   {'parent': parent, 'textures': {'layer0': f'recrafted:item/{name}'}})
        if name in PROP_NAMES:
            lang[f'item.recrafted.{name}'] = PROP_NAMES[name]
    for role, (m, a) in OUTFIT_COLORS.items():
        save(outfit_sprite(m, a).finish(), 'textures', 'item', f'outfit_{role}.png')
        write_json(os.path.join(ASSETS, 'models/item', f'outfit_{role}.json'),
                   {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'recrafted:item/outfit_{role}'}})
        lang[f'item.recrafted.outfit_{role}'] = ROLE_TITLES[role] + ' Outfit'
    # ---- blocks ----
    for name, im in block_textures(rnd).items():
        save(im, 'textures', 'block', name + '.png')
    B = 'recrafted:block/'

    def cube_all(model, tex):
        write_json(os.path.join(ASSETS, 'models/block', model + '.json'),
                   {'parent': 'minecraft:block/cube_all', 'textures': {'all': B + tex}})

    def block_item(name, model=None):
        write_json(os.path.join(ASSETS, 'models/item', name + '.json'), {'parent': B + (model or name)})

    for tier in ('lab', 'estate', 'harbour'):
        cube_all(f'card_reader_{tier}', f'card_reader_{tier}')
    write_json(os.path.join(ASSETS, 'blockstates/card_reader.json'),
               {'variants': {f'tier={t}': {'model': B + f'card_reader_{t}'} for t in ('lab', 'estate', 'harbour')}})
    block_item('card_reader', 'card_reader_lab')
    write_json(os.path.join(ASSETS, 'models/block/hiding_crate.json'),
               {'parent': 'minecraft:block/cube_column', 'textures': {'end': B + 'hiding_crate_top', 'side': B + 'hiding_crate_side'}})
    for name in ('lab_console', 'purge_console'):
        write_json(os.path.join(ASSETS, 'models/block', name + '.json'),
                   {'parent': 'minecraft:block/cube_bottom_top',
                    'textures': {'top': B + 'console_side', 'bottom': B + 'console_side', 'side': B + name}})
    cube_all('pathogen_core', 'pathogen_core')
    cube_all('exit_point', 'exit_point')
    cube_all('fuse_box', 'fuse_box')
    cube_all('fuse_box_broken', 'fuse_box_broken')
    for name in ('hiding_crate', 'lab_console', 'purge_console', 'pathogen_core', 'exit_point'):
        write_json(os.path.join(ASSETS, 'blockstates', name + '.json'), {'variants': {'': {'model': B + name}}})
        block_item(name)
    write_json(os.path.join(ASSETS, 'blockstates/fuse_box.json'),
               {'variants': {'broken=false': {'model': B + 'fuse_box'}, 'broken=true': {'model': B + 'fuse_box_broken'}}})
    block_item('fuse_box')
    # plate and glass: small custom boxes
    write_json(os.path.join(ASSETS, 'models/block/meal.json'), {
        'textures': {'top': B + 'meal', 'side': B + 'meal_side', 'particle': B + 'meal_side'},
        'elements': [{'from': [3, 0, 3], 'to': [13, 1, 13], 'faces': {
            'up': {'uv': [0, 0, 16, 16], 'texture': '#top'}, 'down': {'uv': [0, 0, 16, 16], 'texture': '#side'},
            'north': {'uv': [0, 0, 16, 2], 'texture': '#side'}, 'south': {'uv': [0, 0, 16, 2], 'texture': '#side'},
            'east': {'uv': [0, 0, 16, 2], 'texture': '#side'}, 'west': {'uv': [0, 0, 16, 2], 'texture': '#side'}}}],
        'display': {'gui': {'rotation': [30, 225, 0], 'translation': [0, 4, 0], 'scale': [1.1, 1.1, 1.1]}}})
    faces = {k: {'uv': [0, 0, 16, 16], 'texture': '#all'} for k in ('north', 'south', 'east', 'west', 'up', 'down')}
    write_json(os.path.join(ASSETS, 'models/block/drink.json'), {
        'textures': {'all': B + 'drink', 'particle': B + 'drink'},
        'elements': [
            {'from': [6.5, 0, 6.5], 'to': [9.5, 0.5, 9.5], 'faces': faces},
            {'from': [7.5, 0.5, 7.5], 'to': [8.5, 3, 8.5], 'faces': faces},
            {'from': [6, 3, 6], 'to': [10, 7, 10], 'faces': faces}],
        'display': {'gui': {'rotation': [30, 225, 0], 'translation': [0, 3, 0], 'scale': [1.4, 1.4, 1.4]}}})
    for name in ('meal', 'drink'):
        write_json(os.path.join(ASSETS, 'blockstates', name + '.json'),
                   {'variants': {f'poison={p}': {'model': B + name} for p in ('none', 'emetic', 'lethal')}})
        block_item(name)
    # ---- skins ----
    for role, variants in ROLE_SKINS.items():
        for i, spec in enumerate(variants):
            save(make_skin(spec, random.Random(hash((role, i)) & 0xffff)), 'textures', 'entity', 'npc', f'{role}_{i}.png')
    save(agent_skin(), 'textures', 'entity', 'npc', 'agent_0.png')
    from ams_blocks import LANG as AMS_LANG
    from ams_cast import LANG as CAST_LANG
    lang.update(AMS_LANG)
    lang.update(CAST_LANG)
    write_json(os.path.join(ASSETS, 'lang/en_us.json'), lang)
    print(f'{len(sprites) + len(OUTFIT_COLORS)} item sprites, {sum(len(v) for v in ROLE_SKINS.values())} skins')


if __name__ == '__main__':
    main()
