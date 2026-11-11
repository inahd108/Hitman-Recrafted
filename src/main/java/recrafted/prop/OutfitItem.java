package recrafted.prop;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import recrafted.mission.PlayerData;
import recrafted.npc.NpcRole;

import javax.annotation.Nullable;
import java.util.List;

/** A folded uniform. Use it to change clothes; your previous outfit comes back as an item. */
public class OutfitItem extends Item {
    public final NpcRole role;

    public OutfitItem(NpcRole role, Properties props) {
        super(props);
        this.role = role;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) return InteractionResultHolder.success(stack);
        ServerPlayer sp = (ServerPlayer) player;
        NpcRole old = PlayerData.disguise(sp);
        PlayerData.setDisguise(sp, role, level.random.nextInt(role.variants));
        level.playSound(null, player.blockPosition(), SoundEvents.ARMOR_EQUIP_LEATHER, SoundSource.PLAYERS, 1f, 1f);
        sp.displayClientMessage(Component.literal("Disguise: " + role.title).withStyle(ChatFormatting.AQUA), true);
        ItemStack back = old != null && old.wearable
                ? new ItemStack(recrafted.ModRegistry.OUTFITS.get(old).get()) : ItemStack.EMPTY;
        return InteractionResultHolder.consume(player.getAbilities().instabuild ? stack : back);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.literal("Use to change into this outfit.").withStyle(ChatFormatting.GRAY));
        if (role.guard) tip.add(Component.literal("Lets you carry weapons openly.").withStyle(ChatFormatting.DARK_AQUA));
    }
}
