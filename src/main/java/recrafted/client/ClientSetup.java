package recrafted.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.item.RoutePlannerItem;
import recrafted.npc.Route;
import recrafted.npc.Waypoint;

import java.util.Locale;

public final class ClientSetup {
    public static final KeyMapping FOCUS = new KeyMapping("key.recrafted.focus", InputConstants.KEY_V, "key.categories.recrafted");
    public static final KeyMapping THROW = new KeyMapping("key.recrafted.throw", InputConstants.KEY_X, "key.categories.recrafted");

    private ClientSetup() {}

    @Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class ModBus {
        @SubscribeEvent
        public static void renderers(EntityRenderersEvent.RegisterRenderers e) {
            e.registerEntityRenderer(ModRegistry.NPC.get(), NpcRenderer::new);
            e.registerEntityRenderer(ModRegistry.PROP.get(), PropRenderer::new);
            e.registerEntityRenderer(ModRegistry.THROWN_PROP.get(), ThrownItemRenderer::new);
        }

        @SubscribeEvent
        public static void overlays(RegisterGuiOverlaysEvent e) {
            e.registerAboveAll("hud", new HudOverlay());
        }

        @SubscribeEvent
        public static void keys(RegisterKeyMappingsEvent e) {
            e.register(FOCUS);
            e.register(THROW);
        }
    }

    @Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
    public static final class ForgeBus {
        @SubscribeEvent
        public static void tick(TickEvent.ClientTickEvent e) {
            if (e.phase != TickEvent.Phase.END) return;
            Minecraft mc = Minecraft.getInstance();
            if (mc.player == null) {
                ClientState.missionActive = false;
                ClientState.focus = false;
                ClientState.holdingPlanner = false;
                ClientState.DISGUISES.clear();
                return;
            }
            ClientState.focus = FOCUS.isDown();
            while (THROW.consumeClick()) {
                if (mc.screen == null && recrafted.mission.Throwing.canThrow(mc.player.getMainHandItem())) {
                    recrafted.net.Net.CHANNEL.sendToServer(new recrafted.net.Net.ThrowC2S());
                    mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                }
            }
            ClientState.holdingPlanner = mc.player.getMainHandItem().getItem() instanceof RoutePlannerItem
                    || mc.player.getOffhandItem().getItem() instanceof RoutePlannerItem;
        }

        @SubscribeEvent
        public static void renderWorld(RenderLevelStageEvent e) {
            if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
            Route route = ClientState.selectedRoute;
            if (!ClientState.holdingPlanner || route == null || route.isEmpty()) return;
            Minecraft mc = Minecraft.getInstance();
            Vec3 cam = e.getCamera().getPosition();
            PoseStack pose = e.getPoseStack();
            MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
            pose.pushPose();
            pose.translate(-cam.x, -cam.y, -cam.z);
            VertexConsumer lines = buf.getBuffer(RenderType.lines());
            int n = route.points.size();
            for (int i = 0; i < n; i++) {
                Waypoint w = route.points.get(i);
                boolean stop = w.wait > 0;
                float r = stop ? 1f : 0.3f, g = stop ? 0.75f : 0.85f, b = stop ? 0.2f : 1f;
                LevelRenderer.renderLineBox(pose, lines, new AABB(w.x - 0.3, w.y + 0.02, w.z - 0.3, w.x + 0.3, w.y + 0.12, w.z + 0.3), r, g, b, 1f);
                if (w.hasYaw()) {
                    Vec3 d = Vec3.directionFromRotation(0, w.yaw).scale(0.7);
                    line(pose, lines, w.x, w.y + 0.07, w.z, w.x + d.x, w.y + 0.07, w.z + d.z, 1f, 1f, 1f);
                }
                Waypoint next = i + 1 < n ? route.points.get(i + 1) : (route.mode == Route.Mode.LOOP && n > 2 ? route.points.get(0) : null);
                if (next != null) {
                    boolean closing = i + 1 >= n;
                    line(pose, lines, w.x, w.y + 0.07, w.z, next.x, next.y + 0.07, next.z, closing ? 0.5f : 0.25f, closing ? 0.5f : 0.9f, closing ? 0.5f : 1f);
                }
            }
            buf.endBatch(RenderType.lines());
            Font font = mc.font;
            for (int i = 0; i < n; i++) {
                Waypoint w = route.points.get(i);
                if (cam.distanceToSqr(w.x, w.y, w.z) > 40 * 40) continue;
                String text = "#" + (i + 1) + (w.wait > 0 ? " " + w.pose.label + String.format(Locale.ROOT, " %.0fs", w.wait / 20f) : "");
                pose.pushPose();
                pose.translate(w.x, w.y + 0.55, w.z);
                pose.mulPose(e.getCamera().rotation());
                pose.scale(-0.025f, -0.025f, 0.025f);
                Matrix4f m = pose.last().pose();
                font.drawInBatch(text, -font.width(text) / 2f, 0, 0xFFFFFFFF, false, m, buf, Font.DisplayMode.SEE_THROUGH, 0x80000000, 0xF000F0);
                pose.popPose();
            }
            buf.endBatch();
            pose.popPose();
        }

        private static void line(PoseStack pose, VertexConsumer vc, double x0, double y0, double z0, double x1, double y1, double z1,
                                 float r, float g, float b) {
            Matrix4f m = pose.last().pose();
            Matrix3f nm = pose.last().normal();
            float dx = (float) (x1 - x0), dy = (float) (y1 - y0), dz = (float) (z1 - z0);
            float len = (float) Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (len < 1e-4f) return;
            dx /= len; dy /= len; dz /= len;
            vc.vertex(m, (float) x0, (float) y0, (float) z0).color(r, g, b, 1f).normal(nm, dx, dy, dz).endVertex();
            vc.vertex(m, (float) x1, (float) y1, (float) z1).color(r, g, b, 1f).normal(nm, dx, dy, dz).endVertex();
        }
    }
}
