package recrafted.item;

import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import recrafted.ModRegistry;
import recrafted.compat.Guns;
import recrafted.mission.Awareness;

import javax.annotation.Nullable;
import java.util.List;

/**
 * The Cicala's briefcase. Perfectly legal to carry. Hold use to unlatch it and assemble the rifle (anyone
 * watching gets suspicious); the Pack key folds the rifle back into it. The case remembers the rifle,
 * rounds and scope included; a fresh case holds a loaded, scoped rifle and two spare magazines.
 */
public class CicalaCaseItem extends Item {
    public static final int ASSEMBLE_TICKS = 50;
    private static final String RIFLE = "Rifle";

    public CicalaCaseItem(Properties props) {
        super(props);
    }

    @Override public int getUseDuration(ItemStack stack) { return ASSEMBLE_TICKS; }
    @Override public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.BLOCK; }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!Guns.loaded()) {
            if (!level.isClientSide) player.displayClientMessage(Component.literal("The rifle needs Timeless and Classics Zero"), true);
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        if (!level.isClientSide) {
            level.playSound(null, player.blockPosition(), SoundEvents.IRON_TRAPDOOR_OPEN, SoundSource.PLAYERS, 0.6f, 1.6f);
            player.displayClientMessage(Component.literal("Assembling the Cicala...").withStyle(ChatFormatting.GRAY), true);
        }
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
        if (!(level instanceof ServerLevel sl) || !(user instanceof ServerPlayer sp)) return;
        int done = ASSEMBLE_TICKS - remaining;
        if (done % 12 == 6) sl.playSound(null, sp.blockPosition(), SoundEvents.CROSSBOW_LOADING_MIDDLE, SoundSource.PLAYERS, 0.5f, 1.3f);
        if (done % 10 == 0 && !sp.isCreative()) Awareness.suspiciousAct(sl, sp, 0.3f);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity user) {
        if (level.isClientSide || !(user instanceof Player player)) return stack;
        boolean fresh = !stack.hasTag() || !stack.getTag().contains(RIFLE);
        ItemStack rifle = fresh ? Guns.freshCicala() : ItemStack.of(stack.getTag().getCompound(RIFLE));
        if (rifle.isEmpty()) {
            player.displayClientMessage(Component.literal("The case is empty (is the Recrafted Arsenal gun pack installed?)"), true);
            return stack;
        }
        if (fresh) {
            for (int i = 0; i < 2; i++) {
                ItemStack ammo = Guns.spareAmmo(rifle);
                if (!ammo.isEmpty() && !player.getInventory().add(ammo)) player.drop(ammo, false);
            }
        }
        level.playSound(null, player.blockPosition(), SoundEvents.ARMOR_EQUIP_IRON, SoundSource.PLAYERS, 0.9f, 1.1f);
        player.displayClientMessage(Component.literal("Cicala assembled").withStyle(ChatFormatting.GRAY), true);
        return rifle;
    }

    /** The Pack key: the Cicala in the main hand goes back into its case. */
    public static boolean packHeld(ServerPlayer p) {
        if (!Guns.isCicala(p.getMainHandItem())) return false;
        p.setItemInHand(InteractionHand.MAIN_HAND, packed(p.getMainHandItem()));
        p.level().playSound(null, p.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 0.7f, 1.4f);
        p.displayClientMessage(Component.literal("Packed into the case").withStyle(ChatFormatting.GRAY), true);
        return true;
    }

    /** A case holding this rifle. */
    public static ItemStack packed(ItemStack rifle) {
        ItemStack c = new ItemStack(ModRegistry.CICALA_CASE.get());
        c.getOrCreateTag().put(RIFLE, rifle.save(new CompoundTag()));
        return c;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.literal("A businessman's briefcase. Legal to carry.").withStyle(ChatFormatting.GRAY));
        tip.add(Component.literal("Hold use to assemble the rifle inside.").withStyle(ChatFormatting.DARK_AQUA));
        tip.add(Component.literal("With the rifle in hand, press Pack (B) to put it away.").withStyle(ChatFormatting.DARK_AQUA));
        if (stack.hasTag() && stack.getTag().contains(RIFLE)) {
            int rounds = stack.getTag().getCompound(RIFLE).getCompound("tag").getInt("GunCurrentAmmoCount");
            tip.add(Component.literal("Packed rifle: " + rounds + " in the magazine").withStyle(ChatFormatting.DARK_GRAY));
        }
    }
}
