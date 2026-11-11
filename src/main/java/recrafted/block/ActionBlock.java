package recrafted.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import recrafted.mission.MissionManager;

/** Simple blocks whose only job is to hand a right-click to the mission logic. */
public class ActionBlock extends Block {
    public enum Action { HIDE_BODY, SMASH_CORE, PURGE, EXIT, NONE }

    private final Action action;

    public ActionBlock(Properties props, Action action) {
        super(props);
        this.action = action;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand,
                                 BlockHitResult hit) {
        if (action == Action.NONE || hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
        if (level.isClientSide) return InteractionResult.SUCCESS;
        ServerLevel sl = (ServerLevel) level;
        ServerPlayer sp = (ServerPlayer) player;
        switch (action) {
            case HIDE_BODY -> MissionManager.hideBody(sl, sp, pos);
            case SMASH_CORE -> MissionManager.smashCore(sl, sp, pos);
            case PURGE -> MissionManager.startPurge(sl, sp, pos);
            case EXIT -> MissionManager.tryExit(sl, sp);
            default -> { }
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource rnd) {
        if (action == Action.SMASH_CORE && rnd.nextInt(2) == 0) {
            level.addParticle(ParticleTypes.SPORE_BLOSSOM_AIR, pos.getX() + rnd.nextDouble(), pos.getY() + 1.1,
                    pos.getZ() + rnd.nextDouble(), 0, 0, 0);
        } else if (action == Action.EXIT && rnd.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.END_ROD, pos.getX() + rnd.nextDouble(), pos.getY() + 1.2,
                    pos.getZ() + rnd.nextDouble(), 0, 0.03, 0);
        }
    }
}
