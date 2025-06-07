from random import choice

def adjectives():
    return choice(["bloody", "ashen", "ebon", "dark", "lost", "forgotten", "black", "red", "sunless", 
                   "iron", "sinister", "icy", "evil", "chaotic", "forsaken", "burning", "damned", 
                   "buried", "stone", "ruined", "collapsed", "dread", "secret", "hellish",
                   "putrid", "rotten", "decayed", "white", "shadowed", "festering", "frozen",
                   "weird", "blue", "green", "yellow", "orange", "purple", "golden", "silver",
                   "scarred", "charred", "hidden", "mysterious", "mad", "slave", "subterranean",
                   "fey", "glowing", "sunken"])

def locations():
    return choice(["castle", "city", "field", "tomb", "crypt", "island", "plain", "keep", "citadel", 
                   "tower", "ruin", "caverns", "shrine", "vault", "fortress", "pit", "door", 
                   "bog", "swamp", "chasm", "lake", "tarn", "tor", "village", "temple", "gate", 
                   "fountain", "barrow", "burial" "mound", "lair", "watchtower", "eyrie", 
                   "sepulcher", "catacombs", "fort", "isle", "cave", "well", "pyramid", "ziggurat",
                   "hall", "cathedral", "library"])

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
                   "shadows", "sphinxes", "stags", "unicorns", "troglodytes", "toads", "wasps", "wyverns",
                   "flies", "maggots", "angels", "thieves", "assassins", "druids", "bards"])

def things():
    return choice(["bone", "ash", "blood", "night", "snake", "reaver", "wonder", "obelisk", 
                   "horror", "secret", "ice", "frost", "stone", "hell", "mold", "rot", "slime",
                   "filth", "sword", "wand", "crown", "tombstone", "throne", "staff", "helm",
                   "bile", "flesh", "soot", "spear", "evil", "chaos", "skull", "souls", "spirits",
                   "fire", "axe", "madness", "orb", "tome", "codex", "grimoire", "cauldron",
                   "victory", "hope"])

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
                   "shadow", "sphinx", "stag", "unicorn", "troglodyte", "toad", "wasp", "wyvern",
                   "fly", "maggot", "angel", "thief", "assassin", "druid", "bard"])

def make_title():
    return choice([
        f"The {adjectives()} {locations()}",
        f"{locations()} of {groups()}",
        f"{locations()} of {things()}",
        f"{locations()} on the {landscapes()}",
        f"The {locations()} of the {individuals()}",
        f"{locations()} of the {groups()}",
        f"The {locations()} of {adjectives()} {things()}",
        f"The {things()} of {adjectives()} {locations()}"])


if __name__ == '__main__':
    for i in range(30):
        print(make_title().title())

