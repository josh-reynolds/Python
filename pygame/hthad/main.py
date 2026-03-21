"""Play Tony Dowler's 'How to Host a Dungeon'."""
from engine import screen, run
from landscape import strata_depth, make_strata
from constants import WIDTH, HEIGHT, TITLE, GROUND_LEVEL
from constants import CREATURE
from constants import SKY, BORDER
from primordial_age import PrimordialAge
from monster_age import MonsterAge
from civilization_age import CivilizationAge
from utilities import get_all_entities

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

    if (counter - 50) % 200 == 0:
        groups = {}

        for entity in get_all_entities(locations):
            if entity.color == CREATURE:
                #print(f"Adding {entity.name} = {id(entity)} = {id(entity.parent)}")
                if entity.name in groups:
                    groups[entity.name] += 1
                else:
                    groups[entity.name] = 1
            entity.update()
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

    for index in range(6):
        screen.draw.text(f"{index+1}", center=(10, strata_depth(index)))
        screen.draw.text(f"{index+1}", center=(WIDTH-10, strata_depth(index)))

    # pylint: disable=E1121
    # E1121: Too many positional arguments for method call
    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    screen.draw.text(f"{current_stage.name}", center=(WIDTH//2, 30))

run()
