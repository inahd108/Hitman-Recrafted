package recrafted.client.menu;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * A screen laid out on a virtual canvas of roughly 480 x 270 units and scaled to the window, so the menus look
 * the same whatever GUI scale is set. {@link #width} and {@link #height} are the virtual size; mouse
 * positions are converted on the way in.
 */
public abstract class ScaledScreen extends Screen {
    protected float k = 1f;

    protected ScaledScreen(Component title) {
        super(title);
    }

    /** Sizes the virtual canvas from the window's GUI size, then lays the screen out on it. */
    @Override
    protected final void init() {
        int rw = minecraft.getWindow().getGuiScaledWidth(), rh = minecraft.getWindow().getGuiScaledHeight();
        k = Math.max(0.8f, Math.min(rw / 480f, rh / 270f));
        width = Math.round(rw / k);
        height = Math.round(rh / k);
        layout();
    }

    protected abstract void layout();

    @Override
    public final void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        g.pose().pushPose();
        g.pose().scale(k, k, 1f);
        renderScaled(g, (int) (mouseX / k), (int) (mouseY / k), partial);
        g.pose().popPose();
    }

    protected abstract void renderScaled(GuiGraphics g, int mouseX, int mouseY, float partial);

    /** The widgets, drawn in virtual units. */
    protected void renderWidgets(GuiGraphics g, int mouseX, int mouseY, float partial) {
        super.render(g, mouseX, mouseY, partial);
    }

    /** Scissor in virtual units (GuiGraphics' scissor ignores the pose). */
    protected void scissor(GuiGraphics g, float x0, float y0, float x1, float y1) {
        g.enableScissor((int) Math.floor(x0 * k), (int) Math.floor(y0 * k), (int) Math.ceil(x1 * k), (int) Math.ceil(y1 * k));
    }

    @Override
    public boolean mouseClicked(double x, double y, int button) {
        return super.mouseClicked(x / k, y / k, button);
    }

    @Override
    public boolean mouseReleased(double x, double y, int button) {
        return super.mouseReleased(x / k, y / k, button);
    }

    @Override
    public boolean mouseDragged(double x, double y, int button, double dx, double dy) {
        return super.mouseDragged(x / k, y / k, button, dx / k, dy / k);
    }

    @Override
    public boolean mouseScrolled(double x, double y, double delta) {
        return super.mouseScrolled(x / k, y / k, delta);
    }

    @Override
    public void mouseMoved(double x, double y) {
        super.mouseMoved(x / k, y / k);
    }
}
