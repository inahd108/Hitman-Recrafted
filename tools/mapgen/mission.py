"""Mission data for Corvara: cast, routes, props, zones and objectives.

Everything is expressed through named anchors recorded while the map was
built, so the routes stay valid when the geometry changes.
"""
YAW = {'s': 0, 'w': 90, 'n': 180, 'e': -90, None: None}


class Cast:
    def __init__(self, ctx):
        self.ctx = ctx
        self.A = ctx['anchors']
        self.w = ctx['w']
        self.npcs = []
        self.warn = []

    def P(self, a, off=(0, 0, 0)):
        p = self.A[a] if isinstance(a, str) else a
        return (p[0] + off[0], p[1] + off[1], p[2] + off[2])

    def wp(self, a, wait=0, pose='stand', face=None, run=False, say=None, off=(0, 0, 0), seat=False):
        x, y, z = self.P(a, off)
        x, y, z = int(x), int(y), int(z)
        if seat:
            y += 1
        else:
            x, y, z = self._free(a, x, y, z)
        d = dict(pos=[x + .5, y, z + .5], wait=int(wait * 20), pose=pose)
        if face is not None:
            d['yaw'] = YAW[face] if isinstance(face, str) else face
        if run:
            d['run'] = True
        if say:
            d['say'] = say
        return d

    def _ok(self, x, y, z):
        w = self.w
        soft = ('air', 'grass', 'fern', 'poppy', 'dandelion', 'azure_bluet', 'oxeye_daisy', 'cornflower',
                'white_tulip', 'rail')
        nm = w.name(w.get(x, y, z)).split(':')[1].split('[')[0]
        up = w.name(w.get(x, y + 1, z)).split(':')[1].split('[')[0]
        below = w.name(w.get(x, y - 1, z)).split(':')[1].split('[')[0]
        if nm not in soft and 'carpet' not in nm:
            return False
        if up not in soft:
            return False
        if below in soft or below == 'water' or 'leaves' in below or 'fence' in below or 'wall' in below \
                or 'bars' in below or 'pane' in below or 'lantern' in below:
            return False
        return True

    def _free(self, a, x, y, z):
        """Snap a waypoint to the nearest standable cell."""
        best = None
        for r in range(0, 4):
            for dy in (0, 1, -1, 2, -2):
                for dx in range(-r, r + 1):
                    for dz in range(-r, r + 1):
                        if max(abs(dx), abs(dz)) != r:
                            continue
                        if self._ok(x + dx, y + dy, z + dz):
                            cand = (abs(dy) * 2 + abs(dx) + abs(dz), x + dx, y + dy, z + dz)
                            if best is None or cand < best:
                                best = cand
            if best is not None:
                break
        if best is None:
            self.warn.append(f'{a} -> ({x},{y},{z}) has no standable cell nearby')
            return x, y, z
        if best[0] > 0:
            self.moved = getattr(self, 'moved', 0) + 1
        return best[1], best[2], best[3]

    def add(self, name, role, route, mode='loop', target=False, enforcer=False, skin=None, id=None,
            follow=None, sick=None, hidden_name=True):
        first = route[0]['pos']
        d = dict(name=name, role=role, pos=first, yaw=route[0].get('yaw', 0),
                 route=dict(mode=mode, points=route))
        if id:
            d['id'] = id
        if target:
            d['target'] = True
        if enforcer:
            d['enforcer'] = True
        if skin is not None:
            d['skin'] = skin
        if follow:
            d['follow'] = follow
        if sick:
            p = self.P(sick)
            d['sickSpot'] = [int(p[0]) + .5, int(p[1]), int(p[2]) + .5]
        self.npcs.append(d)
        return d

    def idle(self, name, role, a, pose='stand', face=None, say=None, seat=False, off=(0, 0, 0), **kw):
        return self.add(name, role, [self.wp(a, 30, pose, face, say=say, seat=seat, off=off)], mode='once', **kw)


