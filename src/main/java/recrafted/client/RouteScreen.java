package recrafted.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import recrafted.net.Net;
import recrafted.npc.NpcPose;
import recrafted.npc.Route;
import recrafted.npc.Waypoint;

import java.util.Arrays;
import java.util.Locale;

/**
 * Route editor. Stops on the left, everything about the selected stop on the right:
 * how long the NPC stays, what it does there, which way it faces and what it says.
 */
public class RouteScreen extends Screen {
    private static final int ROW = 20, LIST_W = 150;

    public final int entityId;
    private final String npcName;
    private final Route route;
    public boolean frozen;
    private int selected;
    private int scroll;
    private EditBox waitBox, sayBox;

    public RouteScreen(int entityId, String npcName, Route route, boolean frozen) {
        super(Component.literal("Route — " + npcName));
        this.entityId = entityId;
        this.npcName = npcName;
        this.route = route;
        this.frozen = frozen;
    }

    private int visibleRows() {
        return Math.max(3, (height - 74) / ROW);
    }

    private Waypoint sel() {
        return selected >= 0 && selected < route.points.size() ? route.points.get(selected) : null;
    }

    private void push(int action) {
        Net.CHANNEL.sendToServer(new Net.RouteEditC2S(entityId, route, action));
        ClientState.selectedRoute = route.copy();
    }

    private void changed() {
        push(Net.ACT_SAVE);
        rebuildWidgets();
    }

    private static String describe(int i, Waypoint w) {
        String stay = w.wait <= 0 ? "pass" : String.format(Locale.ROOT, "%.0fs", w.wait / 20f);
        return "#" + (i + 1) + "  " + (w.wait <= 0 ? "Walk through" : w.pose.label) + "  ·  " + stay;
    }

