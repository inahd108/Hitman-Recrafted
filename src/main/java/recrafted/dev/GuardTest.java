package recrafted.dev;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.compat.Guns;
import recrafted.entity.PropEntity;
import recrafted.mission.MissionManager;
import recrafted.mission.Throwing;
import recrafted.npc.Gunfight;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;

import java.util.ArrayList;
import java.util.List;

/**
 * Armed-guard check, enabled with -Drecrafted.guardtest=true (gradle -Pguardtest). Spawns armed guards
 * on the quay, knocks one out, picks up the dropped gun, throws it at a second guard, fires a shot near
 * two civilians, then lets an armed guard draw and shoot at the player. Logs GUARDTEST ok/FAIL per check, saves screenshots, then closes the game.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class GuardTest {
    private static final Logger LOG = LogManager.getLogger("recrafted-guardtest");
    private static final boolean ENABLED = Boolean.getBoolean("recrafted.guardtest");
    private static final double X = 160.5, Y = 66, Z = 200.5;

    private static final List<Runnable> STEPS = new ArrayList<>();
    private static final List<Long> DELAYS = new ArrayList<>();
    private static int index = -1;
    private static long nextAt;
    private static boolean prepared;
    private static int failures;
    private static NpcEntity guardA, guardB, watcher, deaf, gunman;
    private static float healthBefore;

    private GuardTest() {}

    private static void step(long delayMs, Runnable r) {
        STEPS.add(r);
        DELAYS.add(delayMs);
    }

    private static void check(String what, boolean ok, Object detail) {
        if (!ok) failures++;
        LOG.info("GUARDTEST {} {} ({})", ok ? "ok  " : "FAIL", what, detail);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "guard_" + name + ".png", mc.getMainRenderTarget(), c -> LOG.info("GUARDTEST saved {}", name));
    }

    private static NpcEntity spawn(ServerLevel level, NpcRole role, String name, double x, double z, float yaw) {
        NpcEntity n = ModRegistry.NPC.get().create(level);
        n.setRole(role);
        n.setCustomName(net.minecraft.network.chat.Component.literal(name));
        n.setSkin(0);
        n.moveTo(x, Y, z, yaw, 0f);
        n.setYHeadRot(yaw);
        n.yBodyRot = yaw;
        n.frozen = true;
        n.arm(Guns.sidearmFor(role));
        level.addFreshEntity(n);
        return n;
    }

    private static List<PropEntity> gunDropsNear(ServerLevel level, Entity e) {
        return level.getEntitiesOfClass(PropEntity.class, e.getBoundingBox().inflate(3), p -> Guns.isGun(p.getItem()));
    }

    private static void look(IntegratedServer server, double x, double y, double z, float yaw, float pitch) {
        server.execute(() -> {
            ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
            sp.teleportTo(MissionManager.missionLevel(server), x, y, z, yaw, pitch);
            sp.connection.teleport(x, y, z, yaw, pitch);
        });
    }

    private static void onServer(IntegratedServer server, java.util.function.BiConsumer<ServerLevel, ServerPlayer> work) {
        server.execute(() -> {
            try {
                work.accept(MissionManager.missionLevel(server), server.getPlayerList().getPlayers().get(0));
            } catch (Exception ex) {
                failures++;
                LOG.error("GUARDTEST step crashed", ex);
            }
        });
    }

    /** Removes test guards, civilians and gun pickups left around the quay by this test. */
    private static void cleanUp(ServerLevel level) {
        net.minecraft.world.phys.AABB box = new net.minecraft.world.phys.AABB(X - 24, Y - 6, Z - 24, X + 24, Y + 6, Z + 24);
        level.getEntitiesOfClass(NpcEntity.class, box, n -> n.getName().getString().startsWith("Test ")).forEach(Entity::discard);
        level.getEntitiesOfClass(PropEntity.class, box, p -> Guns.isGun(p.getItem())).forEach(Entity::discard);
    }

    private static void prepare(Minecraft mc, IntegratedServer server) {
        step(500, () -> onServer(server, (level, sp) -> {
            cleanUp(level);
            sp.setGameMode(GameType.SURVIVAL);
            sp.getInventory().clearContent();
            guardA = spawn(level, NpcRole.ESTATE_GUARD, "Test Estate Guard", X + 1.2, Z + 3.0, 90f);
            guardB = spawn(level, NpcRole.HARBOUR_GUARD, "Test Harbour Guard", X - 1.6, Z + 3.4, 90f);
            check("estate guard carries the Lupara", Guns.isGun(guardA.getSidearm())
                    && guardA.getSidearm().getOrCreateTag().getString("GunId").equals("recrafted:lupara"), guardA.getSidearm().getTag());
            check("Halcyon security carry the Bulwark AR", Guns.sidearmFor(NpcRole.SECURITY).getOrCreateTag().getString("GunId").equals("recrafted:bulwark"), "");
            check("lab guards carry the Halcyon PDW", Guns.sidearmFor(NpcRole.LAB_GUARD).getOrCreateTag().getString("GunId").equals("recrafted:halcyon")
                    && Guns.isLongGun(Guns.sidearmFor(NpcRole.LAB_GUARD)), "");
            check("bodyguards carry the Vento", Guns.sidearmFor(NpcRole.BODYGUARD).getOrCreateTag().getString("GunId").equals("recrafted:vento"), "");
            check("the Lupara counts as a long gun, the Bastone doesn't", Guns.isLongGun(guardA.getSidearm())
                    && !Guns.isLongGun(guardB.getSidearm()), "");
            check("harbour guard carries the Bastone", guardB.getSidearm().getOrCreateTag().getString("GunId").equals("recrafted:bastone"),
                    guardB.getSidearm().getTag());
            check("civilians are unarmed", Guns.sidearmFor(NpcRole.CIVILIAN).isEmpty(), "");
        }));
        step(200, () -> look(server, X, Y, Z, 0f, 12f));
        step(3000, () -> { mc.getToasts().clear(); shot(mc, "01_holstered"); });
        // close-ups of the estate guard's holster: from its right side, then from the front
        step(200, () -> look(server, X + 1.2, Y, Z + 1.5, 0f, 38f));
        step(1500, () -> shot(mc, "01b_holster_side"));
        step(200, () -> look(server, X - 0.4, Y, Z + 3.0, -90f, 38f));
        step(1500, () -> shot(mc, "01c_holster_front"));
        step(200, () -> look(server, X + 3.6, Y - 0.2, Z + 3.0, 90f, 8f));
        step(1500, () -> shot(mc, "01d_sling_back"));
        step(200, () -> look(server, X + 1.2, Y - 0.2, Z + 0.4, 0f, 8f));
        step(1500, () -> shot(mc, "01e_sling_side"));
        step(200, () -> look(server, X, Y, Z, 0f, 12f));
        step(300, () -> onServer(server, (level, sp) -> {
            guardA.knockOut(sp);
            List<PropEntity> drops = gunDropsNear(level, guardA);
            check("knocked-out guard no longer holsters a gun", guardA.getSidearm().isEmpty(), guardA.getSidearm());
            check("gun dropped beside the body", drops.size() == 1, drops.size());
            check("drop carries spare ammo", !drops.isEmpty() && drops.get(0).getExtras().size() == 1
                    && BuiltInRegistries.ITEM.getKey(drops.get(0).getExtras().get(0).getItem()).toString().equals("tacz:ammo"),
                    drops.isEmpty() ? "-" : drops.get(0).getExtras());
            check("dropped gun is tied to the contract run", !drops.isEmpty() && drops.get(0).missionGen == guardA.missionGen,
                    drops.isEmpty() ? "-" : drops.get(0).missionGen);
        }));
        step(200, () -> look(server, X, Y, Z, 0f, 42f));
        step(2500, () -> shot(mc, "02_dropped"));
        step(300, () -> onServer(server, (level, sp) -> {
            List<PropEntity> drops = gunDropsNear(level, guardA);
            if (!drops.isEmpty()) drops.get(0).interact(sp, InteractionHand.MAIN_HAND);
            ItemStack held = sp.getMainHandItem();
            check("picked-up gun is in hand", Guns.isGun(held), held);
            check("picked-up gun kept its NBT (loaded shotgun)", held.getOrCreateTag().getString("GunId").equals("recrafted:lupara")
                    && held.getOrCreateTag().getInt("GunCurrentAmmoCount") == 2, held.getTag());
            boolean ammo = sp.getInventory().items.stream().anyMatch(s -> BuiltInRegistries.ITEM.getKey(s.getItem()).toString().equals("tacz:ammo")
                    && s.getOrCreateTag().getString("AmmoId").equals("tacz:12g"));
            check("spare 12 gauge shells went into the inventory", ammo, sp.getInventory().items.stream().filter(s -> !s.isEmpty()).toList());
            check("drop is gone after pickup", gunDropsNear(level, guardA).isEmpty(), "");
        }));
        step(200, () -> look(server, X, Y, Z, 0f, 4f));
        step(2500, () -> shot(mc, "03_picked_up"));
        // throw the revolver at the harbour guard
        step(300, () -> onServer(server, (level, sp) -> {
            Vec3 eye = sp.getEyePosition();
            Vec3 to = guardB.position().add(0, 1.2, 0).subtract(eye);
            float yaw = (float) Math.toDegrees(Math.atan2(-to.x, to.z));
            float pitch = (float) -Math.toDegrees(Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)));
            sp.setYRot(yaw);
            sp.setXRot(pitch);
            sp.connection.teleport(sp.getX(), sp.getY(), sp.getZ(), yaw, pitch);
            Throwing.throwHeld(sp);
            check("gun left the hand when thrown", sp.getMainHandItem().isEmpty(), sp.getMainHandItem());
        }));
        step(1500, () -> onServer(server, (level, sp) -> {
            check("thrown gun knocked the guard out", guardB.getState() == NpcEntity.State.UNCONSCIOUS, guardB.getState());
            List<PropEntity> drops = gunDropsNear(level, guardB);
            boolean vento = drops.stream().anyMatch(d -> d.getItem().getOrCreateTag().getString("GunId").equals("recrafted:lupara"));
            boolean bastone = drops.stream().anyMatch(d -> d.getItem().getOrCreateTag().getString("GunId").equals("recrafted:bastone"));
            check("thrown shotgun landed as a pickup", vento, drops.size());
            check("second guard dropped the Bastone", bastone, drops.size());
        }));
        step(200, () -> look(server, X, Y, Z, -15f, 40f));
        step(2500, () -> shot(mc, "04_thrown"));
        // a gunshot: a civilian facing us sees it, one facing away only hears it
        step(300, () -> onServer(server, (level, sp) -> {
            watcher = spawn(level, NpcRole.CIVILIAN, "Test Watcher", X + 4, Z + 6, 180f);
            deaf = spawn(level, NpcRole.CIVILIAN, "Test Listener", X - 5, Z - 9, 180f);
            watcher.frozen = false;
            deaf.frozen = false;
        }));
        step(1000, () -> onServer(server, (level, sp) -> {
            ItemStack gun = Guns.sidearmFor(NpcRole.HARBOUR_GUARD);
            sp.setItemInHand(InteractionHand.MAIN_HAND, gun);
            sp.setYRot(0);
            sp.setXRot(0);
            Guns.simulateShot(sp, gun);
            check("witness facing the shooter is compromised", watcher.inCombat() || watcher.getState() == NpcEntity.State.FLEE,
                    watcher.getState());
            check("unseeing civilian heard it and comes to look", deaf.getSpeech().contains("gunshot"), "'" + deaf.getSpeech() + "'");
        }));
        step(200, () -> look(server, X, Y, Z, 0f, 4f));
        step(1500, () -> shot(mc, "05_gunshot"));
        // ---- a guard draws and fires -------------------------------------------------------------
        step(300, () -> onServer(server, (level, sp) -> {
            cleanUp(level);
            sp.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
            gunman = spawn(level, NpcRole.ESTATE_GUARD, "Test Gunman", X + 8.5, Z + 2.0, 90f);
        }));
        step(600, () -> onServer(server, (level, sp) -> {
            // posed: alert, gun drawn, aiming at where the player stands; frozen so the pose holds for photos
            gunman.onCompromised(sp);
            gunman.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, gunman.getSidearm().copy());
            gunman.setYHeadRot(90f);
            gunman.setXRot(4f);
            check("alert guard holds its gun", Guns.isGun(gunman.getMainHandItem()), gunman.getMainHandItem());
        }));
        step(200, () -> { mc.getToasts().clear(); look(server, X + 3.5, Y, Z + 2.0, -90f, 3f); });
        step(1500, () -> shot(mc, "06_aiming_front"));
        step(200, () -> look(server, X + 8.5, Y, Z - 1.6, 0f, 8f));
        step(1500, () -> shot(mc, "07_aiming_side"));
        step(200, () -> look(server, X + 5.2, Y, Z - 1.2, -45f, 8f));
        step(1500, () -> shot(mc, "07b_aiming_three_quarter"));
        // live fire: unfreeze and let it shoot at the player from about 8 blocks
        step(300, () -> onServer(server, (level, sp) -> {
            Gunfight.RESULTS.clear();
            sp.setHealth(sp.getMaxHealth());
            healthBefore = sp.getHealth();
            gunman.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, ItemStack.EMPTY);   // draw for real
            gunman.frozen = false;
            gunman.onCompromised(sp);
        }));
        step(100, () -> { mc.getToasts().clear(); look(server, X + 2.5, Y, Z + 2.0, -90f, 4f); });
        step(100, () -> mc.options.setCameraType(net.minecraft.client.CameraType.THIRD_PERSON_BACK));
        step(1800, () -> shot(mc, "08_firing_a"));
        step(350, () -> shot(mc, "08_firing_b"));
        step(350, () -> shot(mc, "08_firing_c"));
        step(350, () -> shot(mc, "08_firing_d"));
        step(100, () -> mc.options.setCameraType(net.minecraft.client.CameraType.FIRST_PERSON));
        step(900, () -> shot(mc, "09_firing_fp_a"));
        step(300, () -> shot(mc, "09_firing_fp_b"));
        step(2500, () -> onServer(server, (level, sp) -> {
            LOG.info("GUARDTEST balance: {} after the fight (from {}), results {}", sp.getHealth(), healthBefore, Gunfight.RESULTS);
            int ok = Gunfight.RESULTS.getOrDefault("SUCCESS", 0);
            check("guard fired real TACZ shots", ok >= 2, Gunfight.RESULTS);
            check("the player was hit", sp.getHealth() < healthBefore || sp.getCombatTracker().getCombatDuration() > 0
                    || sp.getLastDamageSource() != null, "health " + sp.getHealth() + " last " + sp.getLastDamageSource());
            check("guard keeps within its gun's range", gunman.distanceTo(sp) <= Guns.engageRange(gunman.getMainHandItem()) + 2.5,
                    String.format("%.1f blocks", gunman.distanceTo(sp)));
            gunman.frozen = true;
            sp.setHealth(sp.getMaxHealth());
        }));
        // ---- a lab guard with the PDW fires in bursts -------------------------------------------------
        step(300, () -> onServer(server, (level, sp) -> {
            cleanUp(level);
            Gunfight.RESULTS.clear();
            sp.setHealth(sp.getMaxHealth());
            healthBefore = sp.getHealth();
            gunman = spawn(level, NpcRole.LAB_GUARD, "Test Lab Gunman", X + 9.5, Z + 2.0, 90f);
            gunman.frozen = false;
        }));
        step(100, () -> { mc.getToasts().clear(); look(server, X, Y, Z + 2.0, -90f, 4f); });
        step(300, () -> onServer(server, (level, sp) -> gunman.onCompromised(sp)));
        step(2600, () -> shot(mc, "10_pdw_firing_a"));
        step(250, () -> shot(mc, "10_pdw_firing_b"));
        step(2000, () -> onServer(server, (level, sp) -> {
            LOG.info("GUARDTEST pdw balance: {} after the fight (from {}), results {}", sp.getHealth(), healthBefore, Gunfight.RESULTS);
            check("lab guard fires PDW bursts", Gunfight.RESULTS.getOrDefault("SUCCESS", 0) >= 5, Gunfight.RESULTS);
            gunman.frozen = true;
            sp.setHealth(sp.getMaxHealth());
        }));
        step(500, () -> onServer(server, (level, sp) -> cleanUp(level)));
        step(1000, () -> {
            LOG.info("GUARDTEST DONE failures={}", failures);
            mc.stop();
        });
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (!ENABLED || e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        long now = System.currentTimeMillis();
        if (mc.player == null || mc.level == null) {
            if (mc.screen != null && now > nextAt) {
                for (GuiEventListener l : mc.screen.children()) {
                    if (l instanceof Button b && (b.getMessage().getString().contains("Proceed")
                            || b.getMessage().getString().contains("Yes"))) {
                        b.onPress();
                        break;
                    }
                }
                nextAt = now + 1500;
            }
            return;
        }
        IntegratedServer server = mc.getSingleplayerServer();
        if (server == null || server.getPlayerList().getPlayers().isEmpty()) return;
        if (!prepared) {
            prepared = true;
            prepare(mc, server);
            look(server, X, Y, Z, 0f, 12f);
            mc.options.hideGui = false;
            nextAt = now + 8000;
            return;
        }
        if (now < nextAt || index >= STEPS.size() - 1) return;
        index++;
        try {
            STEPS.get(index).run();
        } catch (Exception ex) {
            failures++;
            LOG.error("GUARDTEST step {} failed", index, ex);
        }
        nextAt = now + (index + 1 < DELAYS.size() ? DELAYS.get(index + 1) : 1000);
    }
}
