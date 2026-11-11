"""Preview renderers for the voxel canvas: top-down map and oblique view."""
import numpy as np
from PIL import Image

COLORS = {
    'air': None, 'cave_air': None, 'light': None, 'barrier': None,
    'water': (52, 128, 196), 'stone': (125, 125, 125), 'andesite': (136, 136, 137),
    'diorite': (190, 190, 191), 'calcite': (224, 225, 221), 'tuff': (108, 109, 102),
    'granite': (149, 103, 85), 'bedrock': (60, 60, 60), 'deepslate': (80, 80, 82),
    'dirt': (134, 96, 67), 'coarse_dirt': (119, 85, 59), 'rooted_dirt': (144, 103, 76),
    'grass_block': (121, 152, 72), 'podzol': (91, 63, 24), 'farmland': (110, 75, 45),
    'sand': (219, 207, 163), 'sandstone': (216, 203, 155), 'gravel': (131, 127, 126),
    'smooth_sandstone': (223, 214, 170), 'cut_sandstone': (217, 206, 159),
    'cobblestone': (127, 127, 127), 'mossy_cobblestone': (110, 118, 94),
    'stone_bricks': (122, 121, 122), 'mossy_stone_bricks': (115, 121, 105),
    'cracked_stone_bricks': (118, 117, 118), 'smooth_stone': (158, 158, 158),
    'polished_andesite': (132, 135, 133), 'polished_diorite': (193, 193, 195),
    'bricks': (150, 97, 83), 'terracotta': (152, 94, 67),
    'white_terracotta': (209, 178, 161), 'yellow_terracotta': (186, 133, 35),
    'orange_terracotta': (161, 83, 37), 'pink_terracotta': (161, 78, 78),
    'red_terracotta': (143, 61, 46), 'light_gray_terracotta': (135, 106, 97),
    'brown_terracotta': (77, 51, 35), 'lime_terracotta': (103, 117, 52),
    'light_blue_terracotta': (113, 108, 137), 'cyan_terracotta': (86, 91, 91),
    'white_concrete': (207, 213, 214), 'light_gray_concrete': (125, 125, 115),
    'gray_concrete': (54, 57, 61), 'yellow_concrete': (240, 175, 21),
    'cyan_concrete': (21, 119, 136), 'red_concrete': (142, 32, 32),
    'black_concrete': (8, 10, 15), 'orange_concrete': (224, 97, 0),
    'lime_concrete': (94, 168, 24), 'blue_concrete': (44, 46, 143),
    'white_concrete_powder': (225, 227, 227),
    'quartz_block': (235, 229, 222), 'smooth_quartz': (235, 229, 222), 'quartz_bricks': (234, 229, 221),
    'quartz_pillar': (235, 230, 224), 'iron_block': (220, 220, 220),
    'mud_bricks': (137, 103, 79), 'packed_mud': (142, 106, 79),
    'oak_planks': (162, 130, 78), 'spruce_planks': (114, 84, 48), 'dark_oak_planks': (66, 43, 20),
    'birch_planks': (192, 175, 121), 'jungle_planks': (160, 115, 80), 'acacia_planks': (168, 90, 50),
    'mangrove_planks': (117, 54, 48), 'warped_planks': (43, 104, 99), 'crimson_planks': (101, 48, 70),
    'cherry_planks': (226, 178, 172), 'bamboo_planks': (193, 173, 80),
    'oak_log': (109, 85, 50), 'spruce_log': (58, 37, 16), 'jungle_log': (85, 67, 25),
    'dark_oak_log': (60, 46, 26), 'stripped_oak_wood': (177, 144, 86),
    'white_wool': (233, 236, 236), 'red_wool': (160, 39, 34), 'blue_wool': (53, 57, 157),
    'yellow_wool': (248, 197, 39), 'green_wool': (84, 109, 27), 'orange_wool': (240, 118, 19),
    'light_blue_wool': (58, 175, 217), 'cyan_wool': (21, 137, 145), 'lime_wool': (112, 185, 25),
    'black_wool': (20, 21, 25), 'gray_wool': (62, 68, 71), 'pink_wool': (237, 141, 172),
    'glass': (200, 225, 235), 'glass_pane': (200, 225, 235), 'sea_lantern': (172, 199, 190),
    'glowstone': (171, 131, 84), 'lantern': (250, 200, 90), 'iron_bars': (136, 139, 135),
    'hay_block': (166, 139, 12), 'melon': (111, 144, 30), 'pumpkin': (195, 114, 24),
    'barrel': (134, 100, 58), 'composter': (112, 70, 31), 'bookshelf': (116, 94, 59),
    'red_nether_bricks': (69, 7, 9), 'nether_bricks': (44, 21, 26),
    'packed_ice': (141, 180, 250), 'blue_ice': (116, 167, 253), 'snow_block': (249, 254, 254),
    'copper_block': (192, 107, 79), 'cut_copper': (191, 106, 80), 'oxidized_copper': (82, 162, 132),
    'oxidized_cut_copper': (79, 153, 126), 'weathered_copper': (108, 153, 110),
    'prismarine': (99, 156, 151), 'dark_prismarine': (51, 91, 75), 'prismarine_bricks': (99, 171, 158),
    'obsidian': (15, 10, 24), 'coal_block': (16, 15, 15), 'gold_block': (246, 208, 61),
    'redstone_lamp': (220, 170, 100), 'redstone_block': (175, 24, 5), 'emerald_block': (42, 203, 87),
    'moss_block': (89, 109, 45), 'clay': (160, 166, 179), 'mud': (60, 57, 60),
    'smooth_red_sandstone': (181, 97, 31), 'red_sandstone': (186, 99, 29), 'cut_red_sandstone': (189, 101, 31),
    'polished_blackstone': (53, 48, 56), 'blackstone': (42, 35, 40), 'polished_deepslate': (72, 72, 73),
    'deepslate_tiles': (54, 54, 55), 'deepslate_bricks': (70, 70, 71),
    'pearlescent_froglight': (245, 240, 240), 'ochre_froglight': (250, 245, 206), 'verdant_froglight': (229, 244, 228),
    'dripstone_block': (134, 107, 92), 'white_stained_glass': (240, 240, 240),
    'lime_stained_glass': (127, 204, 25), 'light_blue_stained_glass': (102, 153, 216),
    'cyan_stained_glass': (76, 127, 153), 'red_stained_glass': (153, 51, 51),
    'yellow_stained_glass': (229, 229, 51), 'blue_stained_glass': (51, 76, 178),
}
KEYWORDS = [
    ('azalea_leaves', (98, 128, 48)), ('spruce_leaves', (48, 80, 48)), ('dark_oak_leaves', (44, 92, 30)),
    ('cherry_leaves', (229, 173, 194)), ('jungle_leaves', (50, 130, 30)), ('leaves', (72, 120, 40)),
    ('azalea', (98, 128, 48)), ('vine', (60, 110, 40)),
    ('carpet', None), ('trapdoor', None), ('door', None), ('fence', (114, 84, 48)),
    ('wall', (122, 121, 122)), ('pane', (200, 225, 235)), ('stained_glass', (180, 200, 220)),
    ('potted', (130, 90, 60)), ('rose', (160, 50, 50)), ('peony', (220, 150, 200)), ('lilac', (180, 140, 190)),
    ('fern', (80, 130, 50)), ('grass', (100, 150, 60)), ('torch', (250, 200, 90)),
    ('log', (90, 70, 40)), ('wood', (120, 95, 55)), ('planks', (150, 120, 75)),
    ('concrete', (150, 150, 150)), ('terracotta', (160, 110, 85)), ('wool', (220, 220, 220)),
    ('recrafted:', (220, 40, 200)),
]
_STRIP = ('_stairs', '_slab', '_wall')
_ALIAS = {'stone_brick': 'stone_bricks', 'brick': 'bricks', 'mossy_stone_brick': 'mossy_stone_bricks',
          'quartz': 'quartz_block', 'spruce': 'spruce_planks', 'oak': 'oak_planks', 'dark_oak': 'dark_oak_planks',
          'birch': 'birch_planks', 'acacia': 'acacia_planks', 'mangrove': 'mangrove_planks',
          'warped': 'warped_planks', 'jungle': 'jungle_planks', 'cherry': 'cherry_planks',
          'red_nether_brick': 'red_nether_bricks', 'nether_brick': 'nether_bricks', 'mud_brick': 'mud_bricks',
          'deepslate_brick': 'deepslate_bricks', 'deepslate_tile': 'deepslate_tiles',
          'prismarine_brick': 'prismarine_bricks', 'bamboo': 'bamboo_planks', 'crimson': 'crimson_planks'}


