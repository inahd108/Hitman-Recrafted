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

PISTOL_DISPLAY = {
    'state_machine': 'tacz:default_state_machine_v2',
    'ads_preset': 'tacz:renew',
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
    'offhand_show': {'pos': [4, 13, -1], 'rotate': [-90, -35, 90], 'scale': [0.5, 0.5, 0.5]},
    'hotbar_show': {'0': {'pos': [-5, 13, -1], 'rotate': [-90, -35, 90], 'scale': [0.5, 0.5, 0.5]}},
}


def emit_pistol(gun, anims, *, name, desc, sort, data, sounds, allow, recipe, side_cz, hud_ortho, slot_ortho,
                display_extra=None):
    """Model, texture, icons, animations, index, display, data, tags and recipe for one handgun."""
    gid = gun.ID
    m = gun.build()
    m.layout()
    tex = m.paint(gun.shader)
    hide = ('righthand_pos', 'lefthand_pos', 'mag_extended_1', 'mag_extended_2', 'mag_extended_3', 'loader_and_round')
    write_json(f'assets/{NS}/geo_models/gun/{gid}_geo.json', m.to_bedrock())
    save_png(f'assets/{NS}/textures/gun/uv/{gid}.png', tex)
    side = dict(eye=(-40, 3.2, side_cz), target=(0, 3.2, side_cz))
    save_png(f'assets/{NS}/textures/gun/hud/{gid}.png', silhouette(m, tex, (384, 128), hide, ortho=hud_ortho, **side))
    save_png(f'assets/{NS}/textures/gun/slot/{gid}.png', icon(m, tex, (64, 64), hide, ortho=slot_ortho, **side))
    write_json(f'assets/{NS}/animations/{gid}.animation.json', {'format_version': '1.8.0', 'animations': anims})
    write_json(f'data/{NS}/index/guns/{gid}.json', {
        'name': f'{NS}.gun.{gid}.name', 'display': f'{NS}:{gid}_display', 'data': f'{NS}:{gid}_data',
        'tooltip': f'{NS}.gun.{gid}.desc', 'type': 'pistol', 'sort': sort,
    })
    display = dict(PISTOL_DISPLAY)
    display.update({'model': f'{NS}:gun/{gid}_geo', 'texture': f'{NS}:gun/uv/{gid}', 'hud': f'{NS}:gun/hud/{gid}',
                    'slot': f'{NS}:gun/slot/{gid}', 'animation': f'{NS}:{gid}', 'sounds': sounds})
    display.update(display_extra or {})
    display = {k: v for k, v in display.items() if v is not None}
    write_json(f'assets/{NS}/display/guns/{gid}_display.json', display)
    write_json(f'data/{NS}/data/guns/{gid}_data.json', data)
    if allow:
        write_json(f'data/{NS}/tacz_tags/attachments/allow_attachments/{gid}.json', allow)
    write_json(f'data/{NS}/recipes/gun/{gid}.json', {
        'materials': recipe, 'result': {'type': 'gun', 'id': f'{NS}:{gid}'}, 'type': 'tacz:gun_smith_table_crafting',
    })
    LANG[f'{NS}.gun.{gid}.name'] = name
    LANG[f'{NS}.gun.{gid}.desc'] = desc
    os.makedirs(PREVIEW, exist_ok=True)
    for lab, ex in (('left', -40), ('right', 40)):
        render(m, tex, eye=(ex, 3.2, side_cz), target=(0, 3.2, side_cz), ortho_height=hud_ortho * 1.25,
               size=(1200, 640), hide=hide).save(os.path.join(PREVIEW, f'{gid}_{lab}.png'))
    render(m, tex, eye=(-10, 8.5, side_cz - 13), target=(0, 3.4, side_cz + 0.3), fov=40, size=(1200, 700),
           hide=hide).save(os.path.join(PREVIEW, f'{gid}_34.png'))
    bb_export(m, tex, gid)
    print(f'  {gid}: {m.cube_count()} cubes')
    return m, tex


