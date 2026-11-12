package recrafted.npc;

import java.util.Locale;

/** What an NPC does while it waits at a waypoint. Drives the animation. */
public enum NpcPose {
    STAND("Stand"), GUARD("Stand guard"), SIT("Sit"), LEAN("Lean"), PHONE("On the phone"), SMOKE("Smoke"),
    DRINK("Drink"), EAT("Eat"), WORK("Work with hands"), SWEEP("Sweep"), TYPE("Type / write"), TALK("Talk"),
    LOOK("Look around"), WAVE("Wave"), CROUCH("Crouch"), SLEEP("Lie down"), DANCE("Dance"), PRAY("Pray"),
    /** Seated, pistol resting in the right hand (the title-screen operative). */
    SIT_ARMED("Sit, armed");

    public final String id;
    public final String label;

    NpcPose(String label) {
        this.id = name().toLowerCase(Locale.ROOT);
        this.label = label;
    }

    public static NpcPose byId(String id) {
        for (NpcPose p : values()) if (p.id.equals(id)) return p;
        return STAND;
    }

    public static NpcPose byOrdinal(int i) {
        NpcPose[] v = values();
        return i >= 0 && i < v.length ? v[i] : STAND;
    }

    public boolean seated() {
        return this == SIT || this == SIT_ARMED;
    }
}
