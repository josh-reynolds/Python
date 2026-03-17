"""Play Tony Dowler's 'How to Host a Dungeon'."""
from engine import screen, run
from landscape import strata_depth, make_strata

# pylint: disable=W0611
# W0611: Unused TITLE imported from constants (unused-import)
from constants import WIDTH, HEIGHT, TITLE, BEAD, GROUND_LEVEL, CAVERN
from constants import FINGER, CREATURE, EVENT, STRATA_HEIGHT, DWARF, TREASURE
from constants import ROOM_SPACING, GROUND, SKY, BORDER, WATER, SHOW_LABELS
from primordial_age import PrimordialAge
from monster_age import MonsterAge
from civilization_age import CivilizationAge
from utilities import get_all_entities, check_for_connections, create_location

locations = []
strata = make_strata()

# TO_DO: need to keep track of yearly events

# TO_DO: don't store all locations in locations list, we just need
#        one node (i.e. location) for each graph

counter = 1
stages = [PrimordialAge(), CivilizationAge(), MonsterAge()]
current_stage = stages.pop(0)

def update() -> None:
    """Update game state once per frame."""
    global counter, locations, current_stage

    # probably want to make the Ages into a FSM
    if counter % 200 == 0:
        locations += current_stage.update(locations)
        if current_stage.is_done():
            current_stage = stages.pop(0)

        groups = {}

        for entity in get_all_entities(locations):
            if entity.color == CREATURE:
                #print(f"Adding {entity.name} = {id(entity)} = {id(entity.parent)}")
                if entity.name in groups:
                    groups[entity.name] += 1
                else:
                    groups[entity.name] = 1
        print(groups)

        #for location in locations:
            #print(f"{location.name} = {id(location)}")

    # TO_DO: all of the update methods are stubs - are we
    #        going to use this?
    for location in locations:
        location.update()

    counter += 1

