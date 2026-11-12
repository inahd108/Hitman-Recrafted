#!/usr/bin/env python3
"""Builds the Amsterdam map ("Oil & Water") for the Recrafted mod.

    python3 tools/mapgen/amsterdam/build.py            # map + previews in docs/preview/amsterdam_*
    python3 tools/mapgen/amsterdam/build.py --no-preview
"""
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))

from core import World  # noqa: E402
import render  # noqa: E402
import ams_layout as L  # noqa: E402
import ams_ground  # noqa: E402
import ams_water  # noqa: E402
import ams_harbour  # noqa: E402
import ams_city  # noqa: E402
import ams_street
import ams_boats  # noqa: E402
import ams_mission  # noqa: E402
import json  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT_MAP = os.path.join(ROOT, 'src/main/resources/data/recrafted/maps/amsterdam.rcmap')
OUT_MISSION = os.path.join(ROOT, 'src/main/resources/data/recrafted/missions/amsterdam.json')
PREVIEW = os.path.join(ROOT, 'docs/preview')


render.COLORS.update({
    'recrafted:canal_window': (238, 190, 120), 'recrafted:bulb_string': (255, 220, 140), 'recrafted:bollard': (104, 42, 32),
    'recrafted:lamp_post': (30, 52, 40), 'recrafted:canal_lamp': (255, 220, 150), 'recrafted:bicycle': (40, 40, 44),
    'recrafted:gable_scroll': (235, 229, 222), 'recrafted:gable_scroll_stone': (216, 203, 155),
    'recrafted:hoist_beam': (66, 43, 20), 'recrafted:chandelier': (212, 175, 55), 'recrafted:winch': (110, 80, 50),
    'recrafted:wage_book': (150, 40, 34), 'recrafted:metal_detector': (170, 172, 176), 'recrafted:shutter': (34, 78, 52)})


def bridges(ctx):
    for (x0, x1) in L.OUTER_BRIDGES:
        ams_water.arch_bridge(ctx, x0, x1, L.OUTER[0], L.OUTER[1], 'z')
    for (x0, x1) in L.INNER_BRIDGES:
        ams_water.arch_bridge(ctx, x0, x1, L.INNER[0], L.INNER[1], 'z')
    ams_water.drawbridge(ctx, L.DRAWBRIDGE[0], L.DRAWBRIDGE[1], L.INNER[0], L.INNER[1])
    for (z0, z1) in L.WEST_BRIDGES:
        ams_water.arch_bridge(ctx, L.WEST_CANAL[0], L.WEST_CANAL[1], z0, z1, 'x')
    for (z0, z1) in L.EAST_BRIDGES:
        ams_water.arch_bridge(ctx, L.EAST_CANAL[0], L.EAST_CANAL[1], z0, z1, 'x')
    ams_water.lock(ctx)


def main():
    t = time.time()
    w = World(L.SX, L.SY, L.SZ)
    ctx = dict(w=w, rng=random.Random(1672), anchors={}, props=[], npcs=[], zones=[])
    steps = [('ground', ams_ground.base), ('water', ams_ground.waters), ('streets', ams_ground.streets),
             ('harbour', ams_harbour.build), ('city', ams_city.build), ('bridges', bridges), ('street', ams_street.build), ('boats', ams_boats.build)]
    for name, fn in steps:
        fn(ctx)
        print(f'  {name} done ({time.time() - t:.1f}s)')
    mission = ams_mission.build(ctx)
    os.makedirs(os.path.dirname(OUT_MAP), exist_ok=True)
    w.save(OUT_MAP)
    with open(OUT_MISSION, 'w') as f:
        json.dump(mission, f, indent=1)
    print(f'houses {len(ctx.get("houses", [])) + len(ctx.get("warehouses", []))}, palette {len(w.palette)} states, '
          f'map {os.path.getsize(OUT_MAP) / 1024:.0f} KiB')
    if '--no-preview' not in sys.argv:
        os.makedirs(PREVIEW, exist_ok=True)
        render.topdown(w, os.path.join(PREVIEW, 'amsterdam_top.png'), scale=2)
        render.oblique(w, os.path.join(PREVIEW, 'amsterdam_south.png'), scale=2, ymin=40)
        render.oblique(w, os.path.join(PREVIEW, 'amsterdam_canal.png'), scale=5, crop=(60, 160, 200, 260), ymin=55)
        render.oblique(w, os.path.join(PREVIEW, 'amsterdam_harbour.png'), scale=4, crop=(0, 0, 200, 130), view='north', ymin=40)
    print(f'done in {time.time() - t:.1f}s')
    return ctx


if __name__ == '__main__':
    main()
