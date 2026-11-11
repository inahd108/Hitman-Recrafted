package recrafted.npc;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.OpenDoorGoal;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.Vec3;
import recrafted.ModRegistry;
import recrafted.block.ConsumableBlock;
import recrafted.block.DoorTimers;
import recrafted.block.FuseBoxBlock;
import recrafted.block.Poison;
import recrafted.client.ClientState;
import recrafted.item.CastingCardItem;
import recrafted.item.RoutePlannerItem;
import recrafted.mission.Awareness;
import recrafted.mission.Combat;
import recrafted.mission.MissionManager;
import recrafted.mission.PlayerData;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;

import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * A townsperson, guard or target. Follows a hand-authored {@link Route}, watches the player,
 * and reacts to crimes, bodies, noise and poison.
 */
public class NpcEntity extends PathfinderMob {
    public enum State {
        CALM, INVESTIGATE, ALERT, SEARCH, FLEE, SICK, UNCONSCIOUS, DEAD;
        public static State of(int i) { return i >= 0 && i < values().length ? values()[i] : CALM; }
    }

    private static final EntityDataAccessor<String> ROLE = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.STRING);
    private static final EntityDataAccessor<Integer> SKIN = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Byte> ANIM = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Byte> STATE = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Byte> FLAGS = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Float> SUSPICION = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<String> SPEECH = SynchedEntityData.defineId(NpcEntity.class, EntityDataSerializers.STRING);

    private static final int F_TARGET = 1, F_ENFORCER = 2, F_STRIPPED = 4;
    private static final double WALK = 0.55, BRISK = 0.8, RUN = 1.15;
    // diagnostics for the headless self-test
    public static int statArrivals, statUnsticks;
    public static final Map<String, Integer> UNSTICK_LOG = new java.util.TreeMap<>();

    // ---- authored data ---------------------------------------------------------
    private Route route = new Route();
    public String contractId = "";
    public String followId = "";
    @Nullable public Vec3 sickSpot;
    public int missionGen = -1;
    /** Index into the mission's cast list, or -1 for NPCs made in the editor. */
    public int castIndex = -1;

    // ---- runtime ---------------------------------------------------------------
    private int routeIndex;
    private int routeDir = 1;
    private boolean waiting;
    private int waitLeft;
    private int stuckTicks;
    private Vec3 lastStuckPos = Vec3.ZERO;
    private int speechTicks;
    public boolean frozen;
    private final Map<UUID, Float> suspicion = new HashMap<>();
    @Nullable private Vec3 investigatePos;
    private int investigateTicks;
    private int investigateLook;
    @Nullable private UUID investigateBody;
    @Nullable private BlockPos repairPos;
    @Nullable private UUID alertTarget;
    @Nullable private Vec3 lastKnown;
    private long lastSeenTick;
    private int attackCooldown;
    private int stateTicks;
    private int poisonTicks;
    public boolean discovered;
    @Nullable private UUID draggedBy;
    @Nullable private NpcEntity leader;

    public NpcEntity(EntityType<? extends NpcEntity> type, Level level) {
        super(type, level);
        setPersistenceRequired();
        setCanPickUpLoot(false);
        if (getNavigation() instanceof GroundPathNavigation nav) {
            nav.setCanOpenDoors(true);
            nav.setCanPassDoors(true);
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 20)
                .add(Attributes.MOVEMENT_SPEED, 0.3)
                .add(Attributes.FOLLOW_RANGE, 64)
                .add(Attributes.ATTACK_DAMAGE, 5)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.3);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(ROLE, NpcRole.CIVILIAN.id);
        entityData.define(SKIN, 0);
        entityData.define(ANIM, (byte) 0);
        entityData.define(STATE, (byte) 0);
        entityData.define(FLAGS, (byte) 0);
        entityData.define(SUSPICION, 0f);
        entityData.define(SPEECH, "");
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new OpenDoorGoal(this, true));
    }

    // ---- accessors ---------------------------------------------------------------
    public NpcRole getRole() { return NpcRole.byId(entityData.get(ROLE)); }

    public void setRole(NpcRole role) {
        entityData.set(ROLE, role.id);
        setPathfindingMalus(BlockPathTypes.DOOR_IRON_CLOSED, role.opensSecurityDoors() ? 0f : -1f);
    }

    public int getSkin() { return entityData.get(SKIN); }
    public void setSkin(int v) { entityData.set(SKIN, Math.floorMod(v, Math.max(1, getRole().variants))); }
    public NpcPose getAnim() { return NpcPose.byOrdinal(entityData.get(ANIM)); }
    public void setAnim(NpcPose p) { if (getAnim() != p) entityData.set(ANIM, (byte) p.ordinal()); }
    public State getState() { return State.of(entityData.get(STATE)); }
    public boolean isDown() { State s = getState(); return s == State.UNCONSCIOUS || s == State.DEAD; }
    public boolean isDead() { return getState() == State.DEAD; }
    public boolean isTarget() { return (entityData.get(FLAGS) & F_TARGET) != 0; }
    public boolean isEnforcer() { return (entityData.get(FLAGS) & F_ENFORCER) != 0; }
    public boolean isStripped() { return (entityData.get(FLAGS) & F_STRIPPED) != 0; }
    public void setTarget(boolean b) { flag(F_TARGET, b); }
    public void setEnforcer(boolean b) { flag(F_ENFORCER, b); }
    public float getSuspicionLevel() { return entityData.get(SUSPICION); }
    public String getSpeech() { return entityData.get(SPEECH); }
    public Route getRoute() { return route; }
    public boolean inCombat() { return getState() == State.ALERT; }
    @Nullable public UUID getDraggedBy() { return draggedBy; }

    private void flag(int f, boolean on) {
        byte b = entityData.get(FLAGS);
        entityData.set(FLAGS, (byte) (on ? b | f : b & ~f));
    }

    private void setState(State s) {
        if (getState() != s) {
            entityData.set(STATE, (byte) s.ordinal());
            stateTicks = 0;
        }
    }

    public void setRoute(Route r) {
        route = r;
        routeIndex = Mth.clamp(routeIndex, 0, Math.max(0, r.points.size() - 1));
        routeDir = 1;
        waiting = false;
    }

    /** Puts the NPC back on its first waypoint (editor preview). */
    public void restartRoute() {
        routeIndex = 0;
        routeDir = 1;
        waiting = false;
        if (!route.isEmpty()) {
            Waypoint w = route.points.get(0);
            teleportTo(w.x, w.y, w.z);
        }
        getNavigation().stop();
    }

    public void say(String text, int ticks) {
        entityData.set(SPEECH, text);
        speechTicks = ticks;
    }

    public float suspicionOf(Player p) {
        return suspicion.getOrDefault(p.getUUID(), 0f);
    }

    public void addSuspicion(Player p, float amount) {
        suspicion.merge(p.getUUID(), amount, (a, b) -> Math.min(1f, a + b));
    }

    // ---- vanilla hooks -------------------------------------------------------------
    @Override public boolean removeWhenFarAway(double d) { return false; }
    @Override public boolean isPushable() { return !isDown() && !(waiting && getState() == State.CALM) && super.isPushable(); }
    @Override protected boolean isImmobile() { return super.isImmobile() || isDown(); }

    /** Townspeople slip past each other instead of shoving: no deadlocks in alleys and doorways. */
    @Override
    public void push(Entity other) {
        if (other instanceof NpcEntity) return;
        super.push(other);
    }
    @Override public boolean shouldDropExperience() { return false; }
    @Override protected boolean shouldDropLoot() { return false; }
    @Override @Nullable protected SoundEvent getAmbientSound() { return null; }
    @Override protected SoundEvent getHurtSound(DamageSource s) { return SoundEvents.PLAYER_HURT; }
    @Override public boolean canBeLeashed(Player p) { return false; }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return isDown() ? EntityDimensions.scalable(1.1f, 0.45f) : super.getDimensions(pose);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (STATE.equals(key)) refreshDimensions();
    }

    @Override
    public boolean isCurrentlyGlowing() {
        if (level().isClientSide) return ClientState.shouldGlow(this) || super.isCurrentlyGlowing();
        return super.isCurrentlyGlowing();
    }

    @Override
    public int getTeamColor() {
        if (level().isClientSide) return ClientState.glowColor(this);
        return super.getTeamColor();
    }

    @Override
    public boolean isCustomNameVisible() {
        return isTarget() && !isDown();
    }

    // ---- main loop -------------------------------------------------------------------
    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;
        if (isDown()) tickDown();
    }

    @Override
    protected void customServerAiStep() {
        stateTicks++;
        if (speechTicks > 0 && --speechTicks == 0) entityData.set(SPEECH, "");
        if (attackCooldown > 0) attackCooldown--;
        if (frozen) {
            getNavigation().stop();
            return;
        }
        if (poisonTicks > 0 && --poisonTicks == 0) {
            kill(null, true);
            return;
        }
        if ((tickCount + getId()) % 5 == 0) perceive();
        switch (getState()) {
            case CALM -> tickRoutine();
            case INVESTIGATE -> tickInvestigate();
            case ALERT -> tickAlert();
            case SEARCH -> tickSearch();
            case FLEE -> tickFlee();
            case SICK -> tickSick();
            default -> { }
        }
        if (tickCount % 4 == 0 && getRole().opensSecurityDoors() && !getNavigation().isDone()) openSecurityDoors();
        updateHeldItem();
    }

    private void openSecurityDoors() {
        ServerLevel sl = (ServerLevel) level();
        BlockPos base = blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(base.offset(-1, 0, -1), base.offset(1, 0, 1))) {
            BlockState s = sl.getBlockState(p);
            if (DoorTimers.isSecurityDoor(s) && !s.getValue(DoorBlock.OPEN)) DoorTimers.open(sl, p, 50);
        }
    }

    private void updateHeldItem() {
        if (tickCount % 10 != 0) return;
        ItemStack want = ItemStack.EMPTY;
        if (getState() == State.CALM && waiting) {
            want = switch (getAnim()) {
                case SWEEP -> new ItemStack(ModRegistry.prop(PropType.BROOM));
                case DRINK -> new ItemStack(Items.GLASS_BOTTLE);
                case EAT -> new ItemStack(Items.BREAD);
                case WORK -> switch (getRole()) {
                    case COOK -> new ItemStack(ModRegistry.prop(PropType.FRYING_PAN));
                    case GARDENER -> new ItemStack(ModRegistry.prop(PropType.GARDEN_SHEARS));
                    case WORKER -> new ItemStack(ModRegistry.prop(PropType.WRENCH));
                    case FISHERMAN -> new ItemStack(ModRegistry.prop(PropType.FISHING_GAFF));
                    default -> ItemStack.EMPTY;
                };
                case TYPE -> getRole() == NpcRole.SCIENTIST || getRole() == NpcRole.VARGA ? ItemStack.EMPTY : new ItemStack(Items.PAPER);
                default -> ItemStack.EMPTY;
            };
        } else if (getState() == State.ALERT && getRole().guard) {
            want = new ItemStack(ModRegistry.prop(PropType.BATON));
        }
        if (!ItemStack.isSameItem(want, getMainHandItem())) setItemSlot(EquipmentSlot.MAINHAND, want);
    }

    // ---- routine ---------------------------------------------------------------------
    private void tickRoutine() {
        setSprinting(false);
        if (!followId.isEmpty()) {
            tickFollow();
            return;
        }
        if (route.isEmpty()) {
            setAnim(NpcPose.STAND);
            return;
        }
        routeIndex = Mth.clamp(routeIndex, 0, route.points.size() - 1);
        Waypoint wp = route.points.get(routeIndex);
        if (waiting) {
            getNavigation().stop();
            if (wp.hasYaw()) faceYaw(wp.yaw);
            setAnim(wp.pose);
            if (wp.pose == NpcPose.LOOK && tickCount % 60 == 0 && wp.hasYaw()) {
                faceYaw(wp.yaw + (random.nextFloat() - 0.5f) * 120f);
            }
            if (wp.pose == NpcPose.SMOKE && tickCount % 50 == 0) {
                ((ServerLevel) level()).sendParticles(ParticleTypes.SMOKE, getX(), getEyeY(), getZ(), 2, .05, .05, .05, .005);
            }
            if (--waitLeft <= 0) {
                waiting = false;
                advance();
            }
            return;
        }
        setAnim(NpcPose.STAND);
        double dx = wp.x - getX(), dz = wp.z - getZ(), dy = wp.y - getY();
        if (dx * dx + dz * dz < 0.55 && Math.abs(dy) < 1.8) {
            arrive(wp);
            return;
        }
        walkTo(wp.x, wp.y, wp.z, wp.run ? RUN : WALK);
        if (unstick(wp.pos())) arrive(wp);
    }

    /**
     * Paths to an exact spot. Vanilla navigation is happy to stop a block short, so the last
     * couple of steps are walked in a straight line.
     */
    private void walkTo(double x, double y, double z, double speed) {
        double dx = x - getX(), dz = z - getZ();
        boolean close = dx * dx + dz * dz < 1.4 && Math.abs(y - getY()) < 1.3;
        if (getNavigation().isDone()) {
            if (close) {
                getMoveControl().setWantedPosition(x, y, z, speed);
                return;
            }
            net.minecraft.world.level.pathfinder.Path path = getNavigation().createPath(BlockPos.containing(x, y, z), 0);
            if (path != null) getNavigation().moveTo(path, speed);
        } else if (tickCount % 40 == 0 && !close) {
            net.minecraft.world.level.pathfinder.Path path = getNavigation().createPath(BlockPos.containing(x, y, z), 0);
            if (path != null) getNavigation().moveTo(path, speed);
        }
    }

    /** Teleports to the goal if the NPC has made no progress for a while. Returns true if it jumped. */
    private boolean unstick(Vec3 goal) {
        if (tickCount % 20 != 0) return false;
        if (position().distanceToSqr(lastStuckPos) < 0.2) stuckTicks += 20;
        else stuckTicks = 0;
        lastStuckPos = position();
        if (stuckTicks >= 160) {
            stuckTicks = 0;
            if (level().isLoaded(BlockPos.containing(goal))) {
                statUnsticks++;
                if (UNSTICK_LOG.size() < 400) {
                    UNSTICK_LOG.merge(getName().getString() + " [" + getState() + " #" + routeIndex + "] " + blockPosition().toShortString()
                            + " -> " + BlockPos.containing(goal).toShortString(), 1, Integer::sum);
                }
                teleportTo(goal.x, goal.y, goal.z);
                getNavigation().stop();
                return true;
            }
        }
        return false;
    }

    private void arrive(Waypoint wp) {
        statArrivals++;
        getNavigation().stop();
        stuckTicks = 0;
        if (!wp.say.isEmpty()) say(wp.say, 90);
        if (wp.wait > 0) {
            waiting = true;
            waitLeft = wp.wait;
            if (wp.pose == NpcPose.SIT || wp.pose == NpcPose.SLEEP || wp.pose == NpcPose.EAT || wp.pose == NpcPose.DRINK) {
                setPos(wp.x, getY(), wp.z);
            }
            if (wp.hasYaw()) faceYaw(wp.yaw);
            if (wp.pose == NpcPose.EAT || wp.pose == NpcPose.DRINK) consumeNearby();
        } else {
            advance();
        }
    }

    private void advance() {
        int n = route.points.size();
        if (n <= 1) {
            waiting = true;
            waitLeft = n == 1 ? Math.max(200, route.points.get(0).wait) : 200;
            return;
        }
        switch (route.mode) {
            case LOOP -> routeIndex = (routeIndex + 1) % n;
            case PINGPONG -> {
                if (routeIndex + routeDir < 0 || routeIndex + routeDir >= n) routeDir = -routeDir;
                routeIndex += routeDir;
            }
            case ONCE -> {
                if (routeIndex < n - 1) routeIndex++;
                else {
                    waiting = true;
                    waitLeft = 20 * 60 * 60;
                }
            }
        }
    }

    private void faceYaw(float yaw) {
        setYRot(yaw);
        setYHeadRot(yaw);
        yBodyRot = yaw;
    }

    private void tickFollow() {
        if (leader == null || !leader.isAlive() || leader.isRemoved()) {
            leader = null;
            if (tickCount % 20 == 0) {
                for (NpcEntity e : level().getEntitiesOfClass(NpcEntity.class, getBoundingBox().inflate(48, 16, 48))) {
                    if (followId.equals(e.contractId)) { leader = e; break; }
                }
            }
            setAnim(NpcPose.GUARD);
            return;
        }
        if (leader.isDown()) {
            if (!leader.discovered) onBodyFound(leader);
            return;
        }
        double d = distanceTo(leader);
        if (d > 3.2) {
            setAnim(NpcPose.STAND);
            if (getNavigation().isDone() || tickCount % 15 == 0) getNavigation().moveTo(leader, d > 8 ? RUN : BRISK);
            if (d > 24 && tickCount % 40 == 0) teleportTo(leader.getX(), leader.getY(), leader.getZ());
        } else {
            getNavigation().stop();
            setAnim(NpcPose.GUARD);
            if (tickCount % 30 == 0) faceYaw(leader.getYRot() + (getId() % 2 == 0 ? 35 : -35));
        }
    }

    private void consumeNearby() {
        ServerLevel sl = (ServerLevel) level();
        BlockPos base = blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(base.offset(-2, -1, -2), base.offset(2, 2, 2))) {
            BlockState s = sl.getBlockState(p);
            if (s.getBlock() instanceof ConsumableBlock && s.getValue(ConsumableBlock.POISON) != Poison.NONE) {
                Poison poison = s.getValue(ConsumableBlock.POISON);
                MissionManager.setTracked(sl, p.immutable(), s.setValue(ConsumableBlock.POISON, Poison.NONE));
                if (poison == Poison.LETHAL) {
                    poisonTicks = 80;
                    say("That tastes... strange.", 70);
                } else {
                    becomeSick();
                }
                return;
            }
        }
    }

    public void becomeSick() {
        if (isDown()) return;
        setState(State.SICK);
        waiting = false;
        say("Ugh — excuse me —", 60);
        getNavigation().stop();
    }

    private void resumeRoutine() {
        setState(State.CALM);
        waiting = false;
        investigatePos = null;
        investigateBody = null;
        repairPos = null;
        alertTarget = null;
        setSprinting(false);
        getNavigation().stop();
    }

    // ---- perception --------------------------------------------------------------------
    public boolean canSee(Entity e, float range, float halfAngleDeg) {
        double d = distanceTo(e);
        if (d > range) return false;
        if (d > 1.8) {
            Vec3 look = Vec3.directionFromRotation(0, getYHeadRot());
            Vec3 to = new Vec3(e.getX() - getX(), 0, e.getZ() - getZ()).normalize();
            if (look.dot(to) < Math.cos(Math.toRadians(halfAngleDeg))) return false;
        }
        return hasLineOfSight(e);
    }

    public boolean canSeePlayer(Player p) {
        float range = getRole().visionRange() * (p.isCrouching() ? 0.65f : 1f);
        return canSee(p, range, 68f);
    }

    public boolean isBehind(Entity attacker) {
        Vec3 look = Vec3.directionFromRotation(0, yBodyRot);
        Vec3 to = new Vec3(attacker.getX() - getX(), 0, attacker.getZ() - getZ()).normalize();
        return look.dot(to) < -0.2;
    }

    private void perceive() {
        if (getState() == State.SICK) {
            entityData.set(SUSPICION, 0f);
            return;
        }
        ServerLevel sl = (ServerLevel) level();
        float max = 0;
        for (ServerPlayer p : sl.players()) {
            if (p.isSpectator() || p.isCreative() || !p.isAlive() || distanceToSqr(p) > 40 * 40) continue;
            float s = suspicion.getOrDefault(p.getUUID(), 0f);
            boolean sees = canSeePlayer(p);
            if (sees) {
                lastSeenTick = sl.getGameTime();
                if (alertTarget != null && alertTarget.equals(p.getUUID())) lastKnown = p.position();
                float rate = 0;
                double d = distanceTo(p);
                if (MissionManager.isHunted(p) && getRole().guard) {
                    rate = 1f;
                } else if (MissionManager.isDragging(sl, p)) {
                    rate = 1f;
                } else {
                    if (MissionManager.isTrespassing(p)) rate += getRole().guard ? 0.09f : 0.05f;
                    if (holdsIllegal(p)) rate += getRole().guard ? 0.08f : 0.05f;
                    if (seesThrough(p) && d < 9) rate += 0.03f;
                }
                if (rate > 0) s = Math.min(1f, s + rate * (d < 5 ? 1.5f : 1f));
                else s = Math.max(0f, s - 0.02f);
            } else {
                s = Math.max(0f, s - 0.012f);
            }
            if (s <= 0) suspicion.remove(p.getUUID());
            else suspicion.put(p.getUUID(), s);
            if (s >= 1f && getState() != State.ALERT && getState() != State.FLEE) onCompromised(p);
            max = Math.max(max, s);
        }
        entityData.set(SUSPICION, max);
        State st = getState();
        if (st == State.CALM || st == State.SEARCH || (st == State.INVESTIGATE && investigateBody == null)) {
            List<NpcEntity> bodies = sl.getEntitiesOfClass(NpcEntity.class, getBoundingBox().inflate(14, 5, 14),
                    e -> e != this && e.isDown() && !e.discovered);
            for (NpcEntity b : bodies) {
                if (canSee(b, 14f, 75f)) {
                    onBodyFound(b);
                    break;
                }
            }
        }
    }

    private boolean holdsIllegal(ServerPlayer p) {
        PropType t = PropItem.typeOf(p.getMainHandItem());
        if (t == null || !t.illegal()) return false;
        NpcRole worn = PlayerData.disguise(p);
        return worn == null || !worn.guard;
    }

    private boolean seesThrough(ServerPlayer p) {
        NpcRole worn = PlayerData.disguise(p);
        return worn != null && isEnforcer() && (worn == getRole() || (worn.guard && getRole() == NpcRole.BODYGUARD));
    }

    /** The NPC is now certain the player is up to no good. */
    public void onCompromised(ServerPlayer p) {
        if (isDown()) return;
        ServerLevel sl = (ServerLevel) level();
        suspicion.put(p.getUUID(), 1f);
        MissionManager.onSpotted(sl, p);
        waiting = false;
        if (getRole().guard) {
            setState(State.ALERT);
            alertTarget = p.getUUID();
            lastKnown = p.position();
            lastSeenTick = sl.getGameTime();
            say("Stop right there!", 60);
            Awareness.rallyGuards(sl, this, p, 18);
        } else {
            setState(State.FLEE);
            lastKnown = p.position();
            say("Help! Somebody!", 60);
            Awareness.rallyGuards(sl, this, p, 24);
        }
    }

    public void joinAlert(ServerPlayer p) {
        if (isDown() || !getRole().guard || getState() == State.ALERT) return;
        suspicion.put(p.getUUID(), 1f);
        waiting = false;
        setState(State.ALERT);
        alertTarget = p.getUUID();
        lastKnown = p.position();
        lastSeenTick = level().getGameTime();
    }

    private void onBodyFound(NpcEntity body) {
        ServerLevel sl = (ServerLevel) level();
        body.discovered = true;
        MissionManager.onBodyFound(sl, body);
        waiting = false;
        if (getRole().guard) {
            say(body.isDead() ? "Man down! Lock it down!" : "Hey — are you all right?", 70);
            investigate(body.position(), 100);
            investigateBody = body.getUUID();
        } else {
            say("Oh my God — somebody help!", 70);
            setState(State.FLEE);
            lastKnown = body.position();
            Awareness.sendGuard(sl, body.position(), 30, body);
        }
    }

    // ---- investigate -----------------------------------------------------------------------
    public void investigate(Vec3 pos, int lookTicks) {
        if (isDown() || getState() == State.ALERT || getState() == State.FLEE || getState() == State.SICK) return;
        investigatePos = pos;
        investigateTicks = 0;
        investigateLook = lookTicks;
        investigateBody = null;
        repairPos = null;
        waiting = false;
        setState(State.INVESTIGATE);
        setAnim(NpcPose.STAND);
    }

    public void investigateBodyAt(NpcEntity body) {
        investigate(body.position(), 100);
        investigateBody = body.getUUID();
    }

    public void goRepair(BlockPos pos) {
        investigate(Vec3.atBottomCenterOf(pos), 200);
        repairPos = pos;
        say("What now... I'll take a look.", 60);
    }

    public boolean isBusy() {
        return getState() != State.CALM;
    }

    private void tickInvestigate() {
        if (investigatePos == null) {
            resumeRoutine();
            return;
        }
        investigateTicks++;
        double d2 = position().distanceToSqr(investigatePos);
        boolean near = d2 < 6.5;
        if (!near && investigateTicks < 20 * 25) {
            setAnim(NpcPose.STAND);
            if (getNavigation().isDone() || tickCount % 20 == 0) {
                getNavigation().moveTo(investigatePos.x, investigatePos.y, investigatePos.z, BRISK);
            }
            if (unstick(investigatePos)) investigateTicks = 20 * 25;
            return;
        }
        getNavigation().stop();
        setAnim(repairPos != null ? NpcPose.WORK : NpcPose.LOOK);
        if (tickCount % 30 == 0) {
            if (repairPos != null) getLookControl().setLookAt(Vec3.atCenterOf(repairPos));
            else faceYaw(getYRot() + 70 + random.nextInt(80));
        }
        if (--investigateLook > 0) return;
        ServerLevel sl = (ServerLevel) level();
        if (repairPos != null) {
            BlockState s = sl.getBlockState(repairPos);
            if (s.getBlock() instanceof FuseBoxBlock) sl.setBlock(repairPos, s.setValue(FuseBoxBlock.BROKEN, false), 3);
            resumeRoutine();
        } else if (investigateBody != null && sl.getEntity(investigateBody) instanceof NpcEntity body && body.isDown()) {
            if (body.isDead()) {
                say("Nobody leaves! Search the area!", 80);
                Awareness.lockdown(sl, body.position(), 28);
                beginSearch(body.position(), 20 * 30);
            } else {
                body.wakeUp();
                resumeRoutine();
            }
        } else {
            say("Hm. Nothing.", 40);
            resumeRoutine();
        }
    }

    // ---- combat / search / flee / sick -------------------------------------------------------
    private void tickAlert() {
        ServerLevel sl = (ServerLevel) level();
        ServerPlayer t = alertTarget == null ? null : sl.getServer().getPlayerList().getPlayer(alertTarget);
        if (t == null || !t.isAlive() || t.isCreative() || t.isSpectator() || t.level() != sl || distanceToSqr(t) > 60 * 60) {
            beginSearch(lastKnown != null ? lastKnown : position(), 20 * 12);
            return;
        }
        setAnim(NpcPose.STAND);
        setSprinting(true);
        MissionManager.markHunted(t);
        boolean sees = canSee(t, 28f, 100f);
        if (sees) {
            lastSeenTick = sl.getGameTime();
            lastKnown = t.position();
        } else if (sl.getGameTime() - lastSeenTick > 20 * 12) {
            beginSearch(lastKnown != null ? lastKnown : position(), 20 * 20);
            return;
        }
        if (tickCount % 10 == 0 || getNavigation().isDone()) {
            if (sees) getNavigation().moveTo(t, RUN);
            else if (lastKnown != null) getNavigation().moveTo(lastKnown.x, lastKnown.y, lastKnown.z, RUN);
        }
        if (sees) getLookControl().setLookAt(t, 30, 30);
        if (sees && distanceToSqr(t) < 2.4 * 2.4 && attackCooldown <= 0) {
            swing(InteractionHand.MAIN_HAND);
            doHurtTarget(t);
            attackCooldown = 18;
        }
        if (tickCount % 60 == 0) Awareness.rallyGuards(sl, this, t, 14);
    }

    public void beginSearch(Vec3 where, int ticks) {
        if (isDown()) return;
        setState(State.SEARCH);
        investigatePos = where;
        investigateLook = ticks;
        setSprinting(false);
        waiting = false;
    }

    private void tickSearch() {
        if (investigatePos == null || --investigateLook <= 0) {
            suspicion.replaceAll((k, v) -> Math.min(v, 0.4f));
            resumeRoutine();
            return;
        }
        if (position().distanceToSqr(investigatePos) > 9) {
            setAnim(NpcPose.STAND);
            if (getNavigation().isDone() || tickCount % 20 == 0) {
                getNavigation().moveTo(investigatePos.x, investigatePos.y, investigatePos.z, BRISK);
            }
            if (unstick(investigatePos)) investigateLook = Math.min(investigateLook, 100);
        } else {
            setAnim(NpcPose.LOOK);
            if (tickCount % 40 == 0) {
                Vec3 p = DefaultRandomPos.getPos(this, 7, 3);
                if (p != null) getNavigation().moveTo(p.x, p.y, p.z, WALK);
            }
        }
    }

    private void tickFlee() {
        setAnim(NpcPose.STAND);
        setSprinting(true);
        if (stateTicks > 20 * 14) {
            suspicion.replaceAll((k, v) -> Math.min(v, 0.5f));
            resumeRoutine();
            return;
        }
        if (getNavigation().isDone() || stateTicks % 40 == 1) {
            Vec3 from = lastKnown != null ? lastKnown : position();
            Vec3 p = DefaultRandomPos.getPosAway(this, 16, 6, from);
            if (p != null) getNavigation().moveTo(p.x, p.y, p.z, RUN);
        }
    }

    private void tickSick() {
        if (stateTicks > 20 * 45) {
            resumeRoutine();
            return;
        }
        boolean there = sickSpot == null || position().distanceToSqr(sickSpot) < 4 || stateTicks > 20 * 14;
        if (!there) {
            setAnim(NpcPose.STAND);
            setSprinting(true);
            if (getNavigation().isDone() || tickCount % 20 == 0) getNavigation().moveTo(sickSpot.x, sickSpot.y, sickSpot.z, RUN);
        } else {
            setSprinting(false);
            getNavigation().stop();
            setAnim(NpcPose.CROUCH);
            if (tickCount % 25 == 0) {
                ((ServerLevel) level()).sendParticles(ParticleTypes.SNEEZE, getX(), getY() + 0.9, getZ(), 6, .15, .1, .15, .02);
                playSound(SoundEvents.PLAYER_BURP, 0.6f, 0.6f);
            }
        }
    }

    // ---- down: unconscious / dead --------------------------------------------------------------
    private void tickDown() {
        if (draggedBy == null) return;
        Player p = level().getPlayerByUUID(draggedBy);
        if (p == null || !p.isAlive() || distanceToSqr(p) > 6 * 6) {
            draggedBy = null;
            return;
        }
        Vec3 look = Vec3.directionFromRotation(0, p.getYRot());
        Vec3 goal = p.position().subtract(look.scale(1.2));
        Vec3 delta = goal.subtract(position());
        if (delta.lengthSqr() > 0.02) move(MoverType.SELF, new Vec3(delta.x * 0.5, Math.max(delta.y, -0.4) * 0.5 + 0.02, delta.z * 0.5));
        setYRot(p.getYRot());
        yBodyRot = p.getYRot();
    }

    public void toggleDrag(ServerPlayer p) {
        if (!isDown()) return;
        if (p.getUUID().equals(draggedBy)) {
            draggedBy = null;
            p.displayClientMessage(Component.literal("Body dropped"), true);
        } else {
            draggedBy = p.getUUID();
            p.displayClientMessage(Component.literal("Dragging " + getName().getString() + " — sneak-click again to drop"), true);
        }
    }

    public void knockOut(@Nullable ServerPlayer by) {
        if (isDown()) return;
        goDown(State.UNCONSCIOUS);
        MissionManager.onKnockout((ServerLevel) level(), this, by);
    }

    /** Marks the NPC dead but keeps the body in the world. */
    public void kill(@Nullable ServerPlayer by, boolean accident) {
        if (isDead()) return;
        goDown(State.DEAD);
        playSound(SoundEvents.PLAYER_DEATH, 0.5f, 0.9f);
        MissionManager.onNpcDeath((ServerLevel) level(), this, by, accident);
    }

    private void goDown(State s) {
        setState(s);
        getNavigation().stop();
        setSprinting(false);
        setAnim(NpcPose.STAND);
        entityData.set(SUSPICION, 0f);
        entityData.set(SPEECH, "");
        setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
        setHealth(getMaxHealth());
        clearFire();
        waiting = false;
        poisonTicks = 0;
        suspicion.clear();
        setDeltaMovement(Vec3.ZERO);
    }

    public void wakeUp() {
        if (getState() != State.UNCONSCIOUS) return;
        discovered = false;
        draggedBy = null;
        setState(State.CALM);
        say("Ugh... what happened?", 60);
        beginSearch(position(), 20 * 12);
    }

    public void takeOutfit(ServerPlayer p) {
        NpcRole role = getRole();
        if (!role.wearable) {
            p.displayClientMessage(Component.literal("Nothing useful to wear here"), true);
            return;
        }
        if (isStripped()) {
            p.displayClientMessage(Component.literal("Already taken"), true);
            return;
        }
        NpcRole old = PlayerData.disguise(p);
        PlayerData.setDisguise(p, role, getSkin());
        flag(F_STRIPPED, true);
        if (old != null && old.wearable) {
            spawnAtLocation(new ItemStack(ModRegistry.OUTFITS.get(old).get()));
        }
        playSound(SoundEvents.ARMOR_EQUIP_LEATHER, 1f, 1f);
        p.displayClientMessage(Component.literal("Disguise: " + role.title), true);
    }

    @Override
    public boolean hurt(DamageSource src, float amount) {
        if (level().isClientSide) return false;
        if (src.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return super.hurt(src, amount);
        if (isDown()) return false;
        ServerPlayer by = src.getEntity() instanceof ServerPlayer sp ? sp : null;
        if (amount >= getHealth()) {
            kill(by, by == null);
            return true;
        }
        boolean r = super.hurt(src, amount);
        if (r && by != null && !by.isCreative()) onCompromised(by);
        return r;
    }

    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);
        if (held.getItem() instanceof RoutePlannerItem || held.getItem() instanceof CastingCardItem) return InteractionResult.PASS;
        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
        if (isDown()) {
            if (level().isClientSide) return InteractionResult.SUCCESS;
            ServerPlayer sp = (ServerPlayer) player;
            if (player.isShiftKeyDown()) toggleDrag(sp);
            else takeOutfit(sp);
            return InteractionResult.CONSUME;
        }
        PropType t = PropItem.typeOf(held);
        if (t != null && (t.kind == PropType.Kind.SEDATIVE || t.kind == PropType.Kind.INJECT)) {
            if (level().isClientSide) return InteractionResult.SUCCESS;
            Combat.inject((ServerPlayer) player, this, held, t);
            return InteractionResult.CONSUME;
        }
        return InteractionResult.PASS;
    }

    // ---- persistence ------------------------------------------------------------------------------
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putString("Role", getRole().id);
        tag.putInt("Skin", getSkin());
        tag.putByte("Flags", entityData.get(FLAGS));
        tag.putByte("NpcState", entityData.get(STATE));
        tag.put("Route", route.save());
        tag.putInt("RouteIndex", routeIndex);
        tag.putInt("RouteDir", routeDir);
        tag.putString("ContractId", contractId);
        tag.putString("FollowId", followId);
        tag.putInt("Gen", missionGen);
        tag.putInt("CastIndex", castIndex);
        tag.putBoolean("Discovered", discovered);
        tag.putBoolean("Frozen", frozen);
        if (sickSpot != null) {
            tag.putDouble("SickX", sickSpot.x);
            tag.putDouble("SickY", sickSpot.y);
            tag.putDouble("SickZ", sickSpot.z);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setRole(NpcRole.byId(tag.getString("Role")));
        entityData.set(SKIN, tag.getInt("Skin"));
        entityData.set(FLAGS, tag.getByte("Flags"));
        State s = State.of(tag.getByte("NpcState"));
        entityData.set(STATE, (byte) (s == State.UNCONSCIOUS || s == State.DEAD ? s.ordinal() : 0));
        route = Route.load(tag.getCompound("Route"));
        routeIndex = tag.getInt("RouteIndex");
        routeDir = tag.getInt("RouteDir") < 0 ? -1 : 1;
        contractId = tag.getString("ContractId");
        followId = tag.getString("FollowId");
        missionGen = tag.contains("Gen") ? tag.getInt("Gen") : -1;
        castIndex = tag.contains("CastIndex") ? tag.getInt("CastIndex") : -1;
        discovered = tag.getBoolean("Discovered");
        frozen = tag.getBoolean("Frozen");
        sickSpot = tag.contains("SickX") ? new Vec3(tag.getDouble("SickX"), tag.getDouble("SickY"), tag.getDouble("SickZ")) : null;
    }
}
