"""Amsterdam map layout: one place for every coordinate the other modules share.

North is -z. The IJ (harbour) runs along the north edge; two parallel canals cross the map
west to east and are joined at both ends by cross canals; the old harbour front sits between
the IJ and the outer canal; the auction house, the forger's house and the church are on the
south side of the inner canal.

All ranges are inclusive (lo, hi).
"""
SX, SY, SZ = 384, 136, 320

WATER = 62          # top water block (sea level, same as the chunk generator's)
STREET = 63         # top paving block; people walk at y 64
FLOOR0 = 64         # ground-floor floor block of a house (one step up from the street)
CANAL_BED = 58      # canal bottom (mud); water fills 59..62
IJ_BED = 50         # harbour bottom

# ---- rows, north to south ---------------------------------------------------------------
FAR_SHORE = (0, 7)        # low silhouette of the far bank across the IJ
IJ = (8, 43)              # harbour water
ANKERKADE = (44, 57)      # harbour quay
WAREHOUSES = (58, 85)     # warehouse row, fronts on the quay and on the outer canal
OUTER_N_QUAY = (86, 93)
OUTER = (94, 113)         # Touwslagersgracht, 20 wide
OUTER_S_QUAY = (114, 121)
MID_N = (122, 139)        # houses facing the outer canal
MID_GARDENS = (140, 163)
MID_S = (164, 181)        # houses facing the inner canal
INNER_N_QUAY = (182, 189)
INNER = (190, 213)        # Gildegracht, 24 wide
INNER_S_QUAY = (214, 221)
SOUTH_HOUSES = (222, 239)
SOUTH_DEEP = (240, 289)   # gardens, back houses, church, hofje
BACK_STREET = (290, 297)
BACKDROP_S = (298, 319)

# ---- columns, west to east --------------------------------------------------------------
EDGE_W = (0, 7)
WEST_HOUSES = (8, 17)     # houses facing east onto the west cross canal
WEST_QUAY = (18, 25)
WEST_CANAL = (26, 39)     # the lock channel north of the outer canal, Sluisgracht south of it
EAST_OF_WEST_QUAY = (40, 47)
MID_X = (48, 335)         # the block between the canals
EAST_W_QUAY = (336, 343)
EAST_CANAL = (344, 357)   # Oostgracht: IJ to outer to inner canal; the smuggler's dock roofs it in the warehouse row
EAST_E_QUAY = (358, 365)
EAST_HOUSES = (366, 375)
EDGE_E = (376, 383)

ZILVERSTEEG = (191, 196)  # the shopping alley through the middle block (walkable width)

# Lock gates across the west channel (z), keeper's house beside them
LOCK_GATES = (62, 81)
# Bridges: (x0, x1) of the deck, by canal
OUTER_BRIDGES = [(96, 103), (189, 198), (290, 297)]
INNER_BRIDGES = [(118, 125), (189, 198)]
DRAWBRIDGE = (300, 309)   # over the inner canal
WEST_BRIDGES = [(150, 157)]   # z ranges over the west cross canal (south part)
EAST_BRIDGES = [(150, 157)]

# Landmark plots (south of the inner canal unless noted)
GULDEN_HAMER = (60, 90)       # x; front house z 222..251, garden to 279, coach house to 289
FORGER = (150, 156)           # x; 7 floors
BLOEMENPLEIN = (199, 249)     # x of the square; flower barges moored in the inner canal along it
CHURCH = (262, 300)           # x; tower at the north end
HOFJE = (312, 352)            # x
POLICE = (124, 136)           # x
STATION = (8, 25)             # x, north of the outer canal; platform along the quay
FERRY_PIER = (150, 160)       # x, pier runs north into the IJ
BREWERY = (300, 335)          # x, last warehouses


def rows(a, b):
    return range(a, b + 1)
