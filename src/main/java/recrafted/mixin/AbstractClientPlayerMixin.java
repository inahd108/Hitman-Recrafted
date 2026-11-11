package recrafted.mixin;

import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import recrafted.client.ClientState;
import recrafted.client.NpcRenderer;

/** A disguised player is drawn with the outfit's skin instead of their own. */
@Mixin(AbstractClientPlayer.class)
public abstract class AbstractClientPlayerMixin {
    @Inject(method = "getSkinTextureLocation", at = @At("HEAD"), cancellable = true)
    private void recrafted$disguiseSkin(CallbackInfoReturnable<ResourceLocation> cir) {
        String key = ClientState.DISGUISES.get(((Entity) (Object) this).getUUID());
        if (key != null) cir.setReturnValue(NpcRenderer.texture(key));
    }

    @Inject(method = "getModelName", at = @At("HEAD"), cancellable = true)
    private void recrafted$disguiseModel(CallbackInfoReturnable<String> cir) {
        if (ClientState.DISGUISES.containsKey(((Entity) (Object) this).getUUID())) cir.setReturnValue("default");
    }
}
