package recrafted.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.ChatFormatting;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import recrafted.Recrafted;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcPose;

import java.util.HashMap;
import java.util.Map;

public class NpcRenderer extends MobRenderer<NpcEntity, NpcModel> {
    private static final Map<String, ResourceLocation> TEXTURES = new HashMap<>();

    public NpcRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new NpcModel(ctx.bakeLayer(ModelLayers.PLAYER)), 0.5f);
        addLayer(new ItemInHandLayer<>(this, ctx.getItemInHandRenderer()));
    }

    public static ResourceLocation texture(String key) {
        return TEXTURES.computeIfAbsent(key, k -> new ResourceLocation(Recrafted.MODID, "textures/entity/npc/" + k + ".png"));
    }

    @Override
    public ResourceLocation getTextureLocation(NpcEntity e) {
        return texture(e.getRole().id + "_" + e.getSkin());
    }

    @Override
    protected void setupRotations(NpcEntity e, PoseStack pose, float age, float yaw, float partial) {
        if (e.isDown() || e.getAnim() == NpcPose.SLEEP) {
            pose.mulPose(Axis.YP.rotationDegrees(180f - yaw));
            pose.translate(0, 0.16, 0.9);
            pose.mulPose(Axis.XP.rotationDegrees(-90f));
            return;
        }
        super.setupRotations(e, pose, age, yaw, partial);
    }

    @Override
    public void render(NpcEntity e, float yaw, float partial, PoseStack pose, MultiBufferSource buf, int light) {
        boolean seated = NpcModel.seated(e);
        this.shadowRadius = e.isDown() ? 0f : 0.5f;
        pose.pushPose();
        if (seated) pose.translate(0, -0.55, 0);
        super.render(e, yaw, partial, pose, buf, light);
        pose.popPose();
        if (e.isDown()) return;
        double d2 = entityRenderDispatcher.distanceToSqr(e);
        float lift = e.isCustomNameVisible() ? 0.28f : 0f;
        String speech = e.getSpeech();
        if (!speech.isEmpty() && d2 < 24 * 24) {
            pose.pushPose();
            pose.translate(0, lift, 0);
            renderNameTag(e, Component.literal("“" + speech + "”").withStyle(ChatFormatting.WHITE), pose, buf, light);
            pose.popPose();
            lift += 0.28f;
        }
        Component mark = null;
        if (e.inCombat()) mark = Component.literal("!").withStyle(ChatFormatting.RED, ChatFormatting.BOLD);
        else if (e.getSuspicionLevel() > 0.6f) mark = Component.literal("?").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD);
        else if (e.getSuspicionLevel() > 0.05f) mark = Component.literal("?").withStyle(ChatFormatting.YELLOW);
        else if (e.isEnforcer() && d2 < 20 * 20) mark = Component.literal("●").withStyle(ChatFormatting.WHITE);
        if (mark != null && d2 < 40 * 40) {
            pose.pushPose();
            pose.translate(0, lift, 0);
            renderNameTag(e, mark, pose, buf, light);
            pose.popPose();
        }
    }

    @Override
    protected boolean shouldShowName(NpcEntity e) {
        if (e.isDown()) return false;
        double d2 = entityRenderDispatcher.distanceToSqr(e);
        if (e.isTarget()) return d2 < 48 * 48;
        return e == entityRenderDispatcher.crosshairPickEntity && d2 < 12 * 12;
    }
}
