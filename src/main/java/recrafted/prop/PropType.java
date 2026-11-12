package recrafted.prop;

import java.util.Locale;

/** Every pick-up-and-use prop in the mod. One item is registered per entry. */
public enum PropType {
    // blunt: knock out
    WRENCH(Kind.BLUNT, Flag.THROW | Flag.SABOTAGE),
    CROWBAR(Kind.BLUNT, Flag.THROW | Flag.FORCE | Flag.ILLEGAL),
    HAMMER(Kind.BLUNT, Flag.THROW),
    LEAD_PIPE(Kind.BLUNT, Flag.THROW | Flag.ILLEGAL),
    BRICK(Kind.BLUNT, Flag.THROW),
    BOTTLE(Kind.BLUNT, Flag.THROW | Flag.BREAKS),
    FRYING_PAN(Kind.BLUNT, Flag.THROW),
    ROLLING_PIN(Kind.BLUNT, Flag.THROW),
    FISH(Kind.BLUNT, Flag.THROW),
    OAR(Kind.BLUNT, 0),
    SHOVEL(Kind.BLUNT, 0),
    GOLF_CLUB(Kind.BLUNT, 0),
    BROOM(Kind.BLUNT, 0),
    BATON(Kind.BLUNT, Flag.ILLEGAL),
    CANDLESTICK(Kind.BLUNT, Flag.THROW),
    FIRE_EXTINGUISHER(Kind.BLUNT, Flag.THROW),
    NEWSPAPER(Kind.MISC, 0),
    // sharp: lethal
    KITCHEN_KNIFE(Kind.SHARP, Flag.THROW | Flag.ILLEGAL),
    CLEAVER(Kind.SHARP, Flag.THROW | Flag.ILLEGAL),
    SCISSORS(Kind.SHARP, Flag.THROW),
    LETTER_OPENER(Kind.SHARP, Flag.THROW),
    SCREWDRIVER(Kind.SHARP, Flag.THROW | Flag.SABOTAGE),
    GARDEN_SHEARS(Kind.SHARP, 0),
    FIRE_AXE(Kind.SHARP, Flag.ILLEGAL),
    FISHING_GAFF(Kind.SHARP, 0),
    CORKSCREW(Kind.SHARP, 0),
    SCALPEL(Kind.SHARP, Flag.THROW | Flag.ILLEGAL),
    FIBER_WIRE(Kind.WIRE, Flag.ILLEGAL),
    // distractions
    COIN(Kind.COIN, Flag.THROW),
    POCKET_RADIO(Kind.RADIO, Flag.THROW),
    // chemistry
    EMETIC_POISON(Kind.EMETIC, Flag.ILLEGAL),
    RAT_POISON(Kind.EMETIC, 0),
    LETHAL_POISON(Kind.LETHAL, Flag.ILLEGAL),
    SEDATIVE(Kind.SEDATIVE, Flag.ILLEGAL),
    SYRINGE(Kind.INJECT, Flag.ILLEGAL),
    // access
    LOCKPICK(Kind.LOCKPICK, Flag.ILLEGAL),
    KEYCARD_LAB(Kind.KEYCARD, 0),
    KEYCARD_ESTATE(Kind.KEYCARD, 0),
    KEYCARD_HARBOUR(Kind.KEYCARD, 0),
    // Amsterdam
    LEDGER(Kind.MISC, 0);

    public enum Kind { BLUNT, SHARP, WIRE, COIN, RADIO, EMETIC, LETHAL, SEDATIVE, INJECT, LOCKPICK, KEYCARD, MISC }

    public static final class Flag {
        public static final int THROW = 1, SABOTAGE = 2, FORCE = 4, ILLEGAL = 8, BREAKS = 16;
    }

    public final String id;
    public final Kind kind;
    private final int flags;

    PropType(Kind kind, int flags) {
        this.id = name().toLowerCase(Locale.ROOT);
        this.kind = kind;
        this.flags = flags;
    }

    public boolean throwable() { return (flags & Flag.THROW) != 0; }
    public boolean sabotages() { return (flags & Flag.SABOTAGE) != 0; }
    public boolean forces() { return (flags & Flag.FORCE) != 0; }
    /** Carrying it openly raises suspicion unless your outfit explains it. */
    public boolean illegal() { return (flags & Flag.ILLEGAL) != 0; }
    public boolean breaks() { return (flags & Flag.BREAKS) != 0; }
    public boolean lethalMelee() { return kind == Kind.SHARP || kind == Kind.WIRE; }
    public boolean stacks() {
        return kind == Kind.COIN || kind == Kind.EMETIC || kind == Kind.LETHAL || kind == Kind.SEDATIVE
                || kind == Kind.INJECT || this == BRICK || this == BOTTLE;
    }

    public String tooltip() {
        return switch (kind) {
            case BLUNT -> "Blunt. Knocks a target out" + (throwable() ? "; can be thrown." : ".");
            case SHARP -> "Lethal" + (throwable() ? "; can be thrown." : ".");
            case WIRE -> "Silent and lethal. Only from behind.";
            case COIN -> "Throw it. Somebody always goes to look.";
            case RADIO -> "Throw it. Plays loudly for a while where it lands.";
            case EMETIC -> "Use on a meal or a drink. The victim runs for privacy.";
            case LETHAL -> "Use on a meal or a drink. Looks like bad luck.";
            case SEDATIVE -> "Use on someone from behind. They sleep.";
            case INJECT -> "Use on someone from behind. They don't wake up.";
            case LOCKPICK -> "Opens card readers quietly. Sometimes snaps.";
            case KEYCARD -> "Opens matching card readers.";
            case MISC -> this == LEDGER ? "Every lot, every buyer, every guilder. The Agency wants it." : "Somebody left this lying around.";
        };
    }
}
