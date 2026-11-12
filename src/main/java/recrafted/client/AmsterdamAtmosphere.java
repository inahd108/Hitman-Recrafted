package recrafted.client;

import com.mojang.blaze3d.shaders.FogShape;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.DimensionSpecialEffects;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.FogType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterDimensionSpecialEffectsEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import recrafted.Recrafted;

/**
 * Amsterdam's weather, client side only: a steady drizzle whatever the overworld is doing, low cloud,
 * and a slate-blue fog that swallows the far end of a canal.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class AmsterdamAtmosphere {
    public static final ResourceLocation ID = new ResourceLocation(Recrafted.MODID, "amsterdam");
    public static final ResourceKey<Level> DIMENSION = ResourceKey.create(Registries.DIMENSION, ID);
    static final float DRIZZLE = 0.5f;
    static final float FOG_NEAR = 10f, FOG_FAR = 120f;
    static final Vec3 SLATE = new Vec3(0.24, 0.29, 0.38);
    /** Dev harness only: a clear evening for the mission browser's flyover frames. */
    public static boolean clearForPhotos;

    private AmsterdamAtmosphere() {}

    static boolean inAmsterdam() {
        Minecraft mc = Minecraft.getInstance();
        return !clearForPhotos && mc.level != null && mc.level.dimension().equals(DIMENSION);
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (clearForPhotos && mc.level != null) {
            mc.level.setRainLevel(0f);
            return;
        }
        if (!inAmsterdam()) return;
        mc.level.setRainLevel(DRIZZLE);
        mc.level.setThunderLevel(0f);
    }

    @SubscribeEvent
    public static void fog(ViewportEvent.RenderFog e) {
        if (!inAmsterdam() || e.getType() != FogType.NONE || e.getMode() != FogRenderer.FogMode.FOG_TERRAIN) return;
        e.setNearPlaneDistance(FOG_NEAR);
        e.setFarPlaneDistance(Math.min(e.getFarPlaneDistance(), FOG_FAR));
        e.setFogShape(FogShape.SPHERE);
        e.setCanceled(true);
    }

    @SubscribeEvent
    public static void fogColour(ViewportEvent.ComputeFogColor e) {
        if (!inAmsterdam()) return;
        float k = 0.55f;
        float bright = Mth.clamp((e.getRed() + e.getGreen() + e.getBlue()) / 1.2f, 0.25f, 1f);
        e.setRed(Mth.lerp(k, e.getRed(), (float) SLATE.x * bright));
        e.setGreen(Mth.lerp(k, e.getGreen(), (float) SLATE.y * bright));
        e.setBlue(Mth.lerp(k, e.getBlue(), (float) SLATE.z * bright));
    }

    /** Low cloud over the city; otherwise the overworld sky. */
    static final class Effects extends DimensionSpecialEffects {
        Effects() {
            super(140f, true, SkyType.NORMAL, false, false);
        }

        @Override
        public Vec3 getBrightnessDependentFogColor(Vec3 c, float b) {
            return c.multiply(b * 0.94f + 0.06f, b * 0.94f + 0.06f, b * 0.91f + 0.09f);
        }

        @Override
        public boolean isFoggyAt(int x, int z) {
            return false;
        }
    }

    @Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class ModBus {
        @SubscribeEvent
        public static void effects(RegisterDimensionSpecialEffectsEvent e) {
            e.register(ID, new Effects());
        }
    }
}
