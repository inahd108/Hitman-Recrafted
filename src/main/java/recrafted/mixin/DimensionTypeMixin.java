package recrafted.mixin;

import net.minecraft.util.Mth;
import net.minecraft.world.level.dimension.DimensionType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import recrafted.client.SkyTime;

/** Sky, sun and light level at the dev harness's chosen hour (see {@link SkyTime}); untouched otherwise. */
@Mixin(DimensionType.class)
public abstract class DimensionTypeMixin {
    @Inject(method = "timeOfDay", at = @At("HEAD"), cancellable = true)
    private void recrafted$skyTime(long dayTime, CallbackInfoReturnable<Float> cir) {
        long t = SkyTime.override;
        if (t < 0) return;
        double d0 = Mth.frac(t / 24000.0D - 0.25D);
        double d1 = 0.5D - Math.cos(d0 * Math.PI) / 2.0D;
        cir.setReturnValue((float) (d0 * 2.0D + d1) / 3.0F);
    }
}
