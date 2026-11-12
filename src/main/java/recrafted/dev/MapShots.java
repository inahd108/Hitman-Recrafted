package recrafted.dev;

import net.minecraft.client.CloudStatus;
import net.minecraft.client.GraphicsStatus;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.Recrafted;
import recrafted.client.SkyTime;

import java.util.ArrayList;
import java.util.List;

/**
 * Screenshot tour of a map dimension while it is being built (-Pmapshots=amsterdam, see build.gradle).
 * Views come from -PmapViews="name:x,eyeY,z,yaw,pitch;..." and each is shot at every hour in -PmapTimes.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class MapShots {
    private static final Logger LOG = LogManager.getLogger("recrafted-mapshots");
    private static final String DIM = System.getProperty("recrafted.mapshots", "");
    private static final List<Runnable> STEPS = new ArrayList<>();
    private static final List<Long> DELAYS = new ArrayList<>();
    private static int index = -1;
    private static long nextAt;
    private static boolean prepared;
    private static final boolean GUI = Boolean.getBoolean("recrafted.mapshots.gui");

    private MapShots() {}

    private static void step(long delay, Runnable r) {
        STEPS.add(r);
        DELAYS.add(delay);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "map_" + name + ".png", mc.getMainRenderTarget(), c -> LOG.info("MAPSHOTS saved {}", name));
    }

    private static final String[] GATES = System.getProperty("recrafted.mapshots.gates", "").split(",");

    private static ServerLevel level(IntegratedServer server) {
        return server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(Recrafted.MODID, DIM)));
    }

    /** A camera in a boat's own frame: x across, y up from the waterline, z towards the bow; yaw relative to its heading. */
    private static void follow(IntegratedServer server, String boat, double lx, double ly, double lz, float yaw, float pitch) {
        server.execute(() -> {
            ServerLevel level = level(server);
            if (level == null) return;
            recrafted.boat.CanalBoat b = null;
            for (net.minecraft.world.entity.Entity e : level.getAllEntities()) {
                if (e instanceof recrafted.boat.CanalBoat cb && cb.name.equals(boat)) b = cb;
            }
            if (b == null) {
                LOG.error("MAPSHOTS no boat {}", boat);
                return;
            }
            net.minecraft.world.phys.Vec3 at = b.local(lx, ly, lz);
            ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
            sp.setGameMode(GameType.SPECTATOR);
            float y = b.getYRot() + yaw;
            sp.teleportTo(level, at.x, at.y - sp.getEyeHeight(), at.z, y, pitch);
        });
    }

    private static void camera(IntegratedServer server, double x, double eyeY, double z, float yaw, float pitch) {
        server.execute(() -> {
            ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
            ResourceKey<Level> key = ResourceKey.create(Registries.DIMENSION, new ResourceLocation(Recrafted.MODID, DIM));
            ServerLevel level = server.getLevel(key);
            if (level == null) {
                LOG.error("MAPSHOTS no dimension {}", key.location());
                return;
            }
            sp.setGameMode(GameType.SPECTATOR);
            double y = eyeY - sp.getEyeHeight();
            sp.teleportTo(level, x, y, z, yaw, pitch);
            sp.connection.teleport(x, y, z, yaw, pitch);
        });
    }

    private static void prepare(Minecraft mc, IntegratedServer server) {
        mc.options.hideGui = !GUI;
        mc.options.fov().set(Integer.getInteger("recrafted.mapshots.fov", 60));
        mc.options.renderDistance().set(Integer.getInteger("recrafted.mapshots.distance", 16));
        mc.options.graphicsMode().set(GraphicsStatus.FANCY);
        mc.options.cloudStatus().set(CloudStatus.FANCY);
        mc.options.ambientOcclusion().set(true);
        mc.levelRenderer.allChanged();
        if (Boolean.getBoolean("recrafted.mapshots.start")) {
            step(500, () -> server.execute(() -> {
                ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
                recrafted.mission.MissionManager.start(sp, DIM);
            }));
            step(4000, () -> { });
        }
        String[] times = System.getProperty("recrafted.mapshots.times", "-1").split(",");
        long settle = Long.getLong("recrafted.mapshots.settle", 15000L);
        boolean first = true;
        for (String view : System.getProperty("recrafted.mapshots.views", "").split(";")) {
            if (view.isBlank()) continue;
            String[] nv = view.split(":");
            String[] p = nv[1].split(",");
            if (p[0].startsWith("@")) {                     // @boat,lx,ly,lz,yaw,pitch[,delayMs]
                double lx = Double.parseDouble(p[1]), ly = Double.parseDouble(p[2]), lz = Double.parseDouble(p[3]);
                float yaw = Float.parseFloat(p[4]), pitch = Float.parseFloat(p[5]);
                long wait = p.length > 6 ? Long.parseLong(p[6]) : 500;
                step(wait, () -> follow(server, p[0].substring(1), lx, ly, lz, yaw, pitch));
                step(first ? settle + 10000 : 2500, () -> follow(server, p[0].substring(1), lx, ly, lz, yaw, pitch));
                first = false;
                step(300, () -> shot(mc, nv[0]));
                continue;
            }
            double x = Double.parseDouble(p[0]), y = Double.parseDouble(p[1]), z = Double.parseDouble(p[2]);
            float yaw = Float.parseFloat(p[3]), pitch = Float.parseFloat(p[4]);
            step(500, () -> camera(server, x, y, z, yaw, pitch));
            for (String t : times) {
                long time = Long.parseLong(t.trim());
                step(first ? settle + 10000 : settle, () -> SkyTime.override = time);
                first = false;
                step(1200, () -> shot(mc, nv[0] + (time >= 0 ? "_t" + time : "")));
                settle = 1500;
            }
            settle = Long.getLong("recrafted.mapshots.settle", 15000L);
        }
        step(1500, () -> {
            SkyTime.override = -1;
            LOG.info("MAPSHOTS DONE");
            mc.stop();
        });
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (DIM.isEmpty() || e.phase != TickEvent.Phase.END) return;
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
            nextAt = now + 4000;
            return;
        }
        mc.options.hideGui = !GUI;
        if (!GATES[0].isEmpty() && mc.level.getGameTime() % 10 == 0) {
            server.execute(() -> {
                ServerLevel lv = level(server);
                if (lv != null) for (String g : GATES) recrafted.boat.Waterways.request(lv, g);
            });
        }
        if (now < nextAt || index >= STEPS.size() - 1) return;
        index++;
        try {
            STEPS.get(index).run();
        } catch (Exception ex) {
            LOG.error("MAPSHOTS step {} failed", index, ex);
        }
        nextAt = now + (index + 1 < DELAYS.size() ? DELAYS.get(index + 1) : 1000);
    }
}
