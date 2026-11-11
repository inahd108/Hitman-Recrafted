package recrafted.client;

import net.minecraft.client.Minecraft;
import recrafted.net.Net;

/** Client-side packet handling. Only ever loaded on the physical client. */
public final class ClientHandlers {
    private ClientHandlers() {}

    public static void disguise(Net.DisguiseS2C m) {
        if (m.role().isEmpty()) ClientState.DISGUISES.remove(m.player());
        else ClientState.DISGUISES.put(m.player(), m.role() + "_" + m.variant());
    }

    public static void hud(Net.HudS2C m) {
        ClientState.missionActive = m.active();
        ClientState.missionTitle = m.title();
        ClientState.status = m.status();
        ClientState.suspicion = m.suspicion();
        ClientState.zoneLabel = m.zone();
        ClientState.disguiseLabel = m.disguise();
        ClientState.dragging = m.dragging();
        ClientState.OBJECTIVES.clear();
        ClientState.OBJECTIVES.addAll(m.objectives());
        ClientState.OBJECTIVES_DONE.clear();
        ClientState.OBJECTIVES_DONE.addAll(m.done());
    }

    public static void route(Net.RouteS2C m) {
        ClientState.selectedNpc = m.entityId();
        ClientState.selectedRoute = m.route();
        Minecraft mc = Minecraft.getInstance();
        if (m.open()) {
            mc.setScreen(new RouteScreen(m.entityId(), m.name(), m.route().copy(), m.frozen()));
        } else if (mc.screen instanceof RouteScreen rs && rs.entityId == m.entityId()) {
            rs.frozen = m.frozen();
        }
    }

    public static void npcScreen(Net.NpcScreenS2C m) {
        Minecraft.getInstance().setScreen(new NpcEditScreen(m));
    }
}
