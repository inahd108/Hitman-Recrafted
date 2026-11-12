package recrafted.block.ams;

import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;

import java.util.Locale;

/** An opened warehouse shutter flat against the wall, painted in the old diagonal stripes. */
public class ShutterBlock extends DecorBlock {
    public enum Paint implements StringRepresentable {
        GREEN, RED, BLACK;

        @Override
        public String getSerializedName() {
            return name().toLowerCase(Locale.ROOT);
        }
    }

    public static final EnumProperty<Paint> PAINT = EnumProperty.create("paint", Paint.class);

    public ShutterBlock(Properties props) {
        super(props, false, new double[]{0, 0, 14, 16, 16, 16});
        registerDefaultState(defaultBlockState().setValue(PAINT, Paint.GREEN));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        super.createBlockStateDefinition(b);
        b.add(PAINT);
    }
}
