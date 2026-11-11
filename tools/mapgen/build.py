#!/usr/bin/env python3
"""Builds the Corvara map + mission data for the Recrafted mod.

    python3 tools/mapgen/build.py            # writes resources + previews
    python3 tools/mapgen/build.py --no-preview
"""
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import World  # noqa: E402
import terrain  # noqa: E402
import render  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT_MAP = os.path.join(ROOT, 'src/main/resources/data/recrafted/maps/corvara.rcmap')
OUT_MISSION = os.path.join(ROOT, 'src/main/resources/data/recrafted/missions/corvara.json')
PREVIEW = os.path.join(ROOT, 'docs/preview')


def main():
    t = time.time()
    w = World(terrain.SX, terrain.SY, terrain.SZ)
    H, K, land = terrain.build_terrain(w)
    ctx = dict(w=w, H=H, K=K, land=land, rng=random.Random(2024), anchors={}, props=[], npcs=[], zones=[])
    stages = []
    for modname in ('town', 'landmarks', 'estate', 'lab', 'mission'):
        try:
            mod = __import__(modname)
        except ModuleNotFoundError as e:
            if e.name != modname:
                raise
            continue
        stages.append(mod)
    mission = None
    for mod in stages:
        if mod.__name__ == 'mission':
            for m2 in stages:
                if hasattr(m2, 'finish'):
                    m2.finish(ctx)
        res = mod.build(ctx)
        if mod.__name__ == 'mission':
            mission = res
        print(f'  {mod.__name__} done ({time.time() - t:.1f}s)')
    if mission is None:
        for m2 in stages:
            if hasattr(m2, 'finish'):
                m2.finish(ctx)

    os.makedirs(os.path.dirname(OUT_MAP), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MISSION), exist_ok=True)
    w.save(OUT_MAP)
    if mission is not None:
        with open(OUT_MISSION, 'w') as f:
            json.dump(mission, f, indent=1, default=lambda o: int(o) if hasattr(o, '__int__') else str(o))
    print(f'palette {len(w.palette)} states, map {os.path.getsize(OUT_MAP) / 1024:.0f} KiB')

    if '--no-preview' not in sys.argv:
        os.makedirs(PREVIEW, exist_ok=True)
        render.topdown(w, os.path.join(PREVIEW, 'corvara_top.png'), scale=3)
        render.oblique(w, os.path.join(PREVIEW, 'corvara_south.png'), scale=3)
        render.oblique(w, os.path.join(PREVIEW, 'corvara_east.png'), scale=3, view='east')
        render.slice_y(w, os.path.join(PREVIEW, 'corvara_lab.png'), y=45, scale=3, depth=5)
    print(f'done in {time.time() - t:.1f}s')


if __name__ == '__main__':
    main()
