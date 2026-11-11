package recrafted.mission;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import recrafted.npc.NpcEntity;

import javax.annotation.Nullable;
import java.util.Comparator;
import java.util.List;

/** How news travels: witnesses, noise, guards calling guards. */
public final class Awareness {
    private Awareness() {}

    private static List<NpcEntity> near(ServerLevel level, Vec3 at, double r) {
        return level.getEntitiesOfClass(NpcEntity.class, new AABB(at, at).inflate(r, 8, r), e -> !e.isDown());
    }

    /**
     * A violent act. Anyone who can see the culprit or the victim reacts.
     * Returns the number of witnesses.
     */
    public static int crime(ServerLevel level, ServerPlayer culprit, @Nullable NpcEntity victim) {
        int n = 0;
        for (NpcEntity npc : near(level, culprit.position(), 26)) {
            if (npc == victim) continue;
            boolean saw = npc.canSee(culprit, 24f, 85f) || (victim != null && npc.canSee(victim, 20f, 85f));
            if (saw) {
                npc.onCompromised(culprit);
                n++;
            }
        }
        return n;
    }

    /** Something shady but not violent (poisoning, lockpicking). Watching NPCs get suspicious fast. */
    public static void suspiciousAct(ServerLevel level, ServerPlayer p, float weight) {
        for (NpcEntity npc : near(level, p.position(), 16)) {
            if (npc.canSeePlayer(p)) {
                npc.addSuspicion(p, weight);
                if (npc.suspicionOf(p) >= 1f) npc.onCompromised(p);
            }
        }
    }

    /** A sound draws the closest calm NPCs over to look. */
    public static void noise(ServerLevel level, Vec3 at, double radius, int max, @Nullable ServerPlayer source) {
        List<NpcEntity> list = near(level, at, radius);
        list.removeIf(NpcEntity::isBusy);
        list.sort(Comparator.comparingDouble(e -> e.position().distanceToSqr(at)));
        for (int i = 0; i < Math.min(max, list.size()); i++) {
            NpcEntity n = list.get(i);
            n.say("What was that?", 50);
            n.investigate(at, 120);
        }
    }

    /** A guard in a fight pulls nearby guards in. */
    public static void rallyGuards(ServerLevel level, NpcEntity caller, ServerPlayer target, double radius) {
        for (NpcEntity npc : near(level, caller.position(), radius)) {
            if (npc != caller && npc.getRole().guard) npc.joinAlert(target);
        }
    }

    /** Sends the nearest free guard to look at something (a body a civilian found). */
    public static void sendGuard(ServerLevel level, Vec3 at, double radius, @Nullable NpcEntity body) {
        List<NpcEntity> list = near(level, at, radius);
        list.removeIf(e -> !e.getRole().guard || e.isBusy());
        list.sort(Comparator.comparingDouble(e -> e.position().distanceToSqr(at)));
        if (list.isEmpty()) return;
        if (body != null) list.get(0).investigateBodyAt(body);
        else list.get(0).investigate(at, 120);
    }

    /** A dead body was confirmed: guards nearby sweep the area. */
    public static void lockdown(ServerLevel level, Vec3 at, double radius) {
        for (NpcEntity npc : near(level, at, radius)) {
            if (npc.getRole().guard && !npc.inCombat()) npc.beginSearch(at, 20 * 25);
        }
    }

    public static void callRepair(ServerLevel level, BlockPos pos) {
        Vec3 at = Vec3.atCenterOf(pos);
        List<NpcEntity> list = near(level, at, 40);
        list.removeIf(e -> !e.getRole().fixesThings() || e.isBusy() || e.isTarget());
        list.sort(Comparator.comparingDouble(e -> e.position().distanceToSqr(at)));
        if (!list.isEmpty()) list.get(0).goRepair(pos);
    }
}
