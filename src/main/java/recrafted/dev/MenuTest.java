package recrafted.dev;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.gui.screens.ConfirmScreen;
import net.minecraft.client.gui.screens.GenericDirtMessageScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.Recrafted;
import recrafted.client.menu.MenuButton;
import recrafted.client.menu.MissionLauncher;
import recrafted.client.menu.MissionsScreen;
import recrafted.client.menu.RecraftedTitleScreen;
import recrafted.mission.Mission;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;

/**
 * Screenshots of the title screen and the mission browser at a few GUI scales (-Pmenutest). With
 * -PmenutestPlay it then presses Play mission twice: once creating the contracts world, once reopening it, and
 * checks each time that the contract starts and that no experimental-settings prompt gets in the way.
 */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class MenuTest {
    private static final Logger LOG = LogManager.getLogger("recrafted-menutest");
    private static final boolean ON = Boolean.getBoolean("recrafted.menutest");
    private static final boolean PLAY = Boolean.getBoolean("recrafted.menutest.play");

    private record Step(long delay, long timeout, String name, BooleanSupplier action) {}

    private static final List<Step> STEPS = new ArrayList<>();
    private static int index;
    private static long readyAt, startedAt = -1;
    private static boolean prepared;
    private static int failures;

    private MenuTest() {}

    private static void step(long delay, Runnable r) {
        STEPS.add(new Step(delay, 0, "", () -> {
            r.run();
            return true;
        }));
    }

    /** Polls {@code until} every tick; a timeout counts as a failure and moves on. */
    private static void await(String name, long timeout, BooleanSupplier until) {
        STEPS.add(new Step(0, timeout, name, until));
    }

    private static void check(String what, boolean ok) {
        if (!ok) failures++;
        LOG.info("MENUTEST {} {}", ok ? "ok  " : "FAIL", what);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "ui_" + name + ".png", mc.getMainRenderTarget(), c -> LOG.info("MENUTEST saved {}", name));
    }

    private static void focus(Minecraft mc, int n) {
        int i = 0;
        for (GuiEventListener l : mc.screen.children()) {
            if (l instanceof MenuButton b && i++ == n) {
                mc.screen.setFocused(b);
                return;
            }
        }
    }

    private static void scale(Minecraft mc, int s) {
        mc.options.guiScale().set(s);
        mc.resizeDisplay();
    }

    private static boolean inContract(Minecraft mc, String id) {
        return mc.player != null && mc.screen == null && mc.level != null
                && mc.level.dimension().equals(Mission.byId(id).dimension);
    }

    private static void leaveWorld(Minecraft mc) {
        boolean local = mc.isLocalServer();
        mc.level.disconnect();
        if (local) mc.clearLevel(new GenericDirtMessageScreen(Component.translatable("menu.savingLevel")));
        else mc.clearLevel();
        mc.setScreen(new TitleScreen());
    }

    private static void prepare(Minecraft mc) {
        for (int s : new int[]{0, 2, 3}) {
            String tag = s == 0 ? "auto" : "x" + s;
            step(500, () -> {
                scale(mc, s);
                mc.setScreen(new RecraftedTitleScreen());
            });
            step(4500, () -> shot(mc, "title_" + tag));
            step(200, () -> focus(mc, 1));
            step(600, () -> shot(mc, "title_hover_" + tag));
            step(200, () -> mc.setScreen(new MissionsScreen(mc.screen)));
            step(2500, () -> shot(mc, "missions_" + tag));
            step(2600, () -> shot(mc, "missions_fade_" + tag));
            step(200, () -> {
                if (mc.screen instanceof MissionsScreen ms) ms.select("amsterdam");
            });
            step(2500, () -> shot(mc, "missions_amsterdam_" + tag));
            step(200, () -> {
                if (mc.screen instanceof MissionsScreen ms) ms.select("corvara");
            });
        }
        step(500, () -> scale(mc, 0));
        if (PLAY) {
            for (String pass : new String[]{"create", "reopen", "amsterdam"}) {
                String id = pass.equals("amsterdam") ? "amsterdam" : "corvara";
                step(500, () -> {
                    if (!pass.equals("create")) check(pass + ": contracts world exists", MissionLauncher.worldExists());
                    else LOG.info("MENUTEST create: contracts world {}", MissionLauncher.worldExists() ? "already there (reopening)" : "absent");
                    MissionLauncher.play(new MissionsScreen(new RecraftedTitleScreen()), id);
                });
                await(pass + ": no experimental-settings prompt", 120_000, () -> {
                    if (mc.screen instanceof ConfirmScreen) {
                        check(pass + ": no experimental-settings prompt", false);
                        return true;
                    }
                    return mc.player != null;
                });
                await(pass + ": contract started in " + id, 90_000, () -> inContract(mc, id));
                step(8000, () -> {
                    check(pass + ": arrived in " + id, inContract(mc, id));
                    shot(mc, "play_" + pass);
                });
                step(1500, () -> leaveWorld(mc));
                await(pass + ": back on the title screen", 60_000, () -> mc.screen instanceof RecraftedTitleScreen && mc.level == null);
            }
        }
        step(500, () -> {
            LOG.info("MENUTEST DONE ({} failures)", failures);
            mc.stop();
        });
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (!ON || e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        long now = System.currentTimeMillis();
        if (!prepared) {
            if (!(mc.screen instanceof RecraftedTitleScreen) || mc.getOverlay() != null) return;
            prepared = true;
            mc.getToasts().clear();
            prepare(mc);
            readyAt = now + 3000;
            return;
        }
        mc.getToasts().clear();
        if (index >= STEPS.size() || now < readyAt) return;
        Step s = STEPS.get(index);
        if (startedAt < 0) startedAt = now;
        boolean done;
        try {
            done = s.action().getAsBoolean();
        } catch (Exception ex) {
            LOG.error("MENUTEST step {} failed", index, ex);
            done = true;
        }
        if (!done && s.timeout() > 0 && now - startedAt > s.timeout()) {
            check(s.name() + " (timed out)", false);
            done = true;
        }
        if (!done) return;
        index++;
        startedAt = -1;
        readyAt = now + (index < STEPS.size() ? STEPS.get(index).delay() : 0);
    }
}
