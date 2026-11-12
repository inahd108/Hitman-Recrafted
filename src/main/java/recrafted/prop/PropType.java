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
    LEDGER(Kind.MISC, 0),
    CLOG(Kind.BLUNT, Flag.THROW),
    CHEESE_WHEEL(Kind.BLUNT, Flag.THROW),
    DELFT_VASE(Kind.BLUNT, Flag.THROW | Flag.BREAKS),
    JENEVER(Kind.BLUNT, Flag.THROW | Flag.BREAKS),
    BOAT_HOOK(Kind.BLUNT, 0),
    CHAIN_LOCK(Kind.WIRE, 0),
    PALETTE_KNIFE(Kind.SHARP, Flag.THROW),
    GAVEL(Kind.BLUNT, 0),
    UMBRELLA(Kind.BLUNT, 0),
    TURPENTINE(Kind.MISC, 0),
    TULIP_BULBS(Kind.EMETIC, 0),
    LEAD_WHITE(Kind.LETHAL, 0),
    BIDDER_PADDLE(Kind.KEYCARD, 0),
    BRIDGE_KEY(Kind.KEYCARD, 0),
    PRESS_CAMERA(Kind.MISC, 0);

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

    /** An extra line for props that do something of their own. */
    public String note() {
        return switch (this) {
            case BOAT_HOOK -> "Attack to shove someone off a quay or a deck. Non-swimmers don't come up.";
            case CHAIN_LOCK -> "A bike lock. Nobody minds you carrying one.";
            case UMBRELLA -> "Held up in the rain, it hides your face: people who know you take longer to notice.";
            case GAVEL -> "Nobody looks twice at it inside the Gulden Hamer.";
            case TURPENTINE -> "Use it on a stove. The next person to stand at it gets a flash fire.";
            case BIDDER_PADDLE -> "Bidders may go into the saleroom.";
            case BRIDGE_KEY -> "Unlocks the drawbridge lever and the sluice wheel.";
            case PRESS_CAMERA -> "Use it: the flash blinds whoever is looking at you for a moment.";
            case CHEESE_WHEEL -> "Heavy. Doesn't fly far.";
            case LEAD_WHITE -> "Pigment. Very bad for you, slowly.";
            case TULIP_BULBS -> "Look like onions. Are not onions.";
            default -> "";
        };
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
            case MISC -> this == LEDGER ? "Every lot, every buyer, every guilder. The Agency wants it."
                    : this == TURPENTINE || this == PRESS_CAMERA ? "" : "Somebody left this lying around.";
        };
    }
}
