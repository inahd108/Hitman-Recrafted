"""Parts every handgun in the arsenal shares: the TACZ bone rig, hands and camera anchors."""
from geomodel import Model

# Where the hand closes around the grip. All pistols keep their grip here so the hold is right.
GRIP_PIV = [0, 2.9, 2.45]
GRIP_ROT = [16, 0, 0]


def hands(m):
    """Arm anchors where TACZ draws the player's arms (the usual service-pistol hold)."""
    m.part('R', 'gun_and_righthand', [-0.975, 2.125, 1])
    m.part('righthand', 'R', [-0.975, 2.125, 1], [93.01689, 5.80774, -177.55323])
    rh = m.part('righthand_pos', 'righthand', [-6.975, -8.875, 1])
    rh.bar(-2.975, 0.025, -8.875, 3.125, -1, 3, 'arm', data={'k': 2})
    m.part('L', 'mag_and_lefthand', [8, -8.5, 6.2])
    m.part('lefthand', 'L', [8, -8.5, 6.2], [97.5, 0, -180])
    lh = m.part('lefthand_pos', 'lefthand', [14, -19.5, 6.2])
    lh.bar(7, 10, -19.5, -7.5, 4.2, 8.2, 'arm', data={'k': 2})


def pistol_rig(gid, bore_y, muzzle_z, tex_size=1024, k=16):
    """A model with the root / hand / gun bones a TACZ pistol expects. Returns (model, gun bone name)."""
    m = Model(gid, tex_size=tex_size, texels_per_unit=k)
    m.part('root', None, [0, 3.9, 0])
    m.part('gun_and_righthand', 'root', [0, 3.9, 0])
    m.part('mag_and_lefthand', 'root', [0, 1.995, 1.6])
    hands(m)
    m.part(gid, 'gun_and_righthand', [0, 3.9, 0])
    m.part('muzzle_flash', gid, [0, bore_y, muzzle_z - 0.3])
    m.part('shell', gid, [-0.4, bore_y + 0.3, -0.9])
    m.part('constraint', gid, [0, 6.275, 1.175])
    return m


def pistol_views(m, sight_y, muzzle_z):
    """Camera anchors: hip view, iron-sight view and the attachment-screen views."""
    m.part('camera', None, [2.35, 7.275, 13.375])
    m.part('view', None, [8, 0, 0])
    m.part('idle_view', 'view', [2.35, 7.275, 14.375])
    m.part('iron_view', 'view', [0, sight_y, 14.875])
    m.part('refit_view', 'view', [14.1, 2.725, -1], [0, 89, 0])
    m.part('refit_muzzle_view', 'view', [5.6, 5.525, muzzle_z - 3.4], [0, 120, 0])
    m.part('positioning', None, [8, -1, -1])
    m.part('thirdperson_hand', 'positioning', [0, 4.075, -0.15])
    m.part('ground', 'positioning', [0, -3.9, -1.1])
    m.part('fixed', 'positioning', [0.625, 4.009, -0.5375], [0, 90, 0])


def arm_colour(p, c):
    """Placeholder arm paint (only seen in Blockbench; in game TACZ draws the player's real arms)."""
    import numpy as np
    import materials as M
    skin = (p[:, 1] > c.hi[1] - 3.2)
    col = np.where(skin[:, None], np.array([[224, 172, 132]]), np.array([[38, 40, 48]]))
    return M.finish(M.rgba(col * (0.92 + 0.1 * M.vnoise(p, 3))[:, None]))
