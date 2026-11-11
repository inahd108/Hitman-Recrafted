package recrafted.npc;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;

/** One stop on an NPC route. */
public class Waypoint {
    public static final float NO_YAW = Float.NaN;

    public double x, y, z;
    /** How long to stay, in ticks. 0 = walk straight through. */
    public int wait;
    public NpcPose pose = NpcPose.STAND;
    /** Facing while waiting; NaN keeps whatever direction the NPC arrived with. */
    public float yaw = NO_YAW;
    public boolean run;
    public String say = "";

    public Waypoint() {}

    public Waypoint(double x, double y, double z) {
        this.x = x; this.y = y; this.z = z;
    }

    public Vec3 pos() { return new Vec3(x, y, z); }

    public boolean hasYaw() { return !Float.isNaN(yaw); }

    public Waypoint copy() {
        Waypoint w = new Waypoint(x, y, z);
        w.wait = wait; w.pose = pose; w.yaw = yaw; w.run = run; w.say = say;
        return w;
    }

    public CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putDouble("x", x); t.putDouble("y", y); t.putDouble("z", z);
        t.putInt("wait", wait);
        t.putString("pose", pose.id);
        if (hasYaw()) t.putFloat("yaw", yaw);
        if (run) t.putBoolean("run", true);
        if (!say.isEmpty()) t.putString("say", say);
        return t;
    }

    public static Waypoint load(CompoundTag t) {
        Waypoint w = new Waypoint(t.getDouble("x"), t.getDouble("y"), t.getDouble("z"));
        w.wait = t.getInt("wait");
        w.pose = NpcPose.byId(t.getString("pose"));
        w.yaw = t.contains("yaw") ? t.getFloat("yaw") : NO_YAW;
        w.run = t.getBoolean("run");
        w.say = t.getString("say");
        return w;
    }

    public void write(FriendlyByteBuf buf) {
        buf.writeDouble(x); buf.writeDouble(y); buf.writeDouble(z);
        buf.writeVarInt(wait);
        buf.writeByte(pose.ordinal());
        buf.writeFloat(yaw);
        buf.writeBoolean(run);
        buf.writeUtf(say, 256);
    }

    public static Waypoint read(FriendlyByteBuf buf) {
        Waypoint w = new Waypoint(buf.readDouble(), buf.readDouble(), buf.readDouble());
        w.wait = Math.max(0, Math.min(buf.readVarInt(), 20 * 60 * 30));
        w.pose = NpcPose.byOrdinal(buf.readByte());
        w.yaw = buf.readFloat();
        w.run = buf.readBoolean();
        w.say = buf.readUtf(256);
        return w;
    }

    public JsonObject toJson() {
        JsonObject o = new JsonObject();
        JsonArray p = new JsonArray();
        p.add(round(x)); p.add(round(y)); p.add(round(z));
        o.add("pos", p);
        o.addProperty("wait", wait);
        o.addProperty("pose", pose.id);
        if (hasYaw()) o.addProperty("yaw", Math.round(yaw));
        if (run) o.addProperty("run", true);
        if (!say.isEmpty()) o.addProperty("say", say);
        return o;
    }

    public static Waypoint fromJson(JsonObject o) {
        JsonArray p = o.getAsJsonArray("pos");
        Waypoint w = new Waypoint(p.get(0).getAsDouble(), p.get(1).getAsDouble(), p.get(2).getAsDouble());
        if (o.has("wait")) w.wait = o.get("wait").getAsInt();
        if (o.has("pose")) w.pose = NpcPose.byId(o.get("pose").getAsString());
        if (o.has("yaw") && !o.get("yaw").isJsonNull()) w.yaw = o.get("yaw").getAsFloat();
        if (o.has("run")) w.run = o.get("run").getAsBoolean();
        if (o.has("say") && !o.get("say").isJsonNull()) w.say = o.get("say").getAsString();
        return w;
    }

    private static double round(double v) { return Math.round(v * 100.0) / 100.0; }
}
