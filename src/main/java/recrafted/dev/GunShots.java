package recrafted.dev;

import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.Recrafted;
import recrafted.mission.MissionManager;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

/**
 * Gun photo session for the TACZ gun pack, enabled with -Drecrafted.gunshots=id[+attachment],id,...
 * (see the runClient config). For every gun: first person idle, aiming, mid-reload, inspecting,
 * then a third-person shot. TACZ is driven through its public client API by reflection, so the
 * mod itself never needs TACZ on the compile classpath.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class GunShots {
    private static final Logger LOG = LogManager.getLogger("recrafted-gunshots");
    private static final String SPEC = System.getProperty("recrafted.gunshots", "");
    private static final List<Runnable> STEPS = new ArrayList<>();
    private static final List<Long> DELAYS = new ArrayList<>();
    private static int index = -1;
    private static long nextAt;
    private static boolean prepared;

    private GunShots() {}

    private static void step(long delayMs, Runnable r) {
        STEPS.add(r);
        DELAYS.add(delayMs);
    }

    private static Object operator(Minecraft mc) throws Exception {
        Class<?> c = Class.forName("com.tacz.guns.api.client.gameplay.IClientPlayerGunOperator");
        Method m = c.getMethod("fromLocalPlayer", net.minecraft.client.player.LocalPlayer.class);
        return m.invoke(null, mc.player);
    }

    private static void call(Minecraft mc, String method, Object... args) {
        try {
            Object op = operator(mc);
            for (Method m : op.getClass().getMethods()) {
                if (m.getName().equals(method) && m.getParameterCount() == args.length) {
                    m.invoke(op, args);
                    return;
                }
            }
            LOG.warn("GUNSHOTS no method {}", method);
        } catch (Exception e) {
            LOG.error("GUNSHOTS {} failed", method, e);
        }
    }

    /** TACZ re-reads the aim key every tick, so aiming goes through its controller hook. */
    private static void holdAim(boolean on) {
        try {
            Class.forName("com.tacz.guns.client.input.AimKey").getMethod("setControllerAimDown", boolean.class).invoke(null, on);
        } catch (Exception e) {
            LOG.error("GUNSHOTS aim failed", e);
        }
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "gun_" + name.replace(':', '_') + ".png", mc.getMainRenderTarget(),
                c -> LOG.info("GUNSHOTS saved {}", name));
    }

    private static void prepare() {
        Minecraft mc = Minecraft.getInstance();
        for (String raw : SPEC.split(",")) {
            if (raw.isBlank()) continue;
            String[] parts = raw.trim().split("\\+");
            String gun = parts[0];
            String attachment = parts.length > 1 ? parts[1] : null;
            String label = gun + (attachment != null ? "_supp" : "");
            step(500, () -> {
                IntegratedServer server = mc.getSingleplayerServer();
                server.execute(() -> {
                    ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
                    try {
                        StringBuilder nbt = new StringBuilder("{id:\"tacz:modern_kinetic_gun\",Count:1b,tag:{GunId:\"" + gun
                                + "\",GunCurrentAmmoCount:" + Integer.getInteger("recrafted.gunshots.ammo", 2)
                                + ",HasBulletInBarrel:" + (Integer.getInteger("recrafted.gunshots.ammo", 2) > 0 ? "1b" : "0b")
                                + ",GunFireMode:\"SEMI\"");
                        if (attachment != null) {
                            nbt.append(",AttachmentMUZZLE:{id:\"tacz:attachment\",Count:1b,tag:{AttachmentId:\"").append(attachment).append("\"}}");
                        }
                        nbt.append("}}");
                        CompoundTag tag = TagParser.parseTag(nbt.toString());
                        sp.getInventory().setItem(sp.getInventory().selected, ItemStack.of(tag));
                    } catch (Exception e) {
                        LOG.error("GUNSHOTS could not build {}", gun, e);
                    }
                });
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                faceSpot(server);
            });
            step(3500, () -> shot(mc, label + "_1_idle"));
            step(200, () -> holdAim(true));
            step(1600, () -> shot(mc, label + "_2_aim"));
            step(200, () -> holdAim(false));
            step(1200, () -> call(mc, "reload"));
            phase(mc, label, "reload", System.getProperty("recrafted.gunshots.reload", "450,1100"),
                    Long.getLong("recrafted.gunshots.reloadLen", 4300L), new String[]{"_3_reload_a", "_4_reload_b"});
            step(0, () -> call(mc, "inspect"));
            phase(mc, label, "inspect", System.getProperty("recrafted.gunshots.inspect", "1150,2650"),
                    Long.getLong("recrafted.gunshots.inspectLen", 6650L), new String[]{"_5_inspect_a", "_5_inspect_b"});
            step(0, () -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT));
            step(1500, () -> shot(mc, label + "_6_third"));
        }
        step(1500, () -> {
            LOG.info("GUNSHOTS DONE");
            mc.stop();
        });
    }

    /** Screenshots at the given times (ms after the action started), then wait out the action's length. */
    private static void phase(Minecraft mc, String label, String what, String times, long length, String[] names) {
        long last = 0;
        String[] ts = times.split(";|,");
        for (int i = 0; i < ts.length; i++) {
            long t = Long.parseLong(ts[i].trim());
            String name = label + (i < names.length ? names[i] : "_" + what + "_" + (char) ('a' + i));
            step(t - last, () -> shot(mc, name));
            last = t;
        }
        step(Math.max(0, length - last), () -> { });
    }

    /** Stand on the quay looking out to sea: a bright, plain background for the gun. */
    private static void faceSpot(IntegratedServer server) {
        String[] at = System.getProperty("recrafted.gunshots.at", "160.5,66,200.5,0,4").split(",");
        server.execute(() -> {
            ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
            ServerLevel level = MissionManager.missionLevel(server);
            sp.setGameMode(GameType.CREATIVE);
            sp.teleportTo(level, Double.parseDouble(at[0]), Double.parseDouble(at[1]), Double.parseDouble(at[2]),
                    Float.parseFloat(at[3]), Float.parseFloat(at[4]));
            sp.connection.teleport(Double.parseDouble(at[0]), Double.parseDouble(at[1]), Double.parseDouble(at[2]),
                    Float.parseFloat(at[3]), Float.parseFloat(at[4]));
        });
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (SPEC.isEmpty() || e.phase != TickEvent.Phase.END) return;
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
            prepare();
            nextAt = now + 8000;
            faceSpot(server);
            mc.options.hideGui = false;          // F1 mode would also hide the hand and the gun
            return;
        }
        if (now < nextAt || index >= STEPS.size() - 1) return;
        index++;
        try {
            STEPS.get(index).run();
        } catch (Exception ex) {
            LOG.error("GUNSHOTS step {} failed", index, ex);
        }
        nextAt = now + (index + 1 < DELAYS.size() ? DELAYS.get(index + 1) : 1000);
    }
}
