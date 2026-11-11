package recrafted.prop;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import recrafted.entity.ThrownPropEntity;

import javax.annotation.Nullable;
import java.util.List;

/** A usable prop. Melee behaviour lives in {@link recrafted.mission.Combat}; throwing lives here. */
public class PropItem extends Item {
    public final PropType type;

    public PropItem(PropType type, Properties props) {
        super(props);
        this.type = type;
    }

    @Nullable
    public static PropType typeOf(ItemStack stack) {
        return stack.getItem() instanceof PropItem p ? p.type : null;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!type.throwable()) return InteractionResultHolder.pass(stack);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.SNOWBALL_THROW, SoundSource.PLAYERS,
                0.5f, 0.5f / (level.getRandom().nextFloat() * 0.4f + 0.8f));
        if (!level.isClientSide) {
            ThrownPropEntity thrown = new ThrownPropEntity(level, player);
            thrown.setItem(stack.copyWithCount(1));
            thrown.shootFromRotation(player, player.getXRot(), player.getYRot(), 0f,
                    type.kind == PropType.Kind.COIN ? 1.1f : 1.3f, 0.6f);
            level.addFreshEntity(thrown);
        }
        player.awardStat(Stats.ITEM_USED.get(this));
        if (!player.getAbilities().instabuild) stack.shrink(1);
        player.getCooldowns().addCooldown(this, 12);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.literal(type.tooltip()).withStyle(ChatFormatting.GRAY));
        if (type.sabotages()) tip.add(Component.literal("Sabotages fuse boxes.").withStyle(ChatFormatting.DARK_AQUA));
        if (type.forces()) tip.add(Component.literal("Forces card readers. Loudly.").withStyle(ChatFormatting.DARK_AQUA));
        if (type.illegal()) tip.add(Component.literal("Suspicious to carry in the open.").withStyle(ChatFormatting.RED));
    }
}
