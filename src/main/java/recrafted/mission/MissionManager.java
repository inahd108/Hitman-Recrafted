package recrafted.mission;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.registries.ForgeRegistries;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.block.DoorTimers;
import recrafted.entity.PropEntity;
import recrafted.item.RoutePlannerItem;
import recrafted.net.Net;
import recrafted.compat.Guns;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;
import recrafted.npc.Route;
import recrafted.prop.PropType;

import javax.annotation.Nullable;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Runs the Corvara mission: spawning, objectives, zones, statistics and the HUD feed. */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class MissionManager {
    private static final Map<UUID, Long> HUNTED = new HashMap<>();
    private static final Map<UUID, Long> SPOT_COOLDOWN = new HashMap<>();
    private static final Map<UUID, Long> DETECTOR_COOLDOWN = new HashMap<>();
    /** How long each player has been watching a hidden target at work (ticks). */
    private static final Map<UUID, Integer> WATCHING = new HashMap<>();
    private static long serverTick;

    private MissionManager() {}

    // ---- lookups ---------------------------------------------------------------------
    @Nullable
    public static ServerLevel missionLevel(MinecraftServer server) {
        return server.getLevel(Mission.corvara().dimension);
    }

    public static boolean inMission(Entity e) {
        return Mission.forDimension(e.level().dimension()) != null;
    }

    /** The mission of this level; callers have checked that there is one. */
    private static Mission of(Level level) {
        Mission m = Mission.forDimension(level.dimension());
        return m != null ? m : Mission.corvara();
    }

    @Nullable
    private static MissionState activeState(ServerLevel level) {
        if (Mission.forDimension(level.dimension()) == null) return null;
        MissionState st = MissionState.get(level);
        return st.active ? st : null;
    }

    /** The first restricted zone the player is inside without the right outfit. */
    @Nullable
    public static Mission.Zone violatedZone(Player p) {
        if (!inMission(p)) return null;
        NpcRole worn = PlayerData.disguise(p);
        Vec3 at = p.position();
        boolean bidder = hasProp(p, recrafted.prop.PropType.BIDDER_PADDLE);
        for (Mission.Zone z : of(p.level()).zones) {
            if (bidder && z.name().equals("hamer_saleroom")) continue;
            if (z.box().contains(at) && (worn == null || !z.allow().contains(worn))) return z;
        }
        return null;
    }

    public static boolean isTrespassing(Player p) {
        return violatedZone(p) != null;
    }

    public static boolean isHunted(Player p) {
        Long t = HUNTED.get(p.getUUID());
        return t != null && serverTick - t < 60;
    }

    public static void markHunted(Player p) {
        HUNTED.put(p.getUUID(), serverTick);
    }

    public static boolean isDragging(ServerLevel level, Player p) {
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, p.getBoundingBox().inflate(7), NpcEntity::isDown)) {
            if (p.getUUID().equals(n.getDraggedBy())) return true;
        }
        return false;
    }

    // ---- statistics hooks ---------------------------------------------------------------
    public static void onSpotted(ServerLevel level, ServerPlayer p) {
        MissionState st = activeState(level);
        Long last = SPOT_COOLDOWN.get(p.getUUID());
        if (last != null && serverTick - last < 20 * 20) return;
        SPOT_COOLDOWN.put(p.getUUID(), serverTick);
        if (st != null) {
            st.spotted++;
            st.setDirty();
        }
    }

    public static void onBodyFound(ServerLevel level, NpcEntity body) {
        MissionState st = activeState(level);
        if (st != null) {
            st.bodiesFound++;
            st.setDirty();
        }
    }

    public static void onKnockout(ServerLevel level, NpcEntity npc, @Nullable ServerPlayer by) {
        MissionState st = activeState(level);
        if (st != null && by != null) {
            st.knockouts++;
            st.setDirty();
        }
    }

    public static void onNpcDeath(ServerLevel level, NpcEntity npc, @Nullable ServerPlayer by, boolean accident) {
        MissionState st = activeState(level);
        if (st == null) return;
        Mission m = of(level);
        boolean wasObjective = false;
        for (Mission.Objective o : m.objectives) {
            if (o.type().equals("eliminate") && !npc.contractId.isEmpty() && o.target().equals(npc.contractId)) {
                wasObjective = true;
                if (st.done.add(o.id())) {
                    if (accident) st.accidents++;
                    announce(level, Component.literal("✔ " + o.text()).withStyle(ChatFormatting.GREEN),
                            Component.literal(accident ? "Accident" : "Target down").withStyle(ChatFormatting.GRAY));
                }
            }
        }
        if (!wasObjective && by != null) {
            st.nonTargetKills++;
            by.displayClientMessage(Component.literal(npc.getRole() == NpcRole.APPRENTICE
                    ? "Non-target killed: that was not De Meester" : "Non-target killed").withStyle(ChatFormatting.RED), true);
        }
        st.setDirty();
        checkAllDone(level, st);
    }

    private static void checkAllDone(ServerLevel level, MissionState st) {
        Mission m = of(level);
        for (Mission.Objective o : m.objectives) {
            if (!o.type().equals("exit") && !o.optional() && !st.done.contains(o.id())) return;
        }
        for (ServerPlayer p : level.players()) {
            p.displayClientMessage(Component.literal("All objectives complete — find an exit").withStyle(ChatFormatting.GOLD), false);
        }
    }

    private static void announce(ServerLevel level, Component title, Component sub) {
        for (ServerPlayer p : level.players()) {
            p.connection.send(new ClientboundSetSubtitleTextPacket(sub));
            p.connection.send(new ClientboundSetTitleTextPacket(title));
            p.playNotifySound(SoundEvents.PLAYER_LEVELUP, SoundSource.MASTER, 0.5f, 1.4f);
        }
    }

    /** Changes a block and remembers the original so a restart can put it back. */
    public static void setTracked(ServerLevel level, BlockPos pos, BlockState state) {
        if (Mission.forDimension(level.dimension()) != null) {
            MissionState st = MissionState.get(level);
            st.changed.putIfAbsent(pos.immutable(), level.getBlockState(pos));
            st.setDirty();
        }
        level.setBlock(pos, state, 3);
    }

    // ---- block actions --------------------------------------------------------------------
    public static void hideBody(ServerLevel level, ServerPlayer p, BlockPos pos) {
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, new AABB(pos).inflate(6), NpcEntity::isDown)) {
            if (p.getUUID().equals(n.getDraggedBy())) {
                n.discard();
                level.playSound(null, pos, SoundEvents.BARREL_CLOSE, SoundSource.BLOCKS, 1f, 0.8f);
                p.displayClientMessage(Component.literal("Body hidden").withStyle(ChatFormatting.GREEN), true);
                MissionState st = activeState(level);
                if (st != null) {
                    st.bodiesHidden++;
                    if (n.discovered) st.bodiesFound = Math.max(0, st.bodiesFound);
                    st.setDirty();
                }
                return;
            }
        }
        p.displayClientMessage(Component.literal("Drag a body here to hide it (sneak + right-click a body)"), true);
    }

    public static void smashCore(ServerLevel level, ServerPlayer p, BlockPos pos) {
        destroyCore(level, pos);
        level.playSound(null, pos, SoundEvents.GLASS_BREAK, SoundSource.BLOCKS, 1.5f, 0.7f);
        Awareness.noise(level, Vec3.atCenterOf(pos), 20, 4, p);
        Awareness.suspiciousAct(level, p, 1f);
    }

    private static void destroyCore(ServerLevel level, BlockPos pos) {
        setTracked(level, pos, Blocks.AIR.defaultBlockState());
        level.sendParticles(ParticleTypes.SNEEZE, pos.getX() + .5, pos.getY() + .5, pos.getZ() + .5, 60, .6, .6, .6, .05);
        MissionState st = activeState(level);
        if (st == null) return;
        for (Mission.Objective o : of(level).objectives) {
            if (o.type().equals("destroy_core") && st.done.add(o.id())) {
                announce(level, Component.literal("✔ " + o.text()).withStyle(ChatFormatting.GREEN), Component.literal("Sample destroyed").withStyle(ChatFormatting.GRAY));
            }
        }
        st.setDirty();
        checkAllDone(level, st);
    }

    public static void startPurge(ServerLevel level, ServerPlayer p, BlockPos console) {
        MissionState st = MissionState.get(level);
        if (st.purgeAt >= 0) {
            p.displayClientMessage(Component.literal("Purge already running"), true);
            return;
        }
        BlockPos core = null;
        for (BlockPos q : BlockPos.betweenClosed(console.offset(-14, -3, -14), console.offset(14, 6, 14))) {
            if (level.getBlockState(q).is(ModRegistry.PATHOGEN_CORE.get())) {
                core = q.immutable();
                break;
            }
        }
        if (core == null) {
            p.displayClientMessage(Component.literal("Containment chamber is empty"), true);
            return;
        }
        st.purgeAt = level.getGameTime() + 20 * 10;
        st.purgeCore = core;
        st.setDirty();
        level.playSound(null, console, SoundEvents.BELL_RESONATE, SoundSource.BLOCKS, 3f, 0.5f);
        p.displayClientMessage(Component.literal("Sterilisation purge in 10 seconds — get clear").withStyle(ChatFormatting.GOLD), false);
        Awareness.suspiciousAct(level, p, 0.8f);
    }

    private static void tickPurge(ServerLevel level, MissionState st) {
        if (st.purgeAt < 0 || st.purgeCore == null) return;
        long left = st.purgeAt - level.getGameTime();
        BlockPos c = st.purgeCore;
        if (left > 0) {
            if (left % 20 == 0) level.playSound(null, c, SoundEvents.NOTE_BLOCK_BIT.get(), SoundSource.BLOCKS, 3f, left <= 60 ? 1.6f : 1f);
            return;
        }
        st.purgeAt = -1;
        level.playSound(null, c, SoundEvents.GENERIC_EXPLODE, SoundSource.BLOCKS, 2f, 0.7f);
        level.sendParticles(ParticleTypes.FLAME, c.getX() + .5, c.getY() + 1, c.getZ() + .5, 400, 3.5, 2, 3.5, .08);
        level.sendParticles(ParticleTypes.EXPLOSION, c.getX() + .5, c.getY() + 1, c.getZ() + .5, 12, 3, 1.5, 3, 0);
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, new AABB(c).inflate(8, 4, 8), e -> !e.isDown())) {
            n.kill(null, true);
        }
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(c).inflate(6, 4, 6))) {
            p.hurt(level.damageSources().inFire(), 14f);
        }
        if (level.getBlockState(c).is(ModRegistry.PATHOGEN_CORE.get())) destroyCore(level, c);
        st.setDirty();
    }

    public static void tryExit(ServerLevel level, ServerPlayer p) {
        MissionState st = activeState(level);
        if (st == null) {
            p.displayClientMessage(Component.literal("No contract is running. Use /contract start"), true);
            return;
        }
        Mission m = of(level);
        List<String> open = new ArrayList<>();
        for (Mission.Objective o : m.objectives) {
            if (!o.type().equals("exit") && !o.optional() && !st.done.contains(o.id())) open.add(o.text());
        }
        if (!open.isEmpty()) {
            p.displayClientMessage(Component.literal("Not yet: " + String.join(", ", open)).withStyle(ChatFormatting.YELLOW), true);
            return;
        }
        if (isHunted(p)) {
            p.displayClientMessage(Component.literal("You can't leave while they are chasing you").withStyle(ChatFormatting.RED), true);
            return;
        }
        for (Mission.Objective o : m.objectives) if (o.type().equals("exit")) st.done.add(o.id());
        st.complete = true;
        st.active = false;
        st.setDirty();
        long secs = (level.getGameTime() - st.startTick) / 20;
        String rating;
        if (st.nonTargetKills == 0 && st.bodiesFound == 0 && st.spotted == 0) rating = "GHOST";
        else if (st.nonTargetKills == 0 && st.spotted <= 2 && st.bodiesFound <= 2) rating = "SHADOW";
        else if (st.nonTargetKills <= 2) rating = "OPERATIVE";
        else rating = "BUTCHER";
        p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal("Rating: " + rating).withStyle(ChatFormatting.GOLD)));
        p.connection.send(new ClientboundSetTitleTextPacket(Component.literal("CONTRACT COMPLETE").withStyle(ChatFormatting.WHITE)));
        p.playNotifySound(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.MASTER, 1f, 1f);
        p.sendSystemMessage(Component.literal("—— " + m.title + " ——").withStyle(ChatFormatting.GOLD));
        p.sendSystemMessage(Component.literal(String.format("Time %d:%02d   Rating %s", secs / 60, secs % 60, rating)));
        p.sendSystemMessage(Component.literal(String.format("Non-target kills %d · Knockouts %d · Bodies found %d · Times spotted %d · Bodies hidden %d · Accidents %d",
                st.nonTargetKills, st.knockouts, st.bodiesFound, st.spotted, st.bodiesHidden, st.accidents)).withStyle(ChatFormatting.GRAY));
        for (Mission.Objective o : m.objectives) {
            if (!o.optional()) continue;
            boolean got = st.done.contains(o.id());
            p.sendSystemMessage(Component.literal((got ? "✔ Bonus: " : "✘ Bonus: ") + o.text())
                    .withStyle(got ? ChatFormatting.GREEN : ChatFormatting.DARK_GRAY));
        }
        sendHud(level, p);
    }

    // ---- hidden targets, clues, rigged loads, collectables -------------------------------------
    /** The player now knows who the hidden target is: mark them for Focus and say so. */
    public static void identify(ServerLevel level, @Nullable ServerPlayer p, String contractId, String how) {
        MissionState st = activeState(level);
        if (st == null || !st.identified.add(contractId)) return;
        st.setDirty();
        String name = contractId;
        for (Mission.Target t : of(level).targets) if (t.id().equals(contractId)) name = t.name();
        for (Entity e : level.getAllEntities()) {
            if (e instanceof NpcEntity n && n.hiddenTarget && n.contractId.equals(contractId)) n.setTarget(true);
        }
        announce(level, Component.literal("\u25c6 " + name + " identified").withStyle(ChatFormatting.RED),
                Component.literal(how).withStyle(ChatFormatting.GRAY));
    }

    /** A document or overheard detail that gives a hidden target away (the café's wage book). */
    public static void readClue(ServerLevel level, @Nullable ServerPlayer p, BlockPos pos) {
        MissionState st = activeState(level);
        if (st == null) {
            if (p != null) p.displayClientMessage(Component.literal("Columns of names and guilders."), true);
            return;
        }
        for (Entity e : level.getAllEntities()) {
            if (e instanceof NpcEntity n && n.hiddenTarget) {
                identify(level, p, n.contractId, "The wage book: one apprentice draws no wage. He pays the others.");
                return;
            }
        }
        if (p != null) p.displayClientMessage(Component.literal("Columns of names and guilders."), true);
    }

    /** Watching a hidden target at work long enough gives them away. */
    private static void tickWatching(ServerLevel level, MissionState st) {
        for (ServerPlayer p : level.players()) {
            NpcEntity seen = null;
            for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, p.getBoundingBox().inflate(10),
                    e -> e.hiddenTarget && !e.isDown() && e.isLefty() && e.getAnim() == recrafted.npc.NpcPose.WORK
                            && !st.identified.contains(e.contractId))) {
                Vec3 to = n.getEyePosition().subtract(p.getEyePosition()).normalize();
                if (p.getViewVector(1f).dot(to) > 0.93 && p.hasLineOfSight(n)) {
                    seen = n;
                    break;
                }
            }
            if (seen == null) {
                WATCHING.remove(p.getUUID());
                continue;
            }
            int t = WATCHING.merge(p.getUUID(), 5, Integer::sum);
            if (t >= 100) {
                WATCHING.remove(p.getUUID());
                identify(level, p, seen.contractId, "He holds the brush in his left hand.");
            }
        }
    }

    /**
     * A winch lets go of the nearest load hanging on a chain (a chandelier, a crate on a hoist):
     * the chain and the load come down, and anyone under it does not get up.
     */
    public static void dropLoad(ServerLevel level, @Nullable ServerPlayer p, BlockPos winch) {
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        for (BlockPos q : BlockPos.betweenClosed(winch.offset(-12, -12, -12), winch.offset(12, 12, 12))) {
            BlockState s = level.getBlockState(q);
            if (s.isAir() || s.is(Blocks.CHAIN) || s.is(Blocks.LANTERN) || !level.getBlockState(q.above()).is(Blocks.CHAIN)) continue;
            double d = q.distSqr(winch);
            if (d < bestD) {
                bestD = d;
                best = q.immutable();
            }
        }
        if (best == null) {
            if (p != null) p.displayClientMessage(Component.literal("The rope is tied off to nothing."), true);
            return;
        }
        // the chain above and anything hanging round the load
        for (BlockPos c = best.above(); level.getBlockState(c).is(Blocks.CHAIN); c = c.above()) setTracked(level, c.immutable(), Blocks.AIR.defaultBlockState());
        for (BlockPos q : BlockPos.betweenClosed(best.offset(-1, -1, -1), best.offset(1, 1, 1))) {
            BlockState s = level.getBlockState(q);
            if (q.equals(best) || s.is(Blocks.LANTERN) || s.is(Blocks.CHAIN)) setTracked(level, q.immutable(), Blocks.AIR.defaultBlockState());
        }
        // where it lands
        BlockPos floor = best.below();
        while (floor.getY() > level.getMinBuildHeight() && level.getBlockState(floor).getCollisionShape(level, floor).isEmpty()) floor = floor.below();
        AABB under = new AABB(best.getX() - 1.2, floor.getY() + 0.4, best.getZ() - 1.2, best.getX() + 2.2, best.getY(), best.getZ() + 2.2);
        int hit = 0;
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, under, e -> !e.isDead())) {
            n.kill(p, true);
            hit++;
        }
        for (ServerPlayer other : level.getEntitiesOfClass(ServerPlayer.class, under)) other.hurt(level.damageSources().anvil(null), 12f);
        level.playSound(null, best.getX() + .5, floor.getY() + 1, best.getZ() + .5, SoundEvents.ANVIL_LAND, SoundSource.BLOCKS, 1.2f, 0.7f);
        level.sendParticles(ParticleTypes.CLOUD, best.getX() + .5, floor.getY() + 1.2, best.getZ() + .5, 30, .7, .2, .7, .02);
        Awareness.noise(level, Vec3.atCenterOf(floor.above()), 18, 8, p);
        if (hit == 0 && p != null) p.displayClientMessage(Component.literal("It comes down on an empty floor."), true);
    }

    /**
     * The player walks through a metal detector. Guns and illegal props set it off unless the player is dressed
     * as a guard; the guards who can see the gate get very suspicious, twice in a row and they move in.
     * Returns true when the alarm sounds.
     */
    public static boolean metalDetector(ServerLevel level, ServerPlayer p, BlockPos pos) {
        if (activeState(level) == null || p.isSpectator()) return false;
        long now = level.getGameTime();
        Long last = DETECTOR_COOLDOWN.get(p.getUUID());
        if (last != null && now - last < 30) return false;
        DETECTOR_COOLDOWN.put(p.getUUID(), now);
        int found = 0;
        List<ItemStack> all = new ArrayList<>(p.getInventory().items);
        all.addAll(p.getInventory().offhand);
        for (ItemStack s : all) {
            if (s.isEmpty()) continue;
            recrafted.prop.PropType t = recrafted.prop.PropItem.typeOf(s);
            if ((t != null && t.illegal()) || Guns.isGun(s) || s.is(ModRegistry.CICALA_CASE.get())) found++;
        }
        NpcRole worn = PlayerData.disguise(p);
        if (found == 0 || (worn != null && worn.guard)) {
            level.playSound(null, pos, SoundEvents.NOTE_BLOCK_CHIME.value(), SoundSource.BLOCKS, 0.4f, 1.6f);
            return false;
        }
        for (int i = 0; i < 3; i++) {
            final int k = i;
            level.getServer().tell(new net.minecraft.server.TickTask(level.getServer().getTickCount() + k * 5,
                    () -> level.playSound(null, pos, SoundEvents.NOTE_BLOCK_BIT.value(), SoundSource.BLOCKS, 1.2f, 1.9f)));
        }
        Awareness.suspiciousAct(level, p, 0.7f);
        NpcEntity nearest = null;
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, new AABB(pos).inflate(12), e -> !e.isDown() && e.getRole().guard)) {
            if (nearest == null || n.distanceToSqr(p) < nearest.distanceToSqr(p)) nearest = n;
        }
        if (nearest != null && nearest.suspicionOf(p) < 1f) {
            nearest.say(found > 1 ? "Sir, step back through the gate. Empty your pockets." : "Sir? Once more through the gate, please.", 70);
            nearest.investigate(p.position(), 60);
        }
        p.displayClientMessage(Component.literal("The metal detector goes off").withStyle(ChatFormatting.RED), true);
        return true;
    }

    public static boolean hasProp(Player p, recrafted.prop.PropType t) {
        for (ItemStack s : p.getInventory().items) if (recrafted.prop.PropItem.typeOf(s) == t) return true;
        return recrafted.prop.PropItem.typeOf(p.getOffhandItem()) == t;
    }

    /** Using a keeper's controls in plain clothes looks wrong to anyone watching. */
    private static void keeperWork(ServerLevel level, ServerPlayer p) {
        if (PlayerData.disguise(p) != NpcRole.BRIDGE_KEEPER) Awareness.suspiciousAct(level, p, 0.45f);
    }

    /** The keepers' panels are locked: the bridge keeper's key, or the keeper's uniform (and her key in its pocket). */
    private static boolean keeperUnlocked(@Nullable ServerPlayer p) {
        if (p == null || PlayerData.disguise(p) == NpcRole.BRIDGE_KEEPER || hasProp(p, recrafted.prop.PropType.BRIDGE_KEY)) return true;
        p.displayClientMessage(Component.literal("Locked. The keeper has the key.").withStyle(ChatFormatting.GRAY), true);
        return false;
    }

    /** The press camera's flash: everyone looking at the player is dazzled for three seconds. */
    public static void cameraFlash(ServerPlayer p) {
        ServerLevel level = p.serverLevel();
        level.playSound(null, p.blockPosition(), SoundEvents.NOTE_BLOCK_HAT.value(), SoundSource.PLAYERS, 1f, 2f);
        level.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 0.8f, 1.8f);
        Vec3 eye = p.getEyePosition().add(p.getViewVector(1f).scale(0.6));
        level.sendParticles(ParticleTypes.FLASH, eye.x, eye.y, eye.z, 1, 0, 0, 0, 0);
        boolean press = PlayerData.disguise(p) == NpcRole.PHOTOGRAPHER;
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, p.getBoundingBox().inflate(10), e -> !e.isDown())) {
            Vec3 to = p.getEyePosition().subtract(n.getEyePosition()).normalize();
            if (n.getViewVector(1f).dot(to) > 0.6 && n.canSeePlayer(p)) {
                n.blind(60);
                if (!press) n.addSuspicion(p, 0.3f);
            }
        }
    }

    // ---- turpentine on a stove ---------------------------------------------------------------
    private record Rig(BlockPos pos, @Nullable UUID by) {}
    private static final Map<net.minecraft.resources.ResourceKey<Level>, List<Rig>> RIGGED = new HashMap<>();

    public static boolean isStove(BlockState s) {
        return s.is(Blocks.SMOKER) || s.is(Blocks.FURNACE) || s.is(Blocks.BLAST_FURNACE) || s.is(Blocks.CAMPFIRE);
    }

    /** Douses a stove with turpentine. The next person who stands right at it goes up in a flash fire (an accident). */
    public static void rigStove(ServerLevel level, @Nullable ServerPlayer p, BlockPos pos) {
        RIGGED.computeIfAbsent(level.dimension(), k -> new ArrayList<>()).add(new Rig(pos.immutable(), p == null ? null : p.getUUID()));
        level.playSound(null, pos, SoundEvents.BUCKET_EMPTY, SoundSource.BLOCKS, 0.6f, 1.4f);
        if (p != null) {
            p.displayClientMessage(Component.literal("You douse the stove with turpentine.").withStyle(ChatFormatting.GOLD), true);
            Awareness.suspiciousAct(level, p, 0.5f);
        }
    }

    private static void tickRigged(ServerLevel level) {
        List<Rig> list = RIGGED.get(level.dimension());
        if (list == null || list.isEmpty()) return;
        for (Rig r : new ArrayList<>(list)) {
            if (!isStove(level.getBlockState(r.pos()))) {
                list.remove(r);
                continue;
            }
            List<NpcEntity> near = level.getEntitiesOfClass(NpcEntity.class, new AABB(r.pos()).inflate(1.3, 1, 1.3), e -> !e.isDown());
            if (near.isEmpty()) continue;
            list.remove(r);
            ServerPlayer by = r.by() == null ? null : (ServerPlayer) level.getPlayerByUUID(r.by());
            Vec3 c = Vec3.atCenterOf(r.pos());
            level.playSound(null, r.pos(), SoundEvents.FIRECHARGE_USE, SoundSource.BLOCKS, 1.5f, 0.7f);
            level.playSound(null, r.pos(), SoundEvents.GENERIC_BURN, SoundSource.BLOCKS, 1.2f, 0.8f);
            level.sendParticles(ParticleTypes.FLAME, c.x, c.y + 0.5, c.z, 60, .6, .6, .6, .08);
            level.sendParticles(ParticleTypes.LARGE_SMOKE, c.x, c.y + 1, c.z, 30, .5, .5, .5, .03);
            for (NpcEntity n : near) n.kill(by, true);
            Awareness.noise(level, c, 18, 6, by);
        }
    }

    /** The bridge keeper's lever: hold the Gildegracht drawbridge down (boats wait at the crane), or let it work again. */
    public static void bridgeControl(ServerLevel level, @Nullable ServerPlayer p, BlockPos pos) {
        if (!keeperUnlocked(p)) return;
        boolean held = recrafted.boat.Waterways.toggleHold(level, "drawbridge");
        level.playSound(null, pos, SoundEvents.LEVER_CLICK, SoundSource.BLOCKS, 0.8f, held ? 0.6f : 0.9f);
        if (p != null) {
            keeperWork(level, p);
            p.displayClientMessage(Component.literal(held ? "The drawbridge stays down. Boats will have to wait at the crane."
                    : "The drawbridge works again.").withStyle(ChatFormatting.GOLD), true);
        }
    }

    /**
     * The lock keeper's sluice wheel. With a boat in the chamber it dumps the water all at once: the boat drops hard
     * against the sill and whoever can't swim goes over the side.
     */
    public static void lockControl(ServerLevel level, @Nullable ServerPlayer p, BlockPos pos) {
        if (!keeperUnlocked(p)) return;
        level.playSound(null, pos, SoundEvents.PISTON_CONTRACT, SoundSource.BLOCKS, 1f, 0.5f);
        if (p != null) keeperWork(level, p);
        recrafted.boat.CanalBoat inLock = null;
        for (recrafted.boat.CanalBoat b : level.getEntitiesOfClass(recrafted.boat.CanalBoat.class, new AABB(pos).inflate(40))) {
            if (b.isMoored("lock.chamber")) inLock = b;
        }
        if (inLock == null) {
            if (p != null) p.displayClientMessage(Component.literal("The sluices roar. Nothing in the chamber."), true);
            return;
        }
        level.playSound(null, inLock.blockPosition(), SoundEvents.GENERIC_SPLASH, SoundSource.BLOCKS, 2f, 0.6f);
        level.sendParticles(ParticleTypes.SPLASH, inLock.getX(), inLock.getY() + 0.8, inLock.getZ(), 80, 2, .3, 4, .2);
        boolean over = false;
        for (net.minecraft.world.entity.Entity e : new ArrayList<>(inLock.getPassengers())) {
            if (e instanceof NpcEntity n && n.getRole().cantSwim()) {
                Vec3 side = inLock.local(3.4, -0.3, 0);
                n.stopRiding();
                n.teleportTo(side.x, side.y, side.z);
                n.setDeltaMovement(0, -0.1, 0);
                n.drownedBy = p;
                over = true;
            } else if (e instanceof NpcEntity n) {
                n.say("Hold on!", 50);
            }
        }
        Awareness.noise(level, inLock.position(), 20, 6, p);
        if (p != null && !over) p.displayClientMessage(Component.literal("The boat lurches against the sill. Everyone holds on."), true);
    }

    /** Collect objectives: done once the item is in the player's inventory. */
    private static void tickCollect(ServerLevel level, MissionState st) {
        Mission m = of(level);
        for (ServerPlayer p : level.players()) {
            for (Mission.Objective o : m.objectives) {
                if (!o.type().equals("collect") || st.done.contains(o.id())) continue;
                net.minecraft.world.item.Item want = ForgeRegistries.ITEMS.getValue(new ResourceLocation(Recrafted.MODID, o.target()));
                if (want == null) continue;
                if (p.getInventory().contains(new ItemStack(want))) {
                    st.done.add(o.id());
                    st.setDirty();
                    announce(level, Component.literal("\u2714 " + o.text()).withStyle(ChatFormatting.GREEN),
                            Component.literal(o.optional() ? "Bonus" : "Objective").withStyle(ChatFormatting.GRAY));
                }
            }
        }
    }

    // ---- the mission clock ---------------------------------------------------------------------
    public static int minutesSinceStart(ServerLevel level, MissionState st, Mission m) {
        if (m.clock == null) return 0;
        return (int) ((level.getGameTime() - st.startTick) / (20L * m.clock.secondsPerMinute()));
    }

    public static String clockText(Mission m, int minutes) {
        int t = (m.clock.start() + minutes) % (24 * 60);
        return String.format("%02d:%02d", t / 60, t % 60);
    }

    /** Bells on the quarter hours, scheduled announcements, and NPCs switching to their next scheduled route. */
    private static void tickClock(ServerLevel level, MissionState st) {
        Mission m = of(level);
        if (m.clock == null) return;
        int now = minutesSinceStart(level, st, m);
        int period = m.clock.period();
        while (st.clockMinute < now) {
            st.clockMinute++;
            st.setDirty();
            int min = st.clockMinute;
            int abs = m.clock.start() + min;
            if (min > 0 && abs % 15 == 0) {
                int strokes = abs % 60 == 0 ? Math.min(12, Math.max(1, (abs / 60) % 12 == 0 ? 12 : (abs / 60) % 12)) : abs % 60 / 15;
                bells(level, strokes, abs % 60 == 0);
            }
            int rel = period > 0 ? min % period : min;
            for (Mission.ClockEvent ev : m.clock.events()) {
                if (ev.at() == rel && (period > 0 || min == ev.at())) {
                    for (ServerPlayer p : level.players()) {
                        p.displayClientMessage(Component.literal(clockText(m, min) + "  " + ev.text()).withStyle(ChatFormatting.GOLD), false);
                        if (!ev.sub().isEmpty()) p.displayClientMessage(Component.literal(ev.sub()).withStyle(ChatFormatting.GRAY), true);
                    }
                }
            }
        }
        int rel = period > 0 ? now % period : now;
        for (Entity e : level.getAllEntities()) {
            if (!(e instanceof NpcEntity n) || n.missionGen != st.gen || n.castIndex < 0 || n.castIndex >= m.npcs.size() || n.isDown()) continue;
            JsonObject def = m.npcs.get(n.castIndex);
            if (!def.has("schedule")) continue;
            JsonArray sch = def.getAsJsonArray("schedule");
            int stage = -1;
            for (int i = 0; i < sch.size(); i++) if (sch.get(i).getAsJsonObject().get("at").getAsInt() <= rel) stage = i;
            if (stage == n.scheduleStage) continue;
            n.scheduleStage = stage;
            JsonObject route = stage < 0 ? def.getAsJsonObject("route") : sch.get(stage).getAsJsonObject().getAsJsonObject("route");
            n.switchRoute(Route.fromJson(route));
        }
    }

    /** The church carillon: a short run of chimes on the quarters, then the hour struck. */
    private static void bells(ServerLevel level, int strokes, boolean hour) {
        Mission m = of(level);
        for (ServerPlayer p : level.players()) {
            for (int i = 0; i < (hour ? 4 : strokes); i++) {
                final int k = i;
                level.getServer().tell(new net.minecraft.server.TickTask(level.getServer().getTickCount() + 1 + k * 12,
                        () -> p.playNotifySound(SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.AMBIENT, 0.45f, new float[]{1.06f, 0.94f, 0.84f, 0.71f}[k % 4])));
            }
            if (hour) {
                for (int i = 0; i < strokes; i++) {
                    level.getServer().tell(new net.minecraft.server.TickTask(level.getServer().getTickCount() + 60 + i * 30,
                            () -> p.playNotifySound(SoundEvents.BELL_BLOCK, SoundSource.AMBIENT, 0.6f, 0.6f)));
                }
            }
        }
    }

    // ---- start / stop ----------------------------------------------------------------------
    /** Resets the world state and queues the whole cast and every prop for spawning. */
    public static void begin(ServerLevel level) {
        Mission.reload();
        Mission m = of(level);
        MissionState st = MissionState.get(level);
        for (Map.Entry<BlockPos, BlockState> e : st.changed.entrySet()) level.setBlock(e.getKey(), e.getValue(), 3);
        st.changed.clear();
        st.gen++;
        st.done.clear();
        st.identified.clear();
        WATCHING.clear();
        st.deletedCast.clear();
        st.resetStats();
        st.pendingNpcs.clear();
        st.pendingProps.clear();
        for (int i = 0; i < m.npcs.size(); i++) st.pendingNpcs.add(i);
        for (int i = 0; i < m.props.size(); i++) st.pendingProps.add(i);
        st.pendingBoats.clear();
        for (int i = 0; i < m.boats.size(); i++) st.pendingBoats.add(i);
        recrafted.boat.Waterways.reset(level);
        RIGGED.remove(level.dimension());
        st.active = true;
        st.complete = false;
        st.purgeAt = -1;
        st.startTick = level.getGameTime();
        st.clockMinute = -1;
        st.setDirty();
        List<Entity> stale = new ArrayList<>();
        for (Entity e : level.getAllEntities()) {
            if (e instanceof NpcEntity n && n.missionGen != -1) stale.add(e);
            else if (e instanceof PropEntity pe && pe.missionGen != -1) stale.add(e);
            else if (e instanceof recrafted.boat.CanalBoat b && b.missionGen != -1) stale.add(e);
        }
        stale.forEach(Entity::discard);
    }

    public static void smashCoreHeadless(ServerLevel level, BlockPos pos) {
        destroyCore(level, pos);
    }

    public static boolean start(ServerPlayer p) {
        return start(p, "corvara");
    }

    public static boolean start(ServerPlayer p, String missionId) {
        Mission m;
        try {
            m = Mission.byId(missionId);
        } catch (Exception e) {
            p.sendSystemMessage(Component.literal("No such contract: " + missionId).withStyle(ChatFormatting.RED));
            return false;
        }
        MinecraftServer server = p.getServer();
        ServerLevel level = server.getLevel(m.dimension);
        if (level == null) {
            p.sendSystemMessage(Component.literal("The " + m.location + " dimension is missing. Create a new world with the mod installed, or restart the server.").withStyle(ChatFormatting.RED));
            return false;
        }
        begin(level);
        m = of(level);
        p.teleportTo(level, m.spawn.x, m.spawn.y, m.spawn.z, m.spawnYaw, 0f);
        if (p.gameMode.getGameModeForPlayer() == GameType.SURVIVAL) p.setGameMode(GameType.ADVENTURE);
        PlayerData.setDisguise(p, null, 0);
        p.setHealth(p.getMaxHealth());
        give(p, PropType.COIN, 3);
        give(p, PropType.FIBER_WIRE, 1);
        giveStarterPistol(p);
        p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal(m.location).withStyle(ChatFormatting.GRAY)));
        p.connection.send(new ClientboundSetTitleTextPacket(Component.literal(m.title).withStyle(ChatFormatting.WHITE)));
        for (String line : m.briefing) p.sendSystemMessage(Component.literal(line).withStyle(ChatFormatting.GRAY));
        for (Mission.Target t : m.targets) {
            p.sendSystemMessage(Component.literal("◆ " + t.name()).withStyle(ChatFormatting.RED)
                    .append(Component.literal(" — " + t.desc()).withStyle(ChatFormatting.GRAY)));
        }
        p.sendSystemMessage(Component.literal("/contract intel lists what the handler knows. Hold V to focus.").withStyle(ChatFormatting.DARK_GRAY));
        return true;
    }

    /** The Passero .22, loaded, with two spare magazines: quiet, and legal while it stays out of sight. */
    private static void giveStarterPistol(ServerPlayer p) {
        boolean has = p.getInventory().items.stream().anyMatch(s -> Guns.isGun(s, Guns.PASSERO))
                || Guns.isGun(p.getOffhandItem(), Guns.PASSERO);
        if (has) return;
        ItemStack gun = Guns.loadedGun(Guns.PASSERO);
        if (gun.isEmpty()) return;
        ItemStack ammo = Guns.spareAmmo(gun);
        if (!ammo.isEmpty()) ammo.setCount(ammo.getCount() * 2);
        if (!p.getInventory().add(gun)) p.drop(gun, false);
        if (!ammo.isEmpty() && !p.getInventory().add(ammo)) p.drop(ammo, false);
    }

    private static void give(ServerPlayer p, PropType t, int n) {
        if (!p.getInventory().contains(new ItemStack(ModRegistry.prop(t)))) p.getInventory().add(new ItemStack(ModRegistry.prop(t), n));
    }

    public static void stop(ServerLevel level) {
        MissionState st = MissionState.get(level);
        st.active = false;
        st.pendingNpcs.clear();
        st.pendingProps.clear();
        st.setDirty();
    }

    // ---- spawning -----------------------------------------------------------------------------
    public static NpcEntity spawnNpc(ServerLevel level, JsonObject def, int gen, int castIndex) {
        NpcEntity n = ModRegistry.NPC.get().create(level);
        NpcRole role = NpcRole.byId(def.get("role").getAsString());
        n.setRole(role);
        String name = def.has("name") ? def.get("name").getAsString() : role.title;
        n.setCustomName(Component.literal(name));
        n.setSkin(def.has("skin") ? def.get("skin").getAsInt() : Math.floorMod(name.hashCode(), role.variants));
        n.setTarget(def.has("target") && def.get("target").getAsBoolean());
        if (def.has("hidden") && def.get("hidden").getAsBoolean()) {
            n.hiddenTarget = true;
            n.setTarget(false);
        }
        if (def.has("lefty")) n.setLefty(def.get("lefty").getAsBoolean());
        n.setEnforcer(def.has("enforcer") && def.get("enforcer").getAsBoolean());
        if (def.has("id")) n.contractId = def.get("id").getAsString();
        if (n.hiddenTarget && MissionState.get(level).identified.contains(n.contractId)) n.setTarget(true);
        if (def.has("follow")) n.followId = def.get("follow").getAsString();
        if (def.has("aboard")) n.aboard = def.get("aboard").getAsString();
        if (def.has("sickSpot")) {
            JsonArray s = def.getAsJsonArray("sickSpot");
            n.sickSpot = new Vec3(s.get(0).getAsDouble(), s.get(1).getAsDouble(), s.get(2).getAsDouble());
        }
        if (def.has("route")) n.setRoute(Route.fromJson(def.getAsJsonObject("route")));
        n.missionGen = gen;
        n.castIndex = castIndex;
        n.arm(Guns.sidearmFor(role));
        JsonArray pos = def.getAsJsonArray("pos");
        float yaw = def.has("yaw") && !def.get("yaw").isJsonNull() ? def.get("yaw").getAsFloat() : 0f;
        n.moveTo(pos.get(0).getAsDouble(), pos.get(1).getAsDouble(), pos.get(2).getAsDouble(), yaw, 0f);
        n.setYHeadRot(yaw);
        n.yBodyRot = yaw;
        level.addFreshEntity(n);
        return n;
    }

    public static JsonObject npcToJson(NpcEntity n) {
        JsonObject o = new JsonObject();
        o.addProperty("name", n.getName().getString());
        o.addProperty("role", n.getRole().id);
        o.addProperty("skin", n.getSkin());
        if (n.isTarget() && !n.hiddenTarget) o.addProperty("target", true);
        if (n.hiddenTarget) o.addProperty("hidden", true);
        if (n.isLefty()) o.addProperty("lefty", true);
        if (n.isEnforcer()) o.addProperty("enforcer", true);
        if (!n.contractId.isEmpty()) o.addProperty("id", n.contractId);
        if (!n.followId.isEmpty()) o.addProperty("follow", n.followId);
        if (!n.aboard.isEmpty()) o.addProperty("aboard", n.aboard);
        if (n.sickSpot != null) {
            JsonArray s = new JsonArray();
            s.add(n.sickSpot.x); s.add(n.sickSpot.y); s.add(n.sickSpot.z);
            o.add("sickSpot", s);
        }
        Route r = n.getRoute();
        JsonArray pos = new JsonArray();
        if (r.isEmpty()) {
            pos.add(Math.round(n.getX() * 100) / 100.0); pos.add(Math.round(n.getY() * 100) / 100.0); pos.add(Math.round(n.getZ() * 100) / 100.0);
            o.addProperty("yaw", Math.round(n.getYRot()));
        } else {
            pos.add(r.points.get(0).x); pos.add(r.points.get(0).y); pos.add(r.points.get(0).z);
            if (r.points.get(0).hasYaw()) o.addProperty("yaw", Math.round(r.points.get(0).yaw));
        }
        o.add("pos", pos);
        o.add("route", r.toJson());
        return o;
    }

    /** Writes the cast as it currently stands in the world to config/recrafted/corvara.cast.json. */
    public static int exportCast(ServerLevel level) throws Exception {
        Mission m = of(level);
        MissionState st = MissionState.get(level);
        Map<Integer, NpcEntity> live = new HashMap<>();
        List<NpcEntity> extra = new ArrayList<>();
        for (Entity e : level.getAllEntities()) {
            if (!(e instanceof NpcEntity n)) continue;
            if (n.castIndex >= 0 && n.missionGen == st.gen) live.put(n.castIndex, n);
            else extra.add(n);
        }
        JsonArray out = new JsonArray();
        for (int i = 0; i < m.npcs.size(); i++) {
            if (st.deletedCast.contains(i)) continue;
            NpcEntity n = live.get(i);
            out.add(n != null ? npcToJson(n) : m.npcs.get(i));
        }
        for (NpcEntity n : extra) out.add(npcToJson(n));
        JsonObject root = new JsonObject();
        root.add("npcs", out);
        Path file = Mission.castFile(m.id);
        Files.createDirectories(file.getParent());
        try (Writer w = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
            new GsonBuilder().setPrettyPrinting().create().toJson(root, w);
        }
        return out.size();
    }

    private static void spawnPending(ServerLevel level, MissionState st) {
        Mission m = of(level);
        int budget = 24;
        for (Integer i : new ArrayList<>(st.pendingBoats)) {
            if (i >= m.boats.size()) { st.pendingBoats.remove(i); continue; }
            Mission.BoatDef b = m.boats.get(i);
            if (!level.isPositionEntityTicking(BlockPos.containing(b.route().get(0).x(), b.y(), b.route().get(0).z()))) continue;
            level.addFreshEntity(recrafted.boat.CanalBoat.create(level, b, st.gen));
            st.pendingBoats.remove(i);
            st.setDirty();
        }
        if (!st.pendingNpcs.isEmpty()) {
            for (Integer i : new ArrayList<>(st.pendingNpcs)) {
                if (i >= m.npcs.size()) { st.pendingNpcs.remove(i); continue; }
                JsonArray pos = m.npcs.get(i).getAsJsonArray("pos");
                BlockPos bp = BlockPos.containing(pos.get(0).getAsDouble(), pos.get(1).getAsDouble(), pos.get(2).getAsDouble());
                if (!level.isPositionEntityTicking(bp)) continue;
                spawnNpc(level, m.npcs.get(i), st.gen, i);
                st.pendingNpcs.remove(i);
                st.setDirty();
                if (--budget <= 0) return;
            }
        }
        if (!st.pendingProps.isEmpty()) {
            for (Integer i : new ArrayList<>(st.pendingProps)) {
                if (i >= m.props.size()) { st.pendingProps.remove(i); continue; }
                Mission.PropSpawn ps = m.props.get(i);
                if (!level.isPositionEntityTicking(BlockPos.containing(ps.pos()))) continue;
                Item item = ForgeRegistries.ITEMS.getValue(ps.item());
                if (item != null && item != net.minecraft.world.item.Items.AIR) {
                    PropEntity e = new PropEntity(level, ps.pos().x, ps.pos().y + 0.02, ps.pos().z, new ItemStack(item));
                    e.missionGen = st.gen;
                    level.addFreshEntity(e);
                }
                st.pendingProps.remove(i);
                st.setDirty();
                if (--budget <= 0) return;
            }
        }
    }

    // ---- HUD ------------------------------------------------------------------------------------
    private static void sendHud(ServerLevel level, ServerPlayer p) {
        Mission m = of(level);
        MissionState st = MissionState.get(level);
        float max = 0;
        for (NpcEntity n : level.getEntitiesOfClass(NpcEntity.class, p.getBoundingBox().inflate(40, 12, 40), e -> !e.isDown())) {
            max = Math.max(max, n.suspicionOf(p));
        }
        Mission.Zone z = violatedZone(p);
        int status = isHunted(p) ? 3 : max > 0.03f ? 2 : z != null ? 1 : 0;
        NpcRole worn = PlayerData.disguise(p);
        List<String> texts = new ArrayList<>();
        List<Boolean> done = new ArrayList<>();
        if (st.active || st.complete) {
            for (Mission.Objective o : m.objectives) {
                texts.add(o.optional() ? "Bonus: " + o.text() : o.text());
                done.add(st.done.contains(o.id()));
            }
        }
        String title = m.clock != null && st.active ? m.title + "   " + clockText(m, minutesSinceStart(level, st, m)) : m.title;
        Net.CHANNEL.send(PacketDistributor.PLAYER.with(() -> p), new Net.HudS2C(st.active || st.complete, title, status, max,
                z == null ? "" : z.label(), worn == null ? "Suit" : worn.title, isDragging(level, p), texts, done));
    }

    // ---- events ------------------------------------------------------------------------------------
    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !(e.level instanceof ServerLevel level)) return;
        DoorTimers.tick(level);
        if (Mission.forDimension(level.dimension()) == null) return;
        serverTick = level.getGameTime();
        MissionState st = MissionState.get(level);
        if (st.active) {
            if (level.getGameTime() % 10 == 0) spawnPending(level, st);
            if (level.getGameTime() % 5 == 0) tickWatching(level, st);
            if (level.getGameTime() % 20 == 0) tickCollect(level, st);
            if (level.getGameTime() % 20 == 5) tickClock(level, st);
            if (level.getGameTime() % 5 == 2) tickRigged(level);
            tickPurge(level, st);
            recrafted.boat.Waterways.tick(level);
        }
        if (level.getGameTime() % 5 == 0) {
            for (ServerPlayer p : level.players()) sendHud(level, p);
        }
    }

    @SubscribeEvent
    public static void onJoin(EntityJoinLevelEvent e) {
        if (!(e.getLevel() instanceof ServerLevel level) || Mission.forDimension(level.dimension()) == null) return;
        int gen = MissionState.get(level).gen;
        if (e.getEntity() instanceof NpcEntity n && n.missionGen != -1 && n.missionGen != gen) e.setCanceled(true);
        else if (e.getEntity() instanceof PropEntity p && p.missionGen != -1 && p.missionGen != gen) e.setCanceled(true);
    }

    @SubscribeEvent
    public static void onAttack(AttackEntityEvent e) {
        if (e.getTarget() instanceof NpcEntity npc) {
            e.setCanceled(true);
            if (e.getEntity() instanceof ServerPlayer sp) Combat.melee(sp, npc);
        } else if (e.getTarget() instanceof PropEntity) {
            e.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void onLeftClickBlock(PlayerInteractEvent.LeftClickBlock e) {
        if (e.getItemStack().getItem() instanceof RoutePlannerItem && e.getEntity() instanceof ServerPlayer sp) {
            e.setCanceled(true);
            if (e.getAction() == PlayerInteractEvent.LeftClickBlock.Action.START) RoutePlannerItem.removeNear(sp, e.getPos());
        }
    }

    /** Security doors answer to a right-click directly, not only through the reader panel. */
    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock e) {
        BlockState state = e.getLevel().getBlockState(e.getPos());
        if (isStove(state) && e.getHand() == net.minecraft.world.InteractionHand.MAIN_HAND
                && recrafted.prop.PropItem.typeOf(e.getEntity().getMainHandItem()) == recrafted.prop.PropType.TURPENTINE) {
            e.setCanceled(true);
            e.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
            if (e.getEntity() instanceof ServerPlayer sp && e.getLevel() instanceof ServerLevel sl && inMission(sp)) {
                rigStove(sl, sp, e.getPos());
                if (!sp.getAbilities().instabuild) sp.getMainHandItem().shrink(1);
            }
            return;
        }
        if (!DoorTimers.isSecurityDoor(state) || e.getHand() != net.minecraft.world.InteractionHand.MAIN_HAND) return;
        if (state.getValue(net.minecraft.world.level.block.DoorBlock.OPEN)) return;
        e.setCanceled(true);
        e.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
        if (e.getEntity() instanceof ServerPlayer sp && e.getLevel() instanceof ServerLevel sl) {
            recrafted.block.CardReaderBlock.operateDoor(sl, sp, e.getPos());
        }
    }

    @SubscribeEvent
    public static void onPlayerDeath(LivingDeathEvent e) {
        if (e.getEntity() instanceof ServerPlayer p && inMission(p) && MissionState.get(p.serverLevel()).active) {
            p.sendSystemMessage(Component.literal("Contract failed. /contract start to try again.").withStyle(ChatFormatting.RED));
        }
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent e) {
        if (e.getEntity() instanceof ServerPlayer p) PlayerData.syncDisguise(p);
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent e) {
        if (e.getEntity() instanceof ServerPlayer p) PlayerData.syncDisguise(p);
    }

    @SubscribeEvent
    public static void onChangeDim(PlayerEvent.PlayerChangedDimensionEvent e) {
        if (e.getEntity() instanceof ServerPlayer p) {
            PlayerData.syncDisguise(p);
            if (!inMission(p)) {
                Net.CHANNEL.send(PacketDistributor.PLAYER.with(() -> p), new Net.HudS2C(false, "", 0, 0, "", "", false, List.of(), List.of()));
            }
        }
    }

    @SubscribeEvent
    public static void onTrack(PlayerEvent.StartTracking e) {
        if (e.getTarget() instanceof ServerPlayer other && e.getEntity() instanceof ServerPlayer viewer) {
            NpcRole r = PlayerData.disguise(other);
            Net.CHANNEL.send(PacketDistributor.PLAYER.with(() -> viewer),
                    new Net.DisguiseS2C(other.getUUID(), r == null ? "" : r.id, PlayerData.disguiseVariant(other)));
        }
    }
}
