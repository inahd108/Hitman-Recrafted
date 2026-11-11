package recrafted.dev;

import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.GameType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.Recrafted;
import recrafted.client.NpcEditScreen;
import recrafted.client.RouteScreen;
import recrafted.mission.MissionManager;
import recrafted.mission.PlayerData;
import recrafted.net.Net;
import recrafted.npc.NpcPose;
import recrafted.npc.NpcRole;
import recrafted.npc.Route;
import recrafted.npc.Waypoint;

import java.io.File;

/**
 * Screenshot tour, enabled with -Drecrafted.clienttest=true (see the runClient config).
 * Joins the world given on the command line, starts the contract, moves a camera through a
 * list of viewpoints, saves a screenshot at each and then closes the game.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ClientTest {
    private static final Logger LOG = LogManager.getLogger("recrafted-clienttest");
    private static final boolean ENABLED = Boolean.getBoolean("recrafted.clienttest");
    private static final long SETTLE_MS = Long.getLong("recrafted.clienttest.settle", 20000L);

    private record Shot(String name, double x, double y, double z, float yaw, float pitch, String mode) {}

    private static final Shot[] SHOTS = {
            new Shot("01_arrival", 134.5, 66, 229.5, 180, 5, "play"),
            new Shot("02_harbour", 165, 84, 262, 180, 14, "fly"),
            new Shot("03_quay", 141, 67.6, 197.5, -90, 4, "fly"),
            new Shot("04_piazza", 162, 86, 176, 180, 28, "fly"),
            new Shot("05_cafe", 146, 75.6, 150, 100, 6, "fly"),
            new Shot("06_upper_town", 186, 104, 136, 115, 30, "fly"),
            new Shot("06b_chapel", 213.5, 94, 100, 180, 2, "fly"),
            new Shot("06c_beach", 58, 70, 214, 170, 8, "fly"),
            new Shot("07_estate", 100, 108, 100, 180, 30, "fly"),
            new Shot("08_villa_court", 100, 91.6, 71.5, 180, -4, "fly"),
            new Shot("09_cannery", 262, 68, 175.5, -90, 6, "fly"),
            new Shot("10_lab", 234.5, 43.6, 131, 180, 2, "fly"),
            new Shot("11_cellar", 78, 84.6, 50.5, -90, 4, "fly"),
            new Shot("12_disguise", 160.5, 66, 197.5, 180, 12, "third"),
            new Shot("13_route_editor", 160.5, 66, 197.5, 180, 12, "route"),
            new Shot("14_npc_editor", 160.5, 66, 197.5, 180, 12, "npc"),
    };

    private static int index = -2;
    private static long nextAt;
    private static boolean placed;

    private ClientTest() {}

    // ---- scripted gameplay checks, run on the integrated server with the real player ----------
    private static int step;
    private static recrafted.npc.NpcEntity victim;

    private static recrafted.npc.NpcEntity npc(ServerLevel level, String name) {
        for (net.minecraft.world.entity.Entity e : level.getAllEntities()) {
            if (e instanceof recrafted.npc.NpcEntity n && n.getName().getString().equals(name)) return n;
        }
        return null;
    }

    private static void check(String what, boolean ok, Object detail) {
        LOG.info("CLIENTTEST CHECK {}: {} ({})", what, ok ? "PASS" : "FAIL", detail);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "recrafted_" + name + ".png", mc.getMainRenderTarget(), c -> { });
    }

    /** Returns true when the script has finished. */
    private static boolean gameplay(Minecraft mc, IntegratedServer server, ServerPlayer sp, long now) {
        ServerLevel level = MissionManager.missionLevel(server);
        mc.setScreen(null);
        mc.options.setCameraType(CameraType.FIRST_PERSON);
        switch (step++) {
            case 0 -> server.execute(() -> {          // creep up behind the gardener in the olive grove
                victim = npc(level, "Gardener Vito");
                if (victim == null) { check("find gardener", false, "missing"); return; }
                victim.frozen = true;
                net.minecraft.world.phys.Vec3 look = net.minecraft.world.phys.Vec3.directionFromRotation(0, victim.yBodyRot);
                sp.setGameMode(GameType.ADVENTURE);
                PlayerData.setDisguise(sp, null, 0);
                sp.teleportTo(level, victim.getX() - look.x * 1.3, victim.getY(), victim.getZ() - look.z * 1.3, victim.yBodyRot, 25);
            });
            case 1 -> server.execute(() -> {
                if (victim == null) return;
                recrafted.mission.Combat.melee(sp, victim);
                check("subdue from behind", victim.getState() == recrafted.npc.NpcEntity.State.UNCONSCIOUS, victim.getState());
            });
            case 2 -> shot(mc, "15_subdued");
            case 3 -> server.execute(() -> {
                if (victim == null) return;
                victim.takeOutfit(sp);
                check("take outfit", PlayerData.disguise(sp) == NpcRole.GARDENER, PlayerData.disguise(sp));
                sp.teleportTo(level, 100.5, 90, 80.5, 180, 0);       // inside the estate gate, dressed for it
            });
            case 4 -> { }
            case 5 -> server.execute(() -> {
                check("disguise grants access", !MissionManager.isTrespassing(sp) && !MissionManager.isHunted(sp),
                        "trespassing=" + MissionManager.isTrespassing(sp) + " hunted=" + MissionManager.isHunted(sp));
                PlayerData.setDisguise(sp, null, 0);
            });
            case 6, 7 -> { }
            case 8 -> {
                shot(mc, "16_spotted");
                server.execute(() -> {
                    float max = 0;
                    for (net.minecraft.world.entity.Entity e : level.getAllEntities()) {
                        if (e instanceof recrafted.npc.NpcEntity n) max = Math.max(max, n.suspicionOf(sp));
                    }
                    check("trespass detected", MissionManager.isTrespassing(sp) && (max > 0.2f || MissionManager.isHunted(sp)),
                            "suspicion=" + max + " hunted=" + MissionManager.isHunted(sp));
                    sp.setGameMode(GameType.SPECTATOR);
                    recrafted.npc.NpcEntity diner = npc(level, "Diner Henrik");
                    if (diner == null) { check("find diner", false, "missing"); return; }
                    victim = diner;
                    sp.teleportTo(level, diner.getX() + 3, diner.getY() + 1, diner.getZ() + 4, 150, 15);
                    net.minecraft.core.BlockPos base = diner.blockPosition();
                    boolean dosed = false;
                    for (net.minecraft.core.BlockPos p : net.minecraft.core.BlockPos.betweenClosed(base.offset(-2, -1, -2), base.offset(2, 2, 2))) {
                        net.minecraft.world.level.block.state.BlockState st = level.getBlockState(p);
                        if (st.getBlock() instanceof recrafted.block.ConsumableBlock) {
                            MissionManager.setTracked(level, p.immutable(), st.setValue(recrafted.block.ConsumableBlock.POISON, recrafted.block.Poison.LETHAL));
                            dosed = true;
                            break;
                        }
                    }
                    check("found a plate or glass next to the diner", dosed, base);
                });
            }
            case 9, 10, 11 -> { }
            case 12 -> {
                shot(mc, "17_poisoned");
                server.execute(() -> check("poisoned drink kills", victim != null && victim.isDead(), victim == null ? "?" : victim.getState()));
            }
            default -> {
                return true;
            }
        }
        nextAt = now + 2500;
        return false;
    }

    private static void click(Screen screen, String... labels) {
        for (GuiEventListener l : screen.children()) {
            if (l instanceof Button b) {
                String text = b.getMessage().getString();
                for (String want : labels) {
                    if (text.contains(want)) {
                        LOG.info("CLIENTTEST clicking '{}' on {}", text, screen.getClass().getSimpleName());
                        b.onPress();
                        return;
                    }
                }
            }
        }
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (!ENABLED || e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        long now = System.currentTimeMillis();
        if (mc.player == null || mc.level == null) {
            // get past the "experimental settings" and backup prompts while loading
            if (mc.screen != null && now > nextAt) {
                click(mc.screen, "Proceed", "I know what I'm doing", "Yes");
                nextAt = now + 1500;
            }
            return;
        }
        IntegratedServer server = mc.getSingleplayerServer();
        if (server == null || server.getPlayerList().getPlayers().isEmpty()) return;
        if (index == -2) {
            index = -1;
            nextAt = now + 6000;
            return;
        }
        if (now < nextAt) return;
        ServerPlayer sp = server.getPlayerList().getPlayers().get(0);
        if (index == -1) {
            LOG.info("CLIENTTEST starting contract");
            server.execute(() -> MissionManager.start(sp));
            index = 0;
            placed = false;
            nextAt = now + 4000;
            return;
        }
        if (index >= SHOTS.length) {
            if (!gameplay(mc, server, sp, now)) return;
            LOG.info("CLIENTTEST DONE");
            mc.stop();
            index = Integer.MAX_VALUE - 1;
            nextAt = Long.MAX_VALUE;
            return;
        }
        Shot s = SHOTS[index];
        if (!placed) {
            placed = true;
            mc.setScreen(null);
            mc.options.hideGui = false;
            server.execute(() -> {
                ServerLevel level = MissionManager.missionLevel(server);
                sp.setGameMode(s.mode().equals("fly") ? GameType.SPECTATOR : GameType.ADVENTURE);
                sp.teleportTo(level, s.x(), s.y(), s.z(), s.yaw(), s.pitch());
                if (!s.mode().equals("fly") && !s.mode().equals("play")) PlayerData.setDisguise(sp, NpcRole.WAITER, 0);
            });
            mc.options.setCameraType(s.mode().equals("third") ? CameraType.THIRD_PERSON_FRONT : CameraType.FIRST_PERSON);
            if (s.mode().equals("route")) {
                Route r = new Route();
                String[] says = {"", "The usual. And keep them coming.", "", ""};
                NpcPose[] poses = {NpcPose.TYPE, NpcPose.DRINK, NpcPose.SIT, NpcPose.PHONE};
                for (int i = 0; i < 6; i++) {
                    Waypoint w = new Waypoint(100.5 + i * 4, 90, 66.5 + (i % 2) * 5);
                    if (i < 4) { w.wait = 200 + i * 200; w.pose = poses[i]; w.say = says[i]; w.yaw = i * 90f; }
                    r.points.add(w);
                }
                mc.setScreen(new RouteScreen(-1, "Marco Belmonte", r, false));
            } else if (s.mode().equals("npc")) {
                mc.setScreen(new NpcEditScreen(new Net.NpcScreenS2C(-1, sp.blockPosition(), NpcRole.ESTATE_GUARD.id, "Guard Tullio", 0, true, false, "", "")));
            }
            nextAt = now + (s.mode().equals("fly") || s.mode().equals("play") ? SETTLE_MS : 6000);
            return;
        }
        File dir = mc.gameDirectory;
        Screenshot.grab(dir, "recrafted_" + s.name() + ".png", mc.getMainRenderTarget(),
                c -> LOG.info("CLIENTTEST shot {}: {}", s.name(), c.getString()));
        index++;
        placed = false;
        nextAt = now + 1500;
    }
}
