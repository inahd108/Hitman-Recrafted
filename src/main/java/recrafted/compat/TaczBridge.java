package recrafted.compat;

import com.tacz.guns.api.GunProperties;
import com.tacz.guns.api.TimelessAPI;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.event.common.GunFireEvent;
import com.tacz.guns.api.item.IGun;
import com.tacz.guns.api.item.builder.AmmoItemBuilder;
import com.tacz.guns.api.item.builder.GunItemBuilder;
import com.tacz.guns.api.item.gun.FireMode;
import com.tacz.guns.config.common.GunConfig;
import com.tacz.guns.resource.index.CommonGunIndex;
import com.tacz.guns.resource.modifier.AttachmentCacheProperty;
import com.tacz.guns.resource.pojo.data.gun.Bolt;
import com.tacz.guns.resource.pojo.data.gun.FireSound;
import com.tacz.guns.resource.pojo.data.gun.GunData;
import it.unimi.dsi.fastutil.Pair;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.LogicalSide;
import recrafted.mission.Awareness;

import java.util.Optional;

/** The only class that touches TACZ directly. Loaded only when TACZ is installed (see {@link Guns}). */
final class TaczBridge {
    /** NPCs react within this share of the distance TACZ lets players hear a shot. */
    private static final float ALARM_SHARE = 0.5f;
    private static final int MAX_ALARM = 48;

    private TaczBridge() {}

    static ItemStack loadedGun(ResourceLocation id) {
        Optional<CommonGunIndex> index = TimelessAPI.getCommonGunIndex(id);
        if (index.isEmpty()) return ItemStack.EMPTY;
        GunData data = index.get().getGunData();
        return GunItemBuilder.create().setId(id).setAmmoCount(data.getAmmoAmount())
                .setAmmoInBarrel(data.getBolt() != Bolt.OPEN_BOLT).setFireMode(FireMode.SEMI).build();
    }

    static ItemStack spareAmmo(ItemStack gun) {
        IGun iGun = IGun.getIGunOrNull(gun);
        if (iGun == null) return ItemStack.EMPTY;
        return TimelessAPI.getCommonGunIndex(iGun.getGunId(gun))
                .map(i -> AmmoItemBuilder.create().setId(i.getGunData().getAmmoId()).setCount(i.getGunData().getAmmoAmount()).build())
                .orElse(ItemStack.EMPTY);
    }

    static void register() {
        MinecraftForge.EVENT_BUS.addListener(TaczBridge::onFire);
    }

    static void simulateShot(ServerPlayer p, ItemStack gun) {
        MinecraftForge.EVENT_BUS.post(new GunFireEvent(p, gun, LogicalSide.SERVER));
    }

    private static void onFire(GunFireEvent e) {
        if (e.isCanceled() || e.getLogicalSide() != LogicalSide.SERVER) return;
        if (!(e.getShooter() instanceof ServerPlayer p) || p.isCreative() || p.isSpectator()) return;
        Awareness.gunshot(p.serverLevel(), p, alarmRadius(p, e.getGunItemStack()));
    }

    /** How far away NPCs notice this shot, from the same loudness TACZ uses for the sound. */
    static int alarmRadius(ServerPlayer shooter, ItemStack gun) {
        IGun iGun = IGun.getIGunOrNull(gun);
        if (iGun == null) return 24;
        Optional<CommonGunIndex> index = TimelessAPI.getCommonGunIndex(iGun.getGunId(gun));
        if (index.isEmpty()) return 24;
        int distance = GunConfig.DEFAULT_GUN_FIRE_SOUND_DISTANCE.get();
        boolean silenced = false;
        try {
            AttachmentCacheProperty cache = IGunOperator.fromLivingEntity(shooter).getCacheProperty();
            Pair<Integer, Boolean> s = cache == null ? null : cache.getCache(GunProperties.SILENCE);
            if (s != null) {
                distance = s.left();
                silenced = s.right();
            }
        } catch (RuntimeException ignored) {
            // no cached attachment data yet: keep the default loudness
        }
        FireSound fs = index.get().getGunData().getFireSound();
        float mult = fs == null ? 1f : silenced ? fs.getSilenceMultiplier() : fs.getFireMultiplier();
        return Math.max(3, Math.min(MAX_ALARM, Math.round(distance * mult * ALARM_SHARE)));
    }
}
