package recrafted;

import com.mojang.serialization.Codec;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import recrafted.block.ActionBlock;
import recrafted.block.CardReaderBlock;
import recrafted.block.ConsumableBlock;
import recrafted.block.FuseBoxBlock;
import recrafted.entity.PropEntity;
import recrafted.entity.ThrownPropEntity;
import recrafted.item.CastingCardItem;
import recrafted.item.RoutePlannerItem;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcRole;
import recrafted.prop.OutfitItem;
import recrafted.prop.PropItem;
import recrafted.prop.PropType;
import recrafted.world.MapChunkGenerator;

import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

public final class ModRegistry {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Recrafted.MODID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Recrafted.MODID);
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Recrafted.MODID);
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Recrafted.MODID);
    public static final DeferredRegister<Codec<? extends ChunkGenerator>> GENERATORS = DeferredRegister.create(Registries.CHUNK_GENERATOR, Recrafted.MODID);

    private static BlockBehaviour.Properties metal() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(-1f, 3600000f).sound(SoundType.METAL);
    }

    // ---- blocks ---------------------------------------------------------------
    public static final RegistryObject<Block> CARD_READER = block("card_reader", () -> new CardReaderBlock(metal().lightLevel(s -> 4)));
    public static final RegistryObject<Block> HIDING_CRATE = block("hiding_crate", () -> new ActionBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(-1f, 3600000f).sound(SoundType.WOOD), ActionBlock.Action.HIDE_BODY));
    public static final RegistryObject<Block> PATHOGEN_CORE = block("pathogen_core", () -> new ActionBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_GREEN).strength(-1f, 3600000f).sound(SoundType.GLASS)
                    .lightLevel(s -> 12), ActionBlock.Action.SMASH_CORE));
    public static final RegistryObject<Block> PURGE_CONSOLE = block("purge_console", () -> new ActionBlock(metal().lightLevel(s -> 7), ActionBlock.Action.PURGE));
    public static final RegistryObject<Block> LAB_CONSOLE = block("lab_console", () -> new ActionBlock(metal().lightLevel(s -> 7), ActionBlock.Action.NONE));
    public static final RegistryObject<Block> EXIT_POINT = block("exit_point", () -> new ActionBlock(metal().lightLevel(s -> 10), ActionBlock.Action.EXIT));
    public static final RegistryObject<Block> FUSE_BOX = block("fuse_box", () -> new FuseBoxBlock(metal()));
    public static final RegistryObject<Block> MEAL = block("meal", () -> new ConsumableBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.QUARTZ).strength(-1f, 3600000f).noOcclusion().sound(SoundType.STONE),
            Block.box(3, 0, 3, 13, 3, 13)));
    public static final RegistryObject<Block> DRINK = block("drink", () -> new ConsumableBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(-1f, 3600000f).noOcclusion().sound(SoundType.GLASS),
            Block.box(6, 0, 6, 10, 7, 10)));

    // ---- items ----------------------------------------------------------------
    public static final Map<PropType, RegistryObject<Item>> PROPS = new EnumMap<>(PropType.class);
    public static final Map<NpcRole, RegistryObject<Item>> OUTFITS = new LinkedHashMap<>();
    public static final RegistryObject<Item> ROUTE_PLANNER = ITEMS.register("route_planner", () -> new RoutePlannerItem(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<Item> CASTING_CARD = ITEMS.register("casting_card", () -> new CastingCardItem(new Item.Properties().stacksTo(1)));

    static {
        for (PropType t : PropType.values()) {
            PROPS.put(t, ITEMS.register(t.id, () -> new PropItem(t, new Item.Properties().stacksTo(t.stacks() ? 16 : 1))));
        }
        for (NpcRole r : NpcRole.values()) {
            if (r.wearable) OUTFITS.put(r, ITEMS.register("outfit_" + r.id, () -> new OutfitItem(r, new Item.Properties().stacksTo(1))));
        }
    }

    // ---- entities -------------------------------------------------------------
    public static final RegistryObject<EntityType<NpcEntity>> NPC = ENTITIES.register("npc", () ->
            EntityType.Builder.of(NpcEntity::new, MobCategory.MISC).sized(0.6f, 1.8f).clientTrackingRange(10).build("npc"));
    public static final RegistryObject<EntityType<PropEntity>> PROP = ENTITIES.register("prop", () ->
            EntityType.Builder.<PropEntity>of(PropEntity::new, MobCategory.MISC).sized(0.5f, 0.3f).clientTrackingRange(6)
                    .updateInterval(20).build("prop"));
    public static final RegistryObject<EntityType<ThrownPropEntity>> THROWN_PROP = ENTITIES.register("thrown_prop", () ->
            EntityType.Builder.<ThrownPropEntity>of(ThrownPropEntity::new, MobCategory.MISC).sized(0.25f, 0.25f)
                    .clientTrackingRange(4).updateInterval(10).build("thrown_prop"));

    public static final RegistryObject<CreativeModeTab> TAB = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.recrafted"))
            .icon(() -> new ItemStack(PROPS.get(PropType.FIBER_WIRE).get()))
            .displayItems((params, out) -> ITEMS.getEntries().forEach(e -> out.accept(e.get())))
            .build());

    private static RegistryObject<Block> block(String name, Supplier<Block> sup) {
        RegistryObject<Block> b = BLOCKS.register(name, sup);
        ITEMS.register(name, () -> new BlockItem(b.get(), new Item.Properties()));
        return b;
    }

    public static Item prop(PropType t) {
        return PROPS.get(t).get();
    }

    public static void init(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        ENTITIES.register(bus);
        TABS.register(bus);
        GENERATORS.register(bus);
    }

    static {
        GENERATORS.register("map", () -> MapChunkGenerator.CODEC);
    }

    private ModRegistry() {}
}
