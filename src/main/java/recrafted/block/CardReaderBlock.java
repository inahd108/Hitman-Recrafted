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
        operate((ServerLevel) level, (ServerPlayer) player, pos, state.getValue(TIER));
        return InteractionResult.CONSUME;
    }

    /** True if the stack is something that can be tried on a lock. */
    public static boolean isLockTool(ItemStack stack) {
        PropType t = PropItem.typeOf(stack);
        return t != null && (t.kind == PropType.Kind.KEYCARD || t.kind == PropType.Kind.LOCKPICK || t.forces());
    }

    /**
     * Tries to open the security doors around pos with whatever the player has.
     * tier is null for a door that has no reader: only a lockpick or a crowbar works on those.
     */
    public static void operate(ServerLevel sl, ServerPlayer sp, BlockPos pos, @javax.annotation.Nullable KeyTier tier) {
        ItemStack held = sp.getMainHandItem();
        PropType type = PropItem.typeOf(held);
        boolean hasCard = tier != null && (PropItem.typeOf(sp.getMainHandItem()) == tier.card
                || PropItem.typeOf(sp.getOffhandItem()) == tier.card
                || sp.getInventory().items.stream().anyMatch(s -> PropItem.typeOf(s) == tier.card));
        if (hasCard) {
            DoorTimers.openNear(sl, pos, 3, 80);
            sl.playSound(null, pos, SoundEvents.NOTE_BLOCK_PLING.get(), SoundSource.BLOCKS, 0.6f, 1.6f);
            sp.displayClientMessage(Component.literal("Access granted").withStyle(ChatFormatting.GREEN), true);
        } else if (type == PropType.LOCKPICK) {
            DoorTimers.openNear(sl, pos, 3, 100);
            sl.playSound(null, pos, SoundEvents.IRON_TRAPDOOR_OPEN, SoundSource.BLOCKS, 0.4f, 1.8f);
            if (sl.random.nextFloat() < 0.2f) {
                held.shrink(1);
                sp.displayClientMessage(Component.literal("Door open — the pick snapped").withStyle(ChatFormatting.YELLOW), true);
            } else {
                sp.displayClientMessage(Component.literal("Lock picked").withStyle(ChatFormatting.GREEN), true);
            }
            Awareness.suspiciousAct(sl, sp, 0.5f);
        } else if (type != null && type.forces()) {
            DoorTimers.openNear(sl, pos, 3, 200);
            sl.playSound(null, pos, SoundEvents.ZOMBIE_ATTACK_IRON_DOOR, SoundSource.BLOCKS, 1f, 0.8f);
            sp.displayClientMessage(Component.literal("Forced open — that was loud").withStyle(ChatFormatting.RED), true);
            Awareness.noise(sl, Vec3.atCenterOf(pos), 16, 3, sp);
            Awareness.suspiciousAct(sl, sp, 1f);
        } else {
            sl.playSound(null, pos, SoundEvents.NOTE_BLOCK_BASS.get(), SoundSource.BLOCKS, 0.6f, 0.6f);
            String need = tier != null ? tier.label + " keycard, a lockpick or a crowbar" : "a lockpick or a crowbar";
            sp.displayClientMessage(Component.literal("Locked — needs " + need).withStyle(ChatFormatting.RED), true);
        }
    }

    /** Right-clicking the door itself: use the reader beside it if there is one. */
    public static void operateDoor(ServerLevel sl, ServerPlayer sp, BlockPos door) {
        for (BlockPos p : BlockPos.betweenClosed(door.offset(-3, -2, -3), door.offset(3, 3, 3))) {
            BlockState s = sl.getBlockState(p);
            if (s.getBlock() instanceof CardReaderBlock) {
                operate(sl, sp, p.immutable(), s.getValue(TIER));
                return;
            }
        }
        operate(sl, sp, door, null);
    }
}
