package recrafted.item;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import recrafted.mission.PlayerData;
import recrafted.net.Net;
import recrafted.npc.NpcEntity;
import recrafted.npc.Route;
import recrafted.npc.Waypoint;

import javax.annotation.Nullable;
import java.util.List;
import java.util.UUID;

/**
 * The route editor in item form.
 * Right-click an NPC to select it, right-click blocks to drop waypoints,
 * sneak + right-click to open the editor, left-click a waypoint to remove it.
 */
public class RoutePlannerItem extends Item {
    public RoutePlannerItem(Properties props) {
        super(props);
    }

    @Nullable
    public static NpcEntity selected(ServerPlayer p) {
        UUID id = PlayerData.selectedNpc(p);
        if (id == null) return null;
        return ((ServerLevel) p.level()).getEntity(id) instanceof NpcEntity n ? n : null;
    }

    private static void hint(ServerPlayer p, String s, ChatFormatting c) {
        p.displayClientMessage(Component.literal(s).withStyle(c), true);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (!(target instanceof NpcEntity npc)) return InteractionResult.PASS;
        if (player.level().isClientSide) return InteractionResult.SUCCESS;
        ServerPlayer sp = (ServerPlayer) player;
        if (!Net.canEdit(sp)) {
            hint(sp, "Route editing needs creative mode or operator rights", ChatFormatting.RED);
            return InteractionResult.CONSUME;
        }
        PlayerData.selectNpc(sp, npc.getUUID());
        Net.sendRoute(sp, npc, player.isShiftKeyDown());
        hint(sp, "Selected " + npc.getName().getString() + " — right-click blocks to add stops, sneak + right-click to edit",
                ChatFormatting.AQUA);
        return InteractionResult.CONSUME;
    }

    @Override
    public InteractionResult useOn(UseOnContext ctx) {
        Level level = ctx.getLevel();
        if (level.isClientSide) return InteractionResult.SUCCESS;
        ServerPlayer sp = (ServerPlayer) ctx.getPlayer();
        if (sp == null) return InteractionResult.PASS;
        if (!Net.canEdit(sp)) {
            hint(sp, "Route editing needs creative mode or operator rights", ChatFormatting.RED);
            return InteractionResult.CONSUME;
        }
        NpcEntity npc = selected(sp);
        if (npc == null) {
            hint(sp, "Right-click an NPC first", ChatFormatting.YELLOW);
            return InteractionResult.CONSUME;
        }
        if (sp.isShiftKeyDown()) {
            Net.sendRoute(sp, npc, true);
            return InteractionResult.CONSUME;
        }
        if (npc.getRoute().points.size() >= Route.MAX_POINTS) {
            hint(sp, "This route is full", ChatFormatting.RED);
            return InteractionResult.CONSUME;
        }
        BlockPos clicked = ctx.getClickedPos();
        BlockPos stand;
        if (level.getBlockState(clicked).getCollisionShape(level, clicked).isEmpty()) stand = clicked;
        else stand = ctx.getClickedFace() == Direction.DOWN ? clicked.below(2) : clicked.relative(ctx.getClickedFace());
        Waypoint wp = new Waypoint(stand.getX() + 0.5, stand.getY(), stand.getZ() + 0.5);
        wp.yaw = Mth.wrapDegrees(sp.getYRot());
        npc.getRoute().points.add(wp);
        npc.setRoute(npc.getRoute());
        Net.sendRoute(sp, npc, false);
        hint(sp, "Stop #" + npc.getRoute().points.size() + " added for " + npc.getName().getString()
                + " (faces the way you are looking)", ChatFormatting.GREEN);
        return InteractionResult.CONSUME;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) return InteractionResultHolder.success(stack);
        ServerPlayer sp = (ServerPlayer) player;
        NpcEntity npc = selected(sp);
        if (npc == null) hint(sp, "Right-click an NPC first", ChatFormatting.YELLOW);
        else if (Net.canEdit(sp)) Net.sendRoute(sp, npc, player.isShiftKeyDown());
        return InteractionResultHolder.consume(stack);
    }

    /** Left-click: removes the stop closest to the clicked block. */
    public static void removeNear(ServerPlayer sp, BlockPos pos) {
        NpcEntity npc = selected(sp);
        if (npc == null || !Net.canEdit(sp)) return;
        Route r = npc.getRoute();
        int best = -1;
        double bd = 2.6;
        for (int i = 0; i < r.points.size(); i++) {
            Waypoint w = r.points.get(i);
            double d = w.pos().distanceToSqr(pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5);
            if (d < bd) { bd = d; best = i; }
        }
        if (best < 0) return;
        r.points.remove(best);
        npc.setRoute(r);
        Net.sendRoute(sp, npc, false);
        hint(sp, "Stop #" + (best + 1) + " removed", ChatFormatting.YELLOW);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.literal("Right-click an NPC: select it").withStyle(ChatFormatting.GRAY));
        tip.add(Component.literal("Right-click a block: add a stop").withStyle(ChatFormatting.GRAY));
        tip.add(Component.literal("Left-click a stop: remove it").withStyle(ChatFormatting.GRAY));
        tip.add(Component.literal("Sneak + right-click: open the route editor").withStyle(ChatFormatting.AQUA));
    }
}
