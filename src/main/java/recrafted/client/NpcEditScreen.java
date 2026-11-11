package recrafted.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import recrafted.net.Net;
import recrafted.npc.NpcRole;

import java.util.Arrays;

/** Create or edit an NPC: role, name, look, and whether it is a target or sees through disguises. */
public class NpcEditScreen extends Screen {
    private final Net.NpcScreenS2C data;
    private NpcRole role;
    private int skin;
    private boolean enforcer, target;
    private EditBox nameBox, idBox, followBox;

    public NpcEditScreen(Net.NpcScreenS2C data) {
        super(Component.literal(data.entityId() < 0 ? "New NPC" : "Edit NPC"));
        this.data = data;
        this.role = NpcRole.byId(data.role());
        this.skin = data.skin();
        this.enforcer = data.enforcer();
        this.target = data.target();
    }

    @Override
    protected void init() {
        int cx = width / 2, x = cx - 100, y = Math.max(24, height / 2 - 96);
        String name = nameBox != null ? nameBox.getValue() : data.name();
        String id = idBox != null ? idBox.getValue() : data.contractId();
        String follow = followBox != null ? followBox.getValue() : data.followId();
        addRenderableWidget(CycleButton.<NpcRole>builder(r -> Component.literal(r.title))
                .withValues(Arrays.asList(NpcRole.values())).withInitialValue(role)
                .create(x, y, 200, 20, Component.literal("Role"), (b, v) -> { role = v; skin = 0; rebuildWidgets(); }));
        y += 24;
        nameBox = new EditBox(font, x + 60, y, 140, 18, Component.literal("Name"));
        nameBox.setMaxLength(48);
        nameBox.setValue(name);
        addRenderableWidget(nameBox);
        y += 24;
        addRenderableWidget(Button.builder(Component.literal("Look: " + (skin + 1) + " of " + role.variants), b -> {
            skin = (skin + 1) % role.variants;
            rebuildWidgets();
        }).bounds(x, y, 200, 20).build());
        y += 24;
        addRenderableWidget(CycleButton.onOffBuilder(enforcer).create(x, y, 200, 20,
                Component.literal("Sees through this outfit"), (b, v) -> enforcer = v));
        y += 24;
        addRenderableWidget(CycleButton.onOffBuilder(target).create(x, y, 200, 20,
                Component.literal("Is a target"), (b, v) -> target = v));
        y += 24;
        idBox = new EditBox(font, x + 60, y, 140, 18, Component.literal("Contract id"));
        idBox.setMaxLength(32);
        idBox.setValue(id);
        addRenderableWidget(idBox);
        y += 24;
        followBox = new EditBox(font, x + 60, y, 140, 18, Component.literal("Escorts"));
        followBox.setMaxLength(32);
        followBox.setValue(follow);
        addRenderableWidget(followBox);
        y += 28;
        boolean isNew = data.entityId() < 0;
        addRenderableWidget(Button.builder(Component.literal(isNew ? "Create" : "Apply"), b -> send(false))
                .bounds(x, y, isNew ? 98 : 64, 20).build());
        if (!isNew) {
            addRenderableWidget(Button.builder(Component.literal("Remove"), b -> send(true)).bounds(x + 68, y, 64, 20).build());
        }
        addRenderableWidget(Button.builder(Component.literal("Cancel"), b -> onClose())
                .bounds(isNew ? x + 102 : x + 136, y, isNew ? 98 : 64, 20).build());
    }

    private void send(boolean delete) {
        float yaw = Minecraft.getInstance().player != null ? Minecraft.getInstance().player.getYRot() + 180f : 0f;
        Net.CHANNEL.sendToServer(new Net.NpcEditC2S(data.entityId(), data.pos(), yaw, role.id, nameBox.getValue(), skin,
                enforcer, target, idBox.getValue(), followBox.getValue(), delete));
        onClose();
    }

    @Override
    public void render(GuiGraphics g, int mx, int my, float partial) {
        renderBackground(g);
        int cx = width / 2, x = cx - 100, y = Math.max(24, height / 2 - 96);
        g.drawCenteredString(font, title, cx, y - 14, 0xFFFFFF);
        g.drawString(font, "Name", x, y + 24 + 5, 0xC0C0C0);
        g.drawString(font, "Target id", x, y + 24 * 5 + 5, 0xC0C0C0);
        g.drawString(font, "Escorts id", x, y + 24 * 6 + 5, 0xC0C0C0);
        super.render(g, mx, my, partial);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
