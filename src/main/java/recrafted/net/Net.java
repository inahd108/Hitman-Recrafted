package recrafted.net;

import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.client.ClientHandlers;
import recrafted.mission.MissionManager;
import recrafted.mission.MissionState;
import recrafted.mission.PlayerData;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;
import recrafted.npc.Route;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public final class Net {
    private static final String V = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(Recrafted.MODID, "main"), () -> V, V::equals, V::equals);

    private Net() {}

    public static void register() {
        int id = 0;
        CHANNEL.messageBuilder(DisguiseS2C.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(DisguiseS2C::write).decoder(DisguiseS2C::new).consumerMainThread(DisguiseS2C::handle).add();
        CHANNEL.messageBuilder(HudS2C.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(HudS2C::write).decoder(HudS2C::new).consumerMainThread(HudS2C::handle).add();
        CHANNEL.messageBuilder(RouteS2C.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(RouteS2C::write).decoder(RouteS2C::new).consumerMainThread(RouteS2C::handle).add();
        CHANNEL.messageBuilder(NpcScreenS2C.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(NpcScreenS2C::write).decoder(NpcScreenS2C::new).consumerMainThread(NpcScreenS2C::handle).add();
        CHANNEL.messageBuilder(RouteEditC2S.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(RouteEditC2S::write).decoder(RouteEditC2S::new).consumerMainThread(RouteEditC2S::handle).add();
        CHANNEL.messageBuilder(NpcEditC2S.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(NpcEditC2S::write).decoder(NpcEditC2S::new).consumerMainThread(NpcEditC2S::handle).add();
        CHANNEL.messageBuilder(ThrowC2S.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(ThrowC2S::write).decoder(ThrowC2S::new).consumerMainThread(ThrowC2S::handle).add();
        CHANNEL.messageBuilder(PackC2S.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(PackC2S::write).decoder(PackC2S::new).consumerMainThread(PackC2S::handle).add();
    }

    public static boolean canEdit(ServerPlayer p) {
        return p.isCreative() || p.hasPermissions(2);
    }

    public static void sendRoute(ServerPlayer p, NpcEntity npc, boolean open) {
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> p),
                new RouteS2C(npc.getId(), npc.getName().getString(), npc.getRoute(), npc.frozen, open));
    }

    // ---- server -> client ---------------------------------------------------------------
    public record DisguiseS2C(UUID player, String role, int variant) {
        DisguiseS2C(FriendlyByteBuf b) { this(b.readUUID(), b.readUtf(64), b.readVarInt()); }
        void write(FriendlyByteBuf b) { b.writeUUID(player); b.writeUtf(role, 64); b.writeVarInt(variant); }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientHandlers.disguise(this));
            ctx.get().setPacketHandled(true);
        }
    }

    public record HudS2C(boolean active, String title, int status, float suspicion, String zone, String disguise,
                         boolean dragging, List<String> objectives, List<Boolean> done) {
        HudS2C(FriendlyByteBuf b) {
            this(b.readBoolean(), b.readUtf(128), b.readByte(), b.readFloat(), b.readUtf(128), b.readUtf(64), b.readBoolean(),
                    b.readList(x -> x.readUtf(128)), b.readList(FriendlyByteBuf::readBoolean));
        }
        void write(FriendlyByteBuf b) {
            b.writeBoolean(active); b.writeUtf(title, 128); b.writeByte(status); b.writeFloat(suspicion);
            b.writeUtf(zone, 128); b.writeUtf(disguise, 64); b.writeBoolean(dragging);
            b.writeCollection(objectives, (x, s) -> x.writeUtf(s, 128));
            b.writeCollection(done, FriendlyByteBuf::writeBoolean);
        }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientHandlers.hud(this));
            ctx.get().setPacketHandled(true);
        }
    }

    /** The route of the NPC the player is editing; optionally opens the editor screen. */
    public record RouteS2C(int entityId, String name, Route route, boolean frozen, boolean open) {
        RouteS2C(FriendlyByteBuf b) { this(b.readVarInt(), b.readUtf(128), Route.read(b), b.readBoolean(), b.readBoolean()); }
        void write(FriendlyByteBuf b) {
            b.writeVarInt(entityId); b.writeUtf(name, 128); route.write(b); b.writeBoolean(frozen); b.writeBoolean(open);
        }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientHandlers.route(this));
            ctx.get().setPacketHandled(true);
        }
    }

    public record NpcScreenS2C(int entityId, BlockPos pos, String role, String name, int skin, boolean enforcer,
                               boolean target, String contractId, String followId) {
        NpcScreenS2C(FriendlyByteBuf b) {
            this(b.readVarInt(), b.readBlockPos(), b.readUtf(64), b.readUtf(64), b.readVarInt(), b.readBoolean(),
                    b.readBoolean(), b.readUtf(64), b.readUtf(64));
        }
        void write(FriendlyByteBuf b) {
            b.writeVarInt(entityId); b.writeBlockPos(pos); b.writeUtf(role, 64); b.writeUtf(name, 64); b.writeVarInt(skin);
            b.writeBoolean(enforcer); b.writeBoolean(target); b.writeUtf(contractId, 64); b.writeUtf(followId, 64);
        }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientHandlers.npcScreen(this));
            ctx.get().setPacketHandled(true);
        }
    }

    // ---- client -> server ---------------------------------------------------------------
    public static final int ACT_SAVE = 0, ACT_PREVIEW = 1, ACT_FREEZE = 2, ACT_UNFREEZE = 3;

    public record RouteEditC2S(int entityId, Route route, int action) {
        RouteEditC2S(FriendlyByteBuf b) { this(b.readVarInt(), Route.read(b), b.readByte()); }
        void write(FriendlyByteBuf b) { b.writeVarInt(entityId); route.write(b); b.writeByte(action); }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            ServerPlayer p = ctx.get().getSender();
            ctx.get().setPacketHandled(true);
            if (p == null || !canEdit(p)) return;
            Entity e = p.level().getEntity(entityId);
            if (!(e instanceof NpcEntity npc) || npc.distanceToSqr(p) > 96 * 96) return;
            npc.setRoute(route);
            if (action == ACT_PREVIEW) { npc.frozen = false; npc.restartRoute(); }
            else if (action == ACT_FREEZE) npc.frozen = true;
            else if (action == ACT_UNFREEZE) npc.frozen = false;
            sendRoute(p, npc, false);
        }
    }

    public record NpcEditC2S(int entityId, BlockPos pos, float yaw, String role, String name, int skin, boolean enforcer,
                             boolean target, String contractId, String followId, boolean delete) {
        NpcEditC2S(FriendlyByteBuf b) {
            this(b.readVarInt(), b.readBlockPos(), b.readFloat(), b.readUtf(64), b.readUtf(64), b.readVarInt(), b.readBoolean(),
                    b.readBoolean(), b.readUtf(64), b.readUtf(64), b.readBoolean());
        }
        void write(FriendlyByteBuf b) {
            b.writeVarInt(entityId); b.writeBlockPos(pos); b.writeFloat(yaw); b.writeUtf(role, 64); b.writeUtf(name, 64);
            b.writeVarInt(skin); b.writeBoolean(enforcer); b.writeBoolean(target); b.writeUtf(contractId, 64);
            b.writeUtf(followId, 64); b.writeBoolean(delete);
        }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            ServerPlayer p = ctx.get().getSender();
            ctx.get().setPacketHandled(true);
            if (p == null || !canEdit(p)) return;
            ServerLevel level = p.serverLevel();
            NpcEntity npc;
            if (entityId >= 0) {
                if (!(level.getEntity(entityId) instanceof NpcEntity found)) return;
                npc = found;
                if (delete) {
                    if (npc.castIndex >= 0 && MissionManager.inMission(npc)) {
                        MissionState st = MissionState.get(level);
                        st.deletedCast.add(npc.castIndex);
                        st.setDirty();
                    }
                    npc.discard();
                    p.displayClientMessage(Component.literal("NPC removed"), true);
                    return;
                }
            } else {
                if (delete || p.distanceToSqr(pos.getX(), pos.getY(), pos.getZ()) > 64 * 64) return;
                npc = ModRegistry.NPC.get().create(level);
                npc.moveTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, yaw, 0);
                npc.setYHeadRot(yaw);
                if (MissionManager.inMission(p)) npc.missionGen = MissionState.get(level).gen;
            }
            NpcRole r = NpcRole.byId(role);
            npc.setRole(r);
            npc.setSkin(skin);
            npc.setCustomName(Component.literal(name.isBlank() ? r.title : name.trim()));
            npc.setEnforcer(enforcer);
            npc.setTarget(target);
            npc.contractId = contractId.trim();
            npc.followId = followId.trim();
            if (entityId < 0) {
                level.addFreshEntity(npc);
                PlayerData.selectNpc(p, npc.getUUID());
                sendRoute(p, npc, false);
                p.displayClientMessage(Component.literal(npc.getName().getString() + " created and selected — plan a route with the Route Planner"), true);
            } else {
                p.displayClientMessage(Component.literal(npc.getName().getString() + " updated"), true);
            }
        }
    }

    public static List<String> roleIds() {
        List<String> l = new ArrayList<>();
        for (NpcRole r : NpcRole.values()) l.add(r.id);
        return l;
    }

    /** The Throw key was pressed: throw what is in the main hand. */
    public record ThrowC2S() {
        public ThrowC2S(FriendlyByteBuf b) { this(); }
        void write(FriendlyByteBuf b) { }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            ServerPlayer p = ctx.get().getSender();
            ctx.get().setPacketHandled(true);
            if (p != null) recrafted.mission.Throwing.throwHeld(p);
        }
    }

    /** The Pack key: fold the Cicala in the main hand back into its briefcase. */
    public record PackC2S() {
        public PackC2S(FriendlyByteBuf b) { this(); }
        void write(FriendlyByteBuf b) { }
        void handle(Supplier<NetworkEvent.Context> ctx) {
            ServerPlayer p = ctx.get().getSender();
            ctx.get().setPacketHandled(true);
            if (p != null) recrafted.item.CicalaCaseItem.packHeld(p);
        }
    }
}