    @Override
    protected void init() {
        selected = Mth.clamp(selected, 0, Math.max(0, route.points.size() - 1));
        int rows = visibleRows();
        scroll = Mth.clamp(scroll, 0, Math.max(0, route.points.size() - rows));
        int top = 26;
        // ---- stop list -------------------------------------------------------------
        for (int r = 0; r < rows; r++) {
            int i = scroll + r;
            if (i >= route.points.size()) break;
            Waypoint w = route.points.get(i);
            Button b = Button.builder(Component.literal((i == selected ? "▶ " : "") + describe(i, w)), x -> {
                selected = i;
                rebuildWidgets();
            }).bounds(8, top + r * ROW, LIST_W, ROW - 2).build();
            addRenderableWidget(b);
        }
        if (route.points.size() > rows) {
            addRenderableWidget(Button.builder(Component.literal("▲"), x -> { scroll--; rebuildWidgets(); })
                    .bounds(8 + LIST_W + 2, top, 14, ROW - 2).build());
            addRenderableWidget(Button.builder(Component.literal("▼"), x -> { scroll++; rebuildWidgets(); })
                    .bounds(8 + LIST_W + 2, top + (rows - 1) * ROW, 14, ROW - 2).build());
        }
        // ---- detail panel -------------------------------------------------------------
        int px = 8 + LIST_W + 24;
        int pw = Math.max(180, width - px - 10);
        Waypoint w = sel();
        if (w != null) {
            int y = top + 12;
            int lab = 62;
            // stay
            addRenderableWidget(Button.builder(Component.literal("−5"), x -> addWait(-100)).bounds(px + lab, y, 24, 18).build());
            addRenderableWidget(Button.builder(Component.literal("−1"), x -> addWait(-20)).bounds(px + lab + 26, y, 24, 18).build());
            waitBox = new EditBox(font, px + lab + 52, y, 40, 18, Component.literal("Seconds"));
            waitBox.setValue(trim(w.wait / 20f));
            waitBox.setFilter(s -> s.matches("[0-9]{0,4}(\\.[0-9]?)?"));
            waitBox.setResponder(s -> {
                try {
                    w.wait = s.isEmpty() ? 0 : Math.round(Float.parseFloat(s) * 20f);
                } catch (NumberFormatException ignored) { }
            });
            addRenderableWidget(waitBox);
            addRenderableWidget(Button.builder(Component.literal("+1"), x -> addWait(20)).bounds(px + lab + 94, y, 24, 18).build());
            addRenderableWidget(Button.builder(Component.literal("+5"), x -> addWait(100)).bounds(px + lab + 120, y, 24, 18).build());
            y += 22;
            // pose
            addRenderableWidget(CycleButton.<NpcPose>builder(p -> Component.literal(p.label))
                    .withValues(Arrays.asList(NpcPose.values())).withInitialValue(w.pose).displayOnlyValue()
                    .create(px + lab, y, Math.min(150, pw - lab), 18, Component.literal("Pose"), (b, v) -> {
                        w.pose = v;
                        if (w.wait <= 0 && v != NpcPose.STAND) w.wait = 200;
                        changed();
                    }));
            y += 22;
            // speed
            addRenderableWidget(CycleButton.<Boolean>builder(v -> Component.literal(v ? "Run" : "Walk"))
                    .withValues(false, true).withInitialValue(w.run).displayOnlyValue()
                    .create(px + lab, y, 70, 18, Component.literal("Speed"), (b, v) -> { w.run = v; changed(); }));
            y += 22;
            // facing
            addRenderableWidget(Button.builder(Component.literal("Face where I look"), x -> {
                Player pl = Minecraft.getInstance().player;
                if (pl != null) w.yaw = Mth.wrapDegrees(pl.getYRot());
                changed();
            }).bounds(px + lab, y, 104, 18).build());
            addRenderableWidget(Button.builder(Component.literal("Any"), x -> { w.yaw = Waypoint.NO_YAW; changed(); })
                    .bounds(px + lab + 106, y, 34, 18).build());
            y += 22;
            // says
            sayBox = new EditBox(font, px + lab, y, Math.max(100, pw - lab - 2), 18, Component.literal("Line"));
            sayBox.setMaxLength(120);
            sayBox.setValue(w.say);
            sayBox.setResponder(s -> w.say = s);
            addRenderableWidget(sayBox);
            y += 22;
            // position
            addRenderableWidget(Button.builder(Component.literal("Move to me"), x -> {
                Player pl = Minecraft.getInstance().player;
                if (pl != null) {
                    w.x = Math.floor(pl.getX()) + 0.5; w.y = Math.floor(pl.getY() + 0.01); w.z = Math.floor(pl.getZ()) + 0.5;
                }
                changed();
            }).bounds(px + lab, y, 70, 18).build());
            y += 26;
            // order
            int bw = Math.min(58, (pw - 6) / 4);
            addRenderableWidget(Button.builder(Component.literal("Earlier"), x -> move(-1)).bounds(px, y, bw, 18).build());
            addRenderableWidget(Button.builder(Component.literal("Later"), x -> move(1)).bounds(px + bw + 2, y, bw, 18).build());
            addRenderableWidget(Button.builder(Component.literal("Copy"), x -> {
                if (route.points.size() < Route.MAX_POINTS) {
                    route.points.add(selected + 1, w.copy());
                    selected++;
                }
                changed();
            }).bounds(px + (bw + 2) * 2, y, bw, 18).build());
            addRenderableWidget(Button.builder(Component.literal("Delete"), x -> {
                route.points.remove(selected);
                changed();
            }).bounds(px + (bw + 2) * 3, y, bw, 18).build());
        }
        // ---- bottom bar -------------------------------------------------------------------
        int by = height - 24;
        int n = 6, gap = 3;
        int bw = Math.min(88, (width - 16 - gap * (n - 1)) / n);
        int bx = (width - (bw * n + gap * (n - 1))) / 2;
        addRenderableWidget(CycleButton.<Route.Mode>builder(m -> Component.literal(m.label))
                .withValues(Route.Mode.values()).withInitialValue(route.mode).displayOnlyValue()
                .create(bx, by, bw, 20, Component.literal("Repeat"), (b, v) -> { route.mode = v; push(Net.ACT_SAVE); }));
        addRenderableWidget(Button.builder(Component.literal("+ Stop here"), x -> {
            Player pl = Minecraft.getInstance().player;
            if (pl != null && route.points.size() < Route.MAX_POINTS) {
                Waypoint nw = new Waypoint(Math.floor(pl.getX()) + 0.5, Math.floor(pl.getY() + 0.01), Math.floor(pl.getZ()) + 0.5);
                nw.yaw = Mth.wrapDegrees(pl.getYRot());
                route.points.add(nw);
                selected = route.points.size() - 1;
                scroll = Integer.MAX_VALUE;
            }
            changed();
        }).bounds(bx + (bw + gap), by, bw, 20).build());
        addRenderableWidget(Button.builder(Component.literal(frozen ? "Resume NPC" : "Pause NPC"), x -> {
            frozen = !frozen;
            push(frozen ? Net.ACT_FREEZE : Net.ACT_UNFREEZE);
            rebuildWidgets();
        }).bounds(bx + (bw + gap) * 2, by, bw, 20).build());
        addRenderableWidget(Button.builder(Component.literal("Test route"), x -> {
            frozen = false;
            push(Net.ACT_PREVIEW);
            onClose();
        }).bounds(bx + (bw + gap) * 3, by, bw, 20).build());
        addRenderableWidget(Button.builder(Component.literal("Clear all"), x -> {
            route.points.clear();
            changed();
        }).bounds(bx + (bw + gap) * 4, by, bw, 20).build());
        addRenderableWidget(Button.builder(Component.literal("Done"), x -> onClose()).bounds(bx + (bw + gap) * 5, by, bw, 20).build());
    }