def build(ctx):
    c = Cast(ctx)
    wp, add, idle, A = c.wp, c.add, c.idle, c.A

    # ======================= TARGETS ==========================================
    add('Marco Belmonte', 'belmonte', [
        wp('villa.bedroom.table', 25, 'drink', 'w', say='Another vintage wasted on investors.'),
        wp('villa.bedroom'), wp('villa.gallery'),
        wp('villa.office'), wp('villa.office.desk', 45, 'type', 's', seat=True),
        wp('villa.office.window', 15, 'phone', 's', say='The shipment leaves tonight. No delays.'),
        wp('villa.gallery'), wp('villa.landing'), wp('villa.hall.stairs'), wp('villa.hall'),
        wp('court.arches'), wp('court.fountain', 12, 'look', 's'),
        wp('court.w'), wp('garden.w'), wp('pool.path'), wp('pool.south'),
        wp('pool.bar.front', 30, 'drink', 'n', say='The usual. And keep them coming.'),
        wp('pool.lounger1', 40, 'sit', 'w', seat=True),
        wp('pool.south'), wp('pool.path'), wp('kitchen.door'), wp('kitchen.prep'),
        wp('cellar.stairs.top'), wp('cellar.stairs.bottom'), wp('cellar.mid'),
        wp('cellar.tasting', 40, 'drink', 'n', say='Ah. The ninety-eight.'),
        wp('cellar.mid'), wp('cellar.stairs.bottom'), wp('cellar.stairs.top'), wp('kitchen.court_door'),
        wp('court.arches'), wp('villa.hall'), wp('villa.dining'),
        wp('villa.dining.head', 45, 'eat', 's', off=(0, 0, -1), say='Sit. Eat. We will talk business after.'),
        wp('villa.dining'), wp('villa.hall'), wp('villa.hall.stairs'), wp('villa.landing'), wp('villa.gallery'),
        wp('villa.bedroom'),
    ], target=True, id='belmonte', sick='kitchen.door')
    for i, off in enumerate(((1, 0, 1), (-1, 0, 1))):
        add(f'Bodyguard {"Dario" if i == 0 else "Enzo"}', 'bodyguard',
            [wp('villa.bedroom', 5, 'guard', off=off)], follow='belmonte', enforcer=(i == 0))

    add('Dr. Ilse Varga', 'varga', [
        wp('lab.varga.desk', 45, 'type', 's', seat=True, say='Batch nine is stable. Finally.'),
        wp('lab.varga'), wp('lab.hall.e'),
        wp('lab.console2', 30, 'type', 'n'),
        wp('lab.core.door', 20, 'look', 'n', say='Beautiful, isn\'t it? One vial and a harvest is ash.'),
        wp('lab.hall.w'), wp('lab.wetlab'), wp('lab.wetlab.bench', 30, 'work', 'w'),
        wp('lab.wetlab'), wp('lab.hall.w'), wp('lab.hall.nw'), wp('lab.greenhouse'),
        wp('lab.greenhouse.w', 25, 'crouch', 'n'),
        wp('lab.greenhouse'), wp('lab.hall.nw'), wp('lab.hall.s'), wp('lab.c2.2'), wp('lab.c2.4'),
        wp('lab.airlock.n'), wp('lab.airlock'), wp('lab.airlock.s'), wp('lab.c1'),
        wp('lab.canteen'), wp('lab.canteen.seat1', 40, 'drink', 'w', seat=True, say='This coffee is a war crime.'),
        wp('lab.canteen'), wp('lab.c1'), wp('lab.airlock.s'), wp('lab.airlock'), wp('lab.airlock.n'),
        wp('lab.c2.4'), wp('lab.c2.2'), wp('lab.hall.s'), wp('lab.hall.e'), wp('lab.varga'),
    ], target=True, id='varga', sick='lab.lockers.bench')

    add('Capitano Renzo Sordi', 'sordi', [
        wp('office.desk', 40, 'type', 's', seat=True),
        wp('office.window', 15, 'look', 's', say='My harbour. My rules.'),
        wp('office.upstairs'), wp('office.lobby'), wp('harbour_office.door'),
        wp('boat.patrol', 20, 'look', 's', off=(0, 3, -6)),
        wp('quay.walk6'), wp('quay.walk4'), wp('fishmarket.front'),
        wp('fishmarket.center', 20, 'talk', 'n', say='Belmonte\'s crates go through unopened. Understood?'),
        wp('fishmarket.front'), wp('quay.mid'), wp('trattoria.front'),
        wp('trattoria.seat1', 45, 'drink', 'n', seat=True, say='Nino! The house red.'),
        wp('trattoria.front'), wp('quay.mid'), wp('quay.walk6'), wp('harbour_office.door'),
        wp('office.lobby'), wp('office.upstairs'),
    ], target=True, id='sordi', sick='fishmarket.center')
    add('Agente Ricci', 'harbour_guard', [wp('office.upstairs', 5, 'guard', off=(1, 0, 1))], follow='sordi',
        enforcer=True)

    # ======================= HARBOUR ============================================
    idle('Ferryman Aldo', 'fisherman', 'ferry.deck', 'lean', 'n', say='Next crossing is at six. Maybe.', off=(-1, 0, -3))
    add('Harbour Officer Conti', 'harbour_guard', [
        wp('quay.w', 8, 'guard', 's'), wp('quay.walk1'), wp('quay.walk2'), wp('quay.walk3', 6, 'look', 's'), wp('quay.mid'),
        wp('quay.walk5', 6, 'guard', 's'), wp('quay.e', 10, 'guard', 'w'),
    ], mode='pingpong')
    add('Harbour Officer Greco', 'harbour_guard', [
        wp('pier.start', 10, 'guard', 's'), wp('pier.mid'), wp('pier.end', 15, 'look', 's'), wp('pier.mid'),
        wp('quay.walk2', 8, 'guard', 'n'),
    ])
    idle('Harbour Clerk Paola', 'harbour_guard', 'office.counter', 'type', 's')
    idle('Harbour Officer Bruno', 'harbour_guard', 'yacht.gangway', 'guard', 'w', off=(-2, 0, -2), enforcer=True)
    fnames = ['Old Tonio', 'Beppe', 'Salvo', 'Gino']
    spots = [('boat.0', 'quay.bench100'), ('boat.2', 'quay.bench132'), ('boat.4', 'quay.bench172'),
             ('boat.trawler', 'quay.bench190')]
    for i, (b, q) in enumerate(spots):
        bx, by, bz = A[b]
        add(fnames[i], 'fisherman', [
            wp((bx, 66, 202), 25, 'work', 's', say=['Nets are torn again.', None, 'Wind is turning.', None][i]),
            wp(q, 30, 'sit', 's', seat=True),
            wp((bx, 66, 199), 12, 'smoke', 's'),
            wp(f'fishmarket.stall{i}', 15, 'talk', 'n'),
        ])
    for i in range(3):
        idle(['Fishmonger Rosa', 'Fishmonger Carlo', 'Fishmonger Ines'][i], 'shopkeeper', f'fishmarket.monger{i * 2}',
             'work', 's', say=[None, 'Fresh this morning! Fresh!', None][i])
    add('Shopper Lucia', 'civilian', [
        wp('fishmarket.stall1', 15, 'look', 'n'), wp('fishmarket.stall3', 12, 'talk', 'n'),
        wp('fishmarket.front'), wp('quay.walk4', 10, 'look', 's'), wp('fishmarket.stall5', 15, 'look', 'n'),
    ])
    add('Shopper Matteo', 'civilian', [
        wp('fishmarket.stall4', 18, 'look', 'n'), wp('fishmarket.center', 8, 'phone'),
        wp('fishmarket.stall0', 15, 'talk', 'n'),
    ])
    idle('Chef Nino', 'cook', 'trattoria.inside', 'work', 'n', off=(0, 0, -3))
    add('Waiter Fabio', 'waiter', [
        wp('trattoria.table0', 10, 'talk', 'w'), wp('trattoria.front'), wp('trattoria.door'),
        wp('trattoria.inside', 12, 'work', 'n'), wp('trattoria.door'), wp('trattoria.table2', 10, 'talk', 'w'),
        wp('trattoria.front', 8, 'look', 's'),
    ])
    idle('Diner Giulia', 'tourist', 'trattoria.seat0', 'eat', 'n', seat=True)
    idle('Diner Henrik', 'tourist', 'trattoria.seat0b', 'drink', 's', seat=True)
    idle('Diner Sofia', 'civilian', 'trattoria.seat2', 'eat', 'n', seat=True)
    tour = ['Tourist Amelie', 'Tourist Jonas', 'Tourist Priya', 'Tourist Kenji', 'Tourist Marta', 'Tourist Owen']
    add(tour[0], 'tourist', [wp('quay.walk0', 10, 'look', 's'), wp('quay.walk2', 8, 'phone', 's'),
                             wp('quay.bench112', 25, 'sit', 's', seat=True), wp('quay.walk1')])
    add(tour[1], 'tourist', [wp('pier.end', 25, 'look', 's', off=(-1, 0, -2)), wp('pier.mid', 8, 'phone', 'w'),
                             wp('pier.start'), wp('quay.walk2', 10, 'look', 'n')])
    add(tour[2], 'tourist', [wp('quay.walk5', 12, 'phone', 's'), wp('quay.walk7', 12, 'look', 's'),
                             wp('quay.bench232', 20, 'sit', 's', seat=True)])
    add(tour[3], 'tourist', [wp('mole.0', 10, 'look', 'w'), wp('mole.2', 15, 'phone', 'e'),
                             wp('mole.3', 10, 'look', 's'), wp('mole.bench', 20, 'look', 'e')], mode='pingpong')
    idle('Lighthouse Keeper Ugo', 'fisherman', 'lighthouse.door', 'smoke', 'n', say='Forty years. Never one wreck.')
    idle('Skipper Dante', 'civilian', 'yacht.deck', 'lean', 'n', off=(0, 0, 2))
    add('Deckhand Pio', 'cleaner', [wp('yacht.deck', 25, 'sweep', 'n', off=(1, 0, -1)),
                                    wp('yacht.deck', 25, 'sweep', 's', off=(-1, 0, 1))], mode='pingpong')
    # beach
    for i in range(4):
        idle(['Sunbather Chiara', 'Sunbather Tom', 'Sunbather Elena', 'Sunbather Nils'][i], 'tourist',
             f'beach.sunbed{i}', 'sleep' if i % 2 == 0 else 'sit', 's', seat=True)
    idle('Barman Leo', 'waiter', 'beach.bar', 'work', 's')
    add('Beachgoer Sara', 'tourist', [wp('beach.bar.front', 20, 'drink', 'n'), wp('beach.spot2', 15, 'look', 's'),
                                      wp('beach.shore', 20, 'look', 's'), wp('beach.spot0', 10, 'phone')])

    # ======================= PIAZZA ===============================================
    idle('Barista Franca', 'shopkeeper', 'cafe.counter', 'work', 'e')
    add('Waiter Luca', 'waiter', [
        wp('cafe.table0', 8, 'talk', 'n'), wp('cafe.table3', 8, 'talk', 'n'), wp('cafe.door'),
        wp('cafe.inside', 10, 'work', 'w'), wp('cafe.door'), wp('cafe.table4', 8, 'talk', 'n'),
    ])
    add('Waiter Sandro', 'waiter', [
        wp('cafe.table5', 10, 'talk', 'n'), wp('cafe.table1', 8, 'talk', 'n'), wp('cafe.door', 12, 'smoke', 'e'),
    ])
    pat = ['Signora Bianchi', 'Signor Russo', 'Tourist Claire', 'Tourist Diego', 'Professor Vitale', 'Signora Marino']
    for i in range(6):
        idle(pat[i], 'tourist' if 'Tourist' in pat[i] else 'civilian', f'cafe.seat{i * 2 if i < 3 else i * 2 + 1}',
             ['drink', 'sit', 'eat', 'phone', 'drink', 'sit'][i], 'e' if (i * 2 if i < 3 else i * 2 + 1) % 2 == 0 else 'w',
             seat=True)
    for i in range(4):
        idle(['Vendor Pina', 'Vendor Tano', 'Vendor Assunta', 'Vendor Mimmo'][i], 'shopkeeper', f'market.vendor{i}',
             'work', 's', off=(0, 0, -2), say=[None, 'Lemons! Sweet as sin!', None, None][i])
    add('Shopper Elio', 'civilian', [wp('market.stall0', 14, 'look', 'n'), wp('market.stall1', 12, 'talk', 'n'),
                                     wp('market.stall3', 14, 'look', 'n'), wp('piazza.fountain.e', 10, 'look', 'w')])
    add('Shopper Nadia', 'civilian', [wp('market.stall2', 14, 'talk', 'n'), wp('piazza.kiosk', 12, 'look', 's'),
                                      wp('market.stall1', 12, 'look', 'n')])
    idle('Nonno Peppino', 'civilian', 'piazza.bench.s', 'sit', 's', seat=True, say='In my day the fish were bigger.')
    idle('Nonno Ciro', 'civilian', 'piazza.bench.e', 'sit', 'e', seat=True)
    add('Street Sweeper Aldo', 'cleaner', [
        wp('piazza.fountain.w', 15, 'sweep', 'e'), wp('piazza.fountain.n', 15, 'sweep', 's'),
        wp('town_hall.front', 15, 'sweep', 'e'), wp('belvedere.e', 15, 'sweep', 's'),
        wp('belvedere.w', 15, 'sweep', 's'), wp('piazza.kiosk', 10, 'sweep', 's'),
    ])
    add('Carabiniere Fontana', 'harbour_guard', [
        wp('piazza.fountain', 12, 'guard', 's'), wp('belvedere.w', 10, 'look', 's'),
        wp('town_hall.front', 12, 'guard', 'w'), wp('piazza.fountain.n', 8, 'guard', 'n'),
    ])
    add('Carabiniere Leone', 'harbour_guard', [
        wp('via_roma.0', 8, 'guard', 'e'), wp('via_roma.1'), wp('via_roma.2', 8, 'look', 's'),
        wp('piazza.fountain.w', 6, 'guard', 'e'), wp('via_roma.5', 8, 'guard', 'w'), wp('via_roma.6'),
        wp('via_roma.7', 8, 'look', 'w'),
    ], mode='pingpong')
    idle('Clerk Ottavio', 'civilian', 'town_hall.hall', 'type', 'n')
    add('Councillor Ferri', 'civilian', [wp('town_hall.loggia', 20, 'phone', 'w'), wp('town_hall.front', 10, 'look', 'w'),
                                         wp('town_hall.hall', 20, 'talk', 'n')])
    add('Tourist Hana', 'tourist', [wp('belvedere.e', 20, 'phone', 's'), wp('piazza.fountain.e', 10, 'look', 'w'),
                                    wp('belvedere.bench', 25, 'sit', 's', seat=True)])
    add('Tourist Felix', 'tourist', [wp('piazza.fountain', 15, 'phone', 'n'), wp('stairs.h_c.top', 6, 'look', 's'),
                                     wp('stairs.h_c.bottom'), wp('quay.mid', 15, 'look', 's'),
                                     wp('stairs.h_c.bottom'), wp('stairs.h_c.top')])
    idle('Gelataio Remo', 'shopkeeper', 'gelateria.inside', 'work', 'n', off=(0, 0, 2))
    idle('Pharmacist Olga', 'shopkeeper', 'pharmacy.inside', 'work', 's', off=(0, 0, -2))

    # ======================= UPPER TOWN ============================================
    idle('Baker Tilde', 'shopkeeper', 'bakery.inside', 'work', 's', off=(0, 0, -2), say='Cornetti! Still warm!')
    idle('Tailor Arturo', 'shopkeeper', 'tailor.inside', 'work', 's', off=(0, 0, -2))
    add('Signora Costa', 'civilian', [wp('via_alta.1', 10, 'look', 's'), wp('bakery.door', 12, 'talk', 'n'),
                                      wp('via_alta.3', 8, 'phone'), wp('via_alta.2')], mode='pingpong')
    add('Signor Galli', 'civilian', [wp('via_alta.5', 10, 'smoke', 's'), wp('via_alta.4'), wp('stairs.p_c.top'),
                                     wp('stairs.p_c.bottom'), wp('piazza.fountain.n', 15, 'look', 's'),
                                     wp('stairs.p_c.bottom'), wp('stairs.p_c.top')])
    add('Housekeeper Bice', 'cleaner', [wp('via_alta.6', 20, 'sweep', 's'), wp('via_alta.7', 20, 'sweep', 's')],
        mode='pingpong')
    add('Dr. Amato', 'civilian', [wp('doctor.door', 15, 'phone', 's'), wp('via_alta.4', 8, 'look', 's'),
                                  wp('via_alta.3')], mode='pingpong')
    add('Postman Ezio', 'civilian', [wp('via_alta.0', 4, 'work', 'n'), wp('via_alta.2', 4, 'work', 'n'),
                                     wp('via_alta.4', 4, 'work', 'n'), wp('via_alta.6', 4, 'work', 'n')], mode='pingpong')

    # ======================= HILLTOP ================================================
    add('Padre Anselmo', 'priest', [wp('chapel.altar', 40, 'pray', 'n'), wp('chapel.aisle'),
                                    wp('chapel.door', 20, 'look', 's', say='The door is always open, my child.'),
                                    wp('cemetery.gate', 15, 'pray', 'e'), wp('chapel.door'), wp('chapel.aisle')])
    idle('Widow Carmela', 'civilian', 'chapel.pew', 'pray', 'n', off=(0, 0, 1))
    add('Gravedigger Sesto', 'gardener', [wp('cemetery.grave', 30, 'work', 'n'), wp('cemetery.far', 25, 'work', 'n'),
                                          wp('cemetery.gate', 15, 'smoke', 'w')])
    add('Gardener Vito', 'gardener', [wp('grove.w', 25, 'crouch', 'n'), wp('grove.mid', 25, 'work', 'e'),
                                      wp('grove.e', 25, 'crouch', 's'), wp('viewpoint', 15, 'smoke', 's', off=(4, 0, -2))])
    add('Tourist Ingrid', 'tourist', [wp('viewpoint.telescope', 25, 'look', 's'), wp('promenade.3', 10, 'phone'),
                                      wp('promenade.5', 12, 'look', 's')], mode='pingpong')
    add('Tourist Raul', 'tourist', [wp('promenade.4', 12, 'look', 's'), wp('viewpoint', 30, 'sit', 's', seat=True, off=(-2, 0, 0)),
                                    wp('promenade.2', 12, 'phone')])

    # ======================= TENUTA BELMONTE ============================================
    idle('Gate Guard Rocco', 'estate_guard', 'estate.gate.guard_l', 'guard', 's', enforcer=True,
         say='Private estate. Move along.')
    idle('Gate Guard Santo', 'estate_guard', 'estate.gate.guard_r', 'guard', 's')
    idle('Service Gate Guard Milo', 'estate_guard', 'estate.service.in', 'guard', 'e')
    add('Guard Tullio', 'estate_guard', [wp('garden.w', 10, 'guard', 's'), wp('drive.mid', 8, 'look', 's'),
                                         wp('garden.e', 10, 'guard', 's'), wp('estate.gate.in', 8, 'guard', 'n')])
    add('Guard Ivo', 'estate_guard', [wp('pool.south', 12, 'guard', 'n'), wp('pool.edge', 8, 'look', 'n'),
                                      wp('pool.path', 10, 'guard', 'w'), wp('kitchen.door', 8, 'smoke', 'w')],
        mode='pingpong')
    add('Guard Nello', 'estate_guard', [wp('court.w', 10, 'guard', 'e'), wp('court.fountain', 8, 'look', 'n'),
                                        wp('court.e', 10, 'guard', 'w'), wp('court.arches', 10, 'guard', 's')])
    add('Guard Remo', 'estate_guard', [wp('villa.hall', 15, 'guard', 's'), wp('villa.salon', 10, 'look', 'e'),
                                       wp('villa.hall'), wp('villa.dining', 10, 'look', 'w')])
    idle('Security Chief Orso', 'estate_guard', 'security.desk', 'type', 'e', enforcer=True, off=(-1, 0, 0))
    idle('Guard Lino', 'estate_guard', 'villa.gallery', 'guard', 's', off=(3, 0, 2))
    add('Cook Marisa', 'cook', [wp('kitchen.stove', 25, 'work', 'w'), wp('kitchen.prep', 20, 'work', 'n')],
        mode='pingpong')
    add('Cook Tobia', 'cook', [wp('kitchen.prep', 25, 'work', 'n', off=(1, 0, 1)),
                               wp('kitchen.door', 15, 'smoke', 'w', off=(0, 0, 1))], mode='pingpong')
    add('Waiter Elia', 'waiter', [wp('kitchen.prep', 10, 'work', 'n', off=(-1, 0, 1)), wp('kitchen.court_door'),
                                  wp('court.arches'), wp('villa.hall'), wp('villa.dining.serve', 15, 'work', 'n'),
                                  wp('villa.hall'), wp('court.arches'), wp('kitchen.court_door')])
    add('Waiter Bruno', 'waiter', [wp('pool.bar', 25, 'work', 's'), wp('pool.bar.front'),
                                   wp('pool.lounger0', 8, 'talk', 'w', off=(1, 0, 0)), wp('pool.bar.front')])
    add('Sommelier Ottone', 'waiter', [wp('cellar.mid', 25, 'look', 'n'), wp('cellar.tasting', 20, 'work', 'n', off=(-2, 0, 0)),
                                       wp('cellar.east', 20, 'work', 'e', off=(-3, 0, 0))])
    add('Maid Teresa', 'cleaner', [wp('villa.bedroom', 25, 'sweep', 'w'), wp('villa.gallery', 20, 'sweep', 's'),
                                   wp('villa.office', 20, 'sweep', 'n')])
    add('Maid Agnese', 'cleaner', [wp('villa.salon', 25, 'sweep', 'e'), wp('villa.hall', 20, 'sweep', 's'),
                                   wp('villa.dining', 25, 'sweep', 'w')])
    add('Gardener Piero', 'gardener', [wp('garden.bench', 20, 'crouch', 'n', off=(3, 0, 2)),
                                       wp('garden.e', 25, 'work', 'n', off=(2, 0, 1)), wp('drive.mid', 10, 'look', 'n')])
    add('Vintner Gaspare', 'gardener', [wp('vineyard.w', 30, 'crouch', 'n'), wp('vineyard.w2', 30, 'work', 'n')],
        mode='pingpong')
    idle('Guest Contessa Valli', 'civilian', 'pool.lounger0', 'sit', 'w', seat=True)
    idle('Guest Mr. Whitlock', 'civilian', 'villa.salon.sofa', 'drink', 'n', off=(0, 0, -1))
    add('Guest Avvocato Serra', 'civilian', [wp('court.e', 20, 'phone', 'w'), wp('garden.e', 20, 'look', 's'),
                                             wp('villa.salon', 20, 'look', 'n')])

    # ======================= CANNERY ======================================================
    idle('Gate Security Falco', 'security', 'cannery.gate.guard', 'guard', 'w', enforcer=True,
         say='Deliveries only. You a delivery?')
    add('Security Marek', 'security', [wp('cannery.yard.s', 10, 'guard', 's'), wp('cannery.gate.in', 8, 'look', 'w'),
                                       wp('cannery.yard.n', 10, 'guard', 'n')], mode='pingpong')
    add('Security Dolf', 'security', [wp('cannery.dock', 12, 'smoke', 's'), wp('cannery.dockdoor', 8, 'guard', 's'),
                                      wp('cannery.floor', 10, 'look', 'n')], mode='pingpong')
    idle('Security Brandt', 'security', 'cannery.liftdoor', 'guard', 'w', enforcer=True)
    for i in range(6):
        idle(['Worker Alba', 'Worker Rino', 'Worker Dina', 'Worker Pasquale', 'Worker Zita', 'Worker Michele'][i],
             'worker', f'cannery.line{i}', 'work', 'e')
    add('Foreman Guido', 'worker', [wp('mezz.walk', 20, 'look', 's'), wp('mezz.stairs.top'), wp('mezz.stairs.bottom'),
                                    wp('cannery.boilers', 15, 'work', 'e'), wp('cannery.floor', 12, 'talk', 'n'),
                                    wp('mezz.stairs.bottom'), wp('mezz.stairs.top'), wp('mezz.desk', 20, 'eat', 'n')])
    add('Mechanic Tazio', 'worker', [wp('cannery.fuse', 20, 'work', 'w'), wp('cannery.door.in', 10, 'smoke', 'w')],
        mode='pingpong')

    # ======================= LAB ============================================================
    idle('Security Kessler', 'security', 'lab.lobby.desk', 'guard', 'e')
    idle('Security Novak', 'security', 'lab.security.desk', 'type', 'e', off=(-1, 0, 0), enforcer=True)
    add('Security Voss', 'security', [wp('lab.c1', 10, 'guard', 's', off=(0, 0, 12)), wp('lab.c1', 8, 'look', 'n'),
                                      wp('lab.airlock.s', 12, 'guard', 's')], mode='pingpong')
    add('Technician Idris', 'worker', [wp('lab.generator.fuse', 25, 'work', 'n'), wp('lab.generator', 20, 'look', 'e')],
        mode='pingpong')
    idle('Canteen Cook Wanda', 'cook', 'lab.canteen.coffee', 'work', 'n')
    idle('Dr. Lindqvist', 'scientist', 'lab.canteen.seat0', 'eat', 'e', seat=True)
    idle('Hazmat Tech Ko', 'hazmat', 'lab.lockers.bench', 'sit', 'n', off=(0, 0, 0))
    add('Virus Guard Sturm', 'lab_guard', [wp('lab.airlock.n', 10, 'guard', 'w'), wp('lab.c2.3', 8, 'look', 'w'),
                                           wp('lab.c2.0', 10, 'guard', 'e')], mode='pingpong', enforcer=True)
    add('Virus Guard Halla', 'lab_guard', [wp('lab.hall.s', 12, 'guard', 'n'), wp('lab.hall.w', 10, 'look', 'e'),
                                           wp('lab.hall.nw', 10, 'guard', 's'), wp('lab.hall.ne', 10, 'guard', 's'),
                                           wp('lab.hall.e', 10, 'look', 'w')])
    idle('Virus Guard Rask', 'lab_guard', 'lab.core.door', 'guard', 's', off=(2, 0, 0))
    idle('Virus Guard Meyer', 'lab_guard', 'lab.backstair.bottom', 'guard', 'w', off=(-6, 0, 0))
    for i in range(4):
        idle(['Dr. Okafor', 'Dr. Brandao', 'Dr. Sato', 'Dr. Weiss'][i], 'scientist', f'lab.console{i}', 'type', 'n')
    add('Hazmat Tech Ilya', 'hazmat', [wp('lab.tank0', 20, 'work', 'n'), wp('lab.tank2', 20, 'look', 'n'),
                                       wp('lab.tank4', 20, 'work', 'n')], mode='pingpong')
    add('Hazmat Tech Mona', 'hazmat', [wp('lab.bench.w', 25, 'work', 'w'), wp('lab.hall.w'), wp('lab.wetlab'),
                                       wp('lab.wetlab.bench', 25, 'work', 'w', off=(0, 0, 3)), wp('lab.wetlab'),
                                       wp('lab.hall.w')])
    add('Hazmat Tech Jun', 'hazmat', [wp('lab.bench.e', 25, 'work', 'e'), wp('lab.hall.e'), wp('lab.server'),
                                      wp('lab.server.rack', 20, 'type', 'e', off=(-1, 0, 2)), wp('lab.server'),
                                      wp('lab.hall.e')])
    add('Hazmat Tech Petra', 'hazmat', [wp('lab.greenhouse.w', 25, 'crouch', 'n', off=(8, 0, 0)), wp('lab.greenhouse'),
                                        wp('lab.hall.nw', 10, 'look', 's')], mode='pingpong')
    idle('Hazmat Tech Arno', 'hazmat', 'lab.cold', 'work', 'n')
    idle('Dock Guard Hess', 'security', 'cave.dock', 'smoke', 'e')

    # ======================= PROPS ==========================================================
    props = [dict(item=f'recrafted:{p[0]}', pos=[int(p[1]) + .5, int(p[2]), int(p[3]) + .5]) for p in ctx['props']]
    extra = [
        ('coin', 'spawn', (1, 0, 0)), ('coin', 'piazza.fountain', (1, 0, 1)), ('coin', 'quay.walk3', (0, 0, 2)),
        ('brick', 'stairs.h_w.bottom', (2, 0, 1)), ('brick', 'via_alta.2', (1, 0, 2)),
        ('bottle', 'cafe.table2', (0, 0, 1)), ('bottle', 'trattoria.table2', (1, 0, 1)),
        ('newspaper', 'piazza.kiosk', (1, 0, 0)), ('wrench', 'boat.trawler', (0, 0, 2)),
        ('fishing_gaff', 'quay.walk5', (1, 0, 3)), ('oar', 'pier.mid', (1, 0, 3)),
        ('screwdriver', 'lighthouse.inside', (0, 0, 0)), ('outfit_fisherman', 'lighthouse.inside', (-1, 0, 1)),
        ('hammer', 'chandlery.inside', (1, 0, 1)), ('fiber_wire', 'tailor.inside', (1, 0, 0)),
        ('scissors', 'tailor.inside', (-1, 0, 0)), ('outfit_waiter', 'cafe.inside', (0, 0, 3)),
        ('rolling_pin', 'bakery.inside', (1, 0, 0)), ('emetic_poison', 'pharmacy.inside', (1, 0, 0)),
        ('sedative', 'doctor.inside', (0, 0, 1)), ('syringe', 'doctor.inside', (1, 0, 2)),
        ('outfit_gardener', 'grove.mid', (2, 0, 2)), ('garden_shears', 'grove.w', (1, 0, 1)),
        ('outfit_cook', 'trattoria.inside', (2, 0, 0)), ('kitchen_knife', 'trattoria.inside', (-2, 0, -2)),
        ('cleaver', 'kitchen.stove', (2, 0, -2)), ('lockpick', 'manhole', (1, 0, -1)),
        ('pocket_radio', 'town_hall.hall', (2, 0, 2)), ('pocket_radio', 'cannery.floor', (3, 0, 0)),
        ('outfit_cleaner', 'town_hall.loggia', (0, 0, -4)), ('broom', 'belvedere.e', (4, 0, 1)),
        ('lethal_poison', 'cellar.east', (-1, 0, 3)), ('outfit_priest', 'chapel.altar', (-4, 0, -3)),
        ('fire_axe', 'cannery.yard.e', (0, 0, 2)), ('candlestick', 'villa.dining', (0, 0, -6)),
    ]
    for (item, a, off) in extra:
        if a not in A:
            c.warn.append(f'prop anchor missing: {a}')
            continue
        x, y, z = c.P(a, off)
        x, y, z = c._free('prop ' + item, int(x), int(y), int(z))
        props.append(dict(item=f'recrafted:{item}', pos=[x + .5, y, z + .5]))

    sx, sy, sz = A['spawn']
    mission = dict(
        id='corvara',
        title='Salt & Ash',
        location='Corvara — Tyrrhenian Sea',
        dimension='recrafted:corvara',
        briefing=[
            'Corvara. Four hundred residents, one ferry a day, and the best sunsets in the Tyrrhenian.',
            'Beneath the old cannery, Halcyon Agrigenics is finishing CINDER — a blight engineered to wipe a harvest from the map and sell the cure.',
            'Three people keep it alive. Marco Belmonte pays for it from his hilltop estate. Dr. Ilse Varga builds it in the salt mine under the town. Capitano Renzo Sordi makes sure the harbour never sees it leave.',
            'Remove all three. Destroy the pathogen. Take the evening ferry home.',
        ],
        spawn=dict(pos=[int(sx) + .5, int(sy), int(sz) + .5], yaw=180),
        targets=[
            dict(id='belmonte', name='Marco Belmonte', desc='Vintner, financier, owner of the Tenuta. Never without two bodyguards.'),
            dict(id='varga', name='Dr. Ilse Varga', desc='Lead virologist. Lives in the lab; surfaces only for bad coffee.'),
            dict(id='sordi', name='Capitano Renzo Sordi', desc='Harbour master. Takes lunch at the trattoria, wine included.'),
        ],
        objectives=[
            dict(id='kill_belmonte', type='eliminate', target='belmonte', text='Eliminate Marco Belmonte'),
            dict(id='kill_varga', type='eliminate', target='varga', text='Eliminate Dr. Ilse Varga'),
            dict(id='kill_sordi', type='eliminate', target='sordi', text='Eliminate Capitano Renzo Sordi'),
            dict(id='destroy_core', type='destroy_core', text='Destroy the CINDER pathogen'),
            dict(id='exit', type='exit', text='Leave the island'),
        ],
        intel=[
            'The café and the estate dress their waiters alike. Nobody at the gate checks faces.',
            'The Capitano drinks at the middle table of the trattoria. The glass sits there between visits.',
            'A sewer mouth opens under the quay. The cistern beyond it connects to the old salt workings.',
            'Belmonte tastes from the cellar every afternoon. The big vats at the far end hide a door the miners left.',
            'The clean zone needs a suit. Spare ones hang in the locker room behind the security corridor.',
            'The purge console in the core hall sterilises the containment chamber. It was never meant to be run with the sample inside.',
            'Fuse boxes bring someone to fix them. That someone leaves their post.',
        ],
        zones=ctx['zones'],
        props=props,
        npcs=c.npcs,
    )
    if c.warn:
        print(f'  mission: {len(c.warn)} waypoint warnings')
        for wmsg in c.warn[:60]:
            print('    ', wmsg)
    print(f'  mission: {getattr(c, "moved", 0)} waypoints snapped to free cells')
    import walkcheck
    added = walkcheck.split_long_legs(ctx['w'], c.npcs)
    print(f'  mission: {added} pass-through stops inserted on long legs')
    problems = walkcheck.check_routes(ctx['w'], c.npcs)
    print(f'  mission: {len(problems)} unreachable route legs')
    for pr in problems:
        print('    ', pr)
    print(f'  mission: {len(c.npcs)} npcs, {len(props)} props, {len(ctx["zones"])} zones')
    return mission
