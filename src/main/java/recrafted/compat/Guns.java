package recrafted.compat;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.ForgeRegistries;
import recrafted.Recrafted;
import recrafted.npc.NpcRole;

import javax.annotation.Nullable;
import java.util.function.Supplier;

/**
 * Firearms from Timeless and Classics Zero, when it is installed. Everything here is safe to call
 * without TACZ: the TACZ-facing code lives in {@link TaczBridge} and is only touched when the mod is loaded.
 */
public final class Guns {
    public static final ResourceLocation GUN_ITEM = new ResourceLocation("tacz", "modern_kinetic_gun");
    private static final org.apache.logging.log4j.Logger LOG = org.apache.logging.log4j.LogManager.getLogger("recrafted-guns");
    private static boolean loaded = ModList.get().isLoaded("tacz");

    private Guns() {}

    public static boolean loaded() { return loaded; }

    /** Calls into TACZ; a version whose API moved disables the gun features instead of crashing. */
    private static <T> T safely(Supplier<T> call, T fallback) {
        if (!loaded) return fallback;
        try {
            return call.get();
        } catch (LinkageError e) {
            loaded = false;
            LOG.error("This TACZ version doesn't match what Recrafted was built against; guards go unarmed", e);
            return fallback;
        }
    }

    /** Any TACZ firearm (the item TACZ uses for every gun). */
    public static boolean isGun(ItemStack stack) {
        return !stack.isEmpty() && GUN_ITEM.equals(ForgeRegistries.ITEMS.getKey(stack.getItem()));
    }

    /** Which gun from the Recrafted Arsenal pack each armed role carries. */
    @Nullable
    public static ResourceLocation sidearmId(NpcRole role) {
        String id = switch (role) {
            case ESTATE_GUARD -> "lupara";
            case BODYGUARD -> "vento";
            case HARBOUR_GUARD, SECURITY, LAB_GUARD -> "bastone";
            case SORDI -> "argento";
            default -> null;
        };
        return id == null ? null : new ResourceLocation(Recrafted.MODID, id);
    }

    /** A full, ready-to-fire sidearm for this role, or empty (unarmed role, TACZ or the gun pack missing). */
    public static ItemStack sidearmFor(NpcRole role) {
        ResourceLocation id = sidearmId(role);
        if (id == null) return ItemStack.EMPTY;
        return safely(() -> TaczBridge.loadedGun(id), ItemStack.EMPTY);
    }

    /** One reload's worth of the right ammunition for this gun, or empty. */
    public static ItemStack spareAmmo(ItemStack gun) {
        return isGun(gun) ? safely(() -> TaczBridge.spareAmmo(gun), ItemStack.EMPTY) : ItemStack.EMPTY;
    }

    /** How an NPC fires a given gun: shots per burst, ticks between shots, extra ticks between bursts. */
    public record Cadence(int burst, int interval, int pause) {}

    public static Cadence cadence(ItemStack gun) {
        int cap = capacity(gun);
        if (cap <= 6) return new Cadence(1, 18, 4);          // revolver: deliberate single shots
        if (cap <= 9) return new Cadence(1, 13, 6);          // single-stack pistol
        return new Cadence(3, 6, 22);                         // service pistol: short strings
    }

    /** A shoulder gun (shotgun, rifle, PDW...) rather than a handgun: slung on the back, not holstered. */
    public static boolean isLongGun(ItemStack gun) {
        return isGun(gun) && !"pistol".equals(safely(() -> TaczBridge.type(gun), "pistol"));
    }

    /** How close an NPC gets before it stops to shoot: shotguns have to be near to count. */
    public static double engageRange(ItemStack gun) {
        return "shotgun".equals(isGun(gun) ? safely(() -> TaczBridge.type(gun), "pistol") : "pistol") ? 8.0 : 15.0;
    }

    /** Magazine size of this gun (6 if unknown). */
    public static int capacity(ItemStack gun) {
        return isGun(gun) ? safely(() -> TaczBridge.capacity(gun), 6) : 6;
    }

    /** Tops the gun's magazine back up (an NPC reloading). */
    public static void refill(ItemStack gun) {
        if (isGun(gun)) safely(() -> { TaczBridge.refill(gun); return null; }, null);
    }

    /** An NPC has just put this gun in its main hand. */
    public static void npcDraw(net.minecraft.world.entity.LivingEntity npc) {
        safely(() -> { TaczBridge.npcDraw(npc); return null; }, null);
    }

    /** An NPC pulls the trigger, aiming along pitch/yaw. Returns TACZ's result name ("SUCCESS", "COOL_DOWN", ...). */
    public static String npcShoot(net.minecraft.world.entity.LivingEntity npc, float pitch, float yaw) {
        return safely(() -> TaczBridge.npcShoot(npc, pitch, yaw), "NO_TACZ");
    }

    /** Fires TACZ's gunfire event as if this player had shot this gun (dev tests). */
    public static void simulateShot(net.minecraft.server.level.ServerPlayer p, ItemStack gun) {
        safely(() -> { TaczBridge.simulateShot(p, gun); return null; }, null);
    }

    /** Hooks gunfire into the mission (noise, witnesses). Call once at startup. */
    public static void init() {
        safely(() -> { TaczBridge.register(); return null; }, null);
    }
}
