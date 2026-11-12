package recrafted.client.menu;

import net.minecraft.SharedConstants;
import net.minecraft.Util;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.LanguageSelectScreen;
import net.minecraft.client.gui.screens.OptionsScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen;
import net.minecraft.client.gui.screens.multiplayer.SafetyScreen;
import net.minecraft.client.gui.screens.worldselection.SelectWorldScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraftforge.fml.ModList;

import java.util.ArrayList;
import java.util.List;

/**
 * The title screen: the operative in his penthouse over Corvara at dusk, with the menu down the left.
 * Play and Options are the vanilla screens; Missions opens the mission browser.
 */
public class RecraftedTitleScreen extends Screen {
    /** Set by "Classic menu": the vanilla title screen is left alone for the rest of the session. */
    public static boolean classic;
    private static boolean shownOnce;

    static final int BG_W = 1920, BG_H = 1080;

    private final List<MenuButton> entries = new ArrayList<>();
    private final long opened = Util.getMillis();
    private final boolean intro;

    public RecraftedTitleScreen() {
        super(Component.literal("Recrafted: Contracts"));
        intro = !shownOnce;
        shownOnce = true;
    }

    @Override
    protected void init() {
        MissionLauncher.cancelPending();
        MenuUi.smooth(MenuUi.BACKGROUND);
        entries.clear();
        int left = left();
        int y = (int) (height * 0.47f);
        int h = 20, gap = 3, w = Math.max(150, (int) (width * 0.3f));
        add(new MenuButton(left, y, w, h, "PLAY", "Your worlds", MenuButton.Style.BIG,
                () -> minecraft.setScreen(new SelectWorldScreen(this))));
        add(new MenuButton(left, y += h + gap, w, h, "MISSIONS", "Locations and contracts", MenuButton.Style.BIG,
                () -> minecraft.setScreen(new MissionsScreen(this))));
        add(new MenuButton(left, y += h + gap, w, h, "OPTIONS", "Video, sound and controls", MenuButton.Style.BIG,
                () -> minecraft.setScreen(new OptionsScreen(this, minecraft.options))));
        add(new MenuButton(left, y + h + gap, w, h, "QUIT", null, MenuButton.Style.BIG, minecraft::stop));

        int ly = height - 22, lx = left;
        String[] links = {"Multiplayer", "Mods", "Language", "Classic menu"};
        Runnable[] actions = {
                () -> minecraft.setScreen(minecraft.options.skipMultiplayerWarning ? new JoinMultiplayerScreen(this) : new SafetyScreen(this)),
                () -> minecraft.setScreen(new net.minecraftforge.client.gui.ModListScreen(this)),
                () -> minecraft.setScreen(new LanguageSelectScreen(this, minecraft.options, minecraft.getLanguageManager())),
                () -> {
                    classic = true;
                    minecraft.setScreen(new TitleScreen());
                }};
        for (int i = 0; i < links.length; i++) {
            int lw = MenuButton.linkWidth(links[i]);
            add(new MenuButton(lx, ly, lw, 11, links[i], null, MenuButton.Style.LINK, actions[i]));
            lx += lw + 12;
        }
    }

    private void add(MenuButton b) {
        entries.add(b);
        addRenderableWidget(b);
    }

    private int left() {
        return Math.max(22, (int) (width * 0.075f));
    }

    private float seconds() {
        return (Util.getMillis() - opened) / 1000f;
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        float t = seconds();
        float in = intro ? t : t + 3f;            // returning to the menu skips most of the entrance
        drawBackdrop(g, width, height, t);
        Font font = this.font;
        int left = left();

        // title block
        float ty = height * 0.2f;
        float ta = MenuUi.ease((in - 0.5f) / 1.2f);
        float tx = left - (1f - ta) * 10f;
        MenuUi.tracked(g, font, "RECRAFTED", MenuUi.LABEL, tx + 1, ty, 3.2f, MenuUi.alpha(MenuUi.ACCENT, ta));
        MenuUi.tracked(g, font, "CONTRACTS", MenuUi.TITLE, tx, ty + 10, 2.4f, MenuUi.alpha(MenuUi.WHITE, ta));
        float lineW = 34 * MenuUi.ease((in - 1.0f) / 1.0f);
        MenuUi.rect(g, left + 1, ty + 44, left + 1 + lineW, ty + 45, MenuUi.alpha(MenuUi.ACCENT, ta));
        MenuUi.draw(g, font, "Everyone keeps a routine.", MenuUi.SMALL, left + 1, ty + 50, MenuUi.alpha(MenuUi.FAINT, ta));

        for (int i = 0; i < entries.size(); i++) {
            MenuButton b = entries.get(i);
            b.reveal = Mth.clamp((in - 1.0f - i * 0.09f) / 0.7f, 0f, 1f);
        }
        super.render(g, mouseX, mouseY, partial);

        String version = "v" + ModList.get().getModContainerById("recrafted").map(c -> c.getModInfo().getVersion().toString()).orElse("?")
                + "  ·  Minecraft " + SharedConstants.getCurrentVersion().getName();
        float va = MenuUi.ease((in - 1.6f) / 1f);
        MenuUi.draw(g, font, version, MenuUi.SMALL, width - left - MenuUi.width(font, version, MenuUi.SMALL), height - 20,
                MenuUi.alpha(0x60E8E6E2, va));

        if (intro && t < 1.6f) {                                 // fade up from black on launch
            MenuUi.rect(g, 0, 0, width, height, MenuUi.alpha(0xFF000000, 1f - MenuUi.ease(t / 1.6f)));
        }
    }

    /** The photo, slowly breathing, with a dark wash on the left for the menu and a vignette at the bottom. */
    static void drawBackdrop(GuiGraphics g, int width, int height, float t) {
        float zoom = 1.035f + 0.02f * Mth.sin(t * 0.09f);
        MenuUi.photo(g, MenuUi.BACKGROUND, BG_W, BG_H, 0, 0, width, height, zoom, 0.25f * Mth.sin(t * 0.05f), 0.1f, 1f);
        MenuUi.hGradient(g, 0, 0, width * 0.22f, height, 0xE6080A0D, 0xB3080A0D);
        MenuUi.hGradient(g, width * 0.22f, 0, width * 0.55f, height, 0xB3080A0D, 0x00080A0D);
        MenuUi.vGradient(g, 0, height * 0.7f, width, height, 0x00000000, 0xB0000000);
        MenuUi.vGradient(g, 0, 0, width, height * 0.18f, 0x70000000, 0x00000000);
    }

    @Override
    public boolean shouldCloseOnEsc() {
        return false;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