def bb_export(model, texture, name):
    buf = io.BytesIO()
    Image.fromarray(texture).save(buf, 'PNG')
    bbm = model.to_bbmodel(base64.b64encode(buf.getvalue()).decode(), name)
    path = os.path.join(ROOT, 'gunpack', 'blockbench', name + '.bbmodel')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(bbm, f)


def pistol_data(**over):
    """Common handgun stats; each gun overrides what makes it different."""
    d = {
        'allow_ammo_unload': True, 'ammo': 'tacz:9mm', 'rpm': 300,
        'bullet': {'life': 1, 'bullet_amount': 1, 'damage': 10, 'tracer_count_interval': 0,
                   'extra_damage': {'armor_ignore': 0.2, 'head_shot_multiplier': 1.8,
                                    'damage_adjust': [{'distance': 20, 'damage': 10}, {'distance': 40, 'damage': 8},
                                                      {'distance': 'infinite', 'damage': 5}]},
                   'speed': 200, 'gravity': 0.15, 'knockback': 0, 'friction': 0.03, 'ignite': False, 'pierce': 1},
        'ammo_amount': 12, 'bolt': 'closed_bolt',
        'reload': {'type': 'magazine', 'feed': {'empty': 1.32, 'tactical': 1.24},
                   'cooldown': {'empty': 2.35, 'tactical': 1.95}},
        'draw_time': 0.5, 'put_away_time': 0.3, 'aim_time': 0.15, 'sprint_time': 0.05, 'weight': 1.0,
        'movement_speed': {'base': 0, 'aim': 0, 'reload': 0.1},
        'crawl_recoil_multiplier': 0.5, 'fire_mode': ['semi'], 'allow_attachment_types': [],
        'recoil': {'pitch': [{'time': 0, 'value': [1.2, 1.2]}, {'time': 0.2, 'value': [0.1, 0.1]},
                             {'time': 0.3, 'value': [0.05, 0.05]}, {'time': 0.4, 'value': [0, 0]}],
                   'yaw': [{'time': 0, 'value': [-0.45, -0.45]}, {'time': 0.05, 'value': [0.28, 0.28]},
                           {'time': 0.11, 'value': [0.07, 0.07]}, {'time': 0.28, 'value': [0, 0]}]},
        'inaccuracy': {'stand': 1.3, 'move': 1.6, 'sneak': 0.85, 'lie': 0.7, 'aim': 0.1},
    }
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            d[k] = {**d[k], **v}
        else:
            d[k] = v
    return d


def build_bastone():
    import bastone
    import bastone_anim
    S = 'tacz:m9a4/m9a4_'
    emit_pistol(
        bastone, bastone_anim.all_animations(),
        name='Bastone 9', desc='Corvara police service pistol. Fifteen rounds, no subtlety.', sort=3,
        data=pistol_data(
            ammo='tacz:9mm', rpm=380, ammo_amount=15, weight=1.05,
            extended_mag_ammo_amount=[17, 20, 24],
            bullet={'damage': 10, 'speed': 210,
                    'extra_damage': {'armor_ignore': 0.2, 'head_shot_multiplier': 1.8,
                                     'damage_adjust': [{'distance': 22, 'damage': 10}, {'distance': 45, 'damage': 8},
                                                       {'distance': 'infinite', 'damage': 5}]}},
            allow_attachment_types=['muzzle', 'extended_mag', 'laser'],
            fire_sound={'fire_multiplier': 1.1, 'silence_multiplier': 1.0},
        ),
        sounds={'draw': S + 'draw', 'put_away': S + 'put_away', 'shoot': S + 'shoot', 'shoot_3p': S + 'shoot_3p',
                'silence': S + 'silence', 'silence_3p': S + 'silence_3p'},
        allow=['#tacz:pistol_muzzle', '#tacz:light_extended_mag', '#tacz:pistol_laser'],
        recipe=[{'item': {'tag': 'forge:ingots/iron'}, 'count': 14},
                {'item': {'item': 'minecraft:black_dye'}, 'count': 2}],
        side_cz=-2.0, hud_ortho=7.0, slot_ortho=12.5,
    )


