"""The Oil & Water cast: who is where, doing what, on which loop. Reuses Corvara's Cast helper
(waypoints snap to standable cells; long legs get pass-through stops from walkcheck)."""
from ams_layout import *  # noqa: F401,F403
from mission import Cast

# walk lines (the middle of each road), from ams_ground's quay layout
Z_OUTER_N, Z_OUTER_S, Z_INNER_N, Z_INNER_S = 89, 117, 185, 217
Z_HARBOUR, Z_BACK = 51, 293
X_WEST_W, X_WEST_E, X_EAST_W, X_EAST_E = 21, 44, 339, 360
X_ALLEY = 193
Y = STREET + 1


def mid(a):
    return (a[0] + a[1]) // 2


def build(ctx):
    c = Cast(ctx)
    wp, add, idle, A = c.wp, c.add, c.idle, c.A

    def q(x, z, wait=0, pose='stand', face=None, **kw):
        return wp((x, Y, z), wait, pose, face, **kw)

    def line(x_from, x_to, z, step=40, wait=0, pose='stand'):
        """Waypoints along an east-west quay so no leg is too long for the pathfinder."""
        n = max(1, abs(x_to - x_from) // step)
        return [q(round(x_from + (x_to - x_from) * k / n), z, wait if k == n else 0, pose if k == n else 'stand') for k in range(1, n + 1)]

    def cross(bx, z_from, z_to):
        """Over a bridge on an east-west canal: approach, crown, far end."""
        return [q(bx, z_from), q(bx, (z_from + z_to) // 2 + (1 if z_to > z_from else -1)), q(bx, z_to)]

    ob = [mid(b) for b in OUTER_BRIDGES]
    ib = [mid(b) for b in INNER_BRIDGES] + [mid(DRAWBRIDGE)]

    # ============================ TARGETS ============================================================
    add('Margriet Ostendorp', 'ostendorp', [
        wp('hamer.office.desk', 40, 'type', 's', seat=False, say='Lot nine opens at four hundred. Not a cent less.'),
        wp('hamer.office'), wp('hamer.gallery', 15, 'look', 'w'), wp('hamer.landing'), wp('hamer.stairs.foot'),
        wp('hamer.hall', 30, 'talk', 'n', say='Welcome, welcome. The catalogue is on the table.'),
        wp('hamer.reception', 10, 'talk', 'w'),
        wp('hamer.saleroom.door'), wp('hamer.saleroom'),
        wp('hamer.podium', 90, 'talk', 'n', say='Lot nine. A merchant\'s daughter, sixteen-sixty. Do I hear four hundred?'),
        wp('hamer.saleroom'), wp('hamer.corridor.w'), wp('hamer.vault.stairs'), wp('hamer.vault', 20, 'look', 's'),
        wp('hamer.vault.stairs'), wp('hamer.corridor.w'), wp('hamer.stairs.foot'), wp('hamer.landing'),
        wp('hamer.viewing', 40, 'drink', 'e', say='Between us: the provenance is impeccable.'),
        wp('hamer.landing'), wp('hamer.office'),
    ], target=True, id='ostendorp')
    for i, off in enumerate(((1, 0, 1), (-1, 0, 1))):
        add(f'Bodyguard {"Ruud" if i == 0 else "Bas"}', 'bodyguard', [wp('hamer.office', 5, 'guard', off=off)],
            follow='ostendorp', enforcer=(i == 0), skin=1)

    meester = add('Apprentice', 'apprentice', [
        wp('studio.easel0', 60, 'work', 'n', say='Left. Always left.'),
        wp('studio.window', 25, 'drink', 'n'), wp('studio'),
        wp('studio.easel1', 50, 'work', 'n'),
        wp('forger.door'), wp('forger.quay', 30, 'smoke', 'n', say='Turpentine. It gets into your head after a while.'),
        wp('forger.door'), wp('studio'),
    ], id='meester', hidden_name=True)
    meester['hidden'] = True
    meester['lefty'] = True
    for i, (e, said) in enumerate((('studio.easel1', 'He never signs them. Says the paint signs itself.'),
                                   ('studio.easel2', None), ('studio.easel3', 'Pass the lead white.'))):
        add('Apprentice', 'apprentice', [wp(e, 70, 'work', 'n', say=said), wp('studio', 15, 'talk'),
                                         wp('studio.stove', 15, 'drink', 'e'), wp(e, 50, 'work', 'n')])

    add('Sem Kooistra', 'kooistra', [
        wp('kooistra.houseboat', 45, 'drink', 'n', say='Weather like this, nobody looks at the water.'),
        q(240, Z_OUTER_S), *cross(ob[2], Z_OUTER_S, Z_OUTER_N), q(320, Z_OUTER_N), q(X_EAST_W + 2, Z_OUTER_N),
        wp('dock.jetty', 40, 'talk', 'w', say='Count it twice. Then once more.'),
        q(X_EAST_W + 2, Z_OUTER_N), q(320, Z_OUTER_N), *cross(ob[2], Z_OUTER_N, Z_OUTER_S), q(240, Z_OUTER_S),
    ], target=True, id='kooistra')
    for i in range(2):
        add(f'Deckhand {"Joop" if i == 0 else "Kees"}', 'deckhand', [wp('kooistra.houseboat', 5, 'guard', off=(i * 2 - 1, 0, 0))],
            follow='kooistra', enforcer=(i == 0), skin=i)

    # ============================ THE GULDEN HAMER ===================================================
    for i, (a, pose, face) in enumerate((('hamer.door', 'guard', 'n'), ('hamer.door', 'guard', 'n'), ('hamer.hall', 'guard', 'n'),
                                         ('hamer.saleroom.door', 'guard', 's'), ('hamer.podium', 'guard', 'n'),
                                         ('hamer.garden', 'guard', 's'), ('hamer.coach', 'guard', 'n'),
                                         ('hamer.vault', 'guard', 'n'), ('hamer.landing', 'guard', 'n'))):
        off = (2 if i == 1 else -2 if i == 0 else 0, 0, -1 if a == 'hamer.door' else 0)
        idle(f'Security {["Anouk", "Daan", "Femke", "Joris", "Lotte", "Milan", "Noor", "Pim", "Sanne"][i]}', 'auction_security',
             a, pose, face, off=off if a != 'hamer.podium' else (3, 0, -2), enforcer=(i in (0, 7)), skin=i % 2)
    add('Security Thijs', 'auction_security', [wp('hamer.corridor.w', 20, 'guard'), wp('hamer.corridor.e', 20, 'guard'),
                                               wp('hamer.kitchen', 10, 'look')], skin=1)
    for i in range(6):
        add(f'Porter {["Wim", "Gerrit", "Hans", "Jaap", "Klaas", "Arie"][i]}', 'lot_porter', [
            wp('hamer.coach', 20, 'work', off=(i - 3, 0, 1)), wp('hamer.garden'), wp('hamer.garden.door'),
            wp('hamer.corridor.w'), wp('hamer.saleroom'), wp('hamer.podium', 25, 'work', 'n', off=(i - 3, 0, -1)),
            wp('hamer.saleroom'), wp('hamer.corridor.w'), wp('hamer.garden.door'), wp('hamer.garden'),
        ], skin=i % 2)
    names = ['Mr. Haverkamp', 'Mrs. Visser-Teng', 'Count Orlov', 'Ms. Delacroix', 'Mr. Okafor', 'Mrs. Brandt', 'Dr. Lindqvist',
             'Mr. Achterberg', 'Ms. Moreau', 'Mr. Tanaka', 'Mrs. de Graaf', 'Mr. Pereira', 'Lady Ashworth', 'Mr. Vos']
    for i, n in enumerate(names):
        if i < 6:
            route = [wp(f'hamer.row{i}.w', 60, 'sit', 's', seat=True, off=(i % 3, 0, 0)), wp('hamer.saleroom'),
                     wp('hamer.hall', 30, 'drink', 'e', off=(i % 4 - 2, 0, 1)), wp('hamer.saleroom')]
        elif i < 10:
            route = [wp(f'hamer.row{i - 6}.e', 70, 'sit', 's', seat=True, off=(-(i % 3), 0, 0)), wp('hamer.saleroom'),
                     wp('hamer.gallery', 30, 'look', 'w'), wp('hamer.landing'), wp('hamer.stairs.foot'), wp('hamer.saleroom')]
        else:
            route = [wp('hamer.garden', 40, 'drink', 'n', off=(i - 12, 0, 0)), wp('hamer.garden.door'), wp('hamer.corridor.w'),
                     wp('hamer.hall', 40, 'talk', 'w', off=(0, 0, i - 11))]
        add(n, 'collector', route, skin=i % 3)
    for i, a in enumerate(('hamer.balcony', 'hamer.balcony', 'hamer.hall', 'hamer.door')):
        idle(f'Photographer {["Eva", "Luuk", "Iris", "Mees"][i]}', 'photographer', a, 'phone' if i % 2 else 'look', 's',
             off=(i * 3, 0, 0) if i < 2 else (2, 0, -1), skin=i % 2)
    for i in range(3):
        add(f'Waiter {["Bram", "Lieke", "Stijn"][i]}', 'waiter', [
            wp('hamer.kitchen.tray', 15, 'work', 's'), wp('hamer.kitchen'), wp('hamer.hall', 20, 'drink', 'w', off=(i, 0, 0)),
            wp('hamer.saleroom.door'), wp('hamer.saleroom', 15, 'drink'), wp('hamer.saleroom.door'), wp('hamer.kitchen'),
        ], skin=3)
    for i in range(2):
        idle(f'Cook {["Ingrid", "Ruben"][i]}', 'cook', 'hamer.kitchen.counter', 'work', 'e', off=(0, 0, i * 2), skin=2)
    add('Cleaner Fatma', 'cleaner', [wp('hamer.hall', 40, 'sweep'), wp('hamer.reception', 20, 'sweep'), wp('hamer.corridor.e', 30, 'sweep')], skin=2)
    for i in range(2):
        idle(f'Vault Guard {["Erik", "Hugo"][i]}', 'bodyguard', 'hamer.vault', 'guard', 's', off=(i * 2 - 1, 0, 2), skin=1)

    # ============================ THE CAFÉ ===========================================================
    for i in range(3):
        idle(f'Bartender {["Henk", "Marieke", "Youssef"][i]}', 'bartender', 'cafe.behind_bar', 'work', 'w', off=(0, 0, i * 2), skin=i % 2)
    add('Waiter Mila', 'waiter', [wp('cafe.bar', 15, 'work'), wp('cafe.table1', 15, 'talk'), wp('cafe.table2', 15, 'talk'),
                                  wp('cafe.door', 10, 'look')], skin=2)
    for i, a in enumerate(('cafe.table1', 'cafe.table2', 'cafe.bar', 'cafe.bar')):
        idle(f'Regular {["Theo", "Annelies", "Piet", "Gijs"][i]}', 'civilian', a, 'drink', 'e', off=(0, 0, i % 2), skin=3 + i % 3)
    idle('Cook Dewi', 'cook', 'cafe.kitchen', 'work', 'n', skin=2)

    # ============================ STREETS ============================================================
    xs = list(range(60, 330, 18))
    for i in range(14):
        # civilians: a stretch of quay, a bridge, back along the other side
        bi = i % len(ib)
        x0 = xs[i % len(xs)]
        z_a, z_b = (Z_INNER_N, Z_INNER_S) if i % 2 == 0 else (Z_OUTER_S, Z_OUTER_N)
        bx = ib[bi] if i % 2 == 0 else ob[i % 3]
        pose = ['phone', 'look', 'talk', 'drink', 'smoke'][i % 5]
        add(f'{["Lars", "Femke", "Joost", "Saskia", "Ruben", "Mirjam", "Koen", "Ilse", "Wouter", "Esther", "Jesse", "Roos", "Bart", "Nina"][i]}',
            'civilian', [q(x0, z_a, 20, pose), *cross(bx, z_a, z_b), q(x0 + 9, z_b, 15, 'look'), q(x0 + 9, z_b), *cross(bx, z_b, z_a)],
            skin=3 + i % 3)
    pairs = [(('square.centre', 'look'), ('square.organ', 'look')), (('church.door', 'look'), ('square.centre', 'phone')),
             (('hofje.gate', 'look'), ('church.door', 'look')), (('drawbridge.n', 'phone'), ('drawbridge.s', 'look')),
             (('ferry.square', 'phone'), ('station.platform', 'look')), (('square.organ', 'look'), ('hamer.door', 'phone')),
             (('drawbridge.s', 'look'), ('hofje.gate', 'phone'))]
    for i in range(14):
        (a, pose), (b, pose2) = pairs[i % len(pairs)]
        add(f'Tourist {i + 1}', 'tourist', [wp(a, 30, pose, off=(i % 3 - 1, 0, i % 2)), wp(b, 30, pose2, off=(i % 2, 0, 1))],
            skin=3 + i % 3)
    # couriers: fast loops round the canal ring
    loops = [
        [q(60, Z_OUTER_N), *line(60, ob[2], Z_OUTER_N), *cross(ob[2], Z_OUTER_N, Z_OUTER_S), *line(ob[2], ob[0], Z_OUTER_S),
         *cross(ob[0], Z_OUTER_S, Z_OUTER_N)],
        [q(60, Z_INNER_N), *line(60, ib[2], Z_INNER_N), *cross(ib[2], Z_INNER_N, Z_INNER_S), *line(ib[2], ib[0], Z_INNER_S),
         *cross(ib[0], Z_INNER_S, Z_INNER_N)],
        [q(X_ALLEY, MID_N[0] + 2), q(X_ALLEY, MID_S[1] - 2), *cross(ib[1], Z_INNER_N, Z_INNER_S), q(250, Z_INNER_S), q(250, Z_INNER_S),
         *cross(ib[2], Z_INNER_S, Z_INNER_N), q(X_ALLEY + 1, Z_INNER_N)],
    ]
    for i in range(6):
        route = [dict(p, run=True) for p in loops[i % 3]]
        add(f'Courier {["Sem", "Lotte", "Mo", "Fleur", "Dirk", "Yara"][i]}', 'courier', route, skin=i % 2)
    # flower sellers on the barges, the herring cart, the organ
    for i in range(5):
        x = BLOEMENPLEIN[0] + 3 + (i % 3) * 16 + (i // 3) * 6
        idle(f'Flower Seller {["Anja", "Gert", "Ria", "Kim", "Tom"][i]}', 'flower_seller', (x, WATER + 2, INNER[1] - 3),
             'work' if i % 2 else 'talk', 'n', skin=i % 2)
    for i in range(2):
        idle(f'Herring Vendor {["Cor", "Jan"][i]}', 'herring_vendor', (BLOEMENPLEIN[0] + 4 + i * 30, Y, INNER_S_QUAY[1] - 1),
             'work', 'n', say='Hollandse nieuwe! Fresh in this morning.' if i == 0 else None)
    idle('Organist Frits', 'organist', 'square.organ', 'work', 's', say=None)
    # police in pairs
    beats = [
        [q(70, Z_INNER_S, 20, 'guard'), *line(70, 260, Z_INNER_S, wait=20, pose='look'), *line(260, 70, Z_INNER_S)],
        [q(80, Z_INNER_N, 20, 'guard'), *line(80, 280, Z_INNER_N, wait=20, pose='look'), *line(280, 80, Z_INNER_N)],
        [q(70, Z_OUTER_S, 20, 'guard'), *line(70, 300, Z_OUTER_S, wait=20, pose='look'), *line(300, 70, Z_OUTER_S)],
        [q(60, Z_OUTER_N, 20, 'guard'), *line(60, 320, Z_OUTER_N, wait=20, pose='look'), *line(320, 60, Z_OUTER_N)],
        [wp('square.centre', 30, 'guard'), wp('church.door', 20, 'look'), wp('hofje.gate', 20, 'look')],
        [wp('police.door', 60, 'guard', 'n'), q(mid(POLICE) + 6, Z_INNER_S, 20, 'look')],
    ]
    for i in range(12):
        beat = beats[i // 2]
        add(f'Agent {["De Vries", "Jansen", "Bakker", "Visser", "Smit", "Meijer", "Mulder", "Bos", "Peters", "Hendriks", "Dekker", "Dijkstra"][i]}',
            'police', [dict(p, pos=[p['pos'][0] + (i % 2) * 1.0, p['pos'][1], p['pos'][2]]) for p in beat],
            enforcer=(i % 2 == 0), skin=i % 2)
    # cleaners
    add('Cleaner Ahmed', 'cleaner', [wp('station.platform', 40, 'sweep'), q(40, Z_HARBOUR, 30, 'sweep')], skin=2)
    add('Cleaner Petra', 'cleaner', [wp('square.centre', 40, 'sweep', off=(4, 0, 2)), wp('square.organ', 30, 'sweep', off=(3, 0, 3))], skin=2)
    # houseboat residents on their decks
    decks = [b for b in ctx.get('boats', []) if b.get('name') != 'kooistra_houseboat']
    for i, b in enumerate(decks[:6]):
        idle(f'{["Marjolein", "Ab", "Greetje", "Hidde", "Tess", "Olaf"][i]}', 'houseboater', b['deck'],
             ['smoke', 'look', 'drink', 'phone', 'look', 'smoke'][i], 's', skin=i % 2)
    # skippers at the ferry, bridge keepers at their posts
    for i in range(4):
        idle(f'Skipper {["Gerard", "Willem", "Nel", "Bas"][i]}', 'skipper', 'ferry.square' if i < 2 else 'exit.ferry',
             'smoke' if i % 2 else 'look', 'n', off=(i * 2 - 3, 0, 0), skin=i % 2)
    idle('Lock Keeper Hendrik', 'bridge_keeper', 'lock.keeper', 'look', 'w')
    idle('Bridge Keeper Toos', 'bridge_keeper', 'drawbridge.s', 'look', 'n', off=(-3, 0, 1))
    # harbour: warehouse porters and the smuggler's crew
    for i in range(8):
        x = 60 + i * 30
        add(f'Porter {["Daan", "Kevin", "Mustafa", "Rik", "Pieter", "Jens", "Tim", "Rob"][i]}', 'porter', [
            q(x, Z_HARBOUR + 4, 30, 'work', 'n'), q(x + 6, Z_HARBOUR, 10), q(x + 6, Z_HARBOUR + 4, 30, 'work', 'n')], skin=i % 2)
    for i in range(6):
        idle(f'Deckhand {["Arjen", "Bert", "Chris", "Dennis", "Edwin", "Frank"][i]}', 'deckhand', 'dock.jetty',
             'guard' if i % 3 == 0 else 'smoke', 'e', off=(0, 0, i * 3 - 8), enforcer=(i == 0), skin=i % 2)

    zones = [
        dict(name='hamer_vault', box=[GULDEN_HAMER[0], FLOOR0 - 8, SOUTH_HOUSES[0], GULDEN_HAMER[0] + 14, FLOOR0 - 1, SOUTH_HOUSES[0] + 15],
             allow=['auction_security', 'bodyguard'], label='Gulden Hamer — vault'),
        dict(name='hamer_private', box=[GULDEN_HAMER[0], FLOOR0 + 5, SOUTH_HOUSES[0], GULDEN_HAMER[1], FLOOR0 + 12, SOUTH_HOUSES[0] + 16],
             allow=['auction_security', 'bodyguard', 'cleaner'], label='Gulden Hamer — private rooms'),
        dict(name='hamer_kitchen', box=[mid(GULDEN_HAMER) + 6, FLOOR0, SOUTH_HOUSES[0] + 2, GULDEN_HAMER[1], FLOOR0 + 4, SOUTH_HOUSES[0] + 14],
             allow=['waiter', 'cook', 'lot_porter', 'auction_security', 'cleaner'], label='Gulden Hamer — catering'),
        dict(name='hamer_saleroom', box=[GULDEN_HAMER[0], FLOOR0, SOUTH_HOUSES[0] + 16, GULDEN_HAMER[1], FLOOR0 + 9, SOUTH_HOUSES[0] + 29],
             allow=['collector', 'auction_security', 'lot_porter', 'waiter', 'photographer', 'bodyguard', 'cleaner'],
             label='Saleroom — bidders only'),
        dict(name='forger', box=[FORGER[0], FLOOR0, SOUTH_HOUSES[0], FORGER[1], STREET + 50, SOUTH_HOUSES[1] + 20],
             allow=['apprentice'], label='Private house'),
        dict(name='dock', box=[EAST_CANAL[0] - 2, STREET - 6, WAREHOUSES[0], EAST_CANAL[1] + 2, STREET + 20, WAREHOUSES[1]],
             allow=['deckhand'], label='Boathouse — keep out'),
        dict(name='police', box=[POLICE[0], FLOOR0, SOUTH_HOUSES[0] + 1, POLICE[1], FLOOR0 + 14, SOUTH_HOUSES[1]],
             allow=['police'], label='Politie — staff only'),
    ]
    import walkcheck
    added = walkcheck.split_long_legs(ctx['w'], c.npcs)
    problems = walkcheck.check_routes(ctx['w'], c.npcs)
    print(f'  cast: {len(c.npcs)} npcs, {getattr(c, "moved", 0)} snapped, {added} stops added, '
          f'{len(c.warn)} warnings, {len(problems)} unreachable legs')
    for wmsg in c.warn[:20]:
        print('    ', wmsg)
    for pr in problems[:30]:
        print('    ', pr)
    return c.npcs, zones
