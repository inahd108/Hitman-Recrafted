package recrafted.client.menu;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.GenericDirtMessageScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraft.world.level.storage.PrimaryLevelData;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.Recrafted;

import java.nio.file.Path;

/**
 * Plays a contract straight from the mission browser: opens (or first creates) a world kept for the missions,
 * then starts the contract once the player is in it. Also swaps the vanilla title screen for ours.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class MissionLauncher {
    private static final Logger LOG = LogManager.getLogger("recrafted");
    public static final String WORLD_ID = "recrafted_contracts";
    public static final String WORLD_NAME = "Recrafted Contracts";

    private static boolean pending;
    private static int waitTicks;

    private MissionLauncher() {}

    public static boolean worldExists() {
        try {
            return Minecraft.getInstance().getLevelSource().levelExists(WORLD_ID);
        } catch (Exception e) {
            return false;
        }
    }

    public static void play(Screen from) {
        Minecraft mc = Minecraft.getInstance();
        pending = true;
        waitTicks = 30;
        if (worldExists()) {
            mc.createWorldOpenFlows().loadLevel(from, WORLD_ID);
            return;
        }
        mc.forceSetScreen(new GenericDirtMessageScreen(Component.translatable("createWorld.preparing")));
        LevelSettings settings = new LevelSettings(WORLD_NAME, GameType.SURVIVAL, false, Difficulty.NORMAL, true,
                new GameRules(), WorldDataConfiguration.DEFAULT);
        mc.createWorldOpenFlows().createFreshLevel(WORLD_ID, settings, WorldOptions.defaultWithRandomSeed(),
                WorldPresets::createNormalWorldDimensions);
    }

    /** A screen of ours came back up, so whatever we were waiting to start is not happening. */
    public static void cancelPending() {
        pending = false;
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (!pending || e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.getConnection() == null || mc.screen != null) return;
        if (--waitTicks > 0) return;
        pending = false;
        mc.player.connection.sendCommand("contract start");
    }

    @SubscribeEvent
    public static void opening(ScreenEvent.Opening e) {
        if (e.getNewScreen() instanceof TitleScreen && !RecraftedTitleScreen.classic) e.setNewScreen(new RecraftedTitleScreen());
    }

    /** The contracts world has a custom dimension; it was created on purpose, so skip the "experimental" prompt. */
    @SubscribeEvent
    public static void started(ServerStartedEvent e) {
        Path dir = e.getServer().getWorldPath(LevelResource.ROOT).toAbsolutePath().normalize().getFileName();
        if (dir != null && dir.toString().equals(WORLD_ID) && e.getServer().getWorldData() instanceof PrimaryLevelData pld
                && !pld.hasConfirmedExperimentalWarning()) {
            pld.withConfirmedWarning(true);
            LOG.info("Contracts world: experimental-settings prompt confirmed");
        }
    }
}
