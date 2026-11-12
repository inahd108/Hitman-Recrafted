package recrafted.npc;

import java.util.Locale;

/** Who an NPC is. Also the set of outfits the player can wear. */
public enum NpcRole {
    CIVILIAN("Civilian", 3, false, false),
    TOURIST("Tourist", 3, false, false),
    FISHERMAN("Fisherman", 2, false, true),
    SHOPKEEPER("Shopkeeper", 2, false, false),
    WAITER("Waiter", 2, false, true),
    COOK("Cook", 2, false, true),
    CLEANER("Cleaner", 2, false, true),
    GARDENER("Gardener", 2, false, true),
    PRIEST("Priest", 1, false, true),
    WORKER("Cannery Worker", 2, false, true),
    HARBOUR_GUARD("Harbour Police", 2, true, true),
    ESTATE_GUARD("Estate Guard", 2, true, true),
    BODYGUARD("Bodyguard", 1, true, true),
    SECURITY("Halcyon Security", 2, true, true),
    LAB_GUARD("Virus Lab Guard", 1, true, true),
    SCIENTIST("Scientist", 2, false, true),
    HAZMAT("Hazmat Technician", 1, false, true),
    BELMONTE("Marco Belmonte", 1, false, false),
    VARGA("Dr. Ilse Varga", 1, false, false),
    SORDI("Capitano Sordi", 1, true, false),
    /** The operative from the title screen. Not part of any mission cast. */
    AGENT("Operative", 1, false, false);

    public final String id;
    public final String title;
    public final int variants;
    /** Guards fight back, respond to alarms and may carry weapons openly. */
    public final boolean guard;
    /** Can the player take this outfit as a disguise? */
    public final boolean wearable;

    NpcRole(String title, int variants, boolean guard, boolean wearable) {
        this.id = name().toLowerCase(Locale.ROOT);
        this.title = title;
        this.variants = variants;
        this.guard = guard;
        this.wearable = wearable;
    }

    public static NpcRole byId(String id) {
        for (NpcRole r : values()) if (r.id.equals(id)) return r;
        return CIVILIAN;
    }

    public static NpcRole byIdOrNull(String id) {
        for (NpcRole r : values()) if (r.id.equals(id)) return r;
        return null;
    }

    /** Staff who pass security doors on their own. */
    public boolean opensSecurityDoors() {
        return guard || this == SCIENTIST || this == HAZMAT || this == VARGA || this == WORKER;
    }

    /** Roles that come when a fuse box sparks. */
    public boolean fixesThings() {
        return this == WORKER || this == SECURITY || this == ESTATE_GUARD || this == GARDENER;
    }

    public float visionRange() {
        return guard ? 20f : 14f;
    }
}
