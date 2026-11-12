"""Bedrock animation helpers (the format TACZ plays).

Conventions, as in TACZ's own packs: positions are model units relative to the rest pose,
+z moves towards the shooter; rotations are degrees added to the rest rotation, and a
negative x rotation lifts the muzzle.
"""

HANDS = {'lefthand': {'scale': [1, 1.5, 1]}, 'righthand': {'scale': [1, 1.5, 1]}}
CONSTRAINT = {'constraint': {'rotation': [0.2, 0.2, 0.2], 'position': [0.2, 0.2, 0.35]}}


def track(keys, smooth=True):
    """keys: {time: [x, y, z]} -> Bedrock keyframes, Catmull-Rom smoothed unless smooth=False."""
    out = {}
    for t in sorted(keys):
        v = [round(float(a), 4) for a in keys[t]]
        k = f'{float(t):.4f}'.rstrip('0').rstrip('.') if t else '0.0'
        if '.' not in k:
            k += '.0'
        out[k] = {'post': v, 'lerp_mode': 'catmullrom'} if smooth else v
    return out


def step_track(keys):
    """Instant changes (e.g. hiding a round): the value holds until the next key, then jumps.

    TACZ interpolates between one key's 'post' and the next key's 'pre', so each key's 'pre' repeats the
    previous value.
    """
    out = {}
    prev = None
    for t in sorted(keys):
        k = f'{float(t):.4f}'.rstrip('0').rstrip('.') if t else '0.0'
        if '.' not in k:
            k += '.0'
        v = keys[t]
        if isinstance(v, (int, float)):            # TACZ needs three-axis values in keyed channels
            v = [v, v, v]
        out[k] = {'pre': prev if prev is not None else v, 'post': v}
        prev = v
    return out


class Anim:
    def __init__(self, length, loop=False):
        self.length = length
        self.loop = loop
        self.bones = {}
        self.sounds = {}

    def rot(self, bone, keys, smooth=True):
        self.bones.setdefault(bone, {})['rotation'] = track(keys, smooth)
        return self

    def pos(self, bone, keys, smooth=True):
        self.bones.setdefault(bone, {})['position'] = track(keys, smooth)
        return self

    def static(self, bone, **channels):
        self.bones.setdefault(bone, {}).update(channels)
        return self

    def scale(self, bone, keys):
        self.bones.setdefault(bone, {})['scale'] = step_track(keys)
        return self

    def sound(self, t, effect):
        k = f'{float(t):.4f}'.rstrip('0').rstrip('.')
        self.sounds[k if '.' in k else k + '.0'] = {'effect': effect}
        return self

    def with_hands(self):
        for b, ch in HANDS.items():
            self.bones.setdefault(b, {}).update(ch)
        return self

    def to_json(self):
        d = {'animation_length': round(self.length, 4)}
        if self.loop:
            d['loop'] = True
        d['bones'] = self.bones
        if self.sounds:
            d['sound_effects'] = self.sounds
        return d


def sample(anim_json, bone, channel, t):
    """Evaluate a channel at time t (linear between keys) — used by the preview renderer."""
    ch = anim_json['bones'].get(bone, {}).get(channel)
    if ch is None:
        return None
    if isinstance(ch, list):
        return ch
    keys = sorted((float(k), (v['post'] if isinstance(v, dict) else v)) for k, v in ch.items())
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / max(1e-9, t1 - t0)
            if isinstance(v0, (int, float)):
                return v0 + (v1 - v0) * f
            return [a + (b - a) * f for a, b in zip(v0, v1)]
    return keys[-1][1]


def pose_at(anim_json, t, bones):
    pose = {}
    for b in bones:
        r = sample(anim_json, b, 'rotation', t)
        p = sample(anim_json, b, 'position', t)
        sc = anim_json['bones'].get(b, {}).get('scale')
        if isinstance(sc, dict):                       # step track: the last key at or before t holds
            keys = sorted((float(k), v['post'] if isinstance(v, dict) else v) for k, v in sc.items())
            cur = keys[0][1]
            for kt, kv in keys:
                if kt <= t + 1e-9:
                    cur = kv
            sc = cur[0] if isinstance(cur, list) and len(set(cur)) == 1 else cur
        if r is not None or p is not None or sc is not None:
            pose[b] = {}
            if r is not None:
                pose[b]['rotation'] = r
            if p is not None:
                pose[b]['position'] = p
            if isinstance(sc, (list, int, float)):
                pose[b]['scale'] = sc
    return pose
