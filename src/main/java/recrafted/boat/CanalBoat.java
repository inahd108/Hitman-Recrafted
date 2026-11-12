package recrafted.boat;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import recrafted.ModRegistry;
import recrafted.mission.Mission;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * A canal boat on a fixed water route. It moves itself (no physics), stops at named moorings, waits at the
 * drawbridge and the lock for the keeper, and keeps its distance from the boat in front. People ride it as
 * passengers, each on a seat of the design.
 */
public class CanalBoat extends Entity {
    private static final EntityDataAccessor<String> DESIGN = SynchedEntityData.defineId(CanalBoat.class, EntityDataSerializers.STRING);
    private static final double CRUISE = 0.12, SLOW = 0.045;

    public String name = "";
    public int missionGen = -1;
    private int index, waitLeft, holdTicks;
    private boolean atPoint, horned;
    @Nullable private Mission.BoatDef def;
    private final Map<UUID, Integer> seatOf = new HashMap<>();
    @Nullable private CanalBoat blocker;
    // client smoothing
    private int lerpSteps;
    private double lerpX, lerpY, lerpZ, lerpYaw;

    public CanalBoat(EntityType<? extends CanalBoat> type, Level level) {
        super(type, level);
        noPhysics = true;
        setNoGravity(true);
    }

    public static CanalBoat create(ServerLevel level, Mission.BoatDef def, int gen) {
        CanalBoat b = new CanalBoat(ModRegistry.CANAL_BOAT.get(), level);
        b.name = def.name();
        b.def = def;
        b.missionGen = gen;
        b.entityData.set(DESIGN, def.design());
        Mission.BoatPoint p0 = def.route().get(0), p1 = def.route().get(def.route().size() > 1 ? 1 : 0);
        float yaw = (float) Math.toDegrees(Math.atan2(-(p1.x() - p0.x()), p1.z() - p0.z()));
        b.moveTo(p0.x(), def.y(), p0.z(), yaw, 0);
        if (!p0.stop().isEmpty()) {          // starts tied up at its first mooring
            b.index = 0;
            b.atPoint = true;
            b.waitLeft = p0.waitTicks();
        } else {
            b.index = def.route().size() > 1 ? 1 : 0;
        }
        return b;
    }

    public BoatDesign design() {
        return BoatDesign.byName(entityData.get(DESIGN));
    }

    @Override
    protected void defineSynchedData() {
        entityData.define(DESIGN, "zwaluw");
    }

    // ---- finding boats -------------------------------------------------------------------------
    @Nullable
    public static CanalBoat find(Level level, String name, Vec3 near, double radius) {
        CanalBoat best = null;
        for (CanalBoat b : level.getEntitiesOfClass(CanalBoat.class, new AABB(near, near).inflate(radius))) {
            if (b.name.equals(name) && (best == null || b.distanceToSqr(near) < best.distanceToSqr(near))) best = b;
        }
        return best;
    }

    /** Tied up at the named mooring (or at any mooring if the name is empty). */
    public boolean isMoored(String stop) {
        if (def == null || !atPoint || waitLeft < 0) return false;
        Mission.BoatPoint p = def.route().get(index);
        return !p.stop().isEmpty() && (stop.isEmpty() || p.stop().equals(stop));
    }

    // ---- movement --------------------------------------------------------------------------------
    @Override
    public void tick() {
        xo = getX(); yo = getY(); zo = getZ();
        yRotO = getYRot();
        super.tick();
        if (level().isClientSide) {
            tickLerp();
            return;
        }
        if (def == null) {
            Mission m = Mission.forDimension(level().dimension());
            def = m == null ? null : m.boat(name);
            if (def == null || def.route().isEmpty()) return;
            index = Mth.clamp(index, 0, def.route().size() - 1);
        }
        List<Mission.BoatPoint> route = def.route();
        Mission.BoatPoint p = route.get(index);
        if (atPoint) {
            if (!p.gate().isEmpty()) {
                if (!horned && p.gate().equals("drawbridge")) {
                    horned = true;
                    horn();
                }
                if (Waterways.request((ServerLevel) level(), p.gate())) next();
            } else if (waitLeft > 0) {
                waitLeft--;
            } else if (holdSatisfied(p)) {
                next();
            }
            setDeltaMovement(Vec3.ZERO);
            return;
        }
        double dx = p.x() - getX(), dz = p.z() - getZ();
        double dist = Math.sqrt(dx * dx + dz * dz);
        boolean slowDown = !p.stop().isEmpty() || !p.gate().isEmpty();
        double speed = slowDown ? Mth.clamp(dist * 0.03, SLOW, CRUISE) : CRUISE;
        if (blocked()) speed = 0;
        if (dist <= Math.max(speed, 0.02)) {
            setPos(p.x(), getY(), p.z());
            arrive(p);
        } else if (speed > 0) {
            setPos(getX() + dx / dist * speed, getY(), getZ() + dz / dist * speed);
            float want = (float) Math.toDegrees(Math.atan2(-dx, dz));
            setYRot(getYRot() + Mth.clamp(Mth.wrapDegrees(want - getYRot()), -2.5f, 2.5f));
        }
        if (tickCount % 120 == 0 && speed > 0) {
            level().playSound(null, getX(), getY(), getZ(), SoundEvents.BOAT_PADDLE_WATER, SoundSource.NEUTRAL, 0.35f, 0.6f);
        }
    }

