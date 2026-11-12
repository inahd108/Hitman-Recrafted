package recrafted.dev;

import net.minecraft.client.CloudStatus;
import net.minecraft.client.GraphicsStatus;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.TagParser;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.client.NpcModel;
import recrafted.client.SkyTime;
import recrafted.mission.MissionManager;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcPose;
import recrafted.npc.NpcRole;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Photo session for the title screen, enabled with -Precrafted.menushots (see build.gradle).
 * "scene" builds a penthouse over the sea east of Corvara, seats the operative in it and photographs him at
 * dusk; "orbit" circles the island for the mission browser's preview. Everything built is put back afterwards.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class MenuShots {
    private static final Logger LOG = LogManager.getLogger("recrafted-menushots");
    private static final String SPEC = System.getProperty("recrafted.menushots", "");
    private static final List<Runnable> STEPS = new ArrayList<>();
    private static final List<Long> DELAYS = new ArrayList<>();
    private static final Map<BlockPos, BlockState> RESTORE = new LinkedHashMap<>();
    private static int index = -1;
    private static long nextAt;
    private static boolean prepared;
    private static NpcEntity agent;

    private MenuShots() {}

    private static double[] nums(String key, String def) {
        String[] p = System.getProperty(key, def).split(",");
        double[] d = new double[p.length];
        for (int i = 0; i < p.length; i++) d[i] = Double.parseDouble(p[i].trim());
        return d;
    }

    private static void step(long delayMs, Runnable r) {
        STEPS.add(r);
        DELAYS.add(delayMs);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "menu_" + name + ".png", mc.getMainRenderTarget(), c -> LOG.info("MENUSHOTS saved {}", name));
    }

    private static void onServer(IntegratedServer server, java.util.function.BiConsumer<ServerLevel, ServerPlayer> work) {
        server.execute(() -> {
            try {
                work.accept(MissionManager.missionLevel(server), server.getPlayerList().getPlayers().get(0));
            } catch (Exception e) {
                LOG.error("MENUSHOTS server step failed", e);
            }
        });
    }

    private static void camera(IntegratedServer server, double x, double eyeY, double z, float yaw, float pitch) {
        onServer(server, (level, sp) -> {
            sp.setGameMode(GameType.SPECTATOR);
            double y = eyeY - sp.getEyeHeight();
            sp.teleportTo(level, x, y, z, yaw, pitch);
            sp.connection.teleport(x, y, z, yaw, pitch);
        });
    }

    // ---- the penthouse ------------------------------------------------------------------
    private static void put(ServerLevel level, int x, int y, int z, String state) {
        try {
            BlockState s = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), state, false).blockState();
            BlockPos p = new BlockPos(x, y, z);
            RESTORE.putIfAbsent(p.immutable(), original(level, p));
            level.setBlock(p, s, 2 | 16);
        } catch (Exception e) {
            LOG.error("MENUSHOTS bad block {}", state, e);
        }
    }

    /**
     * Anchor (ax, f, az) is the chair; f is the floor level. The window wall runs north-south just west of the
     * chair, so the operative sits with his back to the sunset and the island beyond it.
     */
    private static void build(ServerLevel level, int ax, int f, int az) {
        int wx = ax - 2, x1 = ax + 9, z0 = az - 12, z1 = az + 12, top = f + 6;
        for (int x = wx - 1; x <= x1; x++) {
            for (int z = z0; z <= z1; z++) {
                put(level, x, f, z, "minecraft:dark_oak_planks");
                put(level, x, top, z, "minecraft:spruce_planks");
                for (int y = f + 1; y < top; y++) put(level, x, y, z, "minecraft:air");
            }
        }
        // floor-to-ceiling glass on three sides, black steel mullions every four blocks
        for (int z = z0; z <= z1; z++) {
            boolean mullion = Math.floorMod(z - az, 8) == 5;
            for (int y = f + 1; y < top; y++) {
                put(level, wx, y, z, mullion ? "minecraft:black_concrete" : "minecraft:glass_pane[north=true,south=true]");
            }
            put(level, wx, top - 1, z, "minecraft:black_concrete");
            put(level, wx, f + 1, z, "minecraft:polished_blackstone_slab[type=bottom]");
        }
        for (int x = wx; x <= x1; x++) {
            boolean mullion = Math.floorMod(x - wx, 6) == 0;
            for (int zz : new int[]{z0, z1}) {
                for (int y = f + 1; y < top; y++) {
                    put(level, x, y, zz, mullion ? "minecraft:black_concrete" : "minecraft:glass_pane[east=true,west=true]");
                }
                put(level, x, top - 1, zz, "minecraft:black_concrete");
            }
        }
        for (int z = z0; z <= z1; z++) {
            for (int y = f + 1; y < top; y++) put(level, x1, y, z, "minecraft:dark_oak_planks");
        }
        // rug
        for (int x = ax - 1; x <= ax + 4; x++) {
            for (int z = az - 3; z <= az + 3; z++) {
                boolean edge = x == ax - 1 || x == ax + 4 || z == az - 3 || z == az + 3;
                put(level, x, f + 1, z, edge ? "minecraft:black_carpet" : "minecraft:brown_carpet");
            }
        }
        // wingback chair
        put(level, ax, f + 1, az, "minecraft:dark_oak_stairs[facing=west]");
        put(level, ax, f + 2, az, "minecraft:dark_oak_trapdoor[facing=east,open=true,half=bottom]");
        put(level, ax, f + 1, az - 1, "minecraft:dark_oak_trapdoor[facing=north,open=true,half=bottom]");
        put(level, ax, f + 1, az + 1, "minecraft:dark_oak_trapdoor[facing=south,open=true,half=bottom]");
        // side table with a glass of wine, floor lamp, plant
        put(level, ax, f + 1, az - 2, "minecraft:dark_oak_fence");
        put(level, ax, f + 2, az - 2, "recrafted:drink");
        put(level, ax - 1, f + 1, az - 3, "minecraft:dark_oak_fence");
        put(level, ax - 1, f + 2, az - 3, "minecraft:dark_oak_fence");
        put(level, ax - 1, f + 3, az - 3, "minecraft:lantern[hanging=false]");
        put(level, ax - 1, f + 1, az + 3, "minecraft:decorated_pot");
        put(level, ax - 1, f + 2, az + 3, "minecraft:large_fern[half=lower]");
        put(level, ax - 1, f + 3, az + 3, "minecraft:large_fern[half=upper]");
        // hidden lights: a warm key on his face, a soft fill for the room
        put(level, ax + 2, f + 3, az + 1, "minecraft:light[level=13]");
        put(level, ax + 5, f + 4, az - 4, "minecraft:light[level=10]");
        put(level, ax + 5, f + 4, az + 5, "minecraft:light[level=10]");
    }

    private static void seat(ServerLevel level, int ax, int f, int az, double camX, double camZ) {
        agent = ModRegistry.NPC.get().create(level);
        agent.setRole(NpcRole.AGENT);
        agent.setSkin(0);
        double x = ax + 0.5, z = az + 0.5;
        float face = (float) Math.toDegrees(Math.atan2(-(camX - x), camZ - z));
        float body = (float) nums("recrafted.menushots.agentYaw", "-105")[0];
        float head = body + net.minecraft.util.Mth.wrapDegrees(face - body) * 0.75f;
        agent.moveTo(x, f + 1.5, z, body, (float) nums("recrafted.menushots.agentPitch", "6")[0]);
        agent.setYHeadRot(head);
        agent.yHeadRotO = head;
        agent.yBodyRot = body;
        agent.yBodyRotO = body;
        agent.frozen = true;
        agent.setInvulnerable(true);
        agent.setSilent(true);
        agent.setAnim(NpcPose.SIT_ARMED);
        try {
            agent.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.of(TagParser.parseTag(
                    "{id:\"tacz:modern_kinetic_gun\",Count:1b,tag:{GunId:\"recrafted:argento\",GunCurrentAmmoCount:9,"
                            + "HasBulletInBarrel:1b,GunFireMode:\"SEMI\",AttachmentMUZZLE:{id:\"tacz:attachment\",Count:1b,"
                            + "tag:{AttachmentId:\"recrafted:argento_suppressor\"}}}}")));
        } catch (Exception e) {
            LOG.error("MENUSHOTS no pistol", e);
        }
        level.addFreshEntity(agent);
    }

    /** What the map generator put here, so a session cut short last time never leaves its set behind. */
    private static BlockState original(ServerLevel level, BlockPos p) {
        recrafted.world.MapData map = recrafted.world.MapData.get("corvara");
        if (map.contains(p.getX(), p.getZ())) {
            return p.getY() >= 0 && p.getY() < map.sy ? map.get(p.getX(), p.getY(), p.getZ())
                    : net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
        }
        return p.getY() > 63 ? net.minecraft.world.level.block.Blocks.AIR.defaultBlockState() : level.getBlockState(p);
    }

    private static void restore(ServerLevel level) {
        if (agent != null) agent.discard();
        List<Map.Entry<BlockPos, BlockState>> list = new ArrayList<>(RESTORE.entrySet());
        for (int i = list.size() - 1; i >= 0; i--) level.setBlock(list.get(i).getKey(), list.get(i).getValue(), 2 | 16);
        RESTORE.clear();
    }

    // ---- the session --------------------------------------------------------------------
    private static void prepare(Minecraft mc, IntegratedServer server) {
        mc.options.hideGui = true;
        mc.options.fov().set((int) nums("recrafted.menushots.fov", "36")[0]);
        mc.options.renderDistance().set((int) nums("recrafted.menushots.distance", "16")[0]);
        mc.options.graphicsMode().set(GraphicsStatus.FANCY);
        mc.options.cloudStatus().set(CloudStatus.FANCY);
        mc.options.ambientOcclusion().set(true);
        mc.options.entityShadows().set(true);
        mc.levelRenderer.allChanged();
        mc.getToasts().clear();
        if (SPEC.contains("scene")) scene(mc, server);
        step(1500, () -> {
            onServer(server, (level, sp) -> restore(level));
            SkyTime.override = -1;
        });
        if (SPEC.contains("orbit")) orbit(mc, server);
        step(2500, () -> {
            LOG.info("MENUSHOTS DONE");
            mc.stop();
        });
    }

    private static void scene(Minecraft mc, IntegratedServer server) {
        double[] a = nums("recrafted.menushots.anchor", "262,100,140");
        int ax = (int) a[0], f = (int) a[1], az = (int) a[2];
        double[] c = nums("recrafted.menushots.cam", "4.51,2.6,1.64,100,3");
        double camX = ax + 0.5 + c[0], camZ = az + 0.5 + c[2];
        step(500, () -> onServer(server, (level, sp) -> {
            build(level, ax, f, az);
            seat(level, ax, f, az, camX, camZ);
        }));
        step(500, () -> camera(server, camX, f + c[1], camZ, (float) c[3], (float) c[4]));
        String[] poses = System.getProperty("recrafted.menushots.poses", "").split(";");
        String[] times = System.getProperty("recrafted.menushots.times", "12900").split(",");
        long settle = (long) nums("recrafted.menushots.settle", "20000")[0];
        boolean first = true;
        for (int pi = 0; pi < poses.length; pi++) {
            String pose = poses[pi].trim();
            int pIndex = pi;
            step(0, () -> {
                if (!pose.isEmpty()) {
                    String[] v = pose.split(",");
                    for (int i = 0; i < v.length && i < NpcModel.armed.length; i++) NpcModel.armed[i] = Float.parseFloat(v[i].trim());
                }
            });
            for (String t : times) {
                long time = Long.parseLong(t.trim());
                step(first ? settle : 1500, () -> SkyTime.override = time);
                first = false;
                step(1500, () -> shot(mc, "scene_p" + pIndex + "_t" + time));
            }
        }
    }

    private static void orbit(Minecraft mc, IntegratedServer server) {
        double[] o = nums("recrafted.menushots.orbitAt", "160,72,122,168,58,21");   // centre xyz, radius, height above centre, pitch
        int n = (int) nums("recrafted.menushots.orbitCount", "8")[0];
        double start = nums("recrafted.menushots.orbitStart", "200")[0];
        long settle = (long) nums("recrafted.menushots.orbitSettle", "25000")[0];
        String time = System.getProperty("recrafted.menushots.orbitTime", "-1");
        int fov = (int) nums("recrafted.menushots.orbitFov", "55")[0];
        step(0, () -> {
            SkyTime.override = Long.parseLong(time);
            mc.options.fov().set(fov);
        });
        for (int i = 0; i < n; i++) {
            double yaw = start + 360.0 * i / n;              // where the camera looks from (compass, 0 = south)
            double r = Math.toRadians(yaw);
            double x = o[0] - Math.sin(r) * o[3], z = o[2] + Math.cos(r) * o[3];
            float look = (float) (yaw + 180.0);
            int k = i;
            step(i == 0 ? 1000 : 500, () -> camera(server, x, o[1] + o[4], z, look, (float) o[5]));
            step(settle, () -> shot(mc, "orbit_" + k));
        }
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
            prepare(mc, server);
            nextAt = now + 6000;
            return;
        }
        mc.options.hideGui = true;
        if (now < nextAt || index >= STEPS.size() - 1) return;
        index++;
        try {
            STEPS.get(index).run();
        } catch (Exception ex) {
            LOG.error("MENUSHOTS step {} failed", index, ex);
        }
        nextAt = now + (index + 1 < DELAYS.size() ? DELAYS.get(index + 1) : 1000);
    }
}
