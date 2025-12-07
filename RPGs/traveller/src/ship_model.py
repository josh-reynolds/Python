"""Contains classes and factory/utility functions to manage standard starship designs.

ShipModel - represents a specific ship model.

load_ship_model_data() - load and return the ship model data from a file.

ship_model_from() - return a ShipModel given a name.

get_ship_models() - return a list of available ShipModels.
"""
import json
from typing import List, Any, Dict, cast
from src.credits import Credits
from src.crew import Crew, Pilot, Engineer, Medic, Steward

# pylint: disable=R0902
# R0902: Too many instance attributes (12/7)
class ShipModel:
    """Represents a specific ship model."""

    # TO_DO: ctor is a little weird here... this class holds
    #        data loaded from a file. We are hardcoding one
    #        instance in the ctor.
    #        I think we should either:
    #          * have None values in ctor and trap an incomplete
    #            instance where appropriate
    #          * invoke the factory function from the ctor
    #          * hide the ctor so that the factory function is
    #            the only way to get an instance
    def __init__(self) -> None:
        """Create an instance of a ShipModel."""
        self.name = "Type A Free Trader"
        self.hull = 200
        self.passenger_berths = 6
        self.low_berths = 20
        self.acceleration = 1
        self.streamlined = True
        self.hold_size = 82
        self.fuel_tank = 30
        self.jump_range = 1
        self.jump_fuel_cost = 20
        self.trip_fuel_cost = 10
        self.base_price = Credits(37_080_000)
        self.crew_requirements: List[Crew] = []

    def __eq__(self, other: Any) -> bool:
        """Test if two ShipModels are equal."""
        if type(other) is type(self):
            return self.name == other.name and\
                    self.hull == other.hull and\
                    self.passenger_berths == other.passenger_berths and\
                    self.low_berths == other.low_berths and\
                    self.acceleration == other.acceleration and\
                    self.streamlined == other.streamlined and\
                    self.hold_size == other.hold_size and\
                    self.fuel_tank == other.fuel_tank and\
                    self.jump_range == other.jump_range and\
                    self.jump_fuel_cost == other.jump_fuel_cost and\
                    self.trip_fuel_cost == other.trip_fuel_cost and\
                    self.base_price == other.base_price
        return NotImplemented

    def __repr__(self) -> str:
        """Return the developer string representation of a ShipModel."""
        return f"ShipModel({self.name})"

def load_ship_model_data() -> Dict[str, Any]:
    """Load and return the ship model data from a file."""
    try:
        with open("data/ship_models.json", 'r', encoding='utf-8') as a_file:
            file_contents = json.load(a_file)
    except FileNotFoundError as exc:
        raise FileNotFoundError("Ship model file not found.") from exc
    return file_contents

def ship_model_from(name: str) -> ShipModel:
    """Return a ShipModel given a name."""
    file_contents = load_ship_model_data()
    data = file_contents[name]

    model = ShipModel()
    model.name = name
    model.hull = data["hull"]
    model.passenger_berths = data["passenger_berths"]
    model.low_berths = data["low_berths"]
    model.acceleration = data["acceleration"]
    model.streamlined = data["streamlined"]
    model.hold_size = data["hold_size"]
    model.fuel_tank = data["fuel_tank"]
    model.jump_range = data["jump_range"]
    model.jump_fuel_cost = data["jump_fuel_cost"]
    model.trip_fuel_cost = data["trip_fuel_cost"]
    model.base_price = Credits(data["base_price"])
    for crewmember in data["crew_requirements"]:
        match crewmember:
            case "Pilot":
                model.crew_requirements.append(cast(Crew, Pilot))
            case "Engineer":
                model.crew_requirements.append(cast(Crew, Engineer))
            case "Medic":
                model.crew_requirements.append(cast(Crew, Medic))
            case "Steward":
                model.crew_requirements.append(cast(Crew, Steward))

    return model

def get_ship_models() -> List[str]:
    """Return a list of available ShipModels."""
    file_contents = load_ship_model_data()
    return list(file_contents.keys())
