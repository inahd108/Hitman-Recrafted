package recrafted.block;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import recrafted.mission.Awareness;
import recrafted.mission.MissionManager;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

/** Sabotage it with a wrench or screwdriver and the nearest handyman or guard walks over to fix it. */
public class FuseBoxBlock extends Block {
    public static final BooleanProperty BROKEN = BooleanProperty.create("broken");

    public FuseBoxBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(BROKEN, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(BROKEN);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand,
                                 BlockHitResult hit) {
        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
        if (level.isClientSide) return InteractionResult.SUCCESS;
        ServerPlayer sp = (ServerPlayer) player;
        ServerLevel sl = (ServerLevel) level;
        if (state.getValue(BROKEN)) {
            sp.displayClientMessage(Component.literal("Already sabotaged"), true);
            return InteractionResult.CONSUME;
        }
        PropType type = PropItem.typeOf(player.getMainHandItem());
        if (type == null || !type.sabotages()) {
            sp.displayClientMessage(Component.literal("Needs a wrench or a screwdriver").withStyle(ChatFormatting.YELLOW), true);
            return InteractionResult.CONSUME;
        }
        MissionManager.setTracked(sl, pos, state.setValue(BROKEN, true));
        level.playSound(null, pos, SoundEvents.REDSTONE_TORCH_BURNOUT, SoundSource.BLOCKS, 1f, 0.7f);
        sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, pos.getX() + .5, pos.getY() + .5, pos.getZ() + .5, 20, .4, .4, .4, .05);
        sp.displayClientMessage(Component.literal("Fuse box sabotaged — someone will come").withStyle(ChatFormatting.GREEN), true);
        Awareness.callRepair(sl, pos);
        Awareness.suspiciousAct(sl, sp, 0.6f);
        return InteractionResult.CONSUME;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource rnd) {
        if (state.getValue(BROKEN) && rnd.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.ELECTRIC_SPARK, pos.getX() + rnd.nextDouble(), pos.getY() + rnd.nextDouble(),
                    pos.getZ() + rnd.nextDouble(), 0, 0.02, 0);
        }
    }
}
