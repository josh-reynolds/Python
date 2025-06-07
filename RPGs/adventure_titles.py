from random import choice

# The Black Castle
# City of Reavers
# Field of Blood
# Tomb of Snakes
# Island of Wonders
# City of Kings
# Island of Obelisks
# Plain of Bones
# Tomb of Horrors
# The Forgotten Tomb
# Keep on the Borderlands
# The Sunless Citadel
# The Tower of the Witch
# The Lost Caverns
# The Forgotten Temple
# Shrine of the ...
# Vault of the ...
# Fortress of the ...
# The Forbidden City
# Pit of Night
# The Ebon Door

# Blood, Bone, Ash, Ebon, Night, Dark, Lost, Forgotten, Black, Snakes, Reavers, Wonders, Kings,
# Obelisks, Horrors, Sunless, Iron, Sinister, Secrets, Winter, Ice, Frost, Evil, Chaos, Forsaken,
# Burning, Damned, Buried, Stone, Ruined, Collapsed, Dread, 


# Castle, City, Field, Tomb, Crypt, Island, Plain, Keep, Citadel, Tower, Ruin, Caverns, Shrine,
# Vault, Fortress, Pit, Door, Bog, Swamp, Chasm, Lake, Tarn, Tor, Village, Temple, Gate, Fountain,
# Secret, Mystery, Barrow, Burial Mound, Lair, Watchtower, Eyrie, Sepulcher, Catacombs, 

# Witch, Snake, Demon, Dragon, Beast, Warlord, King, Conqueror, Spiders, Frogs, Wolves, Bear,
# Warlock, Wizard, Dwarf, Elf, 

# The <Adjective> <Location>
# <Location> of <Group>
# <Location> of <Thing>
# <Location> on the <Landscape>
# The <Location> of the <Individual>
# <Location> of the <Group>

def adjectives():
    return choice(["bloody", "ashen", "ebon", "dark", "lost", "forgotten", "black", "red", "sunless", 
                   "iron", "sinister", "icy", "evil", "chaotic", "forsaken", "burning", "damned", 
                   "buried", "stone", "ruined", "collapsed", "dread", "secret", "hellish",
                   "putrid", "rotten", "decayed", "white", "shadowed", "festering", "frozen",
                   "weird", "blue", "green", "yellow", "orange", "purple", "golden", "silver",
                   "scarred"])

def locations():
    return choice(["castle", "city", "field", "tomb", "crypt", "island", "plain", "keep", "citadel", 
                   "tower", "ruin", "caverns", "shrine", "vault", "fortress", "pit", "door", 
                   "bog", "swamp", "chasm", "lake", "tarn", "tor", "village", "temple", "gate", 
                   "fountain", "barrow", "burial" "mound", "lair", "watchtower", "eyrie", 
                   "sepulcher", "catacombs", "fort", "isle", "cave"])

def groups():
    return choice(["witches", "snakes", "demons", "dragons", "beasts", "warlords", "kings", 
                   "conquerors", "spiders", "frogs", "wolves", "bears", "warlocks", "wizards", 
                   "dwarves", "elves", "reavers", "wonders", "obelisks", "horrors", "giants",
                   "ogres", "trolls", "vampires", "bats" , "skeletons", "zombies", "goblins",
                   "wraiths", "phantoms", "ghosts", "ghouls", "griffons", "apes", "beetles", "boars",
                   "crabs", "scorpions", "bulls", "centaurs", "minotaurs", "devils", "fiends", "djinns",
                   "turtles", "lizards", "eagles", "falcons", "hawks", "eels", "fungi", "gargoyles",
                   "hounds", "imps", "jackals", "werewolves", "jaguars", "leopards", "lions", "tigers",
                   "lynx", "mammoths", "elephants", "manticores", "hags", "nightmares", "octopuses",
                   "squids", "orcs", "otters", "owls", "worms", "rats", "salamanders", "sharks",
                   "shadows", "sphinxes", "stags", "unicorns", "troglodytes", "toads", "wasps", "wyverns"])

def things():
    return choice(["bone", "ash", "blood", "night", "snake", "reaver", "wonder", "obelisk", 
                   "horror", "secret", "ice", "frost", "stone", "hell", "mold", "rot", "slime",
                   "filth", "sword", "wand", "crown", "tombstone", "throne", "staff", "helm",
                   "bile", "flesh", "soot", "spear", "evil", "chaos", "skull"])

def landscapes():
    return choice(["borderlands", "hill", "plain", "forest", "swamp", "bog", "canyon", "lake",
                   "pond", "mountain", "peak", "volcano", "caldera", "rift", "chasm", "marsh",
                   "river"])

def individuals():
    return choice(["witch", "snake", "demon", "dragon", "beast", "warlord", "king", "conqueror", 
                   "spider", "frog", "wolf", "bear", "warlock", "wizard", "dwarf", "elf", "giant",
                   "ogre", "troll", "lich", "vampire", "bat", "skeleton", "zombie", "goblin",
                   "wraith", "phantom", "ghost", "ghoul", "griffon", "ape", "beetle", "boar",
                   "crab", "scorpion", "bull", "centaur", "minotaur", "devil", "fiend", "djinn",
                   "turtle", "lizard", "eagle", "falcon", "hawk", "eel", "fungus", "gargoyle",
                   "hound", "imp", "jackal", "werewolf", "jaguar", "leopard", "lion", "tiger",
                   "lynx", "mammoth", "elephant", "manticore", "hag", "nightmare", "octopus",
                   "squid", "orc", "otter", "owl", "worm", "rat", "salamander", "shark",
                   "shadow", "sphinx", "stag", "unicorn", "troglodyte", "toad", "wasp", "wyvern"])

def make_title():
    return choice([
        f"The {adjectives()} {locations()}",
        f"{locations()} of {groups()}",
        f"{locations()} of {things()}",
        f"{locations()} on the {landscapes()}",
        f"The {locations()} of the {individuals()}",
        f"{locations()} of the {groups()}",
        f"The {locations()} of {adjectives()} {things()}"])


if __name__ == '__main__':
    for i in range(30):
        print(make_title().title())

