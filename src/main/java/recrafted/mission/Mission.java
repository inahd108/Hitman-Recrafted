package recrafted.mission;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
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
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;

/** Immutable mission definition read from data/recrafted/missions/&lt;id&gt;.json. */
public final class Mission {
    private static final Logger LOG = LogManager.getLogger("recrafted");
    private static Mission corvara;

    public record Zone(String name, String label, AABB box, Set<NpcRole> allow) {}
    public record Objective(String id, String type, String target, String text) {}
    public record Target(String id, String name, String desc) {}
    public record PropSpawn(ResourceLocation item, Vec3 pos) {}

    public String id, title, location;
    public ResourceKey<Level> dimension;
    public Vec3 spawn;
    public float spawnYaw;
    public final List<String> briefing = new ArrayList<>();
    public final List<String> intel = new ArrayList<>();
    public final List<Zone> zones = new ArrayList<>();
    public final List<Objective> objectives = new ArrayList<>();
    public final List<Target> targets = new ArrayList<>();
    public final List<PropSpawn> props = new ArrayList<>();
    /** Raw NPC definitions; see MissionManager.spawnNpc for the fields. */
    public final List<JsonObject> npcs = new ArrayList<>();

    public static Path castFile(String id) {
        return FMLPaths.CONFIGDIR.get().resolve("recrafted").resolve(id + ".cast.json");
    }

    public static synchronized Mission corvara() {
        if (corvara == null) corvara = load("corvara");
        return corvara;
    }

    /** Forget the cached mission so an exported cast is picked up. */
    public static synchronized void reload() {
        corvara = null;
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
                        t.has("target") ? t.get("target").getAsString() : "", t.get("text").getAsString()));
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
                m.props.add(new PropSpawn(new ResourceLocation(p.get("item").getAsString()), vec(p.getAsJsonArray("pos"))));
            }
            for (JsonElement e : o.getAsJsonArray("npcs")) m.npcs.add(e.getAsJsonObject());
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
