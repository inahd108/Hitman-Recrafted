package recrafted.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcPose;

/** Held items, except that a seated operative rests his pistol with the muzzle down instead of straight ahead. */
public class PosedItemLayer extends ItemInHandLayer<NpcEntity, NpcModel> {
    private final ItemInHandRenderer items;

    public PosedItemLayer(RenderLayerParent<NpcEntity, NpcModel> parent, ItemInHandRenderer items) {
        super(parent, items);
        this.items = items;
    }

    @Override
    protected void renderArmWithItem(LivingEntity e, ItemStack stack, ItemDisplayContext ctx, HumanoidArm arm,
                                     PoseStack pose, MultiBufferSource buf, int light) {
        if (stack.isEmpty() || arm != HumanoidArm.RIGHT || !(e instanceof NpcEntity n) || n.getAnim() != NpcPose.SIT_ARMED) {
            super.renderArmWithItem(e, stack, ctx, arm, pose, buf, light);
            return;
        }
        float[] a = NpcModel.armed;
        pose.pushPose();
        getParentModel().translateToHand(arm, pose);
        pose.mulPose(Axis.XP.rotationDegrees(-90f));
        pose.mulPose(Axis.YP.rotationDegrees(180f));
        pose.translate(1 / 16f, 0.125f, -0.625f);
        pose.mulPose(Axis.XP.rotationDegrees(a[6]));
        pose.mulPose(Axis.YP.rotationDegrees(a[7]));
        pose.mulPose(Axis.ZP.rotationDegrees(a[8]));
        items.renderItem(e, stack, ctx, false, pose, buf, light);
        pose.popPose();
    }
}
