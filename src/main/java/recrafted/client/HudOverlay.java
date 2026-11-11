package recrafted.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/** Objectives, disguise, and how much trouble you are in. */
public class HudOverlay implements IGuiOverlay {
    private static final int[] STATUS_COLOR = {0xFF9FE3A0, 0xFFFFB347, 0xFFFFE066, 0xFFFF4D4D};
    private static final String[] STATUS_TEXT = {"BLENDING IN", "TRESPASSING", "SUSPICIOUS", "HUNTED"};

    @Override
    public void render(ForgeGui gui, GuiGraphics g, float partialTick, int w, int h) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.options.hideGui || mc.player == null || !ClientState.missionActive) return;
        Font font = mc.font;
        // objectives
        int x = 8, y = 8;
        int pw = font.width(ClientState.missionTitle) + 12;
        for (String s : ClientState.OBJECTIVES) pw = Math.max(pw, font.width(s) + 26);
        int ph = 18 + ClientState.OBJECTIVES.size() * 11 + 4;
        g.fill(x - 4, y - 4, x + pw, y + ph - 4, 0x90101418);
        g.fill(x - 4, y - 4, x - 2, y + ph - 4, 0xFFD8322F);
        g.drawString(font, ClientState.missionTitle, x + 2, y, 0xFFFFFFFF, false);
        y += 14;
        for (int i = 0; i < ClientState.OBJECTIVES.size(); i++) {
            boolean done = i < ClientState.OBJECTIVES_DONE.size() && ClientState.OBJECTIVES_DONE.get(i);
            g.drawString(font, done ? "✔" : "○", x + 2, y, done ? 0xFF7CE38B : 0xFFD8322F, false);
            g.drawString(font, ClientState.OBJECTIVES.get(i), x + 14, y, done ? 0xFF8A9199 : 0xFFE8EAED, false);
            y += 11;
        }
        // status strip above the hotbar
        int st = Math.max(0, Math.min(3, ClientState.status));
        int cx = w / 2, by = h - 62;
        String disguise = "Wearing: " + ClientState.disguiseLabel;
        String status = ClientState.dragging ? "DRAGGING A BODY" : STATUS_TEXT[st];
        int col = ClientState.dragging ? 0xFFFF4D4D : STATUS_COLOR[st];
        int tw = Math.max(font.width(disguise), font.width(status)) + 16;
        g.fill(cx - tw / 2, by - 16, cx + tw / 2, by + 12, 0x90101418);
        g.drawCenteredString(font, status, cx, by - 13, col);
        g.drawCenteredString(font, disguise, cx, by - 2, 0xFFC8CCD0);
        int bw = tw - 8;
        g.fill(cx - bw / 2, by + 8, cx + bw / 2, by + 10, 0xFF2A2F35);
        float s = st == 3 ? 1f : Math.max(0f, Math.min(1f, ClientState.suspicion));
        if (s > 0) g.fill(cx - bw / 2, by + 8, cx - bw / 2 + (int) (bw * s), by + 10, col);
        if (st == 1 && !ClientState.zoneLabel.isEmpty()) {
            g.drawCenteredString(font, ClientState.zoneLabel, cx, by - 28, 0xFFFFB347);
        }
    }
}