    private static String trim(float v) {
        return v == Math.floor(v) ? String.valueOf((int) v) : String.format(Locale.ROOT, "%.1f", v);
    }

    private void addWait(int ticks) {
        Waypoint w = sel();
        if (w == null) return;
        w.wait = Mth.clamp(w.wait + ticks, 0, 20 * 3600);
        changed();
    }

    private void move(int d) {
        int j = selected + d;
        if (j < 0 || j >= route.points.size()) return;
        Waypoint a = route.points.get(selected);
        route.points.set(selected, route.points.get(j));
        route.points.set(j, a);
        selected = j;
        changed();
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double delta) {
        if (mx < 8 + LIST_W + 20) {
            scroll -= (int) Math.signum(delta);
            rebuildWidgets();
            return true;
        }
        return super.mouseScrolled(mx, my, delta);
    }

    @Override
    public void render(GuiGraphics g, int mx, int my, float partial) {
        renderBackground(g);
        g.drawString(font, title, 8, 8, 0xFFFFFF);
        String count = route.points.size() + " stop" + (route.points.size() == 1 ? "" : "s");
        g.drawString(font, count, width - 10 - font.width(count), 8, 0xA0A0A0);
        int px = 8 + LIST_W + 24, top = 26;
        Waypoint w = sel();
        if (w == null) {
            g.drawWordWrap(font, Component.literal("No stops yet. Close this screen and right-click blocks with the Route Planner, "
                    + "or press “+ Stop here” to add one where you stand."), px, top + 12, Math.max(120, width - px - 12), 0xC0C0C0);
        } else {
            g.drawString(font, "Stop #" + (selected + 1) + String.format(Locale.ROOT, "   at %.0f, %.0f, %.0f", Math.floor(w.x), w.y, Math.floor(w.z)),
                    px, top, 0xFFD27F);
            int y = top + 17;
            g.drawString(font, "Stay (s)", px, y, 0xC0C0C0); y += 22;
            g.drawString(font, "Does", px, y, 0xC0C0C0); y += 22;
            g.drawString(font, "Arrives", px, y, 0xC0C0C0); y += 22;
            g.drawString(font, "Faces", px, y, 0xC0C0C0);
            g.drawString(font, w.hasYaw() ? compass(w.yaw) : "any", px + 62 + 146, y, 0xFFFFFF); y += 22;
            g.drawString(font, "Says", px, y, 0xC0C0C0); y += 22;
            g.drawString(font, "Position", px, y, 0xC0C0C0);
        }
        super.render(g, mx, my, partial);
    }

    private static String compass(float yaw) {
        String[] names = {"S", "SW", "W", "NW", "N", "NE", "E", "SE"};
        return names[Math.floorMod(Math.round(Mth.wrapDegrees(yaw) / 45f), 8)];
    }

    @Override
    public void removed() {
        push(Net.ACT_SAVE);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
