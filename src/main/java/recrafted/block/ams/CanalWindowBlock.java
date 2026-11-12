package recrafted.block.ams;

import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;

/**
 * A white-framed sash window that fills a facade opening. Lit windows glow amber and light the street
 * in front of them; dark ones show a cold reflection. AXIS is the direction the glass faces along.
 */
public class CanalWindowBlock extends Block {
    public static final EnumProperty<Direction.Axis> AXIS = BlockStateProperties.HORIZONTAL_AXIS;
    public static final BooleanProperty LIT = BlockStateProperties.LIT;

    public CanalWindowBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(AXIS, Direction.Axis.Z).setValue(LIT, true));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(AXIS, LIT);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(AXIS, ctx.getHorizontalDirection().getAxis());
    }
}
