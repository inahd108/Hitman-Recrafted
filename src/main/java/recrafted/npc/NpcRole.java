package recrafted.npc;

import java.util.Locale;

/** Who an NPC is. Also the set of outfits the player can wear. */
public enum NpcRole {
    CIVILIAN("Civilian", 6, false, false),
    TOURIST("Tourist", 6, false, false),
    FISHERMAN("Fisherman", 2, false, true),
    SHOPKEEPER("Shopkeeper", 2, false, false),
    WAITER("Waiter", 4, false, true),
    COOK("Cook", 3, false, true),
    CLEANER("Cleaner", 3, false, true),
    GARDENER("Gardener", 2, false, true),
    PRIEST("Priest", 1, false, true),
    WORKER("Cannery Worker", 2, false, true),
    HARBOUR_GUARD("Harbour Police", 2, true, true),
    ESTATE_GUARD("Estate Guard", 2, true, true),
    BODYGUARD("Bodyguard", 2, true, true),
    SECURITY("Halcyon Security", 2, true, true),
    LAB_GUARD("Virus Lab Guard", 1, true, true),
    SCIENTIST("Scientist", 2, false, true),
    HAZMAT("Hazmat Technician", 1, false, true),
    BELMONTE("Marco Belmonte", 1, false, false),
    VARGA("Dr. Ilse Varga", 1, false, false),
    SORDI("Capitano Sordi", 1, true, false),
    /** The operative from the title screen. Not part of any mission cast. */
    AGENT("Operative", 1, false, false),
    // ---- Amsterdam (Oil & Water) ----
    COURIER("Cycle Courier", 2, false, true),
    SKIPPER("Boat Skipper", 2, false, true),
    HOUSEBOATER("Houseboat Resident", 2, false, false),
    FLOWER_SELLER("Flower Seller", 2, false, true),
    HERRING_VENDOR("Herring Vendor", 1, false, true),
    BARTENDER("Bartender", 2, false, true),
    ORGANIST("Street Organist", 1, false, false),
    POLICE("Politie Officer", 2, true, true),
    AUCTION_SECURITY("Auction Security", 2, true, true),
    LOT_PORTER("Lot Porter", 2, false, true),
    COLLECTOR("Art Collector", 3, false, true),
    PHOTOGRAPHER("Press Photographer", 2, false, true),
    APPRENTICE("Apprentice Painter", 1, false, true),
    BRIDGE_KEEPER("Bridge Keeper", 1, false, true),
    DECKHAND("Deckhand", 2, true, true),
    PORTER("Warehouse Porter", 2, false, true),
    OSTENDORP("Margriet Ostendorp", 1, false, false),
    KOOISTRA("Sem Kooistra", 1, true, false);

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
        return guard || this == SCIENTIST || this == HAZMAT || this == VARGA || this == WORKER
                || this == LOT_PORTER || this == BRIDGE_KEEPER || this == OSTENDORP;
    }

    /** Roles that come when a fuse box sparks. */
    public boolean fixesThings() {
        return this == WORKER || this == SECURITY || this == ESTATE_GUARD || this == GARDENER
                || this == PORTER || this == BRIDGE_KEEPER || this == AUCTION_SECURITY;
    }

    public float visionRange() {
        return guard ? 20f : 14f;
    }
}
