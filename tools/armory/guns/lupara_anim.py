"""Lupara timing (sounds come from the display: TACZ's double-barrel reload and inspect recordings)."""
from breakaction_anim import BreakSpec, all_animations

SPEC = BreakSpec(open_deg=52.0, lever_deg=-20.0, kick=1.05, extra={'inspect_near': [0.6, 1.0, -1.6]})


def animations():
    return all_animations(SPEC)
