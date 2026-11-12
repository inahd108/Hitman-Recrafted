"""Mission data for Oil & Water: briefing, targets, objectives, exits. The cast comes in a later step."""
from ams_layout import STREET

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
    "De Meester never signs his work. His apprentices say he is the only one who paints left-handed.",
    "Watch the four painters at work long enough and he gives himself away. Or read the café's wage book: "
    "In de Gouden Ton pays his apprentices, and one name draws no wage.",
    "Twice an evening De Meester goes down to the quay for air, right under the hoist with the lead white.",
    "Ostendorp takes her champagne in the private viewing room. Kooistra keeps a bottle of jenever in his cabin.",
    "The saleroom chandelier hangs on a rope from the press balcony. Ostendorp stands under it for every lot.",
    "The Gulden Hamer's ledger is kept in the strongbox in the basement vault.",
    "Kooistra can't swim, so he never leaves the boat between stops.",
    "The bridge keeper raises the Gildegracht drawbridge for any boat that sounds its horn twice.",
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
    """Exit points the player walks into: the train, the ferry deck."""
    w, A = ctx['w'], ctx['anchors']
    for key in ('exit.train', 'exit.ferry'):
        if key in A:
            x, y, z = A[key]
            w.set(x, y - 1, z, 'recrafted:exit_point')


def props(ctx):
    A = ctx['anchors']
    out = []
    if 'hamer.vault.ledger' in A:                     # on the strongbox in the vault
        x, y, z = A['hamer.vault.ledger']
        out.append({'item': 'recrafted:ledger', 'pos': [x + .5, y + 1, z - 1 + .5]})
    return out


def build(ctx):
    exits(ctx)
    import ams_cast
    npcs, zones = ams_cast.build(ctx)
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
    }
