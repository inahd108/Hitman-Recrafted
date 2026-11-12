package recrafted.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.NetworkHooks;
import recrafted.ModRegistry;
import recrafted.mission.Awareness;

import java.util.ArrayList;
import java.util.List;

/** A prop lying in the world. It never despawns and is picked up with a right-click. */
public class PropEntity extends Entity {
    private static final EntityDataAccessor<ItemStack> ITEM = SynchedEntityData.defineId(PropEntity.class, EntityDataSerializers.ITEM_STACK);
    private static final EntityDataAccessor<Boolean> PLAYING = SynchedEntityData.defineId(PropEntity.class, EntityDataSerializers.BOOLEAN);

    public int missionGen = -1;
    private int lureTicks;
    /** Picked up together with the main item (a dropped gun's spare ammo). Server side only. */
    private final List<ItemStack> extras = new ArrayList<>();

    public PropEntity(EntityType<? extends PropEntity> type, Level level) {
        super(type, level);
    }

    public PropEntity(Level level, double x, double y, double z, ItemStack stack) {
        this(ModRegistry.PROP.get(), level);
        setPos(x, y, z);
        setItem(stack);
        setYRot(level.random.nextFloat() * 360f);
    }

    @Override
    protected void defineSynchedData() {
        entityData.define(ITEM, ItemStack.EMPTY);
        entityData.define(PLAYING, false);
    }

    public ItemStack getItem() { return entityData.get(ITEM); }
    public void setItem(ItemStack s) { entityData.set(ITEM, s.copy()); }
    public boolean isPlaying() { return entityData.get(PLAYING); }
    public void addExtra(ItemStack s) { if (!s.isEmpty()) extras.add(s.copy()); }
    public List<ItemStack> getExtras() { return extras; }

    /** Makes this prop a noise source for a while (thrown radio). */
    public void startLure(int ticks) {
        lureTicks = ticks;
        entityData.set(PLAYING, true);
    }

    @Override
    public void tick() {
        super.tick();
        if (!isNoGravity()) setDeltaMovement(getDeltaMovement().add(0, -0.04, 0));
        if (!onGround() || getDeltaMovement().horizontalDistanceSqr() > 1e-5 || tickCount % 20 == 0) {
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().multiply(0.6, 0.98, 0.6));
            if (onGround()) setDeltaMovement(getDeltaMovement().multiply(1, 0, 1));
        }
        if (level() instanceof ServerLevel sl && lureTicks > 0) {
            lureTicks--;
            if (lureTicks % 40 == 0) {
                sl.playSound(null, blockPosition(), SoundEvents.NOTE_BLOCK_HARP.get(), SoundSource.RECORDS, 1.5f,
                        0.7f + random.nextFloat() * 0.8f);
                sl.sendParticles(ParticleTypes.NOTE, getX(), getY() + 0.6, getZ(), 1, 0, 0, 0, 1);
                Awareness.noise(sl, position(), 12, 2, null);
            }
            if (lureTicks == 0) entityData.set(PLAYING, false);
        }
    }

    @Override
    public InteractionResult interact(Player player, InteractionHand hand) {
        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
        if (level().isClientSide) return InteractionResult.SUCCESS;
        ItemStack s = getItem();
        if (!s.isEmpty()) {
            if (player.getMainHandItem().isEmpty()) player.setItemInHand(InteractionHand.MAIN_HAND, s.copy());
            else if (!player.getInventory().add(s.copy())) return InteractionResult.FAIL;
            for (ItemStack extra : extras) {
                ItemStack copy = extra.copy();
                if (!player.getInventory().add(copy) && !copy.isEmpty()) player.drop(copy, false);
            }
            level().playSound(null, blockPosition(), SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 0.3f, 1.4f);
        }
        discard();
        return InteractionResult.CONSUME;
    }

    @Override public boolean isPickable() { return true; }
    @Override public boolean hurt(DamageSource src, float amount) { return false; }
    @Override public boolean isAttackable() { return false; }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        setItem(ItemStack.of(tag.getCompound("Item")));
        missionGen = tag.contains("Gen") ? tag.getInt("Gen") : -1;
        lureTicks = tag.getInt("Lure");
        extras.clear();
        ListTag list = tag.getList("Extras", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) addExtra(ItemStack.of(list.getCompound(i)));
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        tag.put("Item", getItem().save(new CompoundTag()));
        tag.putInt("Gen", missionGen);
        tag.putInt("Lure", lureTicks);
        if (!extras.isEmpty()) {
            ListTag list = new ListTag();
            for (ItemStack e : extras) list.add(e.save(new CompoundTag()));
            tag.put("Extras", list);
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
