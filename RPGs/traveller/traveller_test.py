"""Contains tests for the traveller module."""
import unittest
from traveller import Game, Command, Commands

# most of these methods necessarily have side effects,
# so we're going to have to tease out the testable bits
# and or monkeypatch or mock
class GameTestCase(unittest.TestCase):
    """Tests game logic."""

    # __init__
    # run
    # quit
    # list_commands
    # liftoff
    # _low_lottery
    # land
    # outbound_to_jump
    # inbound_from_jump
    # leave_depot
    # leave_terminal
    # book_passengers
    # to_depot
    # to_terminal
    # jump
    # view_world
    # refuel
    # recharge
    # damage_control
    # repair_ship
    # flush
    # buy_cargo
    # sell_cargo
    # goods
    # cargo_hold
    # passenger_manifest
    # crew_roster
    # wait_week
    # view_ship
    # view_map
    # skim
    # maintenance
    # _get_passenger_destinations
    # _get_freight_destinations
    # _select_passengers
    # _select_freight_lots
    # load_freight
    # unload_freight


class CommandTestCase(unittest.TestCase):
    """Test Command objects."""

    # __init__


# for this one, might be helpful to trap whether
# any keys have been duplicated and thus overwritten
class CommandsTestCase(unittest.TestCase):
    """Tests command lists."""

    # no methods


# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
