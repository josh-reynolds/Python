"""Contains tests for the traveller module."""
import unittest
from financials import Credits
from star_map import StarSystemFactory
from traveller import Game

# most of these methods necessarily have side effects,
# so we're going to have to tease out the testable bits
# and or monkeypatch or mock
class GameTestCase(unittest.TestCase):
    """Tests game logic."""

    def test_game_ctor(self) -> None:
        """Tests contstruction of a Game object."""
        game = Game()
        self.assertEqual(game.location,
                         StarSystemFactory.create("Yorbund", (0,0,0),
                                                  "A", 8, 7, 5, 9, 5, 5, 10))
        self.assertEqual(game.financials.balance, Credits(10000000))

    @unittest.skip("test has side effects: input & printing")
    def test_get_input(self) -> None:
        """Test requesting input from the controller."""
        game = Game()

        result2 = game.get_input('', "No constraint test.")

        result2 = game.get_input('confirm', "Confirmation test.")
        self.assertTrue(result2 in ['y', 'n'])

        result3 = game.get_input('int', "Integer input test.")
        self.assertTrue(isinstance(result3, int))

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_passenger_destinations of a client class
    @unittest.skip("test has side effects: printing")
    def test_get_passenger_destinations(self) -> None:
        """Test getting list of passenger destinations."""
        game = Game()
        potential_destinations = game.location.destinations.copy()

        destinations = game._get_passenger_destinations(potential_destinations, 1)
        print(destinations)

        # contracted destination:
        #     freight on board
        #     under contract and in range
        #     under contract but not in range
        # else

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_passenger_destinations of a client class
    @unittest.skip("test has side effects: printing")
    def test_get_freight_destinations(self) -> None:
        """Test getting list of freight destinations."""
        game = Game()
        potential_destinations = game.location.destinations.copy()

        destinations = game._get_freight_destinations(potential_destinations, 1)
        print(destinations)

        # contracted destination:
        #     freight on board
        #     under contract and in range
        #     under contract but not in range
        # else

    # _select_passengers
    # _select_freight_lots

    # side effects only ~ ~ ~ ~ ~ ~ ~
    # on_notify
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
    # _misjump_check
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
