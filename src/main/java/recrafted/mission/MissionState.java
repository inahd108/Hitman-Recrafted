package recrafted.mission;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/** Per-world progress of the running mission. */
public class MissionState extends SavedData {
    public boolean active;
    public boolean complete;
    public int gen;
    public long startTick;
    /** Last mission-clock minute whose bells and events have been played. */
    public int clockMinute = -1;
    public final Set<Integer> pendingNpcs = new HashSet<>();
    public final Set<Integer> pendingProps = new HashSet<>();
    public final Set<Integer> pendingBoats = new HashSet<>();
    public final Set<String> done = new HashSet<>();
    /** Hidden targets the player has identified (contract ids). */
    public final Set<String> identified = new HashSet<>();
    /** Cast entries removed in the editor; skipped by the next export. */
    public final Set<Integer> deletedCast = new HashSet<>();
    public final Map<BlockPos, BlockState> changed = new LinkedHashMap<>();
    public long purgeAt = -1;
    public BlockPos purgeCore;
    // statistics for the rating
    public int nonTargetKills, knockouts, bodiesFound, spotted, bodiesHidden, accidents, disguises;

    public static MissionState get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(MissionState::load, MissionState::new, "recrafted_mission");
    }

    public static MissionState load(CompoundTag t) {
        MissionState s = new MissionState();
        s.active = t.getBoolean("active");
        s.complete = t.getBoolean("complete");
        s.gen = t.getInt("gen");
        s.startTick = t.getLong("start");
        s.clockMinute = t.contains("clockMinute") ? t.getInt("clockMinute") : -1;
        for (int i : t.getIntArray("pendingNpcs")) s.pendingNpcs.add(i);
        for (int i : t.getIntArray("pendingProps")) s.pendingProps.add(i);
        for (int i : t.getIntArray("pendingBoats")) s.pendingBoats.add(i);
        for (int i : t.getIntArray("deletedCast")) s.deletedCast.add(i);
        ListTag d = t.getList("done", Tag.TAG_STRING);
        for (int i = 0; i < d.size(); i++) s.done.add(d.getString(i));
        ListTag idl = t.getList("identified", Tag.TAG_STRING);
        for (int i = 0; i < idl.size(); i++) s.identified.add(idl.getString(i));
        ListTag c = t.getList("changed", Tag.TAG_COMPOUND);
        for (int i = 0; i < c.size(); i++) {
            CompoundTag e = c.getCompound(i);
            s.changed.put(NbtUtils.readBlockPos(e.getCompound("pos")),
                    NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), e.getCompound("state")));
        }
        s.purgeAt = t.contains("purgeAt") ? t.getLong("purgeAt") : -1;
        if (t.contains("purgeCore")) s.purgeCore = NbtUtils.readBlockPos(t.getCompound("purgeCore"));
        int[] st = t.getIntArray("stats");
        if (st.length >= 7) {
            s.nonTargetKills = st[0]; s.knockouts = st[1]; s.bodiesFound = st[2]; s.spotted = st[3];
            s.bodiesHidden = st[4]; s.accidents = st[5]; s.disguises = st[6];
        }
        return s;
    }

    @Override
    public CompoundTag save(CompoundTag t) {
        t.putBoolean("active", active);
        t.putBoolean("complete", complete);
        t.putInt("gen", gen);
        t.putLong("start", startTick);
        t.putInt("clockMinute", clockMinute);
        t.putIntArray("pendingNpcs", pendingNpcs.stream().mapToInt(Integer::intValue).toArray());
        t.putIntArray("pendingProps", pendingProps.stream().mapToInt(Integer::intValue).toArray());
        t.putIntArray("pendingBoats", pendingBoats.stream().mapToInt(Integer::intValue).toArray());
        t.putIntArray("deletedCast", deletedCast.stream().mapToInt(Integer::intValue).toArray());
        ListTag d = new ListTag();
        for (String s : done) d.add(StringTag.valueOf(s));
        t.put("done", d);
        ListTag idl = new ListTag();
        for (String s : identified) idl.add(StringTag.valueOf(s));
        t.put("identified", idl);
        ListTag c = new ListTag();
        for (Map.Entry<BlockPos, BlockState> e : changed.entrySet()) {
            CompoundTag x = new CompoundTag();
            x.put("pos", NbtUtils.writeBlockPos(e.getKey()));
            x.put("state", NbtUtils.writeBlockState(e.getValue()));
            c.add(x);
        }
        t.put("changed", c);
        t.putLong("purgeAt", purgeAt);
        if (purgeCore != null) t.put("purgeCore", NbtUtils.writeBlockPos(purgeCore));
        t.putIntArray("stats", new int[]{nonTargetKills, knockouts, bodiesFound, spotted, bodiesHidden, accidents, disguises});
        return t;
    }

    public void resetStats() {
        nonTargetKills = knockouts = bodiesFound = spotted = bodiesHidden = accidents = disguises = 0;
    }
}
