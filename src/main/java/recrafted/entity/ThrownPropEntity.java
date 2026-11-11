package recrafted.entity;

import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;
import recrafted.ModRegistry;
import recrafted.mission.Awareness;
import recrafted.mission.Combat;
import recrafted.npc.NpcEntity;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

/** A prop in flight. Lands as a pickup again, makes noise, and hurts whoever it hits. */
public class ThrownPropEntity extends ThrowableItemProjectile {
    public ThrownPropEntity(EntityType<? extends ThrownPropEntity> type, Level level) {
        super(type, level);
    }

    public ThrownPropEntity(Level level, LivingEntity owner) {
        super(ModRegistry.THROWN_PROP.get(), owner, level);
    }

    @Override
    protected Item getDefaultItem() {
        return ModRegistry.prop(PropType.COIN);
    }

    @Override
    protected void onHitEntity(EntityHitResult hit) {
        super.onHitEntity(hit);
        if (level().isClientSide) return;
        PropType type = PropItem.typeOf(getItem());
        if (hit.getEntity() instanceof NpcEntity npc && type != null && getOwner() instanceof ServerPlayer sp) {
            Combat.thrownHit(sp, npc, type);
        }
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (!(level() instanceof ServerLevel sl)) return;
        ItemStack stack = getItem();
        PropType type = PropItem.typeOf(stack);
        Vec3 at = hit.getLocation();
        ServerPlayer owner = getOwner() instanceof ServerPlayer sp ? sp : null;
        if (type != null && type.breaks()) {
            sl.playSound(null, at.x, at.y, at.z, SoundEvents.GLASS_BREAK, SoundSource.NEUTRAL, 1f, 1.1f);
            sl.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, stack), at.x, at.y, at.z, 10, .1, .1, .1, .08);
            Awareness.noise(sl, at, 12, 2, owner);
        } else {
            sl.playSound(null, at.x, at.y, at.z,
                    type != null && type.kind == PropType.Kind.COIN ? SoundEvents.CHAIN_PLACE : SoundEvents.ANVIL_LAND,
                    SoundSource.NEUTRAL, type != null && type.kind == PropType.Kind.COIN ? 1.2f : 0.35f, 1.5f);
            PropEntity drop = new PropEntity(sl, at.x, at.y + 0.05, at.z, stack);
            if (hit.getType() == HitResult.Type.BLOCK) {
                Vec3 back = getDeltaMovement().normalize().scale(-0.25);
                drop.setPos(at.x + back.x, at.y + Math.max(0.05, back.y), at.z + back.z);
            }
            sl.addFreshEntity(drop);
            if (type != null && type.kind == PropType.Kind.RADIO) drop.startLure(20 * 18);
            else Awareness.noise(sl, at, 10, type != null && type.kind == PropType.Kind.COIN ? 1 : 2, owner);
        }
        discard();
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
