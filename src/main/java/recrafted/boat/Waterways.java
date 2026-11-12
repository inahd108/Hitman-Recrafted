package recrafted.boat;

import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.state.BlockState;
import recrafted.mission.Mission;
import recrafted.mission.MissionManager;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * The drawbridge and the lock gates. A boat waiting at a gate asks for it every tick; the keeper opens it after a
 * short delay (unless somebody holds the bridge down, or people are still on the span) and closes it again once
 * nothing has asked for a while and no boat is in the way.
 */
public final class Waterways {
    private static final Map<String, Gate> GATES = new HashMap<>();

    private static final class Gate {
        boolean open, held;
        long openAt = -1, lastAsked = -1000;
        final Map<BlockPos, BlockState> original = new LinkedHashMap<>();
    }

    private Waterways() {}

    private static String key(ServerLevel level, String name) {
        return level.dimension().location() + "/" + name;
    }

    private static Gate gate(ServerLevel level, String name) {
        return GATES.computeIfAbsent(key(level, name), k -> new Gate());
    }

    public static void reset(ServerLevel level) {
        Mission m = Mission.forDimension(level.dimension());
        if (m == null) return;
        for (Mission.GateDef d : m.gates) {
            Gate g = GATES.get(key(level, d.name()));
            if (g != null && g.open) close(level, d, g);
            GATES.remove(key(level, d.name()));
        }
    }

    public static boolean isOpen(ServerLevel level, String name) {
        Gate g = GATES.get(key(level, name));
        return g != null && g.open;
    }

    public static boolean isHeld(ServerLevel level, String name) {
        Gate g = GATES.get(key(level, name));
        return g != null && g.held;
    }

    /** Toggles the keeper's hold on a gate; returns the new state. A held gate closes as soon as it can. */
    public static boolean toggleHold(ServerLevel level, String name) {
        Gate g = gate(level, name);
        g.held = !g.held;
        g.openAt = -1;
        return g.held;
    }

    /** A boat at the gate asks for it. Returns true once it is open. */
    public static boolean request(ServerLevel level, String name) {
        Mission m = Mission.forDimension(level.dimension());
        Mission.GateDef d = m == null ? null : m.gate(name);
        if (d == null) return true;
        Gate g = gate(level, name);
        long now = level.getGameTime();
        g.lastAsked = now;
        if (g.open) return true;
        if (g.held) return false;
        if (g.openAt < 0) {
            g.openAt = now + (d.kind().equals("drawbridge") ? 60 : 40);
            BlockPos c = BlockPos.containing(d.clear().getCenter());
            level.playSound(null, c, SoundEvents.BELL_BLOCK, SoundSource.BLOCKS, 1.2f, d.kind().equals("drawbridge") ? 1.4f : 0.9f);
        }
        if (now >= g.openAt && clearOfPeople(level, d)) {
            open(level, d, g);
            return true;
        }
        return false;
    }

    public static void tick(ServerLevel level) {
        Mission m = Mission.forDimension(level.dimension());
        if (m == null) return;
        long now = level.getGameTime();
        for (Mission.GateDef d : m.gates) {
            Gate g = GATES.get(key(level, d.name()));
            if (g == null || !g.open) continue;
            boolean idle = now - g.lastAsked > 160 || g.held;
            if (idle && level.getEntitiesOfClass(CanalBoat.class, d.clear().inflate(3, 2, 3)).isEmpty() && clearOfPeople(level, d)) {
                close(level, d, g);
            }
        }
    }

    private static boolean clearOfPeople(ServerLevel level, Mission.GateDef d) {
        if (!d.kind().equals("drawbridge")) return true;
        return level.getEntitiesOfClass(LivingEntity.class, d.clear().inflate(0, 3, 0), e -> !e.isPassenger() && !e.isSpectator()).isEmpty();
    }

    private static void open(ServerLevel level, Mission.GateDef d, Gate g) {
        g.open = true;
        g.openAt = -1;
        for (Mission.GateBlock b : d.open()) {
            g.original.putIfAbsent(b.pos(), level.getBlockState(b.pos()));
            MissionManager.setTracked(level, b.pos(), parse(level, b.state()));
        }
        BlockPos c = BlockPos.containing(d.clear().getCenter());
        level.playSound(null, c, d.kind().equals("drawbridge") ? SoundEvents.WOODEN_TRAPDOOR_OPEN : SoundEvents.PISTON_EXTEND,
                SoundSource.BLOCKS, 1.4f, 0.6f);
    }

    private static void close(ServerLevel level, Mission.GateDef d, Gate g) {
        g.open = false;
        for (Map.Entry<BlockPos, BlockState> e : g.original.entrySet()) level.setBlock(e.getKey(), e.getValue(), 3);
        g.original.clear();
        BlockPos c = BlockPos.containing(d.clear().getCenter());
        level.playSound(null, c, d.kind().equals("drawbridge") ? SoundEvents.WOODEN_TRAPDOOR_CLOSE : SoundEvents.PISTON_CONTRACT,
                SoundSource.BLOCKS, 1.4f, 0.6f);
    }

    private static BlockState parse(ServerLevel level, String s) {
        try {
            return BlockStateParser.parseForBlock(level.holderLookup(Registries.BLOCK), s, false).blockState();
        } catch (Exception e) {
            return net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
        }
    }
}
