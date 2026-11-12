package recrafted.client.menu;

import net.minecraft.Util;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import recrafted.Recrafted;
import recrafted.mission.Mission;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Mission browser: locations along the top, a slowly turning flyover of the selected map, the briefing,
 * the targets with their faces, and a button that drops you into the contract.
 */
public class MissionsScreen extends ScaledScreen {
    static final int FRAMES = 8, FRAME_W = 960, FRAME_H = 540;
    static final float HOLD = 3.6f, FADE = 1.6f;

    private final Screen parent;
    private final long opened = Util.getMillis();
    private final List<ResourceLocation> frames = new ArrayList<>();
    private Mission mission;
    private static int selected;
    private final List<float[]> tabBoxes = new ArrayList<>();
    private MenuButton play;

    public MissionsScreen(Screen parent) {
        super(Component.literal("Missions"));
        this.parent = parent;
        loadFrames();
    }

    private int margin() {
        return Math.max(16, (int) (width * 0.045f));
    }

    private float[] previewBox() {
        int m = margin();
        float top = m + 40;
        float w = (width - 2 * m) * 0.585f;
        float h = Math.min(w * 9f / 16f, height - m - 18 - 24 - top);
        w = Math.min(w, h * 16f / 9f);
        return new float[]{m, top, w, h};
    }

    @Override
    protected void layout() {
        MissionLauncher.cancelPending();
        selected = Math.floorMod(selected, Mission.IDS.size());
        try {
            mission = Mission.byId(Mission.IDS.get(selected));
        } catch (Exception e) {
            mission = null;
        }
        loadFrames();
        for (ResourceLocation f : frames) MenuUi.smooth(f);
        MenuUi.smooth(MenuUi.BACKGROUND);
        int m = margin();
        int by = height - m - 18;
        addRenderableWidget(new MenuButton(m, by, 64, 18, "BACK", null, MenuButton.Style.GHOST, this::onClose));
        play = new MenuButton(width - m - 118, by, 118, 18, "PLAY MISSION", null, MenuButton.Style.PRIMARY,
                () -> MissionLauncher.play(this, Mission.IDS.get(selected)));
        play.active = mission != null;
        addRenderableWidget(play);
        setInitialFocus(play);
    }

    @Override
    public void onClose() {
        minecraft.setScreen(parent);
    }

    @Override
    protected void renderScaled(GuiGraphics g, int mouseX, int mouseY, float partial) {
        float t = (Util.getMillis() - opened) / 1000f;
        Font font = this.font;
        int m = margin();

        // backdrop: the title photo, pushed far back
        MenuUi.photo(g, MenuUi.BACKGROUND, RecraftedTitleScreen.BG_W, RecraftedTitleScreen.BG_H, 0, 0, width, height, 1.08f, 0f, 0f, 1f);
        MenuUi.rect(g, 0, 0, width, height, 0xE00A0B0E);
        MenuUi.vGradient(g, 0, 0, width, height, 0x30000000, 0xA0000000);

        float in = MenuUi.ease(t / 0.6f);
        // header
        MenuUi.tracked(g, font, "MISSIONS", MenuUi.HEADING, m, m - 2, 2.2f, MenuUi.alpha(MenuUi.WHITE, in));
        drawTabs(g, font, m, m + 20, in);

        float[] box = previewBox();
        drawPreview(g, font, box, t, in);
        drawFacts(g, font, box[0], box[1] + box[3] + 9, in);
        float colX = box[0] + box[2] + 16, colW = width - m - colX;
        drawDetails(g, font, colX, box[1], colW, in);

        // footer note beside the play button
        if (mission != null) {
            String note = MissionLauncher.worldExists() ? "Continues in your world “" + MissionLauncher.WORLD_NAME + "”"
                    : "Creates a world called “" + MissionLauncher.WORLD_NAME + "”";
            float nw = MenuUi.width(font, note, MenuUi.SMALL);
            MenuUi.draw(g, font, note, MenuUi.SMALL, play.getX() - 10 - nw, play.getY() + 6, MenuUi.alpha(MenuUi.FAINT, in));
        }
        renderWidgets(g, mouseX, mouseY, partial);
    }

    /** Corvara's frames are preview_N; later contracts prefix theirs with the mission id. */
    private void loadFrames() {
        frames.clear();
        String id = Mission.IDS.get(Math.floorMod(selected, Mission.IDS.size()));
        for (int i = 0; i < FRAMES; i++) frames.add(MenuUi.gui(id.equals("corvara") ? "preview_" + i : id + "_preview_" + i));
    }

