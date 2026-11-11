package recrafted.world;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.NoiseColumn;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CrossCollisionBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.blending.Blender;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;

/** Serves a prebuilt {@link MapData} as terrain and surrounds it with open sea. */
public class MapChunkGenerator extends ChunkGenerator {
    public static final Codec<MapChunkGenerator> CODEC = RecordCodecBuilder.create(i -> i.group(
            BiomeSource.CODEC.fieldOf("biome_source").forGetter(g -> g.biomeSource),
            Codec.STRING.fieldOf("map").forGetter(g -> g.mapName)
    ).apply(i, MapChunkGenerator::new));

    public static final int SEA_LEVEL = 62;
    private static final int OCEAN_FLOOR = 41;

    private final String mapName;
    private MapData map;

    public MapChunkGenerator(BiomeSource biomeSource, String mapName) {
        super(biomeSource);
        this.mapName = mapName;
    }

    private MapData map() {
        if (map == null) map = MapData.get(mapName);
        return map;
    }

    @Override
    protected Codec<? extends ChunkGenerator> codec() {
        return CODEC;
    }

    @Override
    public CompletableFuture<ChunkAccess> fillFromNoise(Executor executor, Blender blender, RandomState random,
                                                         StructureManager structures, ChunkAccess chunk) {
        MapData m = map();
        ChunkPos cp = chunk.getPos();
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        BlockState stone = Blocks.STONE.defaultBlockState();
        BlockState sand = Blocks.SAND.defaultBlockState();
        BlockState water = Blocks.WATER.defaultBlockState();
        BlockState bedrock = Blocks.BEDROCK.defaultBlockState();
        for (int lx = 0; lx < 16; lx++) {
            for (int lz = 0; lz < 16; lz++) {
                int wx = cp.getMinBlockX() + lx, wz = cp.getMinBlockZ() + lz;
                if (m.contains(wx, wz)) {
                    for (int y = 0; y < m.sy; y++) {
                        BlockState s = m.get(wx, y, wz);
                        if (s.isAir()) continue;
                        chunk.setBlockState(pos.set(wx, y, wz), s, false);
                        if (needsShapeUpdate(s.getBlock())) chunk.markPosForPostprocessing(pos);
                    }
                } else {
                    chunk.setBlockState(pos.set(wx, 0, wz), bedrock, false);
                    for (int y = 1; y < OCEAN_FLOOR - 2; y++) chunk.setBlockState(pos.set(wx, y, wz), stone, false);
                    for (int y = OCEAN_FLOOR - 2; y <= OCEAN_FLOOR; y++) chunk.setBlockState(pos.set(wx, y, wz), sand, false);
                    for (int y = OCEAN_FLOOR + 1; y <= SEA_LEVEL; y++) chunk.setBlockState(pos.set(wx, y, wz), water, false);
                }
            }
        }
        return CompletableFuture.completedFuture(chunk);
    }

    /** Fences, panes, walls and stairs get their connections from the game's own shape logic. */
    private static boolean needsShapeUpdate(Block b) {
        return b instanceof CrossCollisionBlock || b instanceof WallBlock || b instanceof StairBlock;
    }

    @Override
    public void applyCarvers(WorldGenRegion region, long seed, RandomState random, BiomeManager biomes,
                             StructureManager structures, ChunkAccess chunk, GenerationStep.Carving step) {
    }

    @Override
    public void buildSurface(WorldGenRegion region, StructureManager structures, RandomState random, ChunkAccess chunk) {
    }

    @Override
    public void applyBiomeDecoration(WorldGenLevel level, ChunkAccess chunk, StructureManager structures) {
    }

    @Override
    public void spawnOriginalMobs(WorldGenRegion region) {
    }

    @Override
    public int getGenDepth() {
        return 256;
    }

    @Override
    public int getSeaLevel() {
        return SEA_LEVEL + 1;
    }

    @Override
    public int getMinY() {
        return 0;
    }

    @Override
    public int getBaseHeight(int x, int z, Heightmap.Types type, LevelHeightAccessor level, RandomState random) {
        MapData m = map();
        if (!m.contains(x, z)) return SEA_LEVEL + 1;
        for (int y = m.sy - 1; y >= 0; y--) {
            if (type.isOpaque().test(m.get(x, y, z))) return y + 1;
        }
        return 0;
    }

    @Override
    public NoiseColumn getBaseColumn(int x, int z, LevelHeightAccessor level, RandomState random) {
        MapData m = map();
        BlockState[] col = new BlockState[level.getHeight()];
        for (int i = 0; i < col.length; i++) {
            int y = level.getMinBuildHeight() + i;
            if (m.contains(x, z)) {
                col[i] = y >= 0 && y < m.sy ? m.get(x, y, z) : Blocks.AIR.defaultBlockState();
            } else {
                col[i] = y <= OCEAN_FLOOR ? Blocks.STONE.defaultBlockState()
                        : y <= SEA_LEVEL ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState();
            }
        }
        return new NoiseColumn(level.getMinBuildHeight(), col);
    }

    @Override
    public void addDebugScreenInfo(List<String> info, RandomState random, BlockPos pos) {
        info.add("Recrafted map: " + mapName);
    }
}
