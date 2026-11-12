package recrafted.client.menu;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.AbstractTexture;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.joml.Matrix4f;
import recrafted.Recrafted;

/** Shared look for the title screen and the mission browser: fonts, colours and a few drawing helpers. */
public final class MenuUi {
    public static final ResourceLocation TITLE = font("menu_title");
    public static final ResourceLocation HEADING = font("menu_heading");
    public static final ResourceLocation BUTTON = font("menu_button");
    public static final ResourceLocation LABEL = font("menu_label");
    public static final ResourceLocation TEXT = font("menu_text");
    public static final ResourceLocation SMALL = font("menu_small");

    public static final ResourceLocation BACKGROUND = gui("background");

    public static final int WHITE = 0xFFF4F2EE;
    public static final int DIM = 0xB8E8E6E2;
    public static final int FAINT = 0x80E8E6E2;
    public static final int ACCENT = 0xFFD2AA62;   // brass
    public static final int INK = 0xFF0C0D10;

    private MenuUi() {}

    private static ResourceLocation font(String id) {
        return new ResourceLocation(Recrafted.MODID, id);
    }

    public static ResourceLocation gui(String name) {
        return new ResourceLocation(Recrafted.MODID, "textures/gui/menu/" + name + ".png");
    }

    public static Component text(String s, ResourceLocation font) {
        return Component.literal(s).withStyle(st -> st.withFont(font));
    }

    public static int alpha(int argb, float a) {
        int base = argb >>> 24;
        return ((int) (Mth.clamp(a, 0f, 1f) * base) << 24) | (argb & 0xFFFFFF);
    }

    public static float ease(float t) {
        t = Mth.clamp(t, 0f, 1f);
        return 1f - (1f - t) * (1f - t) * (1f - t);
    }

    /** Smooth (linear) filtering for photos drawn at any scale. */
    public static void smooth(ResourceLocation tex) {
        AbstractTexture t = Minecraft.getInstance().getTextureManager().getTexture(tex);
        t.setFilter(true, false);
    }

    public static void draw(GuiGraphics g, Font font, String s, ResourceLocation face, float x, float y, int color) {
        if ((color >>> 24) < 5) return;
        g.pose().pushPose();
        g.pose().translate(x, y, 0);
        g.drawString(font, text(s, face), 0, 0, color, false);
        g.pose().popPose();
    }

    public static int width(Font font, String s, ResourceLocation face) {
        return font.width(text(s, face));
    }

    /** Letter-spaced text (the fonts have no tracking of their own). Returns the drawn width. */
    public static float tracked(GuiGraphics g, Font font, String s, ResourceLocation face, float x, float y, float tracking, int color) {
        float cx = x;
        for (int i = 0; i < s.length(); i++) {
            String c = String.valueOf(s.charAt(i));
            draw(g, font, c, face, cx, y, color);
            cx += width(font, c, face) + tracking;
        }
        return cx - x - tracking;
    }

    public static float trackedWidth(Font font, String s, ResourceLocation face, float tracking) {
        float w = 0;
        for (int i = 0; i < s.length(); i++) w += width(font, String.valueOf(s.charAt(i)), face) + tracking;
        return Math.max(0, w - tracking);
    }

    /** Word-wraps plain text to a width. */
    public static java.util.List<String> wrap(Font font, String s, ResourceLocation face, float maxWidth) {
        java.util.List<String> out = new java.util.ArrayList<>();
        StringBuilder line = new StringBuilder();
        for (String word : s.split(" ")) {
            String next = line.length() == 0 ? word : line + " " + word;
            if (line.length() > 0 && width(font, next, face) > maxWidth) {
                out.add(line.toString());
                line = new StringBuilder(word);
            } else {
                line = new StringBuilder(next);
            }
        }
        if (line.length() > 0) out.add(line.toString());
        return out;
    }

    /** Cuts text at a word so that it and a trailing ellipsis fit the width. */
    public static String ellipsize(Font font, String s, ResourceLocation face, float maxWidth) {
        if (width(font, s, face) <= maxWidth) return s;
        String cut = s.endsWith(" …") ? s.substring(0, s.length() - 2) : s;
        while (!cut.isEmpty() && width(font, cut + "…", face) > maxWidth) {
            int sp = cut.lastIndexOf(' ');
            cut = sp > 0 ? cut.substring(0, sp) : cut.substring(0, cut.length() - 1);
        }
        cut = cut.replaceAll("[\\s,;:.\u2014-]+$", "");
        return cut + "…";
    }

    /** A rectangle shading from one colour on the left to another on the right. */
    public static void hGradient(GuiGraphics g, float x0, float y0, float x1, float y1, int left, int right) {
        VertexConsumer vc = g.bufferSource().getBuffer(RenderType.gui());
        Matrix4f m = g.pose().last().pose();
        vc.vertex(m, x0, y0, 0).color(left).endVertex();
        vc.vertex(m, x0, y1, 0).color(left).endVertex();
        vc.vertex(m, x1, y1, 0).color(right).endVertex();
        vc.vertex(m, x1, y0, 0).color(right).endVertex();
        g.flush();
    }

    public static void vGradient(GuiGraphics g, float x0, float y0, float x1, float y1, int top, int bottom) {
        VertexConsumer vc = g.bufferSource().getBuffer(RenderType.gui());
        Matrix4f m = g.pose().last().pose();
        vc.vertex(m, x0, y0, 0).color(top).endVertex();
        vc.vertex(m, x0, y1, 0).color(bottom).endVertex();
        vc.vertex(m, x1, y1, 0).color(bottom).endVertex();
        vc.vertex(m, x1, y0, 0).color(top).endVertex();
        g.flush();
    }

    public static void rect(GuiGraphics g, float x0, float y0, float x1, float y1, int color) {
        hGradient(g, x0, y0, x1, y1, color, color);
    }

    /**
     * A photo scaled to cover the box (cropping the overflow), zoomed by {@code zoom} about a point that drifts by
     * (panX, panY) of the spare margin, drawn with the given opacity. Clip with a scissor to keep it in the box.
     */
    public static void photo(GuiGraphics g, ResourceLocation tex, int texW, int texH, float x, float y, float w, float h,
                             float zoom, float panX, float panY, float opacity) {
        if (opacity <= 0.003f) return;
        float s = Math.max(w / texW, h / texH) * zoom;
        float dw = texW * s, dh = texH * s;
        float ox = x + (w - dw) / 2f + panX * (dw - w) / 2f;
        float oy = y + (h - dh) / 2f + panY * (dh - h) / 2f;
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.setShaderColor(1f, 1f, 1f, opacity);
        g.pose().pushPose();
        g.pose().translate(ox, oy, 0);
        g.pose().scale(s, s, 1f);
        g.blit(tex, 0, 0, 0f, 0f, texW, texH, texW, texH);
        g.pose().popPose();
        RenderSystem.setShaderColor(1f, 1f, 1f, 1f);
        RenderSystem.disableBlend();
    }
}
