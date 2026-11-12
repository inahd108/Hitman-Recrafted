package recrafted.mission;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.fml.loading.FMLPaths;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.npc.NpcRole;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;

/** Immutable mission definition read from data/recrafted/missions/&lt;id&gt;.json. */
public final class Mission {
    private static final Logger LOG = LogManager.getLogger("recrafted");
    /** Every contract the mod ships, in menu order. */
    public static final List<String> IDS = List.of("corvara", "amsterdam");
    private static final Map<String, Mission> CACHE = new HashMap<>();

    public record Zone(String name, String label, AABB box, Set<NpcRole> allow) {}
    /** optional objectives (bonuses) never hold up the exit. */
    public record Objective(String id, String type, String target, String text, boolean optional) {}
    public record Target(String id, String name, String desc) {}
    /** An item lying on the map; with gun set, item is a gun-pack gun id instead of an item id. */
    public record PropSpawn(ResourceLocation item, Vec3 pos, boolean gun) {}
    /** A line announced when the mission clock reaches a minute (relative to the start, repeating every period). */
    public record ClockEvent(int at, String text, String sub) {}
    /**
     * The mission clock: it starts at {@code start} (minutes after midnight) and runs one minute every
     * {@code secondsPerMinute} real seconds. Schedules and events repeat every {@code period} minutes (0 = never).
     */
    public record Clock(int start, int secondsPerMinute, int period, List<ClockEvent> events) {}
    /** A point on a boat's water route: a stop (name + wait), a gate it needs open, an NPC it waits for. */
    public record BoatPoint(double x, double z, String stop, int waitTicks, String gate, String hold) {}
    public record BoatDef(String name, String design, double y, List<BoatPoint> route) {}
    /** One block a gate sets when it opens; closing puts back whatever was there. */
    public record GateBlock(BlockPos pos, String state) {}
    public record GateDef(String name, String kind, List<GateBlock> open, AABB clear) {}

    public String id, title, location;
    public ResourceKey<Level> dimension;
    public Vec3 spawn;
    @Nullable public Clock clock;
    public float spawnYaw;
    public final List<String> briefing = new ArrayList<>();
    public final List<String> intel = new ArrayList<>();
    public final List<Zone> zones = new ArrayList<>();
    public final List<Objective> objectives = new ArrayList<>();
    public final List<Target> targets = new ArrayList<>();
    public final List<PropSpawn> props = new ArrayList<>();
    /** Raw NPC definitions; see MissionManager.spawnNpc for the fields. */
    public final List<JsonObject> npcs = new ArrayList<>();
    public final List<BoatDef> boats = new ArrayList<>();
    public final List<GateDef> gates = new ArrayList<>();

    public static Path castFile(String id) {
        return FMLPaths.CONFIGDIR.get().resolve("recrafted").resolve(id + ".cast.json");
    }

    public static Mission corvara() {
        return byId("corvara");
    }

    public static synchronized Mission byId(String id) {
        return CACHE.computeIfAbsent(id, Mission::load);
    }

    /** The mission played in this dimension, or null outside every contract. */
    @Nullable
    public static Mission forDimension(ResourceKey<Level> dim) {
        for (String id : IDS) {
            Mission m;
            try {
                m = byId(id);
            } catch (Exception e) {
                continue;
            }
            if (m.dimension.equals(dim)) return m;
        }
        return null;
    }

    /** Forget the cached missions so an exported cast is picked up. */
    public static synchronized void reload() {
        CACHE.clear();
    }

    private static String str(JsonObject o, String k) {
        return o.has(k) && !o.get(k).isJsonNull() ? o.get(k).getAsString() : "";
    }

    @Nullable
    public BoatDef boat(String name) {
        for (BoatDef b : boats) if (b.name().equals(name)) return b;
        return null;
    }

    @Nullable
    public GateDef gate(String name) {
        for (GateDef g : gates) if (g.name().equals(name)) return g;
        return null;
    }

    private static Vec3 vec(JsonArray a) {
        return new Vec3(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble());
    }

