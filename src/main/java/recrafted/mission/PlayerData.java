package recrafted.mission;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.network.PacketDistributor;
import recrafted.net.Net;
import recrafted.npc.NpcRole;

import javax.annotation.Nullable;
import java.util.UUID;

/** Per-player mod state kept in the player's persistent NBT. */
public final class PlayerData {
    private static final String ROOT = "recrafted";

    private PlayerData() {}

    private static CompoundTag tag(Player p) {
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        if (!p.getPersistentData().contains(Player.PERSISTED_NBT_TAG)) p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
        if (!persisted.contains(ROOT)) persisted.put(ROOT, new CompoundTag());
        return persisted.getCompound(ROOT);
    }

    /** The outfit the player wears, or null for their own suit. */
    @Nullable
    public static NpcRole disguise(Player p) {
        String id = tag(p).getString("disguise");
        return id.isEmpty() ? null : NpcRole.byIdOrNull(id);
    }

    public static int disguiseVariant(Player p) {
        return tag(p).getInt("variant");
    }

    public static void setDisguise(ServerPlayer p, @Nullable NpcRole role, int variant) {
        CompoundTag t = tag(p);
        t.putString("disguise", role == null ? "" : role.id);
        t.putInt("variant", variant);
        syncDisguise(p);
    }

    public static void syncDisguise(ServerPlayer p) {
        NpcRole r = disguise(p);
        Net.DisguiseS2C msg = new Net.DisguiseS2C(p.getUUID(), r == null ? "" : r.id, disguiseVariant(p));
        Net.CHANNEL.send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> p), msg);
    }

    @Nullable
    public static UUID selectedNpc(Player p) {
        CompoundTag t = tag(p);
        return t.hasUUID("sel") ? t.getUUID("sel") : null;
    }

    public static void selectNpc(Player p, @Nullable UUID id) {
        if (id == null) tag(p).remove("sel");
        else tag(p).putUUID("sel", id);
    }
}
