package recrafted.dev;

import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.entity.PropEntity;
import recrafted.mission.Mission;
import recrafted.mission.MissionManager;
import recrafted.mission.MissionState;
import recrafted.npc.NpcEntity;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Headless smoke test, enabled with -Drecrafted.selftest=true on a dedicated server.
 * Loads the whole island, starts the contract without a player, lets the town run for
 * a while and logs how the cast is doing, then exercises the objectives and stops the server.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class SelfTest {
    private static final Logger LOG = LogManager.getLogger("recrafted-selftest");
    private static final boolean ENABLED = Boolean.getBoolean("recrafted.selftest");
    private static final int RUN_TICKS = Integer.getInteger("recrafted.selftest.ticks", 2400);
    private static int ticks = -1;
    private static final Map<Integer, Vec3> startPos = new HashMap<>();

    private SelfTest() {}

    @SubscribeEvent
    public static void started(ServerStartedEvent e) {
        if (!ENABLED) return;
        MinecraftServer server = e.getServer();
        ServerLevel level = MissionManager.missionLevel(server);
        if (level == null) {
            LOG.error("SELFTEST FAIL: mission dimension missing");
            server.halt(false);
            return;
        }
        for (int cx = 0; cx < 20; cx++) for (int cz = 0; cz < 18; cz++) level.setChunkForced(cx, cz, true);
        MissionManager.begin(level);
        ticks = 0;
        LOG.info("SELFTEST started: {} NPCs and {} props queued", MissionState.get(level).pendingNpcs.size(),
                MissionState.get(level).pendingProps.size());
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent e) {
        if (!ENABLED || ticks < 0 || e.phase != TickEvent.Phase.END) return;
        MinecraftServer server = e.getServer();
        ServerLevel level = MissionManager.missionLevel(server);
        if (level == null) return;
        ticks++;
        if (ticks % 400 == 0 || ticks == RUN_TICKS) {
            List<NpcEntity> npcs = new ArrayList<>();
            int props = 0;
            for (Entity en : level.getAllEntities()) {
                if (en instanceof NpcEntity n) npcs.add(n);
                else if (en instanceof PropEntity) props++;
            }
            int moved = 0, fell = 0;
            for (NpcEntity n : npcs) {
                Vec3 s = startPos.computeIfAbsent(n.getId(), k -> n.position());
                if (s.distanceToSqr(n.position()) > 4) moved++;
                if (n.getY() < 30) fell++;
            }
            MissionState st = MissionState.get(level);
            LOG.info("SELFTEST t={} npcs={} props={} pending={}/{} movedFromStart={} belowY30={} arrivals={} unsticks={}",
                    ticks, npcs.size(), props, st.pendingNpcs.size(), st.pendingProps.size(), moved, fell,
                    NpcEntity.statArrivals, NpcEntity.statUnsticks);
        }
        if (ticks == RUN_TICKS) {
            Mission m = Mission.corvara();
            MissionState st = MissionState.get(level);
            int coreCount = 0;
            BlockPos core = null;
            for (BlockPos p : BlockPos.betweenClosed(200, 38, 100, 260, 50, 135)) {
                if (level.getBlockState(p).is(ModRegistry.PATHOGEN_CORE.get())) { coreCount++; core = p.immutable(); }
            }
            LOG.info("SELFTEST core blocks found: {} at {}", coreCount, core);
            for (Map.Entry<String, Integer> en : NpcEntity.UNSTICK_LOG.entrySet()) {
                LOG.info("SELFTEST unstick x{}: {}", en.getValue(), en.getKey());
            }
            // exercise objectives
            for (Entity en : level.getAllEntities()) {
                if (en instanceof NpcEntity n && n.isTarget()) n.kill(null, true);
            }
            if (core != null) MissionManager.smashCoreHeadless(level, core);
            LOG.info("SELFTEST objectives done: {} of {}", st.done.size(), m.objectives.size() - 1);
            boolean ok = st.pendingNpcs.isEmpty() && coreCount == 1 && st.done.size() == m.objectives.size() - 1;
            LOG.info(ok ? "SELFTEST PASS" : "SELFTEST FAIL");
            server.halt(false);
        }
    }
}
