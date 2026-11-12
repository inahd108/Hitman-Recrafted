package recrafted.block.ams;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.Map;

/**
 * Street furniture with a facing: bulb strings, bicycles and the like. The outline is given for
 * facing north (in pixels) and turned for the other directions; {@code solid} decides whether it blocks.
 */
public class DecorBlock extends HorizontalDirectionalBlock {
    private final Map<Direction, VoxelShape> shapes = new EnumMap<>(Direction.class);
    private final boolean solid;

    public DecorBlock(Properties props, boolean solid, double[]... boxesNorth) {
        super(props);
        this.solid = solid;
        for (Direction d : Direction.Plane.HORIZONTAL) {
            VoxelShape s = Shapes.empty();
            for (double[] b : boxesNorth) s = Shapes.or(s, rotate(b, d));
            shapes.put(d, s);
        }
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    /** Rotate a north-facing box (x0,y0,z0,x1,y1,z1 in pixels) to face d. */
    private static VoxelShape rotate(double[] b, Direction d) {
        double x0 = b[0], z0 = b[2], x1 = b[3], z1 = b[5];
        double[] r = switch (d) {
            case SOUTH -> new double[]{16 - x1, 16 - z1, 16 - x0, 16 - z0};
            case EAST -> new double[]{16 - z1, x0, 16 - z0, x1};
            case WEST -> new double[]{z0, 16 - x1, z1, 16 - x0};
            default -> new double[]{x0, z0, x1, z1};
        };
        AABB box = new AABB(Math.max(0, r[0]) / 16, b[1] / 16, Math.max(0, r[1]) / 16,
                Math.min(16, r[2]) / 16, b[4] / 16, Math.min(16, r[3]) / 16);
        return Shapes.create(box);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
    }

    @Override
    public VoxelShape getShape(BlockState s, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return shapes.get(s.getValue(FACING));
    }

    @Override
    public VoxelShape getCollisionShape(BlockState s, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return solid ? shapes.get(s.getValue(FACING)) : Shapes.empty();
    }
}
