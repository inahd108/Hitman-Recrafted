"""Mission data for Oil & Water: briefing, targets, objectives, exits. The cast comes in a later step."""
from ams_layout import STREET, WATER, INNER, MID_N, ZILVERSTEEG

BRIEFING = [
    "Amsterdam. Nine hundred thousand people, almost as many bicycles, and a hundred kilometres of canals that have "
    "carried other people's money for four centuries.",
    "The money meant for CINDER didn't vanish with the island. It is being washed through paint.",
    "A forger known only as De Meester turns out Golden Age masters that were never painted. Margriet Ostendorp sells "
    "them under the hammer at the Gulden Hamer to buyers who don't exist. Sem Kooistra takes the proceeds out through "
    "the canals in uncut stones.",
    "Tonight is the autumn sale. All three will be within half a kilometre of each other, and none of them will stand still.",
    "Remove all three. If you can, bring us the Gulden Hamer's ledger. Be gone before the bells strike nine.",
]
INTEL = [
    "Catering at the Gulden Hamer is brought in. Nobody checks the faces of the waiters, but everybody checks their bags.",
    "The guest list is for bidders. A bidder's paddle opens every door the public may use.",
    "There is a metal detector inside the Gulden Hamer's front doors. Guns and anything sharp set it off, "
    "unless you wear a guard's uniform. Staff and caterers come in through the garden door.",
    "De Meester never signs his work. His apprentices say he is the only one who paints left-handed.",
    "Watch the four painters at work long enough and he gives himself away. Or read the café's wage book: "
    "In de Gouden Ton pays his apprentices, and one name draws no wage.",
    "Twice an evening De Meester goes down to the quay for air, right under the hoist with the lead white.",
    "Ostendorp takes her champagne in the private viewing room. Kooistra keeps a bottle of jenever in his cabin.",
    "The saleroom chandelier hangs on a rope from the press balcony. Ostendorp stands under it for every lot.",
    "The Gulden Hamer's ledger is kept in the strongbox in the basement vault.",
    "Ways out: the train, the IJ ferry, a water taxi on the Gildegracht, a courier's cargo bike at the top of "
    "Zilversteeg, or the Zwaluw herself, if you are aboard when the work is done.",
    "A bidder's paddle from the reception desk gets you into the saleroom without questions.",
    "There is turpentine in the forger's studio. Stoves don't like it.",
    "The bridge keeper and the lock keeper lock their panels. Their keys are in the booth and the lock house.",
    "Kooistra can't swim. His salon boat, the Zwaluw, takes him from his houseboat on the Gildegracht through the "
    "drawbridge, up to the smuggler's dock, out on the IJ and home again through the lock.",
    "The bridge keeper raises the Gildegracht drawbridge for any boat that sounds its horn twice. Boats wait for it "
    "under the goods crane on the south quay. The lever in her booth holds the bridge down.",
    "The lock keeper's sluice wheel empties the lock chamber all at once. Nobody should be standing at the rail when it does.",
]
TARGETS = [
    dict(id='ostendorp', name='Margriet Ostendorp', desc='Auctioneer. Runs tonight\'s sale at the Gulden Hamer, never alone.'),
    dict(id='meester', name='De Meester', desc='The forger. Nobody knows his face; he paints among his apprentices.'),
    dict(id='kooistra', name='Sem Kooistra', desc='Smuggler. Rides his salon boat round the canals and can\'t swim.'),
]
OBJECTIVES = [
    dict(id='kill_ostendorp', type='eliminate', target='ostendorp', text='Eliminate Margriet Ostendorp'),
    dict(id='kill_meester', type='eliminate', target='meester', text='Identify and eliminate De Meester'),
    dict(id='kill_kooistra', type='eliminate', target='kooistra', text='Eliminate Sem Kooistra'),
    dict(id='ledger', type='collect', target='ledger', text='Recover the Gulden Hamer ledger', optional=True),
    dict(id='exit', type='exit', text='Leave Amsterdam'),
]


