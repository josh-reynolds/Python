
from random import choice

detail1 = ["Rescue the ", "Find the ", "Destroy the ", "Infiltrate the ", "Bypass the ", "Return the ",
           "Defeat the ", "Spy on the ", "Bribe the ", "Deliver the ", "Escape the ", "Imprison the ",
           "Stop the ", "Befriend the ", "Pacify the ", "Persuade the ", "Steal the ", "Escort the ",
           "Banish the ", "Free the "]
detail2 = ["Goblet ", "Prisoner ", "Sword ", "Vault ", "Cult ", "Spirit ", "Killer ", "Demon ", "Noble ",
           "Hunter ", "Hostage ", "Thief ", "Spy ", "Werewolf ", "Relic ", "High Priest ", "Merchant ",
           "Witch ", "Ritual ", "Vampire "]
detail3 = ["of the Evil Wizard", "stalking the Wastes", "at the Bottom of the River", "in the City Sewers",
           "under the Barrow Mounds", "of the Fallen Hero", "in the Magical Library", "in the King's Court",
           "of the Ancient Lineage", "in the Sorcerer's Tower", "in the Murkwood", "hiding in the Slums",
           "of the Dwarven Lord", "in the Musty Tomb", "of the Royal Knights", "sacrificing Innocents",
           "in the Catacombs", "blackmailing the Baron", "in the Thieves' Guild", "murdering Townsfolk"]

def make_adventure():
    return choice(detail1) + choice(detail2) + choice(detail3)


for i in range(10):
    print(make_adventure())