    private void drawTabs(GuiGraphics g, Font font, float x, float y, float a) {
        MenuUi.tracked(g, font, "LOCATIONS", MenuUi.SMALL, x, y + 1, 1.2f, MenuUi.alpha(MenuUi.FAINT, a));
        float cx = x + MenuUi.trackedWidth(font, "LOCATIONS", MenuUi.SMALL, 1.2f) + 14;
        tabBoxes.clear();
        for (int i = 0; i < Mission.IDS.size(); i++) {
            String name = Mission.IDS.get(i).toUpperCase(Locale.ROOT);
            boolean on = i == selected;
            float w = MenuUi.tracked(g, font, name, MenuUi.LABEL, cx, y, 1.6f, MenuUi.alpha(on ? MenuUi.WHITE : 0x80E8E6E2, a));
            if (on) MenuUi.rect(g, cx, y + 10, cx + w, y + 11, MenuUi.alpha(MenuUi.ACCENT, a));
            tabBoxes.add(new float[]{cx - 3, y - 3, cx + w + 3, y + 13});
            cx += w + 16;
        }
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        double x = mx / k, y = my / k;
        for (int i = 0; i < tabBoxes.size(); i++) {
            float[] b = tabBoxes.get(i);
            if (x >= b[0] && x <= b[2] && y >= b[1] && y <= b[3] && i != selected) {
                selected = i;
                rebuildWidgets();
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_RIGHT || key == org.lwjgl.glfw.GLFW.GLFW_KEY_LEFT) {
            selected += key == org.lwjgl.glfw.GLFW.GLFW_KEY_RIGHT ? 1 : -1;
            rebuildWidgets();
            return true;
        }
        return super.keyPressed(key, scan, mods);
    }

    /** For the menu test: switch to a contract by id. */
    public void select(String id) {
        int i = Mission.IDS.indexOf(id);
        if (i >= 0) {
            selected = i;
            rebuildWidgets();
        }
    }

    /** Cross-fading flyover frames around the island, each drifting in slowly, so the map seems to turn. */
    private void drawPreview(GuiGraphics g, Font font, float[] box, float t, float a) {
        float x = box[0], y = box[1], w = box[2], h = box[3];
        MenuUi.rect(g, x - 1, y - 1, x + w + 1, y + h + 1, MenuUi.alpha(0x40FFFFFF, a));
        MenuUi.rect(g, x, y, x + w, y + h, 0xFF000000);
        scissor(g, x, y, x + w, y + h);
        float period = HOLD + FADE;
        int cur = (int) (t / period) % FRAMES;
        float local = t % period;
        float fade = Mth.clamp((local - HOLD) / FADE, 0f, 1f);
        int next = (cur + 1) % FRAMES;
        drawFrame(g, cur, local + 0f, box, a);
        if (fade > 0f) drawFrame(g, next, local - HOLD, box, a * smoothstep(fade));
        g.disableScissor();
        // caption over the bottom of the picture
        MenuUi.vGradient(g, x, y + h * 0.45f, x + w, y + h, 0x00000000, MenuUi.alpha(0xD0000000, a));
        if (mission != null) {
            float cy = y + h - 33;
            MenuUi.tracked(g, font, mission.location.toUpperCase(Locale.ROOT), MenuUi.SMALL, x + 10, cy, 1.4f, MenuUi.alpha(MenuUi.ACCENT, a));
            MenuUi.tracked(g, font, mission.title.toUpperCase(Locale.ROOT), MenuUi.HEADING, x + 9, cy + 10, 1.8f, MenuUi.alpha(MenuUi.WHITE, a));
        }
        for (int i = 0; i < FRAMES; i++) {                       // progress ticks
            float px = x + w - 10 - (FRAMES - i) * 7;
            float on = i == cur ? 1f - fade : i == next ? fade : 0f;
            MenuUi.rect(g, px, y + h - 9, px + 5, y + h - 8, MenuUi.alpha(MenuButton.blend(0x60FFFFFF, MenuUi.ACCENT, on), a));
        }
    }

    private void drawFrame(GuiGraphics g, int i, float since, float[] box, float opacity) {
        float p = Mth.clamp((since + FADE) / (HOLD + 2 * FADE), 0f, 1f);
        float zoom = 1.02f + 0.07f * p;
        float pan = (i % 2 == 0 ? -1f : 1f) * (0.6f - 1.2f * p);
        MenuUi.photo(g, frames.get(i), FRAME_W, FRAME_H, box[0], box[1], box[2], box[3], zoom, pan, 0.15f, opacity);
    }

    private static float smoothstep(float x) {
        return x * x * (3f - 2f * x);
    }

    /** One line under the picture: what the contract asks and what you start with. */
    private void drawFacts(GuiGraphics g, Font font, float x, float y, float a) {
        if (mission == null) return;
        String gear = net.minecraftforge.fml.ModList.get().isLoaded("tacz") ? "Passero .22, fibre wire, coins" : "Fibre wire, coins";
        String[][] facts = {{"TARGETS", String.valueOf(mission.targets.size())},
                {"OBJECTIVES", String.valueOf(mission.objectives.size())}, {"GEAR", gear}};
        float cx = x;
        for (String[] f : facts) {
            cx += MenuUi.tracked(g, font, f[0], MenuUi.SMALL, cx, y, 1.2f, MenuUi.alpha(MenuUi.ACCENT, a)) + 5;
            MenuUi.draw(g, font, f[1], MenuUi.SMALL, cx, y, MenuUi.alpha(MenuUi.DIM, a));
            cx += MenuUi.width(font, f[1], MenuUi.SMALL) + 14;
        }
    }

    private void drawDetails(GuiGraphics g, Font font, float x, float y, float w, float a) {
        if (mission == null) {
            MenuUi.draw(g, font, "The mission data could not be read.", MenuUi.TEXT, x, y, MenuUi.alpha(MenuUi.DIM, a));
            return;
        }
        MenuUi.tracked(g, font, "BRIEFING", MenuUi.LABEL, x, y, 1.4f, MenuUi.alpha(MenuUi.ACCENT, a));
        float cy = y + 13;
        float bottomTargets = height - margin() - 18 - 10;
        int targetRows = mission.targets.size();
        float targetsH = 14 + targetRows * 25;
        float briefMax = bottomTargets - targetsH - 8;
        // the hook and the closing order; whatever does not fit ends in an ellipsis
        String brief = mission.briefing.size() > 2 ? mission.briefing.get(1) + " " + mission.briefing.get(mission.briefing.size() - 1)
                : String.join(" ", mission.briefing);
        List<String> lines = MenuUi.wrap(font, brief, MenuUi.TEXT, w);
        int room = Math.max(1, (int) ((briefMax - cy) / 10));
        for (int i = 0; i < lines.size() && i < room; i++) {
            String line = i == room - 1 && lines.size() > room ? MenuUi.ellipsize(font, lines.get(i) + " …", MenuUi.TEXT, w) : lines.get(i);
            MenuUi.draw(g, font, line, MenuUi.TEXT, x, cy, MenuUi.alpha(MenuUi.DIM, a));
            cy += 10;
        }
        cy = Math.max(cy + 8, bottomTargets - targetsH);
        MenuUi.tracked(g, font, "TARGETS", MenuUi.LABEL, x, cy, 1.4f, MenuUi.alpha(MenuUi.ACCENT, a));
        cy += 14;
        for (Mission.Target target : mission.targets) {
            face(g, target.id(), x, cy, 18, a);
            MenuUi.draw(g, font, target.name(), MenuUi.TEXT, x + 25, cy + 1, MenuUi.alpha(MenuUi.WHITE, a));
            MenuUi.draw(g, font, MenuUi.ellipsize(font, target.desc(), MenuUi.SMALL, w - 25), MenuUi.SMALL, x + 25, cy + 11,
                    MenuUi.alpha(MenuUi.FAINT, a));
            cy += 25;
        }
    }

    /** The target's face, cut from their skin, behind a thin frame. */
    private void face(GuiGraphics g, String id, float x, float y, int size, float a) {
        ResourceLocation skin = new ResourceLocation(Recrafted.MODID, "textures/entity/npc/" + id + "_0.png");
        MenuUi.rect(g, x - 1, y - 1, x + size + 1, y + size + 1, MenuUi.alpha(0x50FFFFFF, a));
        if (id.equals("meester") || minecraft.getResourceManager().getResource(skin).isEmpty()) {
            MenuUi.rect(g, x, y, x + size, y + size, MenuUi.alpha(0xFF1A1C21, a));
            MenuUi.rect(g, x + size * .3f, y + size * .2f, x + size * .7f, y + size * .62f, MenuUi.alpha(0xFF3A3E46, a));
            MenuUi.rect(g, x + size * .15f, y + size * .66f, x + size * .85f, y + size, MenuUi.alpha(0xFF3A3E46, a));
            MenuUi.draw(g, font, "?", MenuUi.LABEL, x + size / 2f - 2, y + size * .28f, MenuUi.alpha(MenuUi.ACCENT, a));
            return;
        }
        com.mojang.blaze3d.systems.RenderSystem.setShaderColor(1f, 1f, 1f, a);
        com.mojang.blaze3d.systems.RenderSystem.enableBlend();
        g.blit(skin, (int) x, (int) y, size, size, 8f, 8f, 8, 8, 64, 64);
        g.blit(skin, (int) x, (int) y, size, size, 40f, 8f, 8, 8, 64, 64);
        com.mojang.blaze3d.systems.RenderSystem.setShaderColor(1f, 1f, 1f, 1f);
        com.mojang.blaze3d.systems.RenderSystem.disableBlend();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