# 19:30 start, one clock minute per 10 s; the sale repeats every hour (minutes are relative to the hour's cycle)
CLOCK = dict(start=19 * 60 + 30, secondsPerMinute=10, period=60, events=[
    dict(at=13, text='The bell rings in the Gulden Hamer: bidders to the saleroom.', sub='The sale starts at a quarter to.'),
    dict(at=15, text='The sale begins. Ostendorp takes the podium.', sub='She stays at the lectern until a quarter past.'),
    dict(at=43, text='Last lots of the session.'),
    dict(at=45, text='The sale breaks for the interval.', sub='Ostendorp goes down to the vault, then upstairs for champagne.'),
])


def exits(ctx):
    """Exit points: the train, the ferry deck, a courier's cargo bike in Zilversteeg and a water taxi on the
    Gildegracht. (The Zwaluw is an exit too: right-click her while aboard.)"""
    w, A = ctx['w'], ctx['anchors']
    for key in ('exit.train', 'exit.ferry'):
        if key in A:
            x, y, z = A[key]
            w.set(x, y - 1, z, 'recrafted:exit_point')
    # the cargo bike at the north end of Zilversteeg
    p = _floor(w, ZILVERSTEEG[0] + 1, STREET + 1, MID_N[0] + 2, 3)
    if p:
        x, y, z = p
        w.set(x, y, z, 'recrafted:bicycle[facing=north,paint=green]')
        w.set(x, y, z - 1, 'barrel[facing=up]')
        w.set(x + 1, y, z, 'recrafted:exit_point')
        A['exit.bike'] = (x + 1, y, z)
    # a water taxi tied up below the Gildegracht's north quay, with a gangplank
    tx0, tz0 = 226, INNER[0]
    w.fill(tx0, WATER - 1, tz0, tx0 + 6, WATER, tz0 + 2, 'yellow_terracotta')
    w.fill(tx0 + 1, WATER, tz0 + 1, tx0 + 5, WATER, tz0 + 1, 'air')
    w.fill(tx0 + 1, WATER, tz0 + 1, tx0 + 5, WATER, tz0 + 1, 'spruce_slab[type=top]')
    w.fill(tx0, WATER + 1, tz0, tx0 + 6, WATER + 1, tz0, 'white_concrete')
    w.fill(tx0, WATER + 1, tz0 + 2, tx0 + 6, WATER + 1, tz0 + 2, 'white_concrete')
    w.set(tx0 + 6, WATER + 1, tz0 + 1, 'white_concrete')
    w.set(tx0 + 4, WATER + 1, tz0 + 1, 'recrafted:exit_point')
    w.set(tx0 + 2, WATER + 1, tz0 + 1, 'lantern')
    w.set(tx0 + 1, WATER + 1, tz0, 'air')
    w.set(tx0 + 1, STREET, tz0 - 1, 'spruce_slab[type=top]')
    A['exit.taxi'] = (tx0 + 4, WATER + 1, tz0 + 1)


def _floor(w, x, y, z, r=3):
    """The nearest spot to (x, y, z) where something can lie on the floor: an air or carpet cell over a solid one."""
    def ok(cx, cy, cz):
        here = w.name(w.get(cx, cy, cz)).split(':')[-1].split('[')[0]
        below = w.name(w.get(cx, cy - 1, cz)).split(':')[-1].split('[')[0]
        return (here == 'air' or here.endswith('carpet')) and below not in ('air', 'water') and not below.endswith(('fence', 'wall'))
    best = None
    for dy in (0, 1, -1):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if ok(x + dx, y + dy, z + dz):
                    d = dx * dx + dz * dz + abs(dy) * 4
                    if best is None or d < best[0]:
                        best = (d, (x + dx, y + dy, z + dz))
    return best[1] if best else None


