package recrafted.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.BoolArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import recrafted.ModRegistry;
import recrafted.Recrafted;
import recrafted.mission.Mission;
import recrafted.mission.MissionManager;
import recrafted.mission.MissionState;
import recrafted.mission.PlayerData;
import recrafted.net.Net;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;

import java.nio.file.Files;

@Mod.EventBusSubscriber(modid = Recrafted.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ContractCommand {
    private ContractCommand() {}

    /** The contract of the dimension the command came from, or Corvara outside every contract. */
    private static Mission current(CommandSourceStack src) {
        Mission m = Mission.forDimension(src.getLevel().dimension());
        return m != null ? m : Mission.corvara();
    }

    private static ServerLevel levelOf(CommandSourceStack src, Mission m) {
        return src.getServer().getLevel(m.dimension);
    }

    @SubscribeEvent
    public static void register(RegisterCommandsEvent e) {
        CommandDispatcher<CommandSourceStack> d = e.getDispatcher();
        d.register(Commands.literal("contract")
                .then(Commands.literal("start").executes(c -> {
                    ServerPlayer p = c.getSource().getPlayerOrException();
                    return MissionManager.start(p, current(c.getSource()).id) ? 1 : 0;
                }).then(Commands.argument("mission", StringArgumentType.word())
                        .suggests((c, b) -> SharedSuggestionProvider.suggest(Mission.IDS, b))
                        .executes(c -> {
                            ServerPlayer p = c.getSource().getPlayerOrException();
                            return MissionManager.start(p, StringArgumentType.getString(c, "mission")) ? 1 : 0;
                        })))
                .then(Commands.literal("intel").executes(c -> {
                    Mission m = current(c.getSource());
                    c.getSource().sendSystemMessage(Component.literal("Intel — " + m.title).withStyle(ChatFormatting.GOLD));
                    for (String s : m.intel) c.getSource().sendSystemMessage(Component.literal(" • " + s).withStyle(ChatFormatting.GRAY));
                    return 1;
                }))
                .then(Commands.literal("status").executes(c -> {
                    Mission m = current(c.getSource());
                    ServerLevel level = levelOf(c.getSource(), m);
                    if (level == null) return 0;
                    MissionState st = MissionState.get(level);
                    c.getSource().sendSystemMessage(Component.literal(m.title + (st.active ? " — in progress" : st.complete ? " — complete" : " — not started")));
                    for (Mission.Objective o : m.objectives) {
                        boolean done = st.done.contains(o.id());
                        c.getSource().sendSystemMessage(Component.literal((done ? " ✔ " : " ○ ") + o.text())
                                .withStyle(done ? ChatFormatting.GREEN : ChatFormatting.WHITE));
                    }
                    c.getSource().sendSystemMessage(Component.literal("Waiting to spawn: " + st.pendingNpcs.size() + " NPCs, "
                            + st.pendingProps.size() + " props").withStyle(ChatFormatting.DARK_GRAY));
                    return 1;
                }))
                .then(Commands.literal("stop").requires(s -> s.hasPermission(2)).executes(c -> {
                    ServerLevel level = levelOf(c.getSource(), current(c.getSource()));
                    if (level != null) MissionManager.stop(level);
                    c.getSource().sendSystemMessage(Component.literal("Contract stopped"));
                    return 1;
                }))
                .then(Commands.literal("visit").requires(s -> s.hasPermission(2)).executes(c -> visit(c.getSource(), current(c.getSource())))
                        .then(Commands.argument("mission", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(Mission.IDS, b))
                                .executes(c -> visit(c.getSource(), Mission.byId(StringArgumentType.getString(c, "mission"))))))
                .then(Commands.literal("tools").requires(s -> s.hasPermission(2)).executes(c -> {
                    ServerPlayer p = c.getSource().getPlayerOrException();
                    p.getInventory().add(new ItemStack(ModRegistry.ROUTE_PLANNER.get()));
                    p.getInventory().add(new ItemStack(ModRegistry.CASTING_CARD.get()));
                    c.getSource().sendSystemMessage(Component.literal("Route Planner and Casting Card added to your inventory"));
                    return 1;
                }))
                .then(Commands.literal("freeze").requires(s -> s.hasPermission(2))
                        .then(Commands.argument("on", BoolArgumentType.bool()).executes(c -> {
                            boolean on = BoolArgumentType.getBool(c, "on");
                            int n = 0;
                            for (Entity en : c.getSource().getLevel().getAllEntities()) {
                                if (en instanceof NpcEntity npc) { npc.frozen = on; n++; }
                            }
                            c.getSource().sendSystemMessage(Component.literal((on ? "Froze " : "Released ") + n + " NPCs"));
                            return n;
                        })))
                .then(Commands.literal("disguise").requires(s -> s.hasPermission(2))
                        .then(Commands.argument("role", StringArgumentType.word())
                                .suggests((c, b) -> {
                                    java.util.List<String> ids = Net.roleIds();
                                    ids.add("none");
                                    return SharedSuggestionProvider.suggest(ids, b);
                                })
                                .executes(c -> {
                                    ServerPlayer p = c.getSource().getPlayerOrException();
                                    NpcRole r = NpcRole.byIdOrNull(StringArgumentType.getString(c, "role"));
                                    PlayerData.setDisguise(p, r, 0);
                                    c.getSource().sendSystemMessage(Component.literal("Disguise: " + (r == null ? "none" : r.title)));
                                    return 1;
                                })))
                .then(Commands.literal("cast").requires(s -> s.hasPermission(2))
                        .then(Commands.literal("export").executes(c -> {
                            Mission cm = current(c.getSource());
                            ServerLevel level = levelOf(c.getSource(), cm);
                            if (level == null) return 0;
                            try {
                                int n = MissionManager.exportCast(level);
                                c.getSource().sendSystemMessage(Component.literal("Saved " + n + " NPCs to "
                                        + Mission.castFile(cm.id) + ". The next /contract start uses it.").withStyle(ChatFormatting.GREEN));
                                return n;
                            } catch (Exception ex) {
                                c.getSource().sendFailure(Component.literal("Export failed: " + ex.getMessage()));
                                return 0;
                            }
                        }))
                        .then(Commands.literal("reset").executes(c -> {
                            try {
                                boolean had = Files.deleteIfExists(Mission.castFile(current(c.getSource()).id));
                                Mission.reload();
                                c.getSource().sendSystemMessage(Component.literal(had ? "Custom cast removed. The next /contract start uses the built-in cast."
                                        : "There was no custom cast."));
                                return 1;
                            } catch (Exception ex) {
                                c.getSource().sendFailure(Component.literal("Could not remove the cast file: " + ex.getMessage()));
                                return 0;
                            }
                        }))));
    }

    private static int visit(CommandSourceStack src, Mission m) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = src.getPlayerOrException();
        ServerLevel level = levelOf(src, m);
        if (level == null) return 0;
        p.teleportTo(level, m.spawn.x, m.spawn.y, m.spawn.z, m.spawnYaw, 0f);
        return 1;
    }
}
