#!/usr/bin/env python3
"""Builds the Recrafted Arsenal gun pack for TACZ.

    python3 tools/armory/build.py           # writes gunpack/recrafted_arsenal + dist zip + previews

The pack is plain data (no code): models, textures, animations and stats that TACZ loads
from <game dir>/tacz/. See gunpack/README.md for installation.
"""
import base64
import io
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'guns'))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import argento  # noqa: E402
import argento_anim  # noqa: E402
from geomodel import render  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PACK_NAME = 'recrafted_arsenal'
NS = 'recrafted'
OUT = os.path.join(ROOT, 'gunpack', PACK_NAME)
DIST = os.path.join(ROOT, 'dist')
PREVIEW = os.path.join(ROOT, 'docs', 'arsenal')


def write_json(rel, obj):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def save_png(rel, img):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    (img if isinstance(img, Image.Image) else Image.fromarray(img)).save(path)


def silhouette(model, tex, size, hide, eye, target, ortho, color=(214, 214, 214), pad=4):
    """White side-on silhouette, the style TACZ uses for its ammo HUD."""
    img = render(model, tex, eye=eye, target=target, ortho_height=ortho, size=size, hide=hide, bg=(0, 0, 0), ss=2)
    a = np.asarray(img).astype(np.int32).sum(-1) > 12
    out = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    out[a] = color + (255,)
    return Image.fromarray(out)


def icon(model, tex, size, hide, eye, target, ortho):
    """Coloured side view with transparent background (inventory slot)."""
    bg = (1, 2, 3)
    img = render(model, tex, eye=eye, target=target, ortho_height=ortho, size=size, hide=hide, bg=bg, ss=1)
    arr = np.asarray(img).astype(np.int32)
    ref = np.asarray(render(model, tex, eye=eye, target=target, ortho_height=ortho, size=size, hide=hide,
                            bg=(250, 0, 250), ss=1)).astype(np.int32)
    solid = np.abs(arr - ref).sum(-1) < 30
    out = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    out[..., :3] = np.clip(arr, 0, 255)
    out[..., 3] = np.where(solid, 255, 0)
    return Image.fromarray(out)


LANG = {}


