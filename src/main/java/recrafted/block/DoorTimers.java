package recrafted.block;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.phys.AABB;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/** Security doors open for a moment and close again on their own. */
public final class DoorTimers {
    private static final Map<ResourceKey<Level>, Map<BlockPos, Long>> OPEN = new HashMap<>();

    private DoorTimers() {}

    public static boolean isSecurityDoor(BlockState s) {
        return s.is(Blocks.IRON_DOOR);
    }

    /** Opens the iron door whose lower or upper half is at pos. */
    public static boolean open(ServerLevel level, BlockPos pos, int ticks) {
        BlockState s = level.getBlockState(pos);
        if (!isSecurityDoor(s)) return false;
        if (s.getValue(DoorBlock.HALF) == DoubleBlockHalf.UPPER) {
            pos = pos.below();
            s = level.getBlockState(pos);
            if (!isSecurityDoor(s)) return false;
        }
        if (!s.getValue(DoorBlock.OPEN)) ((DoorBlock) s.getBlock()).setOpen(null, level, s, pos, true);
        OPEN.computeIfAbsent(level.dimension(), k -> new HashMap<>()).put(pos.immutable(), level.getGameTime() + ticks);
        return true;
    }

    public static int openNear(ServerLevel level, BlockPos center, int radius, int ticks) {
        int n = 0;
        for (BlockPos p : BlockPos.betweenClosed(center.offset(-radius, -2, -radius), center.offset(radius, 1, radius))) {
            BlockState s = level.getBlockState(p);
            if (isSecurityDoor(s) && s.getValue(DoorBlock.HALF) == DoubleBlockHalf.LOWER && open(level, p, ticks)) n++;
        }
        return n;
    }

    public static void tick(ServerLevel level) {
        Map<BlockPos, Long> m = OPEN.get(level.dimension());
        if (m == null || m.isEmpty()) return;
        long now = level.getGameTime();
        Iterator<Map.Entry<BlockPos, Long>> it = m.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<BlockPos, Long> e = it.next();
            if (now < e.getValue()) continue;
            BlockPos p = e.getKey();
            if (!level.isLoaded(p)) { it.remove(); continue; }
            BlockState s = level.getBlockState(p);
            if (!isSecurityDoor(s)) { it.remove(); continue; }
            if (!level.getEntitiesOfClass(LivingEntity.class, new AABB(p).inflate(0.2, 0.5, 0.2)).isEmpty()) {
                e.setValue(now + 10);
                continue;
            }
            if (s.getValue(DoorBlock.OPEN)) ((DoorBlock) s.getBlock()).setOpen(null, level, s, p, false);
            it.remove();
        }
    }
}
