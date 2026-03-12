"""Play Tony Dowler's 'How to Host a Dungeon'."""
from random import shuffle
from typing import List
from engine import screen, run
from landscape import strata_depth
from landscape import Stratum

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


def make_strata() -> List[Stratum]:
    colors = [(105,99,39),
              (137,131,75),
              (87,84,57),
              (177,169,96),
              (108,86,19),
              (125,117,93),
              (45,48,19)]
    shuffle(colors)

    results = []
    for i in range(6):
        results.append(Stratum(150 + i * 120, colors[i]))
    return results

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
                if entity.name in groups:
                    groups[entity.name] += 1
                else:
                    groups[entity.name] = 1
        print(groups)

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
