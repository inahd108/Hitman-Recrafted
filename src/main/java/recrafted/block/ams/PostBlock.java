package recrafted.block.ams;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A thin upright thing with a fixed outline: bollards, lamp posts, lamp heads. */
public class PostBlock extends Block {
    private final VoxelShape shape;

    public PostBlock(Properties props, double x0, double y0, double z0, double x1, double y1, double z1) {
        super(props);
        this.shape = Block.box(x0, y0, z0, x1, y1, z1);
    }

    @Override
    public VoxelShape getShape(BlockState s, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return shape;
    }
}
