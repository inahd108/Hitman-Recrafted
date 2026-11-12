"""Skins and outfit items for the Amsterdam cast (Oil & Water).

    python3 tools/assets/ams_cast.py

Only writes the Amsterdam files: the new roles, the extra rain-weather variants of the six roles
Amsterdam borrows from Corvara, and outfit items for the new wearable roles. Seeds are stable.
"""
import json
import os
import random
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_assets as g  # noqa: E402

D = g.D

# role -> list of (variant index, spec). Reused roles start after Corvara's variants.
SKINS = {
    'civilian': [(3, D(tone=0, hair=2, shirt='3b4a5a', pants='2b2e33', jacket='5a3b2e', shoes='1c1d21', hat=('beanie', '2c3e50'))),
                 (4, D(tone=1, hair=7, hairstyle='bob', shirt='c0392b', pants='1c1d21', jacket='d4ac0d', shoes='1c1d21')),
                 (5, D(tone=4, hair=4, hairstyle='crop', shirt='f2f2ee', pants='34495e', jacket='1f3a5a', glasses='clear', shoes='5d4037'))],
    'tourist': [(3, D(tone=5, hair=3, shirt='e74c3c', pants='3b4a66', jacket='f1c40f', hat=('cap', '2c3e50'), shoes='f2f2ee')),
                (4, D(tone=0, hair=1, hairstyle='long', shirt='9b59b6', pants='2c3e50', jacket='48c9b0', shoes='e8dcc0')),
                (5, D(tone=2, hair=4, shirt='ecf0f1', pants='566573', jacket='e67e22', glasses='dark', hat=('beanie', 'c0392b'), shoes='1c1d21'))],
    'waiter': [(2, D(tone=0, hair=4, shirt='f2f2ee', pants='1c1d21', vest='1c1d21', apron='f2f2ee', shoes='1c1d21')),
               (3, D(tone=3, hair=6, hairstyle='crop', shirt='f2f2ee', pants='1c1d21', jacket='f7f7f2', tie='1c1d21', shoes='1c1d21'))],
    'cook': [(2, D(tone=1, hair=4, shirt='f7f7f2', pants='1c1d21', buttons='1c1d21', hat=('toque', 'f7f7f2'), apron='34495e'))],
    'cleaner': [(2, D(tone=4, hair=4, hairstyle='bob', shirt='5d6d7e', pants='34495e', stripe='f39c12', gloves='f39c12'))],
    'bodyguard': [(1, D(tone=2, hair=4, hairstyle='bald', shirt='1c1d21', pants='15161a', jacket='15161a', tie='15161a', glasses='dark',
                        beard=True, shoes='0d0d0f'))],
    'courier': [(0, D(tone=1, hair=4, shirt='27ae60', pants='1c1d21', hat=('helmet', 'f1c40f'), gloves='1c1d21', stripe='1c1d21', shoes='1c1d21')),
                (1, D(tone=4, hair=4, hairstyle='crop', shirt='e67e22', pants='2c3e50', stripe='1c1d21', hat=('cap', '1c1d21'), shoes='f2f2ee'))],
    'skipper': [(0, D(tone=0, hair=5, shirt='1f3a6e', pants='2c3e50', stripe='f2f2ee', hat=('cap', '1f3a6e'), beard=True, shoes='1c1d21')),
                (1, D(tone=2, hair=4, shirt='f2f2ee', pants='1f3a6e', vest='1f3a6e', hat=('cap', 'f2f2ee'), shoes='1c1d21'))],
    'houseboater': [(0, D(tone=1, hair=7, hairstyle='long', shirt='7d9c5a', pants='4a4038', jacket='6b5a48', shoes='5d4037')),
                    (1, D(tone=0, hair=6, shirt='c0392b', pants='34495e', hat=('beanie', 'f39c12'), beard=True, shoes='1c1d21'))],
    'flower_seller': [(0, D(tone=0, hair=1, hairstyle='bob', shirt='f2f2ee', pants='34495e', apron='27ae60', sleeve=6, shoes='1c1d21')),
                      (1, D(tone=3, hair=4, shirt='d98880', pants='4a4038', apron='1e8449', hat=('scarf', 'f39c12'), shoes='1c1d21'))],
    'herring_vendor': [(0, D(tone=0, hair=5, shirt='f2f2ee', pants='1f3a6e', apron='f2f2ee', stripe='1f3a6e', hat=('cap', '1f3a6e'),
                             moustache=True, shoes='1c1d21'))],
    'bartender': [(0, D(tone=1, hair=4, shirt='f2f2ee', pants='1c1d21', vest='5a3b2e', apron='1c1d21', sleeve=6, moustache=True, shoes='1c1d21')),
                  (1, D(tone=0, hair=2, hairstyle='long', shirt='1c1d21', pants='1c1d21', apron='5a3b2e', shoes='1c1d21'))],
    'organist': [(0, D(tone=0, hair=6, shirt='c0392b', pants='1c1d21', vest='f1c40f', hat=('cap', '1c1d21'), beard=True, shoes='1c1d21'))],
    'police': [(0, D(tone=1, hair=4, hairstyle='crop', shirt='1c2a44', pants='1c2a44', belt='1c1d21', badge='e3b341', stripe='f2f2ee',
                     hat=('cap', '1c2a44'), shoes='1c1d21')),
               (1, D(tone=2, hair=7, hairstyle='bob', shirt='1c2a44', pants='1c2a44', belt='1c1d21', badge='e3b341', vest='d4e157',
                     hat=('cap', '1c2a44'), shoes='1c1d21'))],
    'auction_security': [(0, D(tone=0, hair=4, hairstyle='crop', shirt='f2f2ee', pants='1c1d21', jacket='22262b', tie='22262b', badge='c9a45c',
                               shoes='0d0d0f')),
                         (1, D(tone=4, hair=4, hairstyle='bald', shirt='f2f2ee', pants='1c1d21', jacket='22262b', tie='22262b', badge='c9a45c',
                               shoes='0d0d0f'))],
    'lot_porter': [(0, D(tone=0, hair=1, shirt='7f8c8d', pants='34495e', jacket='95a5a6', gloves='f2f2ee', shoes='1c1d21')),
                   (1, D(tone=2, hair=4, hairstyle='crop', shirt='7f8c8d', pants='34495e', jacket='95a5a6', gloves='f2f2ee', shoes='1c1d21'))],
    'collector': [(0, D(tone=0, hair=6, hairstyle='crop', shirt='f2f2ee', pants='1c1d21', jacket='1c1d21', tie='1c1d21', shoes='0d0d0f')),
                  (1, D(tone=1, hair=4, hairstyle='long', shirt='7b241c', pants='7b241c', dress='7b241c', shoes='1c1d21')),
                  (2, D(tone=3, hair=5, shirt='f2f2ee', pants='2c3e50', jacket='2c3e50', tie='8e44ad', glasses='clear', moustache=True,
                        shoes='1c1d21'))],
    'photographer': [(0, D(tone=1, hair=4, shirt='566573', pants='2c3e50', vest='6e2c00', hat=('beanie', '1c1d21'), shoes='1c1d21')),
                     (1, D(tone=0, hair=3, hairstyle='bob', shirt='ecf0f1', pants='1c1d21', jacket='5d6d7e', shoes='1c1d21'))],
    'apprentice': [(0, D(tone=1, hair=4, shirt='e8e4d8', pants='566573', apron='e8e4d8', hat=('beanie', '5d4037'), beard=True,
                         shoes='5d4037'))],
    'bridge_keeper': [(0, D(tone=0, hair=5, shirt='2c3e50', pants='2c3e50', vest='f39c12', stripe='f2f2ee', hat=('cap', '2c3e50'),
                            shoes='1c1d21'))],
    'deckhand': [(0, D(tone=2, hair=4, hairstyle='crop', shirt='1c1d21', pants='2c3e50', jacket='1c1d21', hat=('beanie', '1c1d21'),
                       shoes='1c1d21')),
                 (1, D(tone=4, hair=4, shirt='2c3e50', pants='2c3e50', jacket='1c1d21', beard=True, shoes='1c1d21'))],
    'porter': [(0, D(tone=1, hair=4, shirt='5d6d7e', pants='34495e', apron='6e2c00', sleeve=6, hat=('cap', '34495e'), shoes='1c1d21')),
               (1, D(tone=3, hair=4, hairstyle='crop', shirt='5d6d7e', pants='34495e', apron='6e2c00', sleeve=6, shoes='1c1d21'))],
    'ostendorp': [(0, D(tone=0, hair=3, hairstyle='bob', shirt='f2f2ee', pants='1c1d21', jacket='1c1d21', dress='1c1d21', collar='f2f2ee',
                        badge='c9a45c', shoes='1c1d21'))],
    'kooistra': [(0, D(tone=1, hair=4, hairstyle='crop', shirt='34495e', pants='2c3e50', jacket='5a3b2e', beard=True, hat=('cap', '1c1d21'),
                       shoes='1c1d21'))],
}
OUTFITS = {
    'courier': ('27ae60', '1c1d21'), 'skipper': ('1f3a6e', 'f2f2ee'), 'flower_seller': ('27ae60', 'f2f2ee'),
    'herring_vendor': ('f2f2ee', '1f3a6e'), 'bartender': ('5a3b2e', 'f2f2ee'), 'police': ('1c2a44', 'e3b341'),
    'auction_security': ('22262b', 'c9a45c'), 'lot_porter': ('95a5a6', 'f2f2ee'), 'collector': ('1c1d21', 'f2f2ee'),
    'photographer': ('6e2c00', '566573'), 'apprentice': ('e8e4d8', '5d4037'), 'bridge_keeper': ('f39c12', '2c3e50'),
    'deckhand': ('1c1d21', '2c3e50'), 'porter': ('6e2c00', '5d6d7e'),
}
TITLES = {
    'courier': 'Cycle Courier', 'skipper': 'Boat Skipper', 'flower_seller': 'Flower Seller', 'herring_vendor': 'Herring Vendor',
    'bartender': 'Bartender', 'police': 'Politie Officer', 'auction_security': 'Auction Security', 'lot_porter': 'Lot Porter',
    'collector': 'Art Collector', 'photographer': 'Press Photographer', 'apprentice': 'Apprentice Painter',
    'bridge_keeper': 'Bridge Keeper', 'deckhand': 'Deckhand', 'porter': 'Warehouse Porter',
}
LANG = {f'item.recrafted.outfit_{r}': t + ' Outfit' for r, t in TITLES.items()}


