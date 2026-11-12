package recrafted.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.ModelData;
import recrafted.boat.BoatDesign;
import recrafted.boat.CanalBoat;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** Draws a boat as the little structure of blocks its design lists, turned to the boat's heading. */
public class CanalBoatRenderer extends EntityRenderer<CanalBoat> {
    private record Placed(float x, float y, float z, BlockState state) {}

    private final Map<BoatDesign, List<Placed>> cache = new EnumMap<>(BoatDesign.class);

    public CanalBoatRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
        shadowRadius = 0;
    }

    private List<Placed> parts(BoatDesign d) {
        return cache.computeIfAbsent(d, k -> {
            List<Placed> out = new ArrayList<>();
            for (BoatDesign.Part p : k.parts()) {
                BlockState s;
                try {
                    s = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), p.state(), false).blockState();
                } catch (Exception e) {
                    s = Blocks.MAGENTA_CONCRETE.defaultBlockState();
                }
                out.add(new Placed(p.dx() - 0.5f, p.dy(), p.dz() - 0.5f, s));
            }
            return out;
        });
    }

    @Override
    public void render(CanalBoat boat, float yaw, float partial, PoseStack pose, MultiBufferSource buffers, int light) {
        BlockRenderDispatcher blocks = Minecraft.getInstance().getBlockRenderer();
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(-Mth.rotLerp(partial, boat.yRotO, boat.getYRot())));
        for (Placed p : parts(boat.design())) {
            pose.pushPose();
            pose.translate(p.x(), p.y(), p.z());
            blocks.renderSingleBlock(p.state(), pose, buffers, light, OverlayTexture.NO_OVERLAY, ModelData.EMPTY, null);
            pose.popPose();
        }
        pose.popPose();
        super.render(boat, yaw, partial, pose, buffers, light);
    }

    @Override
    public ResourceLocation getTextureLocation(CanalBoat boat) {
        return InventoryMenu.BLOCK_ATLAS;
    }
}
