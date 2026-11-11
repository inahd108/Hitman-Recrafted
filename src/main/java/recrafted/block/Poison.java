package recrafted.block;

import net.minecraft.util.StringRepresentable;

import java.util.Locale;

public enum Poison implements StringRepresentable {
    NONE, EMETIC, LETHAL;

    @Override
    public String getSerializedName() {
        return name().toLowerCase(Locale.ROOT);
    }
}