def paint_stains(im, rnd):
    """Dabs of oil paint on the apprentice's smock (front of the body)."""
    cols = [(178, 34, 34), (30, 90, 160), (212, 172, 13), (39, 120, 70), (236, 236, 228)]
    for _ in range(9):
        x, y = rnd.randint(20, 27), rnd.randint(21, 31)
        im.putpixel((x, y), rnd.choice(cols) + (255,))


def main():
    n = 0
    for role, variants in SKINS.items():
        for idx, spec in variants:
            rnd = random.Random(zlib.crc32(f'{role}_{idx}'.encode()))
            im = g.make_skin(spec, rnd)
            if role == 'apprentice':
                paint_stains(im, rnd)
            g.save(im, 'textures', 'entity', 'npc', f'{role}_{idx}.png')
            n += 1
    for role, (m, a) in OUTFITS.items():
        g.save(g.outfit_sprite(m, a).finish(), 'textures', 'item', f'outfit_{role}.png')
        g.write_json(os.path.join(g.ASSETS, 'models/item', f'outfit_{role}.json'),
                     {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'recrafted:item/outfit_{role}'}})
    path = os.path.join(g.ASSETS, 'lang/en_us.json')
    with open(path) as f:
        lang = json.load(f)
    lang.update(LANG)
    g.write_json(path, lang)
    print(f'{n} skins, {len(OUTFITS)} outfits')


if __name__ == '__main__':
    main()