def build_passero():
    import passero
    import passero_anim
    S = 'tacz:glock_17/glock17_'
    emit_pistol(
        passero, passero_anim.all_animations(),
        name='Passero .22', desc='Compact .22 with an integral suppressor. Heard by almost no one.', sort=2,
        data=pistol_data(
            ammo='tacz:22wmr', rpm=420, ammo_amount=10, weight=0.85, draw_time=0.4, aim_time=0.12,
            bullet={'damage': 7, 'speed': 170, 'gravity': 0.13,
                    'extra_damage': {'armor_ignore': 0.0, 'head_shot_multiplier': 3.0,
                                     'damage_adjust': [{'distance': 16, 'damage': 7}, {'distance': 30, 'damage': 5},
                                                       {'distance': 'infinite', 'damage': 3}]}},
            reload={'feed': {'empty': 1.2, 'tactical': 1.12}, 'cooldown': {'empty': 2.15, 'tactical': 1.8}},
            recoil={'pitch': [{'time': 0, 'value': [0.55, 0.55]}, {'time': 0.15, 'value': [0.05, 0.05]},
                              {'time': 0.25, 'value': [0, 0]}],
                    'yaw': [{'time': 0, 'value': [-0.2, -0.2]}, {'time': 0.05, 'value': [0.12, 0.12]},
                            {'time': 0.2, 'value': [0, 0]}]},
            inaccuracy={'stand': 1.1, 'move': 1.4, 'sneak': 0.7, 'lie': 0.6, 'aim': 0.12},
            fire_sound={'fire_multiplier': 0.12, 'silence_multiplier': 1.0},
        ),
        sounds={'draw': S + 'draw', 'put_away': 'tacz:m1911/m1911_put_away',
                'shoot': S + 'silence', 'shoot_3p': S + 'silence_3p', 'silence': S + 'silence',
                'silence_3p': S + 'silence_3p'},
        allow=[],
        recipe=[{'item': {'tag': 'forge:ingots/iron'}, 'count': 12},
                {'item': {'tag': 'minecraft:logs'}, 'count': 2},
                {'item': {'item': 'minecraft:black_wool'}, 'count': 2}],
        side_cz=-4.2, hud_ortho=7.4, slot_ortho=15.5,
        display_extra={'muzzle_flash': {'type': 'renew', 'texture': 'tacz:flash/common_muzzle_flash', 'scale': 0.15,
                                        'smoke_scale': 0.6, 'initial_speed_scale': 0.8, 'smoke_particle_count': 6}},
    )




