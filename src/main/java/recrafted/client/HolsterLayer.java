package recrafted.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import recrafted.npc.NpcEntity;

/** A guard's sidearm, holstered on the right hip, muzzle down. Gone once they drop it. */
public class HolsterLayer extends RenderLayer<NpcEntity, NpcModel> {
    private final ItemInHandRenderer items;

    public HolsterLayer(RenderLayerParent<NpcEntity, NpcModel> parent, ItemInHandRenderer items) {
        super(parent);
        this.items = items;
    }

    @Override
    public void render(PoseStack pose, MultiBufferSource buf, int light, NpcEntity e, float limb, float limbAmount,
                       float partial, float age, float headYaw, float headPitch) {
        ItemStack gun = e.getSidearm();
        if (gun.isEmpty() || e.isDown() || recrafted.compat.Guns.isGun(e.getMainHandItem())) return;
        pose.pushPose();
        getParentModel().body.translateAndRotate(pose);
        // the vanilla held-item transform for a hanging right hand, moved onto the hip: the gun hangs muzzle-down
        pose.translate(-6.0f / 16f, 3f / 16f, 0.8f / 16f);
        pose.mulPose(Axis.XP.rotationDegrees(-90f));
        pose.mulPose(Axis.YP.rotationDegrees(180f));
        pose.translate(1f / 16f, 0.125f, -0.5f);
        items.renderItem(e, gun, ItemDisplayContext.THIRD_PERSON_RIGHT_HAND, false, pose, buf, light);
        pose.popPose();
    }
}
