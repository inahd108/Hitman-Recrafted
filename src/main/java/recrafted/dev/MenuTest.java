package recrafted.dev;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import recrafted.Recrafted;
import recrafted.client.menu.MenuButton;
import recrafted.client.menu.MissionsScreen;
import recrafted.client.menu.RecraftedTitleScreen;

import java.util.ArrayList;
import java.util.List;

/** Screenshots of the title screen and the mission browser at a few GUI scales, with -Pmenutest. */
@Mod.EventBusSubscriber(modid = Recrafted.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class MenuTest {
    private static final Logger LOG = LogManager.getLogger("recrafted-menutest");
    private static final boolean ON = Boolean.getBoolean("recrafted.menutest");
    private static final List<Runnable> STEPS = new ArrayList<>();
    private static final List<Long> DELAYS = new ArrayList<>();
    private static int index = -1;
    private static long nextAt;
    private static boolean prepared;

    private MenuTest() {}

    private static void step(long delay, Runnable r) {
        STEPS.add(r);
        DELAYS.add(delay);
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

    private static void prepare(Minecraft mc) {
        int[] scales = {0, 2, 3};
        for (int s : scales) {
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
        }
        step(500, () -> {
            scale(mc, 0);
            LOG.info("MENUTEST DONE");
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
            nextAt = now + 3000;
            return;
        }
        mc.getToasts().clear();
        if (now < nextAt || index >= STEPS.size() - 1) return;
        index++;
        try {
            STEPS.get(index).run();
        } catch (Exception ex) {
            LOG.error("MENUTEST step {} failed", index, ex);
        }
        nextAt = now + (index + 1 < DELAYS.size() ? DELAYS.get(index + 1) : 1000);
    }
}
