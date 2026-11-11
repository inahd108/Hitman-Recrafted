package recrafted.npc;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.FriendlyByteBuf;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** An ordered list of waypoints plus how to repeat them. */
public class Route {
    public enum Mode {
        LOOP("Loop"), PINGPONG("Back and forth"), ONCE("Once, then stay");
        public final String label;
        Mode(String label) { this.label = label; }
        public String id() { return name().toLowerCase(Locale.ROOT); }
        public static Mode byId(String s) {
            for (Mode m : values()) if (m.id().equals(s)) return m;
            return LOOP;
        }
    }

    public static final int MAX_POINTS = 128;

    public final List<Waypoint> points = new ArrayList<>();
    public Mode mode = Mode.LOOP;

    public boolean isEmpty() { return points.isEmpty(); }

    public Route copy() {
        Route r = new Route();
        r.mode = mode;
        for (Waypoint w : points) r.points.add(w.copy());
        return r;
    }

    public CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putString("mode", mode.id());
        ListTag l = new ListTag();
        for (Waypoint w : points) l.add(w.save());
        t.put("points", l);
        return t;
    }

    public static Route load(CompoundTag t) {
        Route r = new Route();
        r.mode = Mode.byId(t.getString("mode"));
        ListTag l = t.getList("points", Tag.TAG_COMPOUND);
        for (int i = 0; i < l.size() && i < MAX_POINTS; i++) r.points.add(Waypoint.load(l.getCompound(i)));
        return r;
    }

    public void write(FriendlyByteBuf buf) {
        buf.writeByte(mode.ordinal());
        buf.writeVarInt(points.size());
        for (Waypoint w : points) w.write(buf);
    }

    public static Route read(FriendlyByteBuf buf) {
        Route r = new Route();
        int m = buf.readByte();
        r.mode = m >= 0 && m < Mode.values().length ? Mode.values()[m] : Mode.LOOP;
        int n = Math.min(buf.readVarInt(), MAX_POINTS);
        for (int i = 0; i < n; i++) r.points.add(Waypoint.read(buf));
        return r;
    }

    public JsonObject toJson() {
        JsonObject o = new JsonObject();
        o.addProperty("mode", mode.id());
        JsonArray a = new JsonArray();
        for (Waypoint w : points) a.add(w.toJson());
        o.add("points", a);
        return o;
    }

    public static Route fromJson(JsonObject o) {
        Route r = new Route();
        if (o.has("mode")) r.mode = Mode.byId(o.get("mode").getAsString());
        if (o.has("points")) {
            for (var e : o.getAsJsonArray("points")) {
                if (r.points.size() >= MAX_POINTS) break;
                r.points.add(Waypoint.fromJson(e.getAsJsonObject()));
            }
        }
        return r;
    }
}
