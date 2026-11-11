package recrafted.item;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.PacketDistributor;
import recrafted.net.Net;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;

import javax.annotation.Nullable;
import java.util.List;

/** Creates NPCs (right-click a block) and edits or removes them (right-click an NPC). */
public class CastingCardItem extends Item {
    public CastingCardItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        if (ctx.getLevel().isClientSide) return InteractionResult.SUCCESS;
        ServerPlayer sp = (ServerPlayer) ctx.getPlayer();
        if (sp == null) return InteractionResult.PASS;
        if (!Net.canEdit(sp)) {
            sp.displayClientMessage(Component.literal("Casting needs creative mode or operator rights").withStyle(ChatFormatting.RED), true);
            return InteractionResult.CONSUME;
        }
        BlockPos clicked = ctx.getClickedPos();
        BlockPos stand = ctx.getLevel().getBlockState(clicked).getCollisionShape(ctx.getLevel(), clicked).isEmpty() ? clicked
                : ctx.getClickedFace() == Direction.DOWN ? clicked.below(2) : clicked.relative(ctx.getClickedFace());
        Net.CHANNEL.send(PacketDistributor.PLAYER.with(() -> sp),
                new Net.NpcScreenS2C(-1, stand, NpcRole.CIVILIAN.id, "", 0, false, false, "", ""));
        return InteractionResult.CONSUME;
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (!(target instanceof NpcEntity npc)) return InteractionResult.PASS;
        if (player.level().isClientSide) return InteractionResult.SUCCESS;
        ServerPlayer sp = (ServerPlayer) player;
        if (!Net.canEdit(sp)) return InteractionResult.CONSUME;
        Net.CHANNEL.send(PacketDistributor.PLAYER.with(() -> sp), new Net.NpcScreenS2C(npc.getId(), npc.blockPosition(),
                npc.getRole().id, npc.getName().getString(), npc.getSkin(), npc.isEnforcer(), npc.isTarget(),
                npc.contractId, npc.followId));
        return InteractionResult.CONSUME;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.literal("Right-click a block: create an NPC there").withStyle(ChatFormatting.GRAY));
        tip.add(Component.literal("Right-click an NPC: change role, name, look — or remove it").withStyle(ChatFormatting.GRAY));
    }
}
