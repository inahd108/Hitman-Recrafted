package recrafted.client;

import recrafted.compat.Guns;

import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import recrafted.npc.NpcEntity;
import recrafted.npc.NpcPose;

/** Player-shaped model with a library of idle animations driven by {@link NpcPose}. */
public class NpcModel extends PlayerModel<NpcEntity> {
    public NpcModel(ModelPart root) {
        super(root, false);
    }

    public static boolean seated(NpcEntity e) {
        NpcPose p = e.getAnim();
        if (e.isDown() || p == NpcPose.STAND || p == NpcPose.SLEEP) return false;
        if (p == NpcPose.SIT) return true;
        if (e.getDeltaMovement().horizontalDistanceSqr() > 1e-4) return false;
        // standing on the high half of a chair puts the feet a full block up, so look a little below them
        BlockState below = e.level().getBlockState(net.minecraft.core.BlockPos.containing(e.getX(), e.getY() - 0.3, e.getZ()));
        return below.getBlock() instanceof StairBlock || below.getBlock() instanceof SlabBlock;
    }

    @Override
    public void setupAnim(NpcEntity e, float limbSwing, float limbSwingAmount, float age, float headYaw, float headPitch) {
        NpcPose p = e.getAnim();
        boolean down = e.isDown() || p == NpcPose.SLEEP;
        this.riding = !down && seated(e);
        this.crouching = !down && p == NpcPose.CROUCH;
        super.setupAnim(e, down ? 0 : limbSwing, down ? 0 : limbSwingAmount, age, down ? 0 : headYaw, down ? 0 : headPitch);
        if (down) {
            rightArm.xRot = 0; leftArm.xRot = 0;
            rightArm.zRot = 0.55f; leftArm.zRot = -0.55f;
            rightLeg.xRot = 0; leftLeg.xRot = 0;
            rightLeg.zRot = 0.12f; leftLeg.zRot = -0.12f;
            head.xRot = 0.1f; head.yRot = 0.5f;
            sync();
            return;
        }
        if (e.inCombat() && Guns.isGun(e.getMainHandItem())) {
            // two-handed pistol grip, arms following the head (as a bow is held)
            rightArm.yRot = -0.1f + head.yRot;
            leftArm.yRot = 0.1f + head.yRot + 0.4f;
            rightArm.xRot = -Mth.HALF_PI + head.xRot;
            leftArm.xRot = -Mth.HALF_PI + head.xRot;
            rightArm.zRot = 0;
            leftArm.zRot = 0;
            sync();
            return;
        }
        boolean moving = limbSwingAmount > 0.05f;
        if (moving && p != NpcPose.SWEEP) {
            sync();
            return;
        }
        float s = Mth.sin(age * 0.1f);
        switch (p) {
            case GUARD -> {
                rightArm.xRot = 0.45f; leftArm.xRot = 0.45f;
                rightArm.zRot = -0.18f; leftArm.zRot = 0.18f;
                head.yRot += Mth.sin(age * 0.03f) * 0.35f;
            }
            case LEAN -> {
                rightArm.xRot = -0.95f; leftArm.xRot = -0.95f;
                rightArm.yRot = -0.75f; leftArm.yRot = 0.75f;
                body.xRot = -0.06f;
            }
            case PHONE -> {
                rightArm.xRot = -2.45f; rightArm.yRot = -0.45f; rightArm.zRot = 0.1f;
                head.zRot = 0.12f;
                head.xRot += Mth.sin(age * 0.07f) * 0.04f;
            }
            case SMOKE -> {
                float t = Mth.clamp(Mth.sin(age * 0.045f) * 3f, 0f, 1f);
                rightArm.xRot = Mth.lerp(t, -0.25f, -2.0f);
                rightArm.yRot = Mth.lerp(t, 0f, -0.5f);
            }
            case DRINK -> {
                float t = Mth.clamp(Mth.sin(age * 0.06f) * 2.5f, 0f, 1f);
                rightArm.xRot = Mth.lerp(t, -0.9f, -1.95f);
                rightArm.yRot = -0.4f;
                head.xRot = Mth.lerp(t, head.xRot, -0.25f);
            }
            case EAT -> {
                float t = Mth.clamp(Mth.sin(age * 0.12f) * 2f, 0f, 1f);
                rightArm.xRot = Mth.lerp(t, -0.8f, -1.75f);
                rightArm.yRot = -0.45f;
                leftArm.xRot = -0.7f; leftArm.yRot = 0.3f;
                head.xRot = 0.15f;
            }
            case WORK -> {
                rightArm.xRot = -1.05f + Mth.sin(age * 0.35f) * 0.45f;
                leftArm.xRot = -0.75f + Mth.cos(age * 0.2f) * 0.15f;
                rightArm.yRot = -0.2f; leftArm.yRot = 0.25f;
                head.xRot = 0.3f;
            }
            case SWEEP -> {
                float w = Mth.sin(age * 0.16f);
                rightArm.xRot = -0.85f; leftArm.xRot = -1.05f;
                rightArm.yRot = -0.35f + w * 0.45f; leftArm.yRot = 0.35f + w * 0.45f;
                body.yRot = w * 0.18f;
                head.xRot = 0.35f;
            }
            case TYPE -> {
                rightArm.xRot = -1.2f + Mth.sin(age * 0.9f) * 0.07f;
                leftArm.xRot = -1.2f + Mth.cos(age * 0.8f) * 0.07f;
                rightArm.yRot = -0.25f; leftArm.yRot = 0.25f;
                head.xRot = 0.28f;
            }
            case TALK -> {
                rightArm.xRot = -0.9f + Mth.sin(age * 0.22f) * 0.35f;
                rightArm.yRot = -0.35f + Mth.cos(age * 0.17f) * 0.2f;
                leftArm.xRot = -0.35f + Mth.sin(age * 0.13f) * 0.2f;
                head.xRot += Mth.sin(age * 0.2f) * 0.06f;
            }
            case LOOK -> {
                head.yRot = Mth.sin(age * 0.045f) * 0.95f;
                head.xRot = Mth.sin(age * 0.03f) * 0.12f;
                rightArm.xRot = -2.3f * Mth.clamp(Mth.sin(age * 0.02f) * 4f - 2.5f, 0f, 1f);
            }
            case WAVE -> {
                rightArm.xRot = 0; rightArm.zRot = 2.6f + Mth.sin(age * 0.45f) * 0.3f;
            }
            case CROUCH -> {
                rightArm.xRot = -0.9f + s * 0.2f; leftArm.xRot = -0.8f - s * 0.2f;
            }
            case DANCE -> {
                float d = Mth.sin(age * 0.35f);
                rightArm.xRot = -2.6f + d * 0.4f; leftArm.xRot = -2.6f - d * 0.4f;
                rightArm.zRot = -0.3f; leftArm.zRot = 0.3f;
                body.yRot = d * 0.3f;
                head.yRot = -d * 0.3f;
                rightLeg.xRot = d * 0.35f; leftLeg.xRot = -d * 0.35f;
            }
            case PRAY -> {
                rightArm.xRot = -1.5f; leftArm.xRot = -1.5f;
                rightArm.yRot = -0.5f; leftArm.yRot = 0.5f;
                head.xRot = 0.38f;
            }
            default -> { }
        }
        sync();
    }

    private void sync() {
        hat.copyFrom(head);
        jacket.copyFrom(body);
        leftSleeve.copyFrom(leftArm);
        rightSleeve.copyFrom(rightArm);
        leftPants.copyFrom(leftLeg);
        rightPants.copyFrom(rightLeg);
    }
}