def draw() -> None:
    """Draw the game screen once per frame."""
    for stratum in strata:
        stratum.draw()

    for location in locations:
        location.draw()

    if isinstance(current_stage, CivilizationAge):
        candidates = []
        if current_stage.mine_start:
            candidates = current_stage.mine_start.get_locations_by_name("Great Hall")
        for room in candidates:
            screen.draw.rect(room.rect.x, room.rect.y,
                             room.rect.w, room.rect.h,
                             color=(255,0,0), width=2)

    for index in range(6):
        screen.draw.text(f"{index+1}", center=(10, strata_depth(index)))
        screen.draw.text(f"{index+1}", center=(WIDTH-10, strata_depth(index)))

    # pylint: disable=E1121
    # E1121: Too many positional arguments for method call
    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    screen.draw.text(f"{current_stage.name}", center=(WIDTH//2, 30))

run()

# ---------------------------------------------
# May want to keep the spirit of the original rather than try to exactly
# duplicate - it's a bunch of analog pen-on-paper mechanics, and a lot of
# things are left as aesthetic judgement calls on the part of the player.
#
# Also the rules are very handwavy about a lot of things. Will need to
# make decisions how to handle.
#
# Random ideas:
#
# What if the tailings from mining are gathered and need to go somewhere,
# like a heap on the surface?
#
# I was envisioning mining involving grabbing all the pixels under the
# mine square and treating each one as an entity - either dirt, water,
# gold or mithril right now.

# print(screen.surface.get_at((WIDTH//2,HEIGHT//2)))

# OPEN QUESTIONS
# How to handle collisions during the Primordial and Civilization setup phases?

# ---------------------------------------------
# line segment - rectangle intersection:
#   check intersection of line segment with each side of rectangle
#   special case: line segment entirely within rectangle
#
# line segment intersection:
#   see Stack Overflow 563198
#
# ---------------------------------------------
# We should generalize the pattern for creating a cave/room so we
# get consistent behavior, and can work out things like collisions
# in a uniform manner. Primordial age caves and the start of the
# dwarf mine don't obey the rules laid down later.
#
# In particular we should lay down one cave/room at a time, and check
# for collisions immediately. Then, if there is a connecting room to
# be generated as part of the cluster, test the tunnel first, then
# the new room.
#
# The compound creation functions should be broken up so we can
# do just one location at a time.
#
# Current steps (consolidated):
# 1) get a coordinate to place the location
#       get_random_underground_location()
#       get_orbital_point()
#       <determine x_location of mine>
#       get_parent_room()
#           get_candidate_room()
# 2) set color
# 3) set contents
# 4) embellishments (tunnels)
# 5) check for collisions/connections
# 6) if part of complex, add another per step 1 and connect
#
# ---------------------------------------------
# I'm contemplating compositing all the 'landscape' locations into a
# single bitmap. Ideally the locations list should only contain Caverns
# and Rooms.
#
# This meshes with the per-pixel ideas above. Treat every background image
# pixel as a resource unit. Currently we have dirt, mithril, gold and water.
#
# We'd need to change all the code that interacts with those location's
# coordinates. Drawing is easy - just draw the bitmap. For mine start, we
# could do ray-casting from the surface down until we strike a mineral. And
# so on.
#
# ---------------------------------------------
# How to handle interaction between the groups? I _think_ there's a pretty
# basic one-for-one attrition when groups meet, with only the larger
# group remaining. Probably some nuance, but that's a good place to start.
#
# So how about each update pass we check all entities to see if they can
# reach another team, then kill off the losers? We need:
#
# Tally all creature entities overall
# Clump together into groups (same name in same graph)
# Identify any graphs containing more than one group
# Eliminate entities accordingly
#
# By this logic, a graph shouldn't ever have more than two groups, right?
# Could there be some odd timing where this happens? A newly-added room
# tunnels into two different graphs simultaneously?
#
# ---------------------------------------------
# Another thought - it would be good to show the rooms/caves being added
# one by one. Technically they are, but it's too fast to see.
#
# I think we need to leverage the update() function. Use a counter to
# slow things down (so we invoke object.update() every 10 frames or
# whatever). At least two pulses I can think of right now:
#
# * Creation of new rooms
# * Interaction between creature groups
#
# So we'll need something to receive the update pulses. How about a class
# (or classes) to represent each game phase. Let's start with Primordial.
#
# ---------------------------------------------
# Priorities:
# 1) fix room creation sequence so we properly handle collisions, connections
#    invalid positions and lack of viable candidates in all cases
# 2) implement entity group interaction, population loss, etc.
# 3) refactor bloated code - getting out of hand again
#
# ---------------------------------------------
# It might be helpful to introduce builder objects that can govern
# the goals above. The assorted factory methods are partway there, but the
# current implementation has a mix of approaches. A standardized builder
# could get us there. We can still have a simple list of locations, and
# the builders themselves would be cleaned up once they've finished.
#
# I was intiially thinking about how to do this via the locations themselves.
# That still might be an option. But lots of plumbing required - would need
# to propagate update & draw events through the chain, etc. (This is the
# idea that rather than have a flat locations list, we'd just retain one
# node per graph - or potentially a 'graph' object - and have them manage
# themselves.)
# ---------------------------------------------
# Cataloging current location creation approaches:
#
# Caverns:
# PrimordialAge.update()
#   add_caverns()
#     natural_cavern_factory()
#       get_random_underground_location()
#       create_location()
#       CUSTOMIZE
#
#   cave_complex_factory()
#     get_random_underground_location()
#     create_location()
#     CUSTOMIZE
#     get_orbital_point()
#     create_location()
#     CUSTOMIZE
#     get_orbital_point()
#     create_location()
#     CUSTOMIZE
#     CONNECT
#
#   ancient_wyrm_factory()
#     get_random_underground_location()
#     create_location()
#     CUSTOMIZE
#     get_orbital_point()
#     create_location()
#     CUSTOMIZE
#     CONNECT
#
#   CALCULATE NEW LOCATION  # inside UndergroundRiver creation
#   create_location()
#   CUSTOMIZE

# Rooms:
# PrimordialAge.update()
#   get_mine_start_location()
#   dwarf_mine_factory()
#     create_location()      # start
#     CUSTOMIZE
#     CALCULATE NEW LOCATION
#     create_location()      # barracks
#     CUSTOMIZE
#     CALCULATE NEW LOCATION
#     create_location()      # mine
#     CUSTOMIZE
#     CONNECT
#
#   get_parent_rooms()     # treasure vault, barracks, great hall, hall of records, dwarf city
#   get_candidate_room()
#     add_candidate()
#       CALCULATE NEW LOCATION
#       create_location()
#       if is_viable():
#         CONNECT
#       else:
#         REMOVE CANDIDATE
#   CUSTOMIZE
#   CONNECT
#
#   DETERMINE MINE DIRECTION   # mines
#   get_y_at_x()
#   create_location()
#   CUSTOMIZE
#   CONNECT
#
#   get_parent_rooms()   # workshops
#   CALCULATE NEW LOCATION
#   create_location()
#   CUSTOMIZE
#   CONNECT
#
#   FIND MAIN SHAFT BOTTOM  # exploratory shaft
#   CALCULATE NEW LOCATION
#   create_location()
#   CUSTOMIZE
#   CONNECT
#
#   get_candidate_room()    # treasure room (parents=all)
#     add_candidate()
#       CALCULATE NEW LOCATION
#       create_location()
#       if is_viable():
#         CONNECT
#       else:
#         REMOVE CANDIDATE
#   CUSTOMIZE
#
#   FIND MINE COMPLEX BOTTOM   # dig too deep
#   CALCULATE NEW LOCATION
#   create_location()
#   CUSTOMIZE
#   CONNECT
#
# ----------------------------------------------------------------------------------------------
#                               ROOMS                                    | CAVERNS
#                               DD TR ES GH HR DC WS MN BR TV ST STB STT | UR AW AWT CCS CC+ CV
# 1. find potential coordinates                                          |
#       calculated               .  .  .  .  .  .  .  .  .  .  x   .   . |  x  x   .   x   .  x
#       offset from parent       x  x  x  x  x  x  x  x  x  x  .   x   x |  .  .   x   .   x  .
# 2. test viability              .  x  .  x  x  x  .  .  x  x  .   .   . |  .  .   .   .   .  .
# 3. customize                   x  x  x  x  x  x  x  x  x  x  x   x   x |  x  x   x   x   x  x
# 4. connect parent              x  .  x  x  x  x  x  x  x  x  .   x   x |  .  .   x   .   x  .
# 5. proximity connections                                               |  .  .   .   .   .  .

# generalizing location creation:
#
# 1. is this the start of a new graph, or attached to existing?
#    A. START OF NEW (CV, CCS, AW, AR, UR, ST)
#       1. calculate a coordinate
#          get_random_underground_location() | UndergroundRiver() | get_mine_start_location()
#       2. create location
#          create_location()
#       3. customize it
#          DIRECT ACCESS

#    B. ATTACHED TO EXISTING (CC+, AWT, STB, STT, TV, BR, GH, HR, DC, MN, WS, ES, TR, DD)
#       1. determine parent node candidates
#          BAKED IN | get_parent_rooms() | MINE LAYOUT | SHAFT BOTTOM | COMPLEX BOTTOM | ALL
#       2. calculate offset from parent - if none, bail out
#          get_orbital_point() | BAKED IN OFFSET | DIRECTIONAL CALC
#       3. test for legality
#          TRUE | is_viable()
#          a. if illegal loop back to 1.B.2. with next parent
#          b. if legal
#             1. create location
#                create_location()
#             2. customize it
#                DIRECT ACCESS
#             3. attach to parent
#                OBJECT METHOD
#             4. check for proximity and make more connections
#                check_for_connections()
#
# Notes:
#  - might help to convert some of the inline code to functions, then this could become a strategy
#    that we customize by passing in function objects. The ALL CAPS entries above.
#  - the 'missing' viability tests could be interpreted as a lambda that always returns True
#  - with this kind of flexibilty we could cook up all kinds of variations just by plugging in
#    different functions
#  - the 'clumped' creation sequences should be broken up - mine start, cavern complex, etc. These
#    are really higher level factories or builders - separate them from actual location creation,
#    and probably allow for sequential building rather than all at once.
#
# Current sequencing - - - - - -
# Every 200 frames:
#   Get list of Locations from current_stage.update()
#     PrimordialAge:
#       randomly add either a landscape object or group of locations
#         methods/ctors return individual or lists of objects
#     CivilizationAge:
#       maintain internal state ('step')
#       return group of locations 
#   Add list to global locations
#   If done, next stage
#   
# what if instead we:
#   current_stage.update()
#     if current builder done or none, add one
#     ask current builder for next location
#       builder concrete classes contain body of code from case statements & factory funcs
#     set stage done when builders exhausted
#
# class LocationStrategy:
#   def next() -> List[Location]     # consider landscape 'locations' too
#   def is_done() -> bool
#
# ----------------------------------------------------------------------------------------------
# For creature entities, I was initially thinking of grouping them, then managing behavior by
# group. But what if we let each think for itself?
#
# 1) Only one entity per location
# 2) Each entity can see into its neighboring locations
# 3) If the neighbor is a treasure not belonging to them (how do we know?)
#    they steal it. Can they pick it up? Where do they bring it?
# 4) If the neighbor is a creature not on their team (same name?), they
#    attack it. If they win the fight, they move to the location.
# 5) If the neighbor is empty, they move to it.
#
# Considerations:
# 1) Ordering. Who goes first? Does this give advantage to some teams?
# 2) We aren't accounting for Event entities yet.
# 3) Should we color Locations by ownership? Zones of control?
# 4) If entities can pick up treasure, we could even model things like dwarves
#    carrying mining output back to their base.
# 5) And if we go that far, could even have 'mining' as an action, for digging
#    new rooms. Not all creatures are capable of this.
# 6) But... since the 'turns' are seasons at the fastest, maybe modelling indviduals
#    scurrying around isn't desirable, so don't worry about 4 & 5, at least not yet.
# 7) But we _could_ have defeated creatures drop whatever treasure they are
#    carrying.
# 8) We need to track deaths per year for the dwarven winter.
# 10) There's also the issue of modifying the list we're iterating over: if
#     a creature wins the fight and its opponent is removed, then we'll have bugs.
#     Might be better to mark 'dead' (and potentially even show graphically), then
#     in a later pass remove all dead creatures. This could allow us to tally losses
#     for point 9 - though it does mean that the victor does not move into the
#     captured space.


