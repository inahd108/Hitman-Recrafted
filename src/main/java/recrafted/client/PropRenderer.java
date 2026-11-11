package recrafted.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import recrafted.entity.PropEntity;

/** Draws a prop lying flat on whatever it rests on. */
public class PropRenderer extends EntityRenderer<PropEntity> {
    private final ItemRenderer items;

    public PropRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
        this.items = ctx.getItemRenderer();
        this.shadowRadius = 0.15f;
    }

    @Override
    public void render(PropEntity e, float yaw, float partial, PoseStack pose, MultiBufferSource buf, int light) {
        ItemStack stack = e.getItem();
        if (stack.isEmpty()) return;
        pose.pushPose();
        pose.translate(0, 0.03, 0);
        pose.mulPose(Axis.YP.rotationDegrees(-e.getYRot()));
        pose.mulPose(Axis.XP.rotationDegrees(90f));
        pose.scale(1.5f, 1.5f, 1.5f);
        pose.translate(0, -0.12, 0);
        items.renderStatic(stack, ItemDisplayContext.GROUND, light, OverlayTexture.NO_OVERLAY, pose, buf, e.level(), e.getId());
        pose.popPose();
        super.render(e, yaw, partial, pose, buf, light);
    }

    @Override
    public ResourceLocation getTextureLocation(PropEntity e) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}