    private void arrive(Mission.BoatPoint p) {
        if (p.gate().isEmpty() && p.stop().isEmpty()) {
            next();
            return;
        }
        atPoint = true;
        horned = false;
        waitLeft = p.waitTicks();
        holdTicks = 0;
    }

    private void next() {
        atPoint = false;
        waitLeft = 0;
        index = (index + 1) % def.route().size();
    }

    /** A mooring that waits for somebody stays until they are aboard, gone down, busy elsewhere, or two minutes pass. */
    private boolean holdSatisfied(Mission.BoatPoint p) {
        if (p.hold().isEmpty()) return true;
        if (++holdTicks > 2400) return true;
        for (NpcEntity n : level().getEntitiesOfClass(NpcEntity.class, getBoundingBox().inflate(64, 16, 64), e -> p.hold().equals(e.contractId))) {
            return n.getVehicle() == this || n.isDown() || n.getState() != NpcEntity.State.CALM;
        }
        return true;
    }

    /** Another boat right ahead in the same lane: hold back (the lower id goes first if two block each other). */
    private boolean blocked() {
        double yaw = Math.toRadians(getYRot());
        double fx = -Math.sin(yaw), fz = Math.cos(yaw);
        blocker = null;
        for (CanalBoat o : level().getEntitiesOfClass(CanalBoat.class, getBoundingBox().inflate(16, 2, 16), b -> b != this)) {
            double rx = o.getX() - getX(), rz = o.getZ() - getZ();
            double along = rx * fx + rz * fz, across = Math.abs(rx * fz - rz * fx);
            if (along > 0 && along < 13 && across < 4.5) {
                if (o.blocker == this && getId() < o.getId()) continue;
                blocker = o;
                return true;
            }
        }
        return false;
    }

    public void horn() {
        for (int i = 0; i < 2; i++) {
            final int k = i;
            ((ServerLevel) level()).getServer().tell(new net.minecraft.server.TickTask(((ServerLevel) level()).getServer().getTickCount() + k * 14,
                    () -> level().playSound(null, getX(), getY() + 1, getZ(), SoundEvents.NOTE_BLOCK_DIDGERIDOO.value(), SoundSource.NEUTRAL, 2.5f, 0.75f)));
        }
    }

    // ---- client smoothing ----------------------------------------------------------------------
    @Override
    public void lerpTo(double x, double y, double z, float yRot, float xRot, int steps, boolean teleport) {
        lerpX = x; lerpY = y; lerpZ = z; lerpYaw = yRot;
        lerpSteps = teleport ? 1 : 3;
    }

    private void tickLerp() {
        if (lerpSteps <= 0) return;
        double x = getX() + (lerpX - getX()) / lerpSteps;
        double y = getY() + (lerpY - getY()) / lerpSteps;
        double z = getZ() + (lerpZ - getZ()) / lerpSteps;
        setYRot(getYRot() + (float) Mth.wrapDegrees(lerpYaw - getYRot()) / lerpSteps);
        lerpSteps--;
        setPos(x, y, z);
    }

    // ---- passengers ----------------------------------------------------------------------------
    @Override
    protected boolean canAddPassenger(Entity e) {
        return getPassengers().size() < design().seats.length;
    }

    @Override
    protected void addPassenger(Entity e) {
        super.addPassenger(e);
        BoatDesign.Seat[] seats = design().seats;
        boolean helm = e instanceof NpcEntity n && n.getRole() == NpcRole.SKIPPER;
        boolean vip = e instanceof NpcEntity n && n.isTarget();
        int pick = -1;
        for (int i = 0; i < seats.length && pick < 0; i++) {
            if (seatOf.containsValue(i)) continue;
            if (helm == seats[i].helm() && (!vip || i == 1 || seats.length < 2)) pick = i;
        }
        for (int i = 0; i < seats.length && pick < 0; i++) if (!seatOf.containsValue(i) && !seats[i].helm()) pick = i;
        for (int i = 0; i < seats.length && pick < 0; i++) if (!seatOf.containsValue(i)) pick = i;
        seatOf.put(e.getUUID(), Math.max(0, pick));
    }

