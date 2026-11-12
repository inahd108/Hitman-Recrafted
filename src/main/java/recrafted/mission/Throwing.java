package recrafted.mission;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import recrafted.compat.Guns;
import recrafted.entity.ThrownPropEntity;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

import javax.annotation.Nullable;

/** Throwing things: props on right-click, and anything throwable (guns too) with the Throw key. */
public final class Throwing {
    private Throwing() {}

    /** What a thrown stack does to whoever it hits, or null if it only makes a noise. */
    @Nullable
    public static PropType.Kind impact(ItemStack stack) {
        if (Guns.isGun(stack)) return PropType.Kind.BLUNT;
        PropType t = PropItem.typeOf(stack);
        return t == null ? null : t.kind;
    }

    public static boolean canThrow(ItemStack stack) {
        if (Guns.isGun(stack)) return true;
        PropType t = PropItem.typeOf(stack);
        return t != null && t.throwable();
    }

    /** Launches one of the stack from the player's eyes. Server side only. */
    public static void launch(Player player, ItemStack one, float speed) {
        Level level = player.level();
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.SNOWBALL_THROW, SoundSource.PLAYERS,
                0.5f, 0.5f / (level.getRandom().nextFloat() * 0.4f + 0.8f));
        ThrownPropEntity thrown = new ThrownPropEntity(level, player);
        thrown.setItem(one);
        thrown.shootFromRotation(player, player.getXRot(), player.getYRot(), 0f, speed, 0.6f);
        level.addFreshEntity(thrown);
    }

    /** The Throw key: throws whatever throwable thing is in the main hand. */
    public static void throwHeld(ServerPlayer p) {
        if (p.isSpectator() || p.getCooldowns().isOnCooldown(p.getMainHandItem().getItem())) return;
        ItemStack held = p.getMainHandItem();
        if (held.isEmpty()) return;
        if (!canThrow(held)) {
            p.displayClientMessage(Component.literal("You can't throw that"), true);
            return;
        }
        boolean gun = Guns.isGun(held);
        PropType t = PropItem.typeOf(held);
        net.minecraft.world.item.Item item = held.getItem();
        launch(p, held.copyWithCount(1), gun ? 1.2f : t != null && t.kind == PropType.Kind.COIN ? 1.1f : 1.3f);
        if (!p.getAbilities().instabuild || gun) {
            held.shrink(1);
            if (held.isEmpty()) p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        }
        p.getCooldowns().addCooldown(item, 12);
    }

    /** Thrown guns belong to the running contract, so a restart tidies them away. */
    public static int genFor(ServerLevel level, ItemStack stack) {
        if (!Guns.isGun(stack)) return -1;
        MissionState st = MissionState.get(level);
        return st.active ? st.gen : -1;
    }
}
