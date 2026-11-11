package recrafted.block;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import recrafted.mission.Awareness;
import recrafted.mission.MissionManager;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

/** A plate or a glass that NPCs eat or drink from when their route says so. Can be poisoned. */
public class ConsumableBlock extends Block {
    public static final EnumProperty<Poison> POISON = EnumProperty.create("poison", Poison.class);
    private final VoxelShape shape;

    public ConsumableBlock(Properties props, VoxelShape shape) {
        super(props);
        this.shape = shape;
        registerDefaultState(stateDefinition.any().setValue(POISON, Poison.NONE));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(POISON);
    }

    @Override
    public VoxelShape getShape(BlockState s, BlockGetter g, BlockPos p, CollisionContext c) {
        return shape;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand,
                                 BlockHitResult hit) {
        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
        ItemStack held = player.getMainHandItem();
        PropType type = PropItem.typeOf(held);
        if (type == null || (type.kind != PropType.Kind.EMETIC && type.kind != PropType.Kind.LETHAL)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide) return InteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        ServerPlayer sp = (ServerPlayer) player;
        Poison p = type.kind == PropType.Kind.LETHAL ? Poison.LETHAL : Poison.EMETIC;
        MissionManager.setTracked(sl, pos, state.setValue(POISON, p));
        if (!player.isCreative()) held.shrink(1);
        sl.sendParticles(ParticleTypes.EFFECT, pos.getX() + .5, pos.getY() + .4, pos.getZ() + .5, 6, .1, .1, .1, 0);
        level.playSound(null, pos, SoundEvents.BOTTLE_EMPTY, SoundSource.PLAYERS, 0.4f, 1.4f);
        sp.displayClientMessage(Component.literal(p == Poison.LETHAL ? "Lethal dose added" : "Emetic added")
                .withStyle(ChatFormatting.DARK_GREEN), true);
        Awareness.suspiciousAct(sl, sp, 0.7f);
        return InteractionResult.CONSUME;
    }
}
