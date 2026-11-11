package recrafted.world;

import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.zip.GZIPInputStream;

/** A prebuilt voxel map shipped in the mod jar (written by tools/mapgen). */
public final class MapData {
    private static final Logger LOG = LogManager.getLogger("recrafted");
    private static final Map<String, MapData> CACHE = new ConcurrentHashMap<>();

    public final int sx, sy, sz;
    private final BlockState[] palette;
    private final short[] data;

    private MapData(int sx, int sy, int sz, BlockState[] palette, short[] data) {
        this.sx = sx; this.sy = sy; this.sz = sz;
        this.palette = palette;
        this.data = data;
    }

    public static MapData get(String name) {
        return CACHE.computeIfAbsent(name, MapData::load);
    }

    public boolean contains(int x, int z) {
        return x >= 0 && z >= 0 && x < sx && z < sz;
    }

    public BlockState get(int x, int y, int z) {
        return palette[data[(y * sz + z) * sx + x] & 0xFFFF];
    }

    private static MapData load(String name) {
        String path = "/data/recrafted/maps/" + name + ".rcmap";
        try (InputStream raw = MapData.class.getResourceAsStream(path)) {
            if (raw == null) throw new IOException("missing resource " + path);
            DataInputStream in = new DataInputStream(new GZIPInputStream(raw, 1 << 16));
            byte[] magic = new byte[6];
            in.readFully(magic);
            if (!"RCMAP1".equals(new String(magic, StandardCharsets.US_ASCII))) throw new IOException("bad header");
            int sx = in.readInt(), sy = in.readInt(), sz = in.readInt(), n = in.readInt();
            BlockState[] palette = new BlockState[n];
            int unknown = 0;
            for (int i = 0; i < n; i++) {
                byte[] b = new byte[in.readUnsignedShort()];
                in.readFully(b);
                String s = new String(b, StandardCharsets.UTF_8);
                try {
                    palette[i] = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), s, false).blockState();
                } catch (Exception e) {
                    LOG.warn("Map {}: unknown block state '{}'", name, s);
                    palette[i] = Blocks.AIR.defaultBlockState();
                    unknown++;
                }
            }
            byte[] bytes = new byte[sx * sy * sz * 2];
            in.readFully(bytes);
            short[] data = new short[sx * sy * sz];
            for (int i = 0; i < data.length; i++) {
                data[i] = (short) (((bytes[i * 2] & 0xFF) << 8) | (bytes[i * 2 + 1] & 0xFF));
            }
            LOG.info("Loaded map {} ({}x{}x{}, {} states, {} unknown)", name, sx, sy, sz, n, unknown);
            return new MapData(sx, sy, sz, palette, data);
        } catch (IOException e) {
            throw new IllegalStateException("Could not load map " + name, e);
        }
    }
}