def build_argento():
    gid = argento.ID
    m = argento.build()
    m.layout()
    tex = m.paint(argento.shader)
    hide = ('righthand_pos', 'lefthand_pos')
    write_json(f'assets/{NS}/geo_models/gun/{gid}_geo.json', m.to_bedrock())
    save_png(f'assets/{NS}/textures/gun/uv/{gid}.png', tex)
    side = dict(eye=(-40, 3.2, -2.9), target=(0, 3.2, -2.9))
    save_png(f'assets/{NS}/textures/gun/hud/{gid}.png', silhouette(m, tex, (384, 128), hide, ortho=8.6, **side))
    save_png(f'assets/{NS}/textures/gun/slot/{gid}.png', icon(m, tex, (64, 64), hide, ortho=13.5, **side))
    write_json(f'assets/{NS}/animations/{gid}.animation.json',
               {'format_version': '1.8.0', 'animations': argento_anim.all_animations()})
    write_json(f'data/{NS}/index/guns/{gid}.json', {
        'name': f'{NS}.gun.{gid}.name', 'display': f'{NS}:{gid}_display', 'data': f'{NS}:{gid}_data',
        'tooltip': f'{NS}.gun.{gid}.desc', 'type': 'pistol', 'sort': 1,
    })
    write_json(f'assets/{NS}/display/guns/{gid}_display.json', {
        'state_machine': 'tacz:default_state_machine_v2',
        'ads_preset': 'tacz:renew',
        'model': f'{NS}:gun/{gid}_geo',
        'texture': f'{NS}:gun/uv/{gid}',
        'hud': f'{NS}:gun/hud/{gid}',
        'slot': f'{NS}:gun/slot/{gid}',
        'animation': f'{NS}:{gid}',
        'use_default_animation': 'pistol',
        'player_animator_3rd': 'tacz:pistol_default.player_animation',
        'transform': {'scale': {'thirdperson': [0.6, 0.6, 0.6], 'ground': [0.6, 0.6, 0.6], 'fixed': [1.1, 1.1, 1.1]}},
        'shell': {'initial_velocity': [5.0, 3.0, 1], 'random_velocity': [2.5, 2, 0.25],
                  'acceleration': [0.0, -20, 0.0], 'angular_velocity': [360, -960, 90], 'living_time': 1.0},
        'muzzle_flash': {'type': 'renew', 'texture': 'tacz:flash/common_muzzle_flash', 'scale': 0.6,
                         'smoke_scale': 1.1, 'initial_speed_scale': 1.1, 'smoke_particle_count': 16},
        'iron_zoom': 1.25,
        'model_fov': 60,
        'zoom_model_fov': 45,
        'sounds': {
            'draw': 'tacz:m1911/m1911_draw', 'put_away': 'tacz:m1911/m1911_put_away',
            'shoot': 'tacz:m1911/m1911_shoot', 'shoot_3p': 'tacz:m1911/m1911_shoot_3p',
            'silence': 'tacz:m1911/m1911_silence', 'silence_3p': 'tacz:m1911/m1911_silence_3p',
        },
        'offhand_show': {'pos': [4, 13, -1], 'rotate': [-90, -35, 90], 'scale': [0.5, 0.5, 0.5]},
        'hotbar_show': {'0': {'pos': [-5, 13, -1], 'rotate': [-90, -35, 90], 'scale': [0.5, 0.5, 0.5]}},
    })
    write_json(f'data/{NS}/data/guns/{gid}_data.json', {
        'allow_ammo_unload': True,
        'ammo': 'tacz:45acp',
        'rpm': 300,
        'bullet': {
            'life': 1, 'bullet_amount': 1, 'damage': 13, 'tracer_count_interval': 0,
            'extra_damage': {
                'armor_ignore': 0.25, 'head_shot_multiplier': 2.2,
                'damage_adjust': [{'distance': 24, 'damage': 13}, {'distance': 48, 'damage': 10},
                                  {'distance': 'infinite', 'damage': 6}],
            },
            'speed': 200, 'gravity': 0.15, 'knockback': 0, 'friction': 0.03, 'ignite': False, 'pierce': 1,
        },
        'ammo_amount': 8,
        'bolt': 'closed_bolt',
        'reload': {'type': 'magazine', 'feed': {'empty': 1.32, 'tactical': 1.24},
                   'cooldown': {'empty': 2.35, 'tactical': 1.95}},
        'draw_time': 0.5, 'put_away_time': 0.3, 'aim_time': 0.15, 'sprint_time': 0.05, 'weight': 1.25,
        'movement_speed': {'base': 0, 'aim': 0, 'reload': 0.1},
        'crawl_recoil_multiplier': 0.5,
        'fire_mode': ['semi'],
        'allow_attachment_types': ['muzzle'],
        'recoil': {
            'pitch': [{'time': 0, 'value': [1.3, 1.3]}, {'time': 0.2, 'value': [0.1, 0.1]},
                      {'time': 0.3, 'value': [0.06, 0.06]}, {'time': 0.4, 'value': [0, 0]}],
            'yaw': [{'time': 0, 'value': [-0.5, -0.5]}, {'time': 0.05, 'value': [0.3, 0.3]},
                    {'time': 0.11, 'value': [0.08, 0.08]}, {'time': 0.28, 'value': [0, 0]}],
        },
        'inaccuracy': {'stand': 1.3, 'move': 1.6, 'sneak': 0.85, 'lie': 0.7, 'aim': 0.1},
    })
    write_json(f'data/{NS}/tacz_tags/attachments/allow_attachments/{gid}.json',
               [f'{NS}:{argento.SUPP_ID}', '#tacz:pistol_muzzle'])
    write_json(f'data/{NS}/recipes/gun/{gid}.json', {
        'materials': [{'item': {'tag': 'forge:ingots/iron'}, 'count': 18},
                      {'item': {'tag': 'forge:ingots/gold'}, 'count': 2},
                      {'item': {'item': 'minecraft:bone_block'}, 'count': 1}],
        'result': {'type': 'gun', 'id': f'{NS}:{gid}'},
        'type': 'tacz:gun_smith_table_crafting',
    })
    LANG[f'{NS}.gun.{gid}.name'] = 'Argento .45'
    LANG[f'{NS}.gun.{gid}.desc'] = 'Long-slide stainless .45. Threaded for the house suppressor.'

    # ---- suppressor attachment --------------------------------------------------------
    sid = argento.SUPP_ID
    s = argento.build_suppressor()
    s.layout()
    stex = s.paint(argento.suppressor_shader)
    write_json(f'assets/{NS}/geo_models/attachment/{sid}_geo.json', s.to_bedrock())
    save_png(f'assets/{NS}/textures/attachment/uv/{sid}.png', stex)
    save_png(f'assets/{NS}/textures/attachment/slot/{sid}.png',
             icon(s, stex, (64, 64), (), eye=(-40, 0, -3.6), target=(0, 0, -3.6), ortho=9))
    write_json(f'data/{NS}/index/attachments/{sid}.json', {
        'name': f'{NS}.attachment.{sid}.name', 'display': f'{NS}:{sid}_display',
        'data': f'{NS}:{sid}_data', 'type': 'muzzle', 'sort': 1,
    })
    write_json(f'assets/{NS}/display/attachments/{sid}_display.json', {
        'slot': f'{NS}:attachment/slot/{sid}', 'model': f'{NS}:attachment/{sid}_geo',
        'texture': f'{NS}:attachment/uv/{sid}',
        'sounds': {'install': 'tacz:attachments/muzzle_general', 'uninstall': 'tacz:attachments/muzzle_general'},
        'muzzle_flash_offset': 7.4,
    })
    write_json(f'data/{NS}/data/attachments/{sid}_data.json', {
        'weight': 0.3, 'flash_hider': 0.1,
        'smoke_directions': {'plane_angle': 0, 'out_angle': 90}, 'smoke_spread_angle': 90,
        'ads': {'addend': 0.05},
        'inaccuracy': {'multiplier': 1.05},
        'effective_range': {'multiplier': 0.9},
        'silence': {'distance_addend': -30, 'use_silence_sound': True},
    })
    write_json(f'data/{NS}/recipes/attachments/{sid}.json', {
        'materials': [{'item': {'tag': 'forge:ingots/iron'}, 'count': 6},
                      {'item': {'item': 'minecraft:black_wool'}, 'count': 2},
                      {'item': {'tag': 'forge:ingots/gold'}, 'count': 1}],
        'result': {'type': 'attachment', 'id': f'{NS}:{sid}'},
        'type': 'tacz:gun_smith_table_crafting',
    })
    LANG[f'{NS}.attachment.{sid}.name'] = 'Argento Suppressor'

    # ---- Blockbench projects + previews ------------------------------------------------
    for model, texture, name in ((m, tex, gid), (s, stex, sid)):
        buf = io.BytesIO()
        Image.fromarray(texture).save(buf, 'PNG')
        bbm = model.to_bbmodel(base64.b64encode(buf.getvalue()).decode(), name)
        path = os.path.join(ROOT, 'gunpack', 'blockbench', name + '.bbmodel')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(bbm, f)
    os.makedirs(PREVIEW, exist_ok=True)
    render(m, tex, eye=(-40, 3.5, -2.5), target=(0, 3.5, -2.5), ortho_height=12, size=(1200, 640),
           hide=hide).save(os.path.join(PREVIEW, f'{gid}_right.png'))
    render(m, tex, eye=(40, 3.5, -2.5), target=(0, 3.5, -2.5), ortho_height=12, size=(1200, 640),
           hide=hide).save(os.path.join(PREVIEW, f'{gid}_left.png'))
    print(f'  {gid}: {m.cube_count()} cubes; suppressor {s.cube_count()} cubes')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    write_json('gunpack.meta.json', {'namespace': NS})
    build_argento()
    write_json(f'assets/{NS}/lang/en_us.json', LANG)
    os.makedirs(DIST, exist_ok=True)
    zpath = os.path.join(DIST, f'{PACK_NAME}.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, OUT))
    dev = os.path.join(ROOT, 'run', 'tacz')
    if os.path.isdir(dev):
        target = os.path.join(dev, PACK_NAME)
        if os.path.isdir(target):
            shutil.rmtree(target)
        shutil.copytree(OUT, target)
    print(f'pack written: {os.path.relpath(OUT, ROOT)}, zip {os.path.getsize(zpath) // 1024} KiB')


if __name__ == '__main__':
    main()
