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
    private static long serverTick;

    private MissionManager() {}

    // ---- lookups ---------------------------------------------------------------------
    @Nullable
    public static ServerLevel missionLevel(MinecraftServer server) {
        return server.getLevel(Mission.corvara().dimension);
    }

    public static boolean inMission(Entity e) {
        return e.level().dimension().equals(Mission.corvara().dimension);
    }

    @Nullable
    private static MissionState activeState(ServerLevel level) {
        if (!level.dimension().equals(Mission.corvara().dimension)) return null;
        MissionState st = MissionState.get(level);
        return st.active ? st : null;
    }

    /** The first restricted zone the player is inside without the right outfit. */
    @Nullable
    public static Mission.Zone violatedZone(Player p) {
        if (!inMission(p)) return null;
        NpcRole worn = PlayerData.disguise(p);
        Vec3 at = p.position();
        for (Mission.Zone z : Mission.corvara().zones) {
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
        Mission m = Mission.corvara();
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
            by.displayClientMessage(Component.literal("Non-target killed").withStyle(ChatFormatting.RED), true);
        }
        st.setDirty();
        checkAllDone(level, st);
    }

    private static void checkAllDone(ServerLevel level, MissionState st) {
        Mission m = Mission.corvara();
        for (Mission.Objective o : m.objectives) {
            if (!o.type().equals("exit") && !st.done.contains(o.id())) return;
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
        if (level.dimension().equals(Mission.corvara().dimension)) {
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
        for (Mission.Objective o : Mission.corvara().objectives) {
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
        Mission m = Mission.corvara();
        List<String> open = new ArrayList<>();
        for (Mission.Objective o : m.objectives) {
            if (!o.type().equals("exit") && !st.done.contains(o.id())) open.add(o.text());
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
        sendHud(level, p);
    }

    // ---- start / stop ----------------------------------------------------------------------
    public static boolean start(ServerPlayer p) {
        MinecraftServer server = p.getServer();
        Mission.reload();
        Mission m = Mission.corvara();
        ServerLevel level = server.getLevel(m.dimension);
        if (level == null) {
            p.sendSystemMessage(Component.literal("The Corvara dimension is missing. Create a new world with the mod installed, or restart the server.").withStyle(ChatFormatting.RED));
            return false;
        }
        MissionState st = MissionState.get(level);
        for (Map.Entry<BlockPos, BlockState> e : st.changed.entrySet()) level.setBlock(e.getKey(), e.getValue(), 3);
        st.changed.clear();
        st.gen++;
        st.done.clear();
        st.deletedCast.clear();
        st.resetStats();
        st.pendingNpcs.clear();
        st.pendingProps.clear();
        for (int i = 0; i < m.npcs.size(); i++) st.pendingNpcs.add(i);
        for (int i = 0; i < m.props.size(); i++) st.pendingProps.add(i);
        st.active = true;
        st.complete = false;
        st.purgeAt = -1;
        st.startTick = level.getGameTime();
        st.setDirty();
        List<Entity> stale = new ArrayList<>();
        for (Entity e : level.getAllEntities()) {
            if (e instanceof NpcEntity n && n.missionGen != -1) stale.add(e);
            else if (e instanceof PropEntity pe && pe.missionGen != -1) stale.add(e);
        }
        stale.forEach(Entity::discard);

        p.teleportTo(level, m.spawn.x, m.spawn.y, m.spawn.z, m.spawnYaw, 0f);
        if (p.gameMode.getGameModeForPlayer() == GameType.SURVIVAL) p.setGameMode(GameType.ADVENTURE);
        PlayerData.setDisguise(p, null, 0);
        p.setHealth(p.getMaxHealth());
        give(p, PropType.COIN, 3);
        give(p, PropType.FIBER_WIRE, 1);
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
        n.setEnforcer(def.has("enforcer") && def.get("enforcer").getAsBoolean());
        if (def.has("id")) n.contractId = def.get("id").getAsString();
        if (def.has("follow")) n.followId = def.get("follow").getAsString();
        if (def.has("sickSpot")) {
            JsonArray s = def.getAsJsonArray("sickSpot");
            n.sickSpot = new Vec3(s.get(0).getAsDouble(), s.get(1).getAsDouble(), s.get(2).getAsDouble());
        }
        if (def.has("route")) n.setRoute(Route.fromJson(def.getAsJsonObject("route")));
        n.missionGen = gen;
        n.castIndex = castIndex;
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
        if (n.isTarget()) o.addProperty("target", true);
        if (n.isEnforcer()) o.addProperty("enforcer", true);
        if (!n.contractId.isEmpty()) o.addProperty("id", n.contractId);
        if (!n.followId.isEmpty()) o.addProperty("follow", n.followId);
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
        Mission m = Mission.corvara();
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
        Mission m = Mission.corvara();
        int budget = 24;
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
        Mission m = Mission.corvara();
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
                texts.add(o.text());
                done.add(st.done.contains(o.id()));
            }
        }
        Net.CHANNEL.send(PacketDistributor.PLAYER.with(() -> p), new Net.HudS2C(st.active || st.complete, m.title, status, max,
                z == null ? "" : z.label(), worn == null ? "Suit" : worn.title, isDragging(level, p), texts, done));
    }

    // ---- events ------------------------------------------------------------------------------------
    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !(e.level instanceof ServerLevel level)) return;
        DoorTimers.tick(level);
        if (!level.dimension().equals(Mission.corvara().dimension)) return;
        serverTick = level.getGameTime();
        MissionState st = MissionState.get(level);
        if (st.active) {
            if (level.getGameTime() % 10 == 0) spawnPending(level, st);
            tickPurge(level, st);
        }
        if (level.getGameTime() % 5 == 0) {
            for (ServerPlayer p : level.players()) sendHud(level, p);
        }
    }

    @SubscribeEvent
    public static void onJoin(EntityJoinLevelEvent e) {
        if (!(e.getLevel() instanceof ServerLevel level) || !level.dimension().equals(Mission.corvara().dimension)) return;
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
