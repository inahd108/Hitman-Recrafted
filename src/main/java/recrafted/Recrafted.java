package recrafted;

import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import recrafted.net.Net;
import recrafted.npc.NpcEntity;

@Mod(Recrafted.MODID)
public class Recrafted {
    public static final String MODID = "recrafted";

    public Recrafted() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ModRegistry.init(bus);
        bus.addListener((EntityAttributeCreationEvent e) -> e.put(ModRegistry.NPC.get(), NpcEntity.createAttributes().build()));
        bus.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(Net::register));
    }
}
