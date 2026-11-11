package recrafted.mission;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import recrafted.npc.NpcEntity;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

/** What happens when the player hits, stabs, garrotes, injects or throws things at an NPC. */
public final class Combat {
    private Combat() {}

    private static void msg(ServerPlayer p, String text, ChatFormatting col) {
        p.displayClientMessage(Component.literal(text).withStyle(col), true);
    }

    public static void melee(ServerPlayer player, NpcEntity npc) {
        if (npc.isDown()) return;
        if (player.getAttackStrengthScale(0.5f) < 0.85f) return;
        ServerLevel level = (ServerLevel) npc.level();
        ItemStack held = player.getMainHandItem();
        PropType type = PropItem.typeOf(held);
        boolean behind = npc.isBehind(player);
        boolean unaware = !npc.inCombat() && (behind || !npc.canSeePlayer(player));
        player.resetAttackStrengthTicker();

        if (type != null && type.kind == PropType.Kind.WIRE) {
            if (behind && !npc.inCombat()) {
                level.playSound(null, npc.blockPosition(), SoundEvents.LEASH_KNOT_PLACE, SoundSource.PLAYERS, 0.6f, 0.6f);
                npc.kill(player, false);
                msg(player, "Garrotted", ChatFormatting.DARK_RED);
            } else {
                msg(player, "The wire only works from behind", ChatFormatting.YELLOW);
                npc.addSuspicion(player, 1f);
                npc.onCompromised(player);
                return;
            }
        } else if (type != null && type.kind == PropType.Kind.SHARP) {
            if (unaware || !npc.getRole().guard) {
                level.playSound(null, npc.blockPosition(), SoundEvents.PLAYER_ATTACK_CRIT, SoundSource.PLAYERS, 0.8f, 0.9f);
                npc.kill(player, false);
            } else {
                npc.hurt(player.damageSources().playerAttack(player), 9f);
            }
        } else if (type != null && type.kind == PropType.Kind.BLUNT) {
            if (unaware || !npc.inCombat() || level.random.nextFloat() < 0.45f) {
                level.playSound(null, npc.blockPosition(), SoundEvents.PLAYER_ATTACK_KNOCKBACK, SoundSource.PLAYERS, 0.9f, 0.7f);
                npc.knockOut(player);
            } else {
                npc.hurt(player.damageSources().playerAttack(player), 6f);
            }
            if (type.breaks()) {
                level.playSound(null, npc.blockPosition(), SoundEvents.GLASS_BREAK, SoundSource.PLAYERS, 0.8f, 1.1f);
                level.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, held), npc.getX(), npc.getEyeY(), npc.getZ(), 8, .1, .1, .1, .05);
                held.shrink(1);
            }
        } else {
            if (unaware && behind) {
                level.playSound(null, npc.blockPosition(), SoundEvents.PLAYER_ATTACK_WEAK, SoundSource.PLAYERS, 0.7f, 0.6f);
                npc.knockOut(player);
                msg(player, "Subdued", ChatFormatting.GRAY);
            } else {
                npc.hurt(player.damageSources().playerAttack(player), 3f);
                return;
            }
        }
        Awareness.crime(level, player, npc);
    }

    public static void inject(ServerPlayer player, NpcEntity npc, ItemStack held, PropType type) {
        ServerLevel level = (ServerLevel) npc.level();
        if (npc.inCombat() || (!npc.isBehind(player) && npc.canSeePlayer(player))) {
            msg(player, "They are looking right at you", ChatFormatting.YELLOW);
            npc.addSuspicion(player, 0.6f);
            return;
        }
        if (!player.isCreative()) held.shrink(1);
        level.playSound(null, npc.blockPosition(), SoundEvents.BEE_STING, SoundSource.PLAYERS, 0.5f, 1.3f);
        if (type.kind == PropType.Kind.SEDATIVE) {
            npc.knockOut(player);
            msg(player, "Sedated", ChatFormatting.GRAY);
        } else {
            npc.kill(player, false);
            msg(player, "Injected", ChatFormatting.DARK_RED);
        }
        Awareness.crime(level, player, npc);
    }

    public static void thrownHit(ServerPlayer player, NpcEntity npc, PropType type) {
        if (npc.isDown()) return;
        ServerLevel level = (ServerLevel) npc.level();
        if (type.kind == PropType.Kind.SHARP) {
            npc.kill(player, false);
        } else if (type.kind == PropType.Kind.BLUNT) {
            npc.knockOut(player);
        } else {
            npc.addSuspicion(player, 0.5f);
            return;
        }
        level.playSound(null, npc.blockPosition(), SoundEvents.PLAYER_ATTACK_KNOCKBACK, SoundSource.PLAYERS, 0.9f, 0.8f);
        Awareness.crime(level, player, npc);
    }
}