    @Override
    protected void removePassenger(Entity e) {
        super.removePassenger(e);
        seatOf.remove(e.getUUID());
    }

    public BoatDesign.Seat seatOf(Entity e) {
        BoatDesign.Seat[] seats = design().seats;
        Integer i = seatOf.get(e.getUUID());
        if (i == null) {
            int k = getPassengers().indexOf(e);
            i = Math.max(0, k);
        }
        return seats[Math.min(i, seats.length - 1)];
    }

    /** A local offset (x across, z towards the bow) in world space. */
    public Vec3 local(double lx, double ly, double lz) {
        double yaw = Math.toRadians(getYRot());
        double c = Math.cos(yaw), s = Math.sin(yaw);
        return new Vec3(getX() + lx * c - lz * s, getY() + ly, getZ() + lx * s + lz * c);
    }

    @Override
    protected void positionRider(Entity e, MoveFunction move) {
        if (!hasPassenger(e)) return;
        BoatDesign.Seat seat = seatOf(e);
        Vec3 at = local(seat.x(), seat.y(), seat.z());
        move.accept(e, at.x, at.y, at.z);
        if (e instanceof NpcEntity n) {
            float yaw = getYRot() + seat.yaw();
            n.setYBodyRot(yaw);
            if (level().isClientSide || n.tickCount % 10 == 0) n.setYHeadRot(yaw);
        }
    }

    @Override
    public boolean shouldRiderSit() {
        return design().seated;
    }

    @Override
    public Vec3 getDismountLocationForPassenger(LivingEntity rider) {
        BlockPos c = blockPosition();
        Vec3 best = null;
        double bd = Double.MAX_VALUE;
        for (BlockPos q : BlockPos.betweenClosed(c.offset(-7, -1, -7), c.offset(7, 3, 7))) {
            if (!level().getBlockState(q.below()).isFaceSturdy(level(), q.below(), net.minecraft.core.Direction.UP)) continue;
            if (!level().getBlockState(q).getCollisionShape(level(), q).isEmpty() || !level().getFluidState(q).isEmpty()) continue;
            if (!level().getBlockState(q.above()).getCollisionShape(level(), q.above()).isEmpty()) continue;
            double d = q.distToCenterSqr(position());
            if (d < bd) {
                bd = d;
                best = Vec3.atBottomCenterOf(q);
            }
        }
        return best != null ? best : super.getDismountLocationForPassenger(rider);
    }

    @Override
    public InteractionResult interact(Player p, InteractionHand hand) {
        if (hasPassenger(p) && name.equals("zwaluw")) {          // leave the city aboard Kooistra's boat
            if (!level().isClientSide && p instanceof net.minecraft.server.level.ServerPlayer sp) {
                recrafted.mission.MissionManager.tryExit((ServerLevel) level(), sp);
            }
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if (p.isSecondaryUseActive() || hasPassenger(p)) return InteractionResult.PASS;
        if (!level().isClientSide) {
            if (!canAddPassenger(p)) return InteractionResult.FAIL;
            p.startRiding(this);
        }
        return InteractionResult.sidedSuccess(level().isClientSide);
    }

    @Override public boolean isPickable() { return !isRemoved(); }
    @Override public boolean isPushable() { return false; }
    @Override public boolean canBeCollidedWith() { return false; }
    @Override public boolean hurt(DamageSource src, float amount) { return false; }
    @Override public boolean isInvulnerable() { return true; }

    // ---- persistence -----------------------------------------------------------------------------
    @Override
    protected void readAdditionalSaveData(CompoundTag t) {
        name = t.getString("Name");
        entityData.set(DESIGN, t.getString("Design"));
        missionGen = t.contains("Gen") ? t.getInt("Gen") : -1;
        index = t.getInt("Index");
        waitLeft = t.getInt("Wait");
        atPoint = t.getBoolean("AtPoint");
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag t) {
        t.putString("Name", name);
        t.putString("Design", entityData.get(DESIGN));
        t.putInt("Gen", missionGen);
        t.putInt("Index", index);
        t.putInt("Wait", waitLeft);
        t.putBoolean("AtPoint", atPoint);
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return new ClientboundAddEntityPacket(this);
    }
}
