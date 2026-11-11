package recrafted.block;

import net.minecraft.util.StringRepresentable;
import recrafted.prop.PropType;

import java.util.Locale;

public enum KeyTier implements StringRepresentable {
    LAB(PropType.KEYCARD_LAB, "Lab"), ESTATE(PropType.KEYCARD_ESTATE, "Estate"), HARBOUR(PropType.KEYCARD_HARBOUR, "Harbour");

    public final PropType card;
    public final String label;

    KeyTier(PropType card, String label) {
        this.card = card;
        this.label = label;
    }

    @Override
    public String getSerializedName() {
        return name().toLowerCase(Locale.ROOT);
    }
}