# prop -> anchors (with offsets) it lies at
PROPS = [
    ('palette_knife', [('studio.easel1', (1, 0, 0))]), ('turpentine', [('studio.stove', (-1, 0, 0))]),
    ('lead_white', [('studio.window', (-1, 0, 1))]),
    ('gavel', [('hamer.podium', (2, 0, 0)), ('hamer.office.desk', (1, 0, 1))]),
    ('delft_vase', [('hamer.gallery', (0, 0, 1)), ('hamer.viewing.easel', (-1, 0, -1))]),
    ('bidder_paddle', [('hamer.reception.desk', (0, 0, 1))]), ('press_camera', [('hamer.balcony', (2, 0, 0))]),
    ('jenever', [('cafe.bar', (0, 0, 1)), ('cafe.table2', (1, 0, 0))]),
    ('boat_hook', [('kooistra.landing', (-2, 0, 0))]),
    ('bridge_key', [('drawbridge.booth', (1, 0, 0)), ('lock.keeper', (0, 0, 1))]),
    ('umbrella', [('station.platform', (2, 0, 1)), ('cafe.door', (1, 0, -1)), ('square.centre', (-4, 0, 3))]),
    ('tulip_bulbs', [('square.centre', (3, 0, -3)), ('square.centre', (-3, 0, -4))]),
    ('cheese_wheel', [('square.centre', (5, 0, 2)), ('ferry.square', (1, 0, 1))]),
]


def props(ctx):
    A, w = ctx['anchors'], ctx['w']
    out = []
    if 'hamer.vault.ledger' in A:                     # on the strongbox in the vault
        x, y, z = A['hamer.vault.ledger']
        out.append({'item': 'recrafted:ledger', 'pos': [x + .5, y + 1, z - 1 + .5]})
    missing = []
    for item, spots in PROPS:
        for a, (ox, oy, oz) in spots:
            if a not in A:
                missing.append(a)
                continue
            x, y, z = A[a]
            p = _floor(w, int(x) + ox, int(y) + oy, int(z) + oz)
            if p:
                out.append({'item': f'recrafted:{item}', 'pos': [p[0] + .5, p[1], p[2] + .5]})
    # clogs and boat hooks on the houseboat decks, bike locks by the racks on the quays
    decks = [b['deck'] for b in ctx.get('boats', []) if b.get('name') is None]
    for i, (x, y, z) in enumerate(decks[:4]):
        out.append({'item': 'recrafted:' + ('clog' if i % 2 == 0 else 'boat_hook'), 'pos': [x + .5, y, z + .5]})
    for x, z in ((250, 185), (120, 89), (330, 217)):
        p = _floor(w, x, STREET + 1, z, 4)
        if p:
            out.append({'item': 'recrafted:chain_lock', 'pos': [p[0] + .5, p[1], p[2] + .5]})
    if missing:
        print('  props: missing anchors', sorted(set(missing)))
    print(f'  props: {len(out)} placed')
    return out


def build(ctx):
    exits(ctx)
    import ams_cast
    import ams_boats
    npcs, zones = ams_cast.build(ctx)
    boats, gate_defs = ams_boats.mission_data(ctx)
    npcs += ams_boats.crews(ctx, boats)
    sp = ctx['anchors'].get('station.platform', (20, STREET + 2, 50))
    return {
        'id': 'amsterdam',
        'title': 'Oil & Water',
        'location': 'Amsterdam — Netherlands',
        'dimension': 'recrafted:amsterdam',
        'briefing': BRIEFING,
        'spawn': {'pos': [sp[0] + .5, sp[1], sp[2] + .5], 'yaw': -90},
        'targets': TARGETS,
        'objectives': OBJECTIVES,
        'intel': INTEL,
        'zones': zones,
        'props': props(ctx),
        'npcs': npcs,
        'clock': CLOCK,
        'boats': boats,
        'gates': gate_defs,
    }
