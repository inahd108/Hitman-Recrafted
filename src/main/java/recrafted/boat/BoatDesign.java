package recrafted.boat;

import java.util.ArrayList;
import java.util.List;

/**
 * What a canal boat looks like (a little structure of block states drawn on the moving entity) and where its
 * passengers ride. Local frame: +z is the bow, x runs across the boat, y = 0 is the hull course at the waterline
 * (the entity's own y). The deck is a bottom slab, so people stand at y + 0.5.
 */
public enum BoatDesign {
    /** Kooistra's salon launch: black hull, mahogany deck and gunwale, a windscreen, benches amidships. */
    ZWALUW(false, new Seat[]{
            new Seat(0, -4, 0.5, 0, true),       // the helm
            new Seat(0, 0, 0.5, 0, false),       // the owner, amidships
            new Seat(-1, 2, 0.5, 30, false), new Seat(1, -2, 0.5, 150, false),
            new Seat(1, 2, 0.5, -30, false), new Seat(-1, -2, 0.5, -150, false)}),
    /** A long open tour boat with bench rows: everyone but the skipper sits. */
    TOUR(true, tourSeats());

    public record Seat(double x, double z, double y, float yaw, boolean helm) {}
    public record Part(int dx, int dy, int dz, String state) {}

    public final boolean seated;
    public final Seat[] seats;
    private List<Part> parts;

    BoatDesign(boolean seated, Seat[] seats) {
        this.seated = seated;
        this.seats = seats;
    }

    public static BoatDesign byName(String s) {
        for (BoatDesign d : values()) if (d.name().equalsIgnoreCase(s)) return d;
        return ZWALUW;
    }

    private static Seat[] tourSeats() {
        List<Seat> s = new ArrayList<>();
        s.add(new Seat(0, -6, 0.5, 0, true));
        for (int row = 4; row >= -4; row -= 2) {
            s.add(new Seat(-1, row, 1.0, 0, false));
            s.add(new Seat(1, row, 1.0, 0, false));
        }
        return s.toArray(new Seat[0]);
    }

    public synchronized List<Part> parts() {
        if (parts == null) parts = build(this);
        return parts;
    }

    private static List<Part> build(BoatDesign d) {
        List<Part> p = new ArrayList<>();
        if (d == ZWALUW) {
            String hull = "minecraft:black_concrete", deck = "minecraft:spruce_slab[type=bottom]", trim = "minecraft:dark_oak_slab[type=bottom]";
            for (int z = -5; z <= 5; z++) for (int x = -2; x <= 2; x++) {
                if (z == 5 && Math.abs(x) == 2) continue;
                p.add(new Part(x, -1, z, hull));
                boolean side = Math.abs(x) == 2 || z == -5 || z == 5;
                p.add(new Part(x, 0, z, side ? hull : deck));
                if (side) p.add(new Part(x, 1, z, trim));
            }
            p.add(new Part(0, 0, 6, hull));
            p.add(new Part(0, 1, 6, trim));
            for (int x = -1; x <= 1; x++) p.add(new Part(x, 1, 3, "minecraft:glass_pane[east=true,west=true]"));
            p.add(new Part(0, 1, -3, "minecraft:dark_oak_fence"));
            for (int z = -1; z <= 1; z++) {
                p.add(new Part(-1, 1, z, "minecraft:dark_oak_stairs[facing=west,half=bottom]"));
                p.add(new Part(1, 1, z, "minecraft:dark_oak_stairs[facing=east,half=bottom]"));
            }
            p.removeIf(q -> q.dy == 1 && Math.abs(q.dx) == 2 && q.dz == -5);
            p.add(new Part(-2, 1, -5, "minecraft:lantern[hanging=false]"));
            p.add(new Part(2, 1, -5, "minecraft:lantern[hanging=false]"));
        } else {
            String hull = "minecraft:blue_concrete", deck = "minecraft:spruce_slab[type=bottom]", trim = "minecraft:quartz_slab[type=bottom]";
            for (int z = -7; z <= 7; z++) for (int x = -2; x <= 2; x++) {
                if (z == 7 && Math.abs(x) == 2) continue;
                p.add(new Part(x, -1, z, hull));
                boolean side = Math.abs(x) == 2 || z == -7 || z == 7;
                boolean bench = !side && x != 0 && z >= -4 && z <= 4 && (z % 2 == 0);
                p.add(new Part(x, 0, z, side ? hull : bench ? "minecraft:spruce_stairs[facing=north,half=bottom]" : deck));
                if (side) p.add(new Part(x, 1, z, trim));
            }
            p.add(new Part(0, 0, 8, hull));
            p.add(new Part(0, 1, 8, trim));
            p.add(new Part(0, 1, -5, "minecraft:spruce_fence"));
            p.removeIf(q -> q.dy == 1 && Math.abs(q.dx) == 2 && (q.dz == -7 || q.dz == 6));
            for (int z : new int[]{-7, 6}) {
                p.add(new Part(-2, 1, z, "minecraft:lantern[hanging=false]"));
                p.add(new Part(2, 1, z, "minecraft:lantern[hanging=false]"));
            }
        }
        return p;
    }
}
