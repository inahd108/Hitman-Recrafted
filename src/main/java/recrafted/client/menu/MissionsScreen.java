package recrafted.client.menu;

import net.minecraft.Util;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
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
public class MissionsScreen extends Screen {
    static final int FRAMES = 8, FRAME_W = 960, FRAME_H = 540;
    static final float HOLD = 3.6f, FADE = 1.6f;

    private final Screen parent;
    private final long opened = Util.getMillis();
    private final List<ResourceLocation> frames = new ArrayList<>();
    private Mission mission;
    private MenuButton play;

    public MissionsScreen(Screen parent) {
        super(Component.literal("Missions"));
        this.parent = parent;
        for (int i = 0; i < FRAMES; i++) frames.add(MenuUi.gui("preview_" + i));
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
    protected void init() {
        MissionLauncher.cancelPending();
        try {
            mission = Mission.corvara();
        } catch (Exception e) {
            mission = null;
        }
        for (ResourceLocation f : frames) MenuUi.smooth(f);
        MenuUi.smooth(MenuUi.BACKGROUND);
        int m = margin();
        int by = height - m - 18;
        addRenderableWidget(new MenuButton(m, by, 64, 18, "BACK", null, MenuButton.Style.GHOST, this::onClose));
        play = new MenuButton(width - m - 118, by, 118, 18, "PLAY MISSION", null, MenuButton.Style.PRIMARY,
                () -> MissionLauncher.play(this));
        play.active = mission != null;
        addRenderableWidget(play);
        setInitialFocus(play);
    }

    @Override
    public void onClose() {
        minecraft.setScreen(parent);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
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
        super.render(g, mouseX, mouseY, partial);
    }

    private void drawTabs(GuiGraphics g, Font font, float x, float y, float a) {
        MenuUi.tracked(g, font, "LOCATIONS", MenuUi.SMALL, x, y + 1, 1.2f, MenuUi.alpha(MenuUi.FAINT, a));
        float cx = x + MenuUi.trackedWidth(font, "LOCATIONS", MenuUi.SMALL, 1.2f) + 14;
        float w = MenuUi.tracked(g, font, "CORVARA", MenuUi.LABEL, cx, y, 1.6f, MenuUi.alpha(MenuUi.WHITE, a));
        MenuUi.rect(g, cx, y + 10, cx + w, y + 11, MenuUi.alpha(MenuUi.ACCENT, a));
        cx += w + 16;
        float lw = MenuUi.tracked(g, font, "CLASSIFIED", MenuUi.LABEL, cx, y, 1.6f, MenuUi.alpha(0x50E8E6E2, a));
        MenuUi.draw(g, font, "more contracts on the way", MenuUi.SMALL, cx + lw + 8, y + 1, MenuUi.alpha(0x40E8E6E2, a));
    }

    /** Cross-fading flyover frames around the island, each drifting in slowly, so the map seems to turn. */
    private void drawPreview(GuiGraphics g, Font font, float[] box, float t, float a) {
        float x = box[0], y = box[1], w = box[2], h = box[3];
        MenuUi.rect(g, x - 1, y - 1, x + w + 1, y + h + 1, MenuUi.alpha(0x40FFFFFF, a));
        MenuUi.rect(g, x, y, x + w, y + h, 0xFF000000);
        g.enableScissor((int) x, (int) y, (int) Math.ceil(x + w), (int) Math.ceil(y + h));
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
        // as many whole paragraphs as fit, the closing order always last
        List<String> paras = new ArrayList<>(mission.briefing);
        String last = paras.isEmpty() ? "" : paras.remove(paras.size() - 1);
        List<FormattedCharSequence> lines = new ArrayList<>(font.split(MenuUi.text(last, MenuUi.TEXT), (int) w));
        int room = (int) ((briefMax - cy) / 10);
        for (int i = paras.size() - 1; i >= 1; i--) {
            List<FormattedCharSequence> p = font.split(MenuUi.text(paras.get(i), MenuUi.TEXT), (int) w);
            if (lines.size() + p.size() + 1 > room) continue;
            List<FormattedCharSequence> merged = new ArrayList<>(p);
            merged.add(FormattedCharSequence.EMPTY);
            merged.addAll(lines);
            lines = merged;
        }
        for (FormattedCharSequence line : lines) {
            if (cy + 10 > briefMax) break;
            g.drawString(font, line, (int) x, (int) cy, MenuUi.alpha(MenuUi.DIM, a), false);
            cy += line == FormattedCharSequence.EMPTY ? 5 : 10;
        }
        cy = Math.max(cy + 8, bottomTargets - targetsH);
        MenuUi.tracked(g, font, "TARGETS", MenuUi.LABEL, x, cy, 1.4f, MenuUi.alpha(MenuUi.ACCENT, a));
        cy += 14;
        for (Mission.Target target : mission.targets) {
            face(g, target.id(), x, cy, 18, a);
            MenuUi.draw(g, font, target.name(), MenuUi.TEXT, x + 25, cy + 1, MenuUi.alpha(MenuUi.WHITE, a));
            List<FormattedCharSequence> d = font.split(MenuUi.text(target.desc(), MenuUi.SMALL), (int) (w - 25));
            if (!d.isEmpty()) g.drawString(font, d.get(0), (int) x + 25, (int) cy + 11, MenuUi.alpha(MenuUi.FAINT, a), false);
            cy += 25;
        }
    }

    /** The target's face, cut from their skin, behind a thin frame. */
    private static void face(GuiGraphics g, String id, float x, float y, int size, float a) {
        ResourceLocation skin = new ResourceLocation(Recrafted.MODID, "textures/entity/npc/" + id + "_0.png");
        MenuUi.rect(g, x - 1, y - 1, x + size + 1, y + size + 1, MenuUi.alpha(0x50FFFFFF, a));
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