    private static Mission load(String id) {
        Mission m = new Mission();
        String path = "/data/recrafted/missions/" + id + ".json";
        try (InputStream in = Mission.class.getResourceAsStream(path)) {
            if (in == null) throw new IllegalStateException("missing " + path);
            JsonObject o = new Gson().fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
            m.id = o.get("id").getAsString();
            m.title = o.get("title").getAsString();
            m.location = o.get("location").getAsString();
            m.dimension = ResourceKey.create(Registries.DIMENSION, new ResourceLocation(o.get("dimension").getAsString()));
            JsonObject sp = o.getAsJsonObject("spawn");
            m.spawn = vec(sp.getAsJsonArray("pos"));
            m.spawnYaw = sp.get("yaw").getAsFloat();
            for (JsonElement e : o.getAsJsonArray("briefing")) m.briefing.add(e.getAsString());
            for (JsonElement e : o.getAsJsonArray("intel")) m.intel.add(e.getAsString());
            for (JsonElement e : o.getAsJsonArray("targets")) {
                JsonObject t = e.getAsJsonObject();
                m.targets.add(new Target(t.get("id").getAsString(), t.get("name").getAsString(), t.get("desc").getAsString()));
            }
            for (JsonElement e : o.getAsJsonArray("objectives")) {
                JsonObject t = e.getAsJsonObject();
                m.objectives.add(new Objective(t.get("id").getAsString(), t.get("type").getAsString(),
                        t.has("target") ? t.get("target").getAsString() : "", t.get("text").getAsString(),
                        t.has("optional") && t.get("optional").getAsBoolean()));
            }
            for (JsonElement e : o.getAsJsonArray("zones")) {
                JsonObject z = e.getAsJsonObject();
                JsonArray b = z.getAsJsonArray("box");
                Set<NpcRole> allow = EnumSet.noneOf(NpcRole.class);
                for (JsonElement r : z.getAsJsonArray("allow")) {
                    NpcRole role = NpcRole.byIdOrNull(r.getAsString());
                    if (role != null) allow.add(role);
                }
                m.zones.add(new Zone(z.get("name").getAsString(), z.get("label").getAsString(),
                        new AABB(b.get(0).getAsDouble(), b.get(1).getAsDouble(), b.get(2).getAsDouble(),
                                b.get(3).getAsDouble() + 1, b.get(4).getAsDouble() + 1, b.get(5).getAsDouble() + 1), allow));
            }
            for (JsonElement e : o.getAsJsonArray("props")) {
                JsonObject p = e.getAsJsonObject();
                boolean gun = p.has("gun");
                m.props.add(new PropSpawn(new ResourceLocation(p.get(gun ? "gun" : "item").getAsString()), vec(p.getAsJsonArray("pos")), gun));
            }
            for (JsonElement e : o.getAsJsonArray("npcs")) m.npcs.add(e.getAsJsonObject());
            if (o.has("boats")) for (JsonElement e : o.getAsJsonArray("boats")) {
                JsonObject b = e.getAsJsonObject();
                List<BoatPoint> pts = new ArrayList<>();
                for (JsonElement pe : b.getAsJsonArray("route")) {
                    JsonObject p = pe.getAsJsonObject();
                    JsonArray xz = p.getAsJsonArray("pos");
                    pts.add(new BoatPoint(xz.get(0).getAsDouble(), xz.get(1).getAsDouble(), str(p, "stop"),
                            p.has("wait") ? p.get("wait").getAsInt() : 0, str(p, "gate"), str(p, "hold")));
                }
                m.boats.add(new BoatDef(b.get("name").getAsString(), b.get("design").getAsString(), b.get("y").getAsDouble(), pts));
            }
            if (o.has("gates")) for (JsonElement e : o.getAsJsonArray("gates")) {
                JsonObject g = e.getAsJsonObject();
                List<GateBlock> blocks = new ArrayList<>();
                for (JsonElement be : g.getAsJsonArray("open")) {
                    JsonArray a = be.getAsJsonArray();
                    blocks.add(new GateBlock(new BlockPos(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt()), a.get(3).getAsString()));
                }
                JsonArray c = g.getAsJsonArray("clear");
                m.gates.add(new GateDef(g.get("name").getAsString(), g.get("kind").getAsString(), blocks,
                        new AABB(c.get(0).getAsDouble(), c.get(1).getAsDouble(), c.get(2).getAsDouble(),
                                c.get(3).getAsDouble() + 1, c.get(4).getAsDouble() + 1, c.get(5).getAsDouble() + 1)));
            }
            if (o.has("clock")) {
                JsonObject c = o.getAsJsonObject("clock");
                List<ClockEvent> ev = new ArrayList<>();
                if (c.has("events")) for (JsonElement e : c.getAsJsonArray("events")) {
                    JsonObject t = e.getAsJsonObject();
                    ev.add(new ClockEvent(t.get("at").getAsInt(), t.get("text").getAsString(), t.has("sub") ? t.get("sub").getAsString() : ""));
                }
                m.clock = new Clock(c.get("start").getAsInt(), c.get("secondsPerMinute").getAsInt(),
                        c.has("period") ? c.get("period").getAsInt() : 0, ev);
            }
        } catch (Exception e) {
            throw new IllegalStateException("Could not load mission " + id, e);
        }
        // a cast exported with /contract cast export replaces the bundled one
        Path cast = castFile(id);
        if (Files.exists(cast)) {
            try (Reader r = Files.newBufferedReader(cast, StandardCharsets.UTF_8)) {
                JsonObject o = new Gson().fromJson(r, JsonObject.class);
                List<JsonObject> list = new ArrayList<>();
                for (JsonElement e : o.getAsJsonArray("npcs")) list.add(e.getAsJsonObject());
                m.npcs.clear();
                m.npcs.addAll(list);
                LOG.info("Mission {}: using custom cast from {} ({} NPCs)", id, cast, list.size());
            } catch (Exception e) {
                LOG.error("Mission {}: could not read custom cast {}, using the bundled one", id, cast, e);
            }
        }
        LOG.info("Mission {} loaded: {} NPCs, {} props, {} zones", id, m.npcs.size(), m.props.size(), m.zones.size());
        return m;
    }
}
