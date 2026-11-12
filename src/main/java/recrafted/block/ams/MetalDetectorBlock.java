package recrafted.block.ams;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import recrafted.mission.MissionManager;

/**
 * A walk-through security arch. Anyone carrying a gun or an illegal prop sets it off (unless dressed as
 * security); the lamp on the crossbar goes red for two seconds.
 */
public class MetalDetectorBlock extends DecorBlock {
    public static final BooleanProperty ALARM = BooleanProperty.create("alarm");

    public MetalDetectorBlock(Properties props) {
        super(props, false, new double[]{0, 0, 6, 2, 30, 10}, new double[]{14, 0, 6, 16, 30, 10});
        registerDefaultState(defaultBlockState().setValue(ALARM, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        super.createBlockStateDefinition(b);
        b.add(ALARM);
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (level instanceof ServerLevel sl && entity instanceof ServerPlayer sp && MissionManager.metalDetector(sl, sp, pos)) {
            sl.setBlock(pos, state.setValue(ALARM, true), 3);
            sl.scheduleTick(pos, this, 40);
        }
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource rnd) {
        if (state.getValue(ALARM)) level.setBlock(pos, state.setValue(ALARM, false), 3);
    }
}
