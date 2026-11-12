# Mission 2 plan: **Oil & Water** (Amsterdam, Netherlands)

> Design plan for the second contract. Nothing here is built yet. Names of people, businesses, canals and
> streets are invented. The city is real, but this neighbourhood is our own composite of the canal ring and the
> old harbour front.

---

## 1. Pitch

Salt & Ash ended with CINDER destroyed, but the money behind it is still moving. Halcyon's buyers were going
to pay for the "cure" through Amsterdam. A forger paints Golden Age pictures that never existed, an auction house
sells them to shell companies for clean money, and a smuggler carries the proceeds out in uncut stones.

**Three partners who need each other and trust nobody.** Like oil and water: they share a city and never mix.

- **Title:** Oil & Water.
- **Location line:** Amsterdam — Netherlands.
- **Time:** blue hour, steady drizzle, the evening of the Gulden Hamer's autumn sale.
- **Tone:** quieter and closer than Corvara: narrow streets, black water, warm windows, wet brick.

---

## 2. Mood and atmosphere

This is the part that has to land, so it gets its own systems rather than being left to block choice.

| | |
|---|---|
| **Hour** | Fixed dimension time ~13300: the sun just gone, a deep blue sky with a last bruise of orange in the west, every window and lamp lit. (The menu harness already proved this hour reads well.) |
| **Weather** | Permanent fine drizzle and low cloud *in this dimension only*: a custom `DimensionSpecialEffects` (`recrafted:amsterdam`) draws rain and plays the rain loop regardless of overworld weather, and sets a slate-blue fog that starts closer than vanilla so the far end of a canal fades out. |
| **Light** | Warm amber windows against cool blue dusk. Bridges are outlined in strings of small bulbs. That is the city's signature look, and photos show the bulbs doubled in the water. Cast-iron canal lanterns every ~12 blocks along the quays. Hidden light blocks just under the waterline beneath bridges and lanterns fake the reflections. |
| **Sound** | Rain on cobbles and on canvas awnings, a carillon in the church tower every in-game quarter hour (an original tune), bicycle bells, a distant tram bell, gulls near the IJ, idling boat engines, muffled talk and glasses from the brown café, and the street organ's tune near the flower market. |
| **Clutter** | Bicycles chained to every railing (and one or two half-sunk in the canal), flower boxes, hoist hooks on every gable, bike racks, mooring ropes, puddles, cats in windows, wet umbrellas outside the café door. |
| **People** | Raincoats, scarves and umbrellas: every reused role gets new rain-weather skins. |

**Colour palette:** wet red-brown and near-black brick, white sash-window frames, white sandstone gable trim,
dark green shutters, black water, amber light, and copper-green church roofs.

---

## 3. Reference photos

For our eyes only: look, don't copy. No reference image goes into the repo; everything in game is built from blocks and our own textures.

