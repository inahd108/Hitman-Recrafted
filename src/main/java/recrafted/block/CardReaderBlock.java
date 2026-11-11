package recrafted.block;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import recrafted.mission.Awareness;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

/** Wall panel beside a security door. Swipe a matching card, pick it, or force it. */
public class CardReaderBlock extends Block {
    public static final EnumProperty<KeyTier> TIER = EnumProperty.create("tier", KeyTier.class);

    public CardReaderBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(TIER, KeyTier.LAB));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
        b.add(TIER);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand,
                                 BlockHitResult hit) {
        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
        if (level.isClientSide) return InteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        ServerPlayer sp = (ServerPlayer) player;
        KeyTier tier = state.getValue(TIER);
        ItemStack held = player.getMainHandItem();
        PropType type = PropItem.typeOf(held);
        boolean hasCard = PropItem.typeOf(player.getMainHandItem()) == tier.card
                || PropItem.typeOf(player.getOffhandItem()) == tier.card
                || player.getInventory().items.stream().anyMatch(s -> PropItem.typeOf(s) == tier.card);
        if (hasCard) {
            DoorTimers.openNear(sl, pos, 2, 80);
            level.playSound(null, pos, SoundEvents.NOTE_BLOCK_PLING.get(), SoundSource.BLOCKS, 0.6f, 1.6f);
            sp.displayClientMessage(Component.literal("Access granted").withStyle(ChatFormatting.GREEN), true);
        } else if (type == PropType.LOCKPICK) {
            DoorTimers.openNear(sl, pos, 2, 100);
            level.playSound(null, pos, SoundEvents.IRON_TRAPDOOR_OPEN, SoundSource.BLOCKS, 0.4f, 1.8f);
            if (level.random.nextFloat() < 0.2f) {
                held.shrink(1);
                sp.displayClientMessage(Component.literal("Door open — the pick snapped").withStyle(ChatFormatting.YELLOW), true);
            } else {
                sp.displayClientMessage(Component.literal("Lock bypassed").withStyle(ChatFormatting.GREEN), true);
            }
            Awareness.suspiciousAct(sl, sp, 0.5f);
        } else if (type != null && type.forces()) {
            DoorTimers.openNear(sl, pos, 2, 200);
            level.playSound(null, pos, SoundEvents.ZOMBIE_ATTACK_IRON_DOOR, SoundSource.BLOCKS, 1f, 0.8f);
            sp.displayClientMessage(Component.literal("Forced open — that was loud").withStyle(ChatFormatting.RED), true);
            Awareness.noise(sl, Vec3.atCenterOf(pos), 16, 3, sp);
            Awareness.suspiciousAct(sl, sp, 1f);
        } else {
            level.playSound(null, pos, SoundEvents.NOTE_BLOCK_BASS.get(), SoundSource.BLOCKS, 0.6f, 0.6f);
            sp.displayClientMessage(Component.literal(tier.label + " keycard required").withStyle(ChatFormatting.RED), true);
        }
        return InteractionResult.CONSUME;
    }
}