def build_vento():
    import vento
    import vento_anim
    R = 'tacz:rhino357/rhino_'
    emit_pistol(
        vento, vento_anim.animations(),
        name='Vento .357', desc='Heavy six-shot revolver. A long double-action pull and a very loud answer.', sort=4,
        data=pistol_data(
            ammo='tacz:357mag', rpm=220, ammo_amount=6, bolt='open_bolt', weight=1.6,
            draw_time=0.55, put_away_time=0.4, aim_time=0.16,
            bullet={'damage': 12.5, 'speed': 210, 'knockback': 0.08,
                    'extra_damage': {'armor_ignore': 0.3, 'head_shot_multiplier': 2.0,
                                     'damage_adjust': [{'distance': 25, 'damage': 12.5},
                                                       {'distance': 40, 'damage': 9.5},
                                                       {'distance': 'infinite', 'damage': 6.5}]}},
            reload={'feed': {'empty': 2.1, 'tactical': 2.1}, 'cooldown': {'empty': 3.9, 'tactical': 3.25}},
            charging={'semi': {'type': 'auto', 'increase_per_tick': 0.1, 'decrease_per_tick': 0.1,
                               'decrease_on_fire': 0.3, 'max_charge': 0.3, 'fire_threshold': 0.3,
                               'charge_during_cooldown': False}},
            recoil={'pitch': [{'time': 0, 'value': [2.4, 2.4]}, {'time': 0.25, 'value': [0.2, 0.2]},
                              {'time': 0.4, 'value': [0, 0]}],
                    'yaw': [{'time': 0, 'value': [-0.7, -0.7]}, {'time': 0.06, 'value': [0.4, 0.4]},
                            {'time': 0.3, 'value': [0, 0]}]},
            inaccuracy={'stand': 1.5, 'move': 1.9, 'sneak': 1.0, 'lie': 0.8, 'aim': 0.08},
            fire_sound={'fire_multiplier': 1.35, 'silence_multiplier': 1.0},
        ),
        sounds={'draw': R + 'draw', 'put_away': R + 'put_away', 'shoot': R + 'shoot', 'shoot_3p': R + 'shoot_3p',
                'silence': 'tacz:deagle/deagle_silence', 'silence_3p': 'tacz:deagle/deagle_silence_3p'},
        allow=[],
        recipe=[{'item': {'tag': 'forge:ingots/iron'}, 'count': 16},
                {'item': {'item': 'minecraft:dark_oak_planks'}, 'count': 2},
                {'item': {'tag': 'forge:nuggets/gold'}, 'count': 2}],
        side_cz=-1.0, hud_ortho=7.0, slot_ortho=12.5,
        display_extra={'state_machine': 'tacz:taurus500_state_machine', 'shell': None,
                       'muzzle_flash': {'type': 'renew', 'texture': 'tacz:flash/common_muzzle_flash', 'scale': 0.85,
                                        'smoke_scale': 1.3, 'initial_speed_scale': 1.2, 'smoke_particle_count': 20}},
    )


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
    # studio shots with the suppressor fitted (preview only: both parts in one atlas)
    combo = argento.build()
    mz = np.array([0, argento.BORE_Y, argento.MUZZLE_Z])
    sp = combo.part('supp_preview', 'barrel', list(mz))
    for c in s.parts['silencer'].cubes:
        cc = sp.box(np.array(c.lo) + mz, np.array(c.hi) + mz, c.mat, data=dict(c.data, supp=True),
                    pivot=(list(np.array(c.pivot) + mz) if c.pivot is not None else None), rotation=c.rotation)
    combo.tex = 1024
    combo.layout()

    def both(p_, n_, f_, c_, uv_, wh_):
        if c_.data.get('supp'):
            return argento.suppressor_shader(p_ - mz, n_, f_, c_, uv_, wh_)
        return argento.shader(p_, n_, f_, c_, uv_, wh_)

    ctex = combo.paint(both)
    render(combo, ctex, eye=(-40, 3.5, -5.5), target=(0, 3.5, -5.5), ortho_height=13, size=(1400, 640),
           hide=hide).save(os.path.join(PREVIEW, f'{gid}_suppressed_right.png'))
    render(combo, ctex, eye=(-15, 11, -20), target=(0, 3.5, -5), fov=34, size=(1200, 700),
           hide=hide).save(os.path.join(PREVIEW, f'{gid}_suppressed_34.png'))
    render(m, tex, eye=(13, 9, 10), target=(0, 3.4, -3.5), fov=36, size=(1200, 700),
           hide=hide).save(os.path.join(PREVIEW, f'{gid}_rear34.png'))
    print(f'  {gid}: {m.cube_count()} cubes; suppressor {s.cube_count()} cubes')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    write_json('gunpack.meta.json', {'namespace': NS})
    build_argento()
    build_passero()
    build_bastone()
    build_vento()
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