def color_of(name):
    base = name.split('[')[0]
    if base.startswith('minecraft:'):
        base = base[10:]
    if base in COLORS:
        return COLORS[base]
    for suf in _STRIP:
        if base.endswith(suf):
            core = base[:-len(suf)]
            core = _ALIAS.get(core, core)
            if core in COLORS:
                return COLORS[core]
    for part in ('carpet', 'trapdoor'):
        if base.endswith(part):
            core = base[:-len(part) - 1]
            for cand in (core + '_wool', _ALIAS.get(core, core)):
                if cand in COLORS:
                    return COLORS[cand]
            return (150, 120, 80)
    if base.endswith('door'):
        return (100, 70, 40)
    for kw, col in KEYWORDS:
        if kw in base and col is not None:
            return col
    return (170, 120, 170)


def palette_colors(w):
    pal = np.zeros((len(w.palette), 3), dtype=np.float32)
    solid = np.zeros(len(w.palette), dtype=bool)
    for i, n in enumerate(w.palette):
        c = color_of(n)
        if c is not None:
            pal[i] = c
            solid[i] = True
    return pal, solid


def topdown(w, path, scale=3, ymax=None):
    pal, solid = palette_colors(w)
    G = w.G if ymax is None else w.G[:ymax]
    sy = G.shape[0]
    mask = solid[G]
    idx = sy - 1 - np.argmax(mask[::-1], axis=0)
    top = np.take_along_axis(G, idx[None], axis=0)[0]
    img = pal[top].copy()
    h = idx.astype(np.float32)
    shade = np.ones_like(h)
    shade[1:, :] += np.clip((h[1:, :] - h[:-1, :]) * 0.06, -0.25, 0.25)
    shade[:, 1:] += np.clip((h[:, 1:] - h[:, :-1]) * 0.04, -0.2, 0.2)
    shade += (h - 62) * 0.004
    img = np.clip(img * shade[..., None], 0, 255).astype(np.uint8)
    im = Image.fromarray(img, 'RGB')
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)


