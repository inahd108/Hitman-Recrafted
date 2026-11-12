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
    private static final String MISSION = System.getProperty("recrafted.selftest.mission", "corvara");
    private static int ticks = -1;
    private static final Map<Integer, Vec3> startPos = new HashMap<>();

    private SelfTest() {}

    @SubscribeEvent
    public static void started(ServerStartedEvent e) {
        if (!ENABLED) return;
        MinecraftServer server = e.getServer();
        ServerLevel level = level(server);
        if (level == null) {
            LOG.error("SELFTEST FAIL: mission dimension missing");
            server.halt(false);
            return;
        }
        int ncx = MISSION.equals("corvara") ? 20 : 24, ncz = MISSION.equals("corvara") ? 18 : 20;
        for (int cx = 0; cx < ncx; cx++) for (int cz = 0; cz < ncz; cz++) level.setChunkForced(cx, cz, true);
        MissionManager.begin(level);
        ticks = 0;
        LOG.info("SELFTEST started: {} NPCs and {} props queued", MissionState.get(level).pendingNpcs.size(),
                MissionState.get(level).pendingProps.size());
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent e) {
        if (!ENABLED || ticks < 0 || e.phase != TickEvent.Phase.END) return;
        MinecraftServer server = e.getServer();
        ServerLevel level = level(server);
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
        if (ticks == RUN_TICKS && !MISSION.equals("corvara")) {
            boolean ok = amsterdam(level);
            LOG.info(ok ? "SELFTEST PASS" : "SELFTEST FAIL");
            server.halt(false);
            return;
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

    private static ServerLevel level(MinecraftServer server) {
        Mission m = Mission.byId(MISSION);
        return m == null ? null : server.getLevel(m.dimension);
    }

    private static boolean check(boolean cond, String what) {
        LOG.info("SELFTEST {} {}", cond ? "ok  " : "FAIL", what);
        return cond;
    }

    @org.jetbrains.annotations.Nullable
    private static NpcEntity npc(ServerLevel level, String id) {
        for (Entity en : level.getAllEntities()) if (en instanceof NpcEntity n && n.contractId.equals(id)) return n;
        return null;
    }

    private static BlockPos find(ServerLevel level, net.minecraft.world.level.block.Block b, BlockPos from, BlockPos to) {
        for (BlockPos p : BlockPos.betweenClosed(from, to)) if (level.getBlockState(p).is(b)) return p.immutable();
        return null;
    }

    /** Oil & Water: the hidden target, the clue, both rigged loads and the ledger prop. */
    private static boolean amsterdam(ServerLevel level) {
        Mission m = Mission.byId("amsterdam");
        MissionState st = MissionState.get(level);
        boolean ok = check(st.pendingNpcs.isEmpty(), "all " + m.npcs.size() + " NPCs spawned");
        boolean ledger = false;
        for (Entity en : level.getAllEntities()) {
            if (en instanceof PropEntity pe && pe.getItem().is(ModRegistry.prop(recrafted.prop.PropType.LEDGER))) ledger = true;
        }
        ok &= check(ledger, "ledger prop in the vault");
        NpcEntity meester = npc(level, "meester"), ost = npc(level, "ostendorp"), koo = npc(level, "kooistra");
        ok &= check(meester != null && ost != null && koo != null, "three targets present");
        if (meester == null || ost == null || koo == null) return false;
        ok &= check(meester.hiddenTarget && !meester.isTarget() && meester.isLefty(), "De Meester hidden and left-handed");
        BlockPos book = find(level, ModRegistry.WAGE_BOOK.get(), new BlockPos(180, 60, 130), new BlockPos(215, 90, 175));
        ok &= check(book != null, "wage book at " + book);
        if (book != null) MissionManager.readClue(level, null, book);
        ok &= check(st.identified.contains("meester") && meester.isTarget(), "wage book identifies De Meester");
        // the chandelier: Ostendorp at the lectern, somebody lets go of the rope on the balcony
        BlockPos hw = find(level, ModRegistry.WINCH.get(), new BlockPos(60, 60, 222), new BlockPos(92, 80, 252));
        ok &= check(hw != null, "saleroom winch at " + hw);
        BlockPos chand = find(level, ModRegistry.CHANDELIER.get(), new BlockPos(70, 66, 245), new BlockPos(80, 74, 252));
        ok &= check(chand != null, "chandelier at " + chand);
        if (hw != null && chand != null) {
            ost.getNavigation().stop();
            ost.teleportTo(chand.getX() + .5, 65.5, chand.getZ() + .5);
            MissionManager.dropLoad(level, null, hw);
        }
        ok &= check(st.done.contains("kill_ostendorp"), "chandelier kills Ostendorp");
        // the hoist crate: De Meester on the quay below
        BlockPos sw = find(level, ModRegistry.WINCH.get(), new BlockPos(148, 70, 220), new BlockPos(160, 100, 240));
        ok &= check(sw != null, "studio winch at " + sw);
        BlockPos crate = null;
        if (sw != null) {
            for (BlockPos p : BlockPos.betweenClosed(sw.offset(-12, -12, -12), sw.offset(12, 12, 12))) {
                if (level.getBlockState(p).is(net.minecraft.world.level.block.Blocks.BARREL)
                        && level.getBlockState(p.above()).is(net.minecraft.world.level.block.Blocks.CHAIN)) { crate = p.immutable(); break; }
            }
        }
        ok &= check(crate != null, "hoist crate at " + crate);
        if (crate != null) {
            meester.getNavigation().stop();
            meester.teleportTo(crate.getX() + .5, 64, crate.getZ() + .5);
            MissionManager.dropLoad(level, null, sw);
        }
        ok &= check(st.done.contains("kill_meester"), "hoist crate kills De Meester");
        koo.kill(null, true);
        ok &= check(st.done.contains("kill_kooistra"), "Kooistra objective");
        ok &= check(!st.done.contains("ledger"), "ledger bonus still open");
        return ok;
    }
}
