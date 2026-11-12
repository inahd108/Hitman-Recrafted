package recrafted.npc;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import recrafted.compat.Guns;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * How an armed guard fights: a beat to react after drawing, then aimed, deliberately imperfect fire in
 * the gun's own rhythm (single shots from a revolver, short bursts from an automatic), a pause to reload
 * when the magazine runs dry, and a pistol-whip if you get too close.
 */
public final class Gunfight {
    /** Shot results by TACZ outcome, for the dev tests. */
    public static final Map<String, Integer> RESULTS = new ConcurrentHashMap<>();

    private static final int RELOAD_TICKS = 50;

    private int aim;
    private int cooldown;
    private int burst;
    private int mag;
    private int reload;

    /** The gun just came out of the holster. */
    public void drew(NpcEntity npc) {
        ItemStack gun = npc.getMainHandItem();
        Guns.npcDraw(npc);
        RandomSource r = npc.getRandom();
        aim = 14 + r.nextInt(12);
        mag = Guns.capacity(gun);
        burst = Guns.cadence(gun).burst();
        cooldown = 0;
        reload = 0;
    }

    public void tick(NpcEntity npc, ServerPlayer target, boolean sees, double dist) {
        ItemStack gun = npc.getMainHandItem();
        Guns.Cadence c = Guns.cadence(gun);
        if (reload > 0) {
            if (--reload == 0) {
                Guns.refill(gun);
                mag = Guns.capacity(gun);
                burst = c.burst();
            }
            return;
        }
        if (aim > 0) {
            if (sees) aim--;
            return;
        }
        if (cooldown > 0) {
            cooldown--;
            return;
        }
        if (!sees) return;
        RandomSource r = npc.getRandom();
        if (dist < 1.9) {
            // too close to aim: pistol-whip
            npc.swing(InteractionHand.MAIN_HAND);
            npc.doHurtTarget(target);
            cooldown = 18;
            return;
        }
        Vec3 eye = npc.getEyePosition();
        Vec3 chest = target.position().add(0, target.getBbHeight() * 0.62, 0);
        Vec3 d = chest.subtract(eye);
        float yaw = (float) Math.toDegrees(Math.atan2(-d.x, d.z));
        float pitch = (float) -Math.toDegrees(Math.atan2(d.y, d.horizontalDistance()));
        // degrees of aim error (one standard deviation): worse with range and against a running target
        // (TACZ bullets hit generously, so this is wider than it sounds: about two in three land at 6 blocks
        // against a standing target, one in three at 12, fewer if you run)
        float spread = 4.0f + (float) dist * 0.3f + (target.isSprinting() ? 3.0f : 0f) + (target.isCrouching() ? 0.8f : 0f);
        yaw += (float) r.nextGaussian() * spread;
        pitch += (float) r.nextGaussian() * spread * 0.7f;
        String result = Guns.npcShoot(npc, Mth.clamp(pitch, -89f, 89f), yaw);
        RESULTS.merge(result, 1, Integer::sum);
        if ("SUCCESS".equals(result)) mag--;
        if (mag <= 0) {
            reload = RELOAD_TICKS;
            npc.say("Reloading!", 30);
        } else if (--burst > 0) {
            cooldown = c.interval();
        } else {
            burst = c.burst();
            cooldown = c.interval() + c.pause() + r.nextInt(10);
        }
    }
}
