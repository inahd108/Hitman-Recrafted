package recrafted.block.ams;

import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;

import java.util.Locale;

/** A parked city bike. Walks through, like the real ones never let you. */
public class BicycleBlock extends DecorBlock {
    public enum Paint implements StringRepresentable {
        BLACK, NAVY, RED, GREEN, CREAM;

        @Override
        public String getSerializedName() {
            return name().toLowerCase(Locale.ROOT);
        }
    }

    public static final EnumProperty<Paint> PAINT = EnumProperty.create("paint", Paint.class);

    public BicycleBlock(Properties props) {
        super(props, false, new double[]{0, 0, 7, 16, 14, 9});
        registerDefaultState(defaultBlockState().setValue(PAINT, Paint.BLACK));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        super.createBlockStateDefinition(b);
        b.add(PAINT);
    }
}