**Gables, the most important single detail**
- Gable types and dates: step (≈1600–1665), neck (≈1640–1770), bell (≈1660–1790), spout (warehouses), cornice (later).
  - [Fodor's: gables and hooks](https://www.fodors.com/world/europe/netherlands/amsterdam/experiences/amsterdam-architecture-gables-and-hooks-83465890)
  - [Museum of the Canals: architecture in the canal district](https://grachten.museum/en/?p=5673)
  - [Buffalo Architecture: Amsterdam gables](https://buffaloah.com/a/virtual/hol/amster/amstergables/index.html)
  - [Snail in the City: examples of Dutch gables](https://snailinthecity.blogspot.nl/2015/01/dutch-gables-examples-from-amsterdam.html)
  - [Amsterdam for Visitors: bell gables](https://www.amsterdamforvisitors.com/?p=628)

**Hoisting beams and hooks**
- Every gable has a beam with a hook and pulley for hauling goods and furniture to the top floors.
  - [Amsterdamian: why Dutch houses have hooks](https://amsterdamian.com/see/amsterdam/why-dutch-houses-have-those-hooks-on-the-facades/)
  - [DutchReview: canal houses](https://dutchreview.com/culture/amsterdam-canal-houses/)
  - [Wikipedia: Canal house](https://en.wikipedia.com/wiki/Canal_house)

**Inside a canal house**
- Narrow front, deep plan, front house and back house, very steep stairs, attic reached by an even steeper stair.
  - [Getty: canal house rooms](https://getty.edu/conservation/publications_resources/teaching/case/olita/building/other_rooms.html)
  - [Domino: 200-year-old staircase](https://www.domino.com/design-inspiration/ra-studio-home-tour-amsterdam-netherlands-canal-house/)
  - [Dwell: i29 canal house](https://dwell.com/article/canal-house-i29-67c9db55)

**A grand house with garden and coach house** (model for the auction house)
- [Wikipedia: Museum Van Loon](https://en.wikipedia.org/wiki/Museum_Van_Loon) (Keizersgracht 672, 1672): house, formal garden and coach house together.

**Bridges at night**
- [Amsterdam for Visitors: Magere Brug](https://www.amsterdamforvisitors.com/magere-brug-skinny-bridge-amsterdam/): white wooden drawbridge outlined in lights. Our drawbridge is an original design in this spirit.
- [Archilovers: Lightbridge (TJEP)](https://www.archilovers.com/projects/142960/lightbridge.html): describes the strings of plain bulbs that outline the arches of the old bridges.
- [Malay Mail: Amsterdam's glowing canals at night](https://malaymail.com/amp/news/travel/2017/11/29/light-up-exploring-the-glowing-canals-of-amsterdam-at-night/1521063)

**Houseboats**
- [Floating Homes: the houseboats of Amsterdam](https://ft.floatinghomes.org/the-houseboats-of-amsterdam/): roughly 2,400 in the city, several hundred in the canal ring.
- [Livius: Prinsengracht (CC0 photo)](https://www.livius.org/pictures/a/cdb/amsterdam-prinsengracht)

**Brown cafés**
- [I amsterdam: best brown bars](https://www.iamsterdam.com/en/see-and-do/eating-and-drinking/best-brown-bars): dark panelling, tobacco-brown ceilings, barrels over the bar, clutter on every wall.
- [National Geographic: Amsterdam bar life](https://www.nationalgeographic.com/travel/article/how-amsterdams-bar-life-continues-to-shape-the-city)

**Hofjes**
- [Culture Trip: Amsterdam's secret hofjes](https://theculturetrip.com/europe/netherlands/articles/the-story-behind-amsterdams-secret-hofjes)
- [Begijnhof photo, Dietmar Rabich, CC BY-SA 4.0](https://commons.wikipedia.com/wiki/File:Amsterdam_(NL),_Begijnhof_--_2015_--_7214.jpg): small houses around a quiet green courtyard, behind a single door from the street.

**Warehouses on the water**
- [Wikipedia: Entrepotdok](https://en.wikipedia.org/wiki/Entrepotdok): a long row of near-identical warehouses with shuttered loading doors, spout gables and hoist beams.

**Street furniture**
- [Wikipedia: Amsterdammertje](https://en.wikipedia.org/wiki/Amsterdammertje): red-brown bollard, about 1.35 m tall. Ours is plain, without the city arms.
- [Gijs Bakker: canal lamp post](https://gijsbakker.com/project/lamp-post-for-the-amsterdam-canals)
- [Selux: the historic canal lanterns](https://www.selux.com/fin/en/cases/grachten-lanterns-amsterdam)

**Markets and street life**
- [Amsterdam Sights: the floating flower market](https://amsterdamsights.com/shopping/flower-market.html): covered stalls built on barges moored along the canal.
- [DutchReview: barrel organs](https://dutchreview.com/dutch-quirks/dutch-quirk-3-barrel-organs-draaiorgel/)
- [Victorian Collections: herring cart model](https://victoriancollections.net.au/items/53cdbc8f2162f10c2c896b0a)

**Tower and lock**
- [Wikipedia: Westerkerk](https://Www.Wikipedia.org/wiki/Westerkerk): crowned spire and carillon. Our tower is an original design with a copper-green spire and a gilded ship weathervane.
- [Café de Sluyswacht listing](https://www.airbnb.nl/things-to-do/places/172180): a small leaning lock-keeper's house beside a lock (the listing gives 1695 for the building).

---

## 4. The map

**Dimension:** `recrafted:amsterdam`, built by a new `tools/mapgen/amsterdam/` module and served by the existing
`MapChunkGenerator`.
- **Size:** 384 × 320 blocks, a little larger than Corvara.
- **Water:** canal surface at y 62, quays at y 64, canals 4 blocks deep.

```
 N                                     THE IJ  (open harbour water, ferry lane)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  │
 │  [Station platform]  [Ferry pier]   ANKERKADE warehouses ▤▤▤▤▤▤  [Smuggler dock] │
 │      exit ▲              exit ▲      (De Ster brewery in the last two)           │
 │  ══ lock ═╗ ~~~~~~~~~~ WESTERDOK basin ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ │
 │  [keeper] ║                                                                     │
 │ ~~~~~~~~~~╩~~~~~~~~~~~~~~~ TOUWSLAGERSGRACHT (outer canal) ~~~~~~~~~~~~~~~~~~~~~ │
 │  houseboats ▭▭▭▭  Kooistra's houseboat ▭   ▭▭   [bridge keeper's booth]          │
 │  ▥▥▥▥▥ canal houses ▥▥▥▥▥ │ ZILVERSTEEG │ ▥▥ café · herring · bike shop ▥▥▥      │
 │ ~~~~~~~~~~~~~~~ GILDEGRACHT (inner canal) ~~~~ drawbridge ╪ ~~~~~~~~~~~~~~~~~~~~ │
 │  ▓ GULDEN HAMER ▓ formal garden ▓ coach house │ forger's house ▥ (7 floors)      │
 │  BLOEMENPLEIN · floating flower market         │ ANKERKERK ♜ + carillon            │
 │  Hofje van de Zeven Zusters                    │ police post                       │
 └───────────────────────────────────────────────────────────────────────────────┘
```

### Districts

| District | What's there | Feel |
|---|---|---|
| **Ankerkade** (north) | Harbour front on the IJ: station platform (exit), free ferry pier (exit), a row of shuttered warehouses with hoist beams, De Ster brewery in the last two, and the smuggler's covered dock. | Industrial, wide open, wind and gulls, sodium-orange light. |
| **Westerdok basin and the lock** | Basin between harbour and canals. A working lock (sluis) with a tiny leaning lock-keeper's house. Every boat into the canals passes here. | Narrow, mechanical, a choke point. |
| **Touwslagersgracht** (outer canal) | Houseboats along the quay (one is Kooistra's), simpler 18th-c. houses with bell and neck gables, the bridge keeper's booth, elms and bike racks. | Residential, lived-in, plants on the houseboat roofs. |
| **Zilversteeg** (cross street) | Narrow shopping alley linking the two canals: brown café *In de Gouden Ton*, herring cart, bike shop, cheese shop, tobacconist, Delftware shop. | Cosy, crowded, warm light spilling out. |
| **Gildegracht** (inner canal) | The grand canal: wide double houses with cornice and neck gables, the white drawbridge, stone arched bridges lit with bulbs. | Wealth, quiet, polished brass doorbells. |
| **Gulden Hamer** | Auction house in a double-wide 1670s patrician house (modelled on the Van Loon layout): marble hall, saleroom under a chandelier, gallery, catering kitchen, offices, basement vault; formal garden and a coach house used as the loading bay. | Candlelight, oil paintings, evening dress. |
| **Bloemenplein** | Small square with the floating flower market (covered stalls on barges) and the street organ. | Colour, crowds, tourists. |
| **Forger's house** | Tall, narrow 1630s step-gabled house, 7 floors. The attic studio has a hoist door; a back house is joined by a courtyard; neighbouring attics connect. | Vertical, cramped, turpentine. |
| **Ankerkerk** | Church with a tall copper-green spire, carillon and climbable bell loft. | Landmark you can see from everywhere. |
| **Hofje van de Zeven Zusters** | Hidden almshouse courtyard behind a plain door: a dozen tiny houses round a garden. | Silent. The safe place on the map. |

### Vertical layers

1. **Canals:** swimmable. Dark water hides a swimmer, and NPCs on the quay can't see into it at dusk. Low arches let you pass under bridges.
2. **Quays:** cobbles (klinkers in herringbone), elms, bollards, lanterns, parked bikes.
3. **Houses:** about a third enterable. Front house and back house, steep stairs, a basement half below street level with its own door under the stoop.
4. **Rooftops:** a continuous route across the gables of the forger's block and the Gildegracht row. Skylights, gutters and downpipes to climb, hoist doors as entry points.
5. **Under:** auction vault, brewery cellars, a canal-side storm-drain run from the lock to the Gildegracht, and the café's beer cellar.

---

## 5. Story and briefing (draft)

> Amsterdam. Nine hundred thousand people, almost as many bicycles, and a hundred kilometres of canals that have
> carried other people's money for four centuries.
>
> The money meant for CINDER didn't vanish with the island. It is being washed through paint. A forger known only
> as *De Meester* turns out Golden Age masters that were never painted. Margriet Ostendorp sells them under the
> hammer at the Gulden Hamer to buyers who don't exist. Sem Kooistra takes the proceeds out through the canals
> in uncut stones.
>
> Tonight is the autumn sale. All three will be within half a kilometre of each other, and none of them will
> stand still.
>
> Remove all three. Recover the Gulden Hamer ledger. Be gone before the bells strike nine.

**Objectives:**
- Eliminate Margriet Ostendorp.
- Identify and eliminate De Meester.
- Eliminate Sem Kooistra.
- Recover the ledger.
- Leave Amsterdam.

**Intel (draft):**
- Catering at the Gulden Hamer is brought in. Nobody checks the faces of the waiters, but everybody checks their bags.
- The guest list is for bidders. A bidder's paddle opens every door the public may use.
- *De Meester* never signs his work. His apprentices say he is the only one who paints left-handed.
- Kooistra can't swim, so he never leaves the boat between stops.
- The bridge keeper raises the Gildegracht drawbridge for any boat that sounds its horn twice.

---

## 6. The targets: three different problems

### Margriet Ostendorp, auctioneer: **the crowd**
Owner of the Gulden Hamer. Charming, theatrical, never alone tonight.

- **Challenge:** a public event on a schedule. She is always in view of guests, press and security, so you work inside the crowd rather than around it.
- **Routine:** a timed script.
  - Receives guests in the marble hall.
  - Gives a toast on the gallery stairs.
  - Runs the sale from the podium, a fixed spot in front of ~40 guests, for a long block of time.
  - Takes a private viewing with one buyer in the vault.
  - Leaves by water taxi at the end. Too slow, and she's gone.
- **Security:**
  - A metal detector at the front door flags anything ILLEGAL and any gun.
  - The staff entrance through the coach house has no detector, but needs a staff outfit.
  - Ten auction security guards, two bodyguards (reused role).
- **Opportunities:**
  - *The chandelier:* its winch is in the attic. Loosen it and wait for her at the podium. Accident.
  - *The toast:* poison the champagne tray in the catering kitchen. Only her glass if you take it to her yourself as a waiter, or the whole tray (risky).
  - *The winning bid:* become the collector who wins Lot 9 (bidder's paddle plus the collector disguise). She takes you down to the vault alone for the handover.
  - *Lights out:* the saleroom spotlights run on one fuse board. Cut them mid-sale and act in the dark, but everyone turns.
  - *Long shot:* the saleroom's tall windows face the forger's attic across the canal. The Cicala Case pays off here.

### *De Meester*, the forger: **the unknown**
- **Challenge:** nobody knows his face.
  - Four painters in identical paint-stained smocks share the attic studio; three are apprentices.
  - Focus doesn't mark him and the objective reads *Identify De Meester* until you find out which one he is.
  - Killing the wrong painter is a non-target kill, and the real one panics. He locks himself in the back-house strongroom.
- **Ways to identify him:**
  - Watch them paint: he is the only left-hander, a distinct animation.
  - Read the wage book in the café's back room: he is the one who pays the others.
  - Overhear two apprentices in the courtyard.
  - Find the unfinished self-portrait in the strongroom.
- **Getting there:** the house is seven floors of steep stairs with a model in every room. The real route is up the rooftops and in through the hoist door.
- **Opportunities:**
  - *The hoist:* a crate of canvases hangs from the hoist beam over the quay. Cut the rope when he steps out for air under it. Accident.
  - *Turpentine:* soak the rags by the studio stove. A flash fire when he lights his pipe. Accident.
  - *Lead white:* he tastes his own pigments (the apprentices joke about it). A pinch of lead white in his tea. Poison.
  - *The sitter:* take the model's place for the portrait he's painting; he works close, back to the room.
  - *The drop:* the hoist door stands open seven floors above the cobbles.

### Sem Kooistra, smuggler: **the mover**
- **Challenge:** a moving target on water. He rides his salon boat *Zwaluw* in a loop: his houseboat → the drawbridge → under two bulb-lit stone bridges → the lock → the smuggler's dock on the IJ → back.
  - He stays aboard between stops with two deckhands and a skipper.
  - You can't simply follow on foot: quays run on one side at a time, and bridges are the only crossings.
- **Opportunities:**
  - *The drawbridge:* in the bridge keeper's booth, hold the bridge down or raise it at the wrong moment and the *Zwaluw* waits under the warehouse hoist with its crate.
  - *The lock:* open the wrong gate while the *Zwaluw* is in the chamber and the boat drops hard against the sill. He goes over and he can't swim. Accident.
  - *The cabin heater:* sabotage the gas line on his houseboat before he boards at his first stop. He lights the heater on the second leg.
  - *His jenever:* the stone bottle on the houseboat bar.
  - *Take the wheel:* knock out the skipper at the smuggler's dock and steer the *Zwaluw* yourself. A new disguise, a new route, and nobody on board checks who's steering.
  - *The pike:* a deckhand's boat hook leans by the gangway. Shove him over the rail at a stop.
  - *Underneath:* a speargun on a diver's houseboat, fired from the water.

**Exits:**
- The station platform.
- The IJ ferry.
- A water taxi at the Gildegracht landing.
- A courier's cargo bike in Zilversteeg.
- The *Zwaluw* herself, if you're on board when you finish.

---

## 7. The cast

**About 145 NPCs across 25 roles.** Reuse stays well under 35% on both counts:
- **By role:** 6 of 25 roles are reused (24%).
- **By head count:** about 46 of 145 NPCs are in reused roles (32%).
- Every reused role still gets new Amsterdam skins.

| Role | Count | Reused? | Notes |
|---|---:|:---:|---|
| Civilian (Amsterdammer) | 14 | ♻ | Raincoats, scarves, umbrellas. |
| Tourist | 14 | ♻ | Rain ponchos, maps, cameras; clump at the flower market. |
| Waiter | 7 | ♻ | Café and Gulden Hamer catering. **Disguise:** catering kitchen. |
| Cook | 3 | ♻ | Café kitchen, catering. |
| Cleaner | 4 | ♻ | Auction house, station. |
| Bodyguard | 4 | ♻ | Ostendorp's two plus two at the vault. Vento .357. |
| Cycle courier | 6 | new | Fast routes, cut across bridges. **Disguise:** most of the map plus the cargo-bike exit. |
| Tour-boat skipper | 4 | new | Glass-roofed canal boats on a slow loop (uses the boat system). |
| Houseboat resident | 6 | new | Potter about on deck, water plants. |
| Flower seller | 5 | new | Floating market stalls. |
| Herring vendor | 2 | new | Cart in Zilversteeg. |
| Bartender | 3 | new | *In de Gouden Ton*. **Disguise:** café back room and wage book. |
| Street organist | 1 | new | Plays the organ in the square. The music masks noise nearby. |
| Police officer | 12 | new | Patrol in pairs; guard role. Reiger pistols. |
| Auction security | 10 | new | Guard role, earpiece and dark suit. **Disguise:** the vault and the detector. |
| Lot porter | 6 | new | White gloves, carry paintings. **Disguise:** staff areas, coach house. |
| Art collector | 14 | new | Evening dress, bidder paddles. **Disguise:** the saleroom and the Lot 9 route. |
| Press photographer | 4 | new | Flash bursts. **Disguise:** the gallery mezzanine. |
| Apprentice painter | 3 | new | De Meester's lookalikes. **Disguise:** the studio. |
| Bridge keeper | 2 | new | Booth and lock house. **Disguise:** bridge and lock controls. |
| Deckhand | 8 | new | Kooistra's crew; guard role. Snoek SMG. **Disguise:** the smuggler's dock. |
| Warehouse porter | 8 | new | Brewery and warehouses. |
| Margriet Ostendorp | 1 | target | |
| *De Meester* | 1 | target | Shares the apprentice skin set; tells only by behaviour. |
| Sem Kooistra | 1 | target | |

Map-only extras: a sixth wearable role is the *model* (the forger's sitter), who exists only in the studio.

---

## 8. New props

All are placed on the map like Corvara's props and use the existing prop system (Kind + flags). They can be
thrown with **X** where marked.

| Prop | Kind / flags | Where | Use |
|---|---|---|---|
| Clog (klomp) | BLUNT, THROW | Souvenir shop, houseboats | Knock-out throw. |
| Cheese wheel | BLUNT, THROW | Cheese shop | Heavy, short range, loud. |
| Delft vase | BLUNT, THROW, BREAKS | Delftware shop, auction gallery | Breaks with a crash: distraction. |
| Stone jenever bottle | BLUNT, THROW, BREAKS | Café, houseboats | Like the wine bottle, louder. |
| Boat hook (pikhaak) | BLUNT | Houseboats, the *Zwaluw* | Long reach; **shove** someone off a quay or deck into the water. |
| Bike chain lock | WIRE | Bike shop, racks | A second, legal-looking garrotte. |
| Palette knife | SHARP, THROW | Forger's studio | Quiet blade. |
| Gavel | BLUNT | Auction podium, offices | Legal inside the Gulden Hamer. |
| Umbrella | BLUNT | Everywhere | Legal anywhere. Held open in the rain, it makes enforcers take longer to recognise you. |
| Turpentine | SABOTAGE | Studio, bike shop | Soak rags or a stove: flash-fire accident. |
| Tulip bulbs | EMETIC | Flower market | Mild emetic in food or drink (they are mildly toxic). |
| Lead-white pigment | LETHAL | Studio | Slow poison. The forger's opportunity. |
| Bidder paddle | KEYCARD | Collectors, reception desk | Opens the public rooms of the Gulden Hamer. |
| Bridge keeper's key | KEYCARD | Booth, lock house | Bridge and lock controls. |
| Press camera | MISC | Photographers | Flash: blinds a guard for a moment; part of the press disguise. |

---

## 9. New weapons (Recrafted Arsenal, same pipeline as the first nine)

| Gun | What it is | Who carries it / where it is |
|---|---|---|
| **Reiger** | Slim 9 mm service pistol, light trigger. | Police officers; one in the police post locker. |
| **Snoek** | Compact SMG with an integral suppressor. | Kooistra's deckhands; spare in the dock office. |
| **Kievit** | Two-shot pocket derringer, tiny and loud. | Lot 3 in the auction vault display case; Ostendorp keeps a second in her desk. |
| **Harpoen** | Pneumatic speargun: one silent bolt, which you can pull back out of what it hits; works from the water. | Diver's houseboat on the Touwslagersgracht. |

Existing guns reused by role: bodyguards keep the Vento .357; auction security mixes Reiger and Halcyon PDW.

---

## 10. Custom blocks

Textures generated by `tools/assets` like the current set, in our own pixel art.

**Structure**
- **Canal-house brick ×4:** red-brown, dark plum, tarred black, ochre. Includes a "gable stone" variant with a small carved picture panel (several original motifs: ship, tulip, anchor, fish).
- **Gable pieces:** step, neck-gable scrolls, bell-gable curves, sandstone cornice and pediment: custom models so the skyline actually reads Amsterdam.
- **Sash windows:** white 8-pane, *lit* (emissive warm glow, readable from across a canal) and *dark*. Dark green and oxblood **shutters**.
- **Hoisting beam with hook and pulley:** functional. Holds a crate on a rope; cut the rope to drop it.
- **Klinker paving:** herringbone brick, dry and *wet* (with a sheen). Blue hardstone **quay edging**.
- **Rain gutter and downpipe:** climbable.

**Street**
- **Canal lantern:** cast-iron lamp post plus a wall-mounted version.
- **Bridge bulbs:** small emissive bulbs placed along the arches.
- **Bollard:** red-brown, plain.
- **Low canal railing, mooring post with rope.**
- **Bicycles:** parked, several colours, plus a bike rack.
- **Herring cart, cheese stack, tulip buckets, flower-stall awning.**
- **Street organ:** functional. Plays music; the area around it gets a noise mask.

**Water**
- **Houseboat hull and deck blocks.**
- **Drawbridge segment:** functional, raised or lowered from the booth.
- **Lock gates:** functional, with a water-level change in the chamber.

**Interiors**
- **Auction house:** podium, display cases with lit vitrines, rope barriers, framed paintings (original fictional artworks), a falling **chandelier**.
- **Forger's studio:** easel with canvas, pigment shelves, studio stove, Delft-blue wall tiles.
- **General:** Persian table carpets, a carillon bell (functional: ring it and the whole district looks up), and the **metal detector gate** (functional).

---

## 11. New systems this mission needs

| System | What it does | Notes / reuse |
|---|---|---|
| **Mission selection** | `/contract start amsterdam`; the Missions screen gets an AMSTERDAM tab with its own flyover frames (made by `-Pmenushots`). | Mission JSON already loads by id. |
| **Mission clock and timed routes** | Waypoints can carry a start time, so the auction runs on schedule and Ostendorp leaves when the sale ends. | Extends the existing routes. |
| **Unidentified targets** | Target flag hidden until a clue is found; clue sources are action blocks, readable items and overheard lines. Wrong kill → non-target plus a panic route. | New objective type `identify_eliminate`. |
| **Canal boats** | Kinematic boat entity that follows a water route with stops, carries NPCs (and the player) as passengers, and can be steered by a disguised player. | The biggest new piece. Also drives the tour boats. |
| **Water interactions** | Shove off a quay or deck; anyone who can't swim drowns as an accident. Bodies dumped in a canal sink out of sight. NPCs don't see swimmers at dusk. | Uses the existing accident and body-hiding rules. |
| **Crowd blending** | Standing among four or more civilians halves suspicion gain. | Matters at the flower market and in the saleroom. |
| **Metal detector** | Gate block that alerts security when anything ILLEGAL or a gun passes, unless you're in a security outfit. | |
| **Drawbridge and lock** | Controlled from booths; boats and pedestrians wait. | |
| **Atmosphere** | Custom dimension effects: drizzle, rain sound and fog colour. Rain shrinks footstep noise radius by ~30%. | Client-side; no change for other dimensions. |
| **Left-handed painting animation** | One extra pose for the forger. | Same `NpcPose` route as `SIT_ARMED`. |

---

## 12. Build order

1. **Greybox:** canals, quays, house massing, bridges, the lock; `walkcheck.py` passes. Screenshots for a layout check.
2. **Facades:** gable grammar (house width 5–9, 4–6 floors, gable type by street "age"), brick and window blocks, hoist beams, lit windows.
3. **Atmosphere:** dimension effects, lighting pass, bridge bulbs, fake reflections, sound. *Checkpoint: a screenshot tour at blue hour.*
4. **Interiors:** Gulden Hamer, forger's house, café, houseboats, warehouses, vault.
5. **Cast:** skins for 19 new roles plus rain variants of the six reused ones; routes for ~145 NPCs.
6. **Systems:**
   1. Mission clock.
   2. Unidentified target.
   3. Metal detector.
   4. Drawbridge and lock.
   5. Canal boats (largest).
7. **Targets and opportunities**, each with a scripted test in the client tour.
8. **Props and the four new guns.**
9. **Polish:** menu tab and flyover, briefing, self-test and client tour extended, README, jar.

---

## 13. Decisions for you

- **Hour and weather:**
  - Blue-hour drizzle (planned above).
  - Full night.
  - A rare winter evening with frozen canals and skaters. That's very atmospheric, but it rules out the boat target.
- **The boat system** is the largest single piece of work. If you'd rather keep scope down, Kooistra can instead move between his houseboat, the café and the dock on foot and by water taxi cut-scenes.
- **De Wallen (the red-light district) is left out on purpose.** It would pull the tone somewhere else and isn't needed for the story.
- **Ledger objective:** mandatory (as above) or optional bonus.
