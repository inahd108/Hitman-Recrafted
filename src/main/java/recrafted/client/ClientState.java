package recrafted.client;

import recrafted.npc.NpcEntity;
import recrafted.npc.Route;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Plain client-side state. Deliberately free of client-only classes so common code
 * (the NPC entity) can ask it questions on either side.
 */
public final class ClientState {
    private ClientState() {}

    // focus vision
    public static boolean focus;
    // route editor
    public static int selectedNpc = -1;
    public static Route selectedRoute;
    public static boolean holdingPlanner;
    // disguises of players in view: uuid -> "role/variant"
    public static final Map<UUID, String> DISGUISES = new HashMap<>();
    // hud
    public static boolean missionActive;
    public static String missionTitle = "";
    public static int status;
    public static float suspicion;
    public static String zoneLabel = "";
    public static String disguiseLabel = "";
    public static boolean dragging;
    public static final List<String> OBJECTIVES = new ArrayList<>();
    public static final List<Boolean> OBJECTIVES_DONE = new ArrayList<>();

    public static boolean shouldGlow(NpcEntity npc) {
        if (holdingPlanner && npc.getId() == selectedNpc) return true;
        return focus && (npc.isTarget() || npc.getRole().guard || npc.isEnforcer());
    }

    public static int glowColor(NpcEntity npc) {
        if (holdingPlanner && npc.getId() == selectedNpc) return 0x40E0FF;
        if (npc.isTarget()) return 0xFF2A2A;
        if (npc.isEnforcer()) return 0xFFFFFF;
        return 0x4F8DFF;
    }
}
