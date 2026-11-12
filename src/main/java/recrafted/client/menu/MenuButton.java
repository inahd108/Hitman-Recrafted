package recrafted.client.menu;

import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.narration.NarratedElementType;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.network.chat.Component;

/**
 * A text-only menu entry: no frame, a brass bar and a small slide to the right when hovered or focused,
 * and an optional caption that fades in beneath it.
 */
public class MenuButton extends AbstractButton {
    public enum Style { BIG, LINK, PRIMARY, GHOST }

    private final Runnable action;
    private final String label;
    private final String caption;
    private final Style style;
    private float hot;
    private long lastFrame = Util.getMillis();
    /** 0..1, set by the screen for its entrance animation. */
    public float reveal = 1f;

    public MenuButton(int x, int y, int w, int h, String label, String caption, Style style, Runnable action) {
        super(x, y, w, h, Component.literal(label));
        this.label = label;
        this.caption = caption;
        this.style = style;
        this.action = action;
    }

    public static int linkWidth(String label) {
        return MenuUi.width(Minecraft.getInstance().font, label, MenuUi.SMALL) + 2;
    }

    @Override
    public void onPress() {
        action.run();
    }

    @Override
    protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partial) {
        long now = Util.getMillis();
        float dt = Math.min(0.1f, (now - lastFrame) / 1000f);
        lastFrame = now;
        float target = isHoveredOrFocused() && active ? 1f : 0f;
        hot += (target - hot) * Math.min(1f, dt * 12f);
        Font font = Minecraft.getInstance().font;
        float a = MenuUi.ease(reveal);
        float slide = (1f - a) * -18f;
        switch (style) {
            case BIG -> {
                float x = getX() + slide + hot * 7f;
                float y = getY() + (height - 12) / 2f;
                if (hot > 0.01f) {
                    MenuUi.hGradient(g, getX() - 14, getY(), getX() + width, getY() + height,
                            MenuUi.alpha(0x30D2AA62, hot * a), 0x00D2AA62);
                    MenuUi.rect(g, getX() - 14, getY() + 3, getX() - 12, getY() + height - 3, MenuUi.alpha(MenuUi.ACCENT, hot * a));
                }
                int color = blend(MenuUi.DIM, MenuUi.WHITE, hot);
                MenuUi.tracked(g, font, label, MenuUi.BUTTON, x, y, 1.6f, MenuUi.alpha(color, a));
                if (caption != null && hot > 0.02f) {
                    float cw = MenuUi.trackedWidth(font, label, MenuUi.BUTTON, 1.6f);
                    MenuUi.draw(g, font, caption, MenuUi.SMALL, x + cw + 10, y + 4.5f, MenuUi.alpha(MenuUi.FAINT, hot * a));
                }
            }
            case LINK -> {
                int color = blend(MenuUi.FAINT, MenuUi.WHITE, hot);
                MenuUi.draw(g, font, label, MenuUi.SMALL, getX() + 1, getY() + (height - 7) / 2f, MenuUi.alpha(color, a));
                if (hot > 0.01f) {
                    MenuUi.rect(g, getX() + 1, getY() + height - 1, getX() + 1 + (width - 2) * hot, getY() + height,
                            MenuUi.alpha(MenuUi.ACCENT, a));
                }
            }
            case PRIMARY -> {
                int fill = blend(0xFFC79D55, 0xFFE2BC74, hot);
                MenuUi.rect(g, getX(), getY(), getX() + width, getY() + height, MenuUi.alpha(fill, a));
                float tw = MenuUi.trackedWidth(font, label, MenuUi.LABEL, 1.4f);
                MenuUi.tracked(g, font, label, MenuUi.LABEL, getX() + (width - tw) / 2f, getY() + (height - 7) / 2f + 1f, 1.4f,
                        MenuUi.alpha(MenuUi.INK, a));
            }
            case GHOST -> {
                int line = blend(0x50FFFFFF, 0xC0FFFFFF, hot);
                MenuUi.rect(g, getX(), getY(), getX() + width, getY() + height, MenuUi.alpha(blend(0x66101216, 0x88303338, hot), a));
                outline(g, getX(), getY(), getX() + width, getY() + height, MenuUi.alpha(line, a));
                float tw = MenuUi.trackedWidth(font, label, MenuUi.LABEL, 1.4f);
                MenuUi.tracked(g, font, label, MenuUi.LABEL, getX() + (width - tw) / 2f, getY() + (height - 7) / 2f + 1f, 1.4f,
                        MenuUi.alpha(blend(MenuUi.DIM, MenuUi.WHITE, hot), a));
            }
        }
    }

    static void outline(GuiGraphics g, float x0, float y0, float x1, float y1, int color) {
        MenuUi.rect(g, x0, y0, x1, y0 + 1, color);
        MenuUi.rect(g, x0, y1 - 1, x1, y1, color);
        MenuUi.rect(g, x0, y0 + 1, x0 + 1, y1 - 1, color);
        MenuUi.rect(g, x1 - 1, y0 + 1, x1, y1 - 1, color);
    }

    static int blend(int a, int b, float t) {
        int r = 0;
        for (int shift = 0; shift < 32; shift += 8) {
            int ca = (a >>> shift) & 0xFF, cb = (b >>> shift) & 0xFF;
            r |= (Math.round(ca + (cb - ca) * t) & 0xFF) << shift;
        }
        return r;
    }

    @Override
    protected void updateWidgetNarration(NarrationElementOutput out) {
        out.add(NarratedElementType.TITLE, Component.literal(caption == null ? label : label + ". " + caption));
    }
}