def oblique(w, path, scale=3, view='south', crop=None):
    """Orthographic view tilted 45 degrees. view = side the camera stands on."""
    pal, solid = palette_colors(w)
    G = w.G
    if view == 'north':
        G = G[:, ::-1, ::-1]
    elif view == 'east':
        G = np.transpose(G, (0, 2, 1))[:, :, ::-1]
    elif view == 'west':
        G = np.transpose(G, (0, 2, 1))[:, ::-1, :]
    if crop:
        x0, z0, x1, z1 = crop
        G = G[:, z0:z1, x0:x1]
    sy, sz, sx = G.shape
    img = np.zeros((sz + sy + 1, sx, 3), dtype=np.float32)
    img[:] = (150, 200, 235)
    water_id = [i for i, n in enumerate(w.palette) if n.startswith('minecraft:water')]
    for z in range(sz):
        sl = G[:, z, :]
        m = solid[sl]
        above = np.zeros_like(m)
        above[:-1] = m[1:]
        col = pal[sl]
        for y in range(sy):
            row = m[y]
            if not row.any():
                continue
            py = z + (sy - 1 - y) + 1
            shade = 0.72 + 0.28 * min(1.0, y / 110.0)
            img[py, row] = col[y, row] * (0.78 * shade + 0.1)
            t = row & ~above[y]
            if t.any():
                img[py - 1, t] = col[y, t] * min(1.08, shade + 0.25)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)


def slice_y(w, path, y, scale=3, depth=6):
    """Horizontal cut: shows the first solid block at or below y (for interiors / the lab)."""
    pal, solid = palette_colors(w)
    G = w.G[max(0, y - depth):y + 1]
    mask = solid[G]
    sy = G.shape[0]
    idx = sy - 1 - np.argmax(mask[::-1], axis=0)
    top = np.take_along_axis(G, idx[None], axis=0)[0]
    img = pal[top].copy()
    img *= (0.55 + 0.45 * (idx / max(1, sy - 1)))[..., None]
    img[~mask.any(axis=0)] = (0, 0, 0)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
