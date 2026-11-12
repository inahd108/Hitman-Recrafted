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


def exits(ctx):
    """Exit points the player walks into: the train, the ferry deck."""
    w, A = ctx['w'], ctx['anchors']
    for key in ('exit.train', 'exit.ferry'):
        if key in A:
            x, y, z = A[key]
            w.set(x, y - 1, z, 'recrafted:exit_point')


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
        'props': [],
        'npcs': npcs,
    }
