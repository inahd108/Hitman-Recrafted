package recrafted.block.ams;

import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;

import java.util.Locale;

/** The carved shoulder piece of a neck or bell gable; SIDE says which side of the neck it sits on, seen from the street. */
public class ScrollBlock extends DecorBlock {
    public enum Side implements StringRepresentable {
        LEFT, RIGHT;

        @Override
        public String getSerializedName() {
            return name().toLowerCase(Locale.ROOT);
        }
    }

    public static final EnumProperty<Side> SIDE = EnumProperty.create("side", Side.class);

    public ScrollBlock(Properties props) {
        super(props, true, new double[]{0, 0, 0, 16, 16, 16});
        registerDefaultState(defaultBlockState().setValue(SIDE, Side.LEFT));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        super.createBlockStateDefinition(b);
        b.add(SIDE);
    }
}
