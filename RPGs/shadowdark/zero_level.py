from random import randint, choice

ancestries = ["Human"] * 4 + ["Elf"] * 2 + ["Dwarf"] * 2 + ["Halfling"] * 2 + ["Half-orc"] + ["Goblin"]
backgrounds = ["Urchin", "Wanted", "Cult Initiate", "Thieves' Guild", "Banished", "Orphaned", "Jeweler",
               "Wizard's Apprentice", "Herbalist", "Barbarian", "Mercenary", "Sailor", "Acolyte", "Soldier",
               "Ranger", "Scout", "Minstrel", "Scholar", "Noble", "Chirurgeon"]
alignments = ["Lawful"] * 3 + ["Neutral"] * 2 + ["Chaotic"]
gear = ["Torch", "Dagger", "Pole", "Shortbow & 5 arrows", "Rope, 60'", "Oil flask", "Crowbar",
        "Iron spikes (10)", "Flint & steel", "Grappling hook", "Club", "Caltrops"]
languages = ["Dwarvish", "Elvish", "Giant", "Goblin", "Merran", "Orcish", "Reptilian", "Sylvan", "Thanian"]
names = {"Human": ["Zali", "Bram", "Clara", "Nattias", "Rina", "Denton", "Mirena", "Aran", "Morgan",
                   "Giralt", "Tamra", "Oscar", "Ishana", "Rogar", "Jasmin", "Tarin", "Yuri",
                   "Malchor", "Lienna", "Godfrey"],
         "Dwarf": ["Hilde", "Torbin", "Marga", "Bruno", "Karina", "Naugrim", "Brenna", "Darvin", "Elga",
                   "Alric", "Isolde", "Gendry", "Bruga", "Junnor", "Vidrid", "Torson", "Brielle",
                   "Ulfgar", "Sarna", "Grimm"],
         "Elf": ["Eliara", "Ryarn", "Sariel", "Tirolas", "Galira", "Varos", "Daeniel", "Axidor", "Hiralia",
                 "Cyrwin", "Lothiel", "Zaphiel", "Nayra", "Ithior", "Amriel", "Elyon", "Jirwyn",
                 "Natinel", "Fiora", "Ruhiel"],
         "Halfling": ["Willow", "Benny", "Annie", "Tucker", "Marie", "Hobb", "Cora", "Gordie", "Rose",
                      "Ardo", "Alma", "Norbert", "Jennie", "Barvin", "Tilly", "Pike", "Lydia",
                      "Marlow", "Astrid", "Jasper"],
         "Half-orc": ["Vara", "Gralk", "Ranna", "Korv", "Zasha", "Hrogar", "Klara", "Tragan", "Brolga",
                      "Drago", "Yelena", "Krull", "Ulara", "Tulk", "Shiraal", "Wulf", "Ivara",
                      "Hirok", "Aja", "Zoraan"],
         "Goblin": ["Iggs", "Tark", "Nix", "Lenk", "Roke", "Fitz", "Tila", "Riggs", "Prim", "Zeb",
                    "Finn", "Borg", "Yark", "Deeg", "Nibs", "Brak", "Fink", "Rizzo", "Squib", "Grix"]}


def die():
    return randint(1,6)

def modifier(num):
    return (num - 10)//2

def fmt(num):
    s = str(num)
    return "+" + s if num >= 0 else s

class Character:
    def __init__(self):
        self.strength = die()+die()+die()
        self.str_mod = modifier(self.strength)

        self.dexterity = die()+die()+die()
        self.dex_mod = modifier(self.dexterity)

        self.constitution = die()+die()+die()
        self.con_mod = modifier(self.constitution)

        self.intelligence = die()+die()+die()
        self.int_mod = modifier(self.intelligence)

        self.wisdom = die()+die()+die()
        self.wis_mod = modifier(self.wisdom)

        self.charisma = die()+die()+die()
        self.cha_mod = modifier(self.charisma)

        self.ancestry = choice(ancestries)

        self.hit_points = max(1, self.con_mod)
        self.armor_class = 10 + self.dex_mod

        self.background = choice(backgrounds)
        self.alignment = choice(alignments)

        self.gear = []
        n = randint(1,4)
        for i in range(n):
            self.gear.append(choice(gear))
        self.gear_slots = (max(10, self.strength))

        self.talents = ["Beginner's Luck"]
        self.languages = ["Common"]
        if self.ancestry == "Dwarf":
            self.talents.append("Stout")
            self.languages.append("Dwarvish")
            self.hit_points += 2
        elif self.ancestry == "Elf":
            self.talents.append("Farsight")
            self.languages.append("Elvish")
            self.languages.append("Sylvan")
        elif self.ancestry == "Goblin":
            self.talents.append("Keen Senses")
            self.languages.append("Goblin")
        elif self.ancestry == "Half-orc":
            self.talents.append("Mighty")
            self.languages.append("Orcish")
        elif self.ancestry == "Halfling":
            self.talents.append("Stealthy")
        elif self.ancestry == "Human":
            self.talents.append("Ambitious")
            self.languages.append(choice(languages))

        self.name = choice(names[self.ancestry])


    def __repr__(self):
        dash_len = 76 - len(self.name)
        score = self.str_mod + self.dex_mod + self.con_mod + self.int_mod + self.wis_mod + self.cha_mod
        return (f"{self.name} {'=' * dash_len}\n" +
                f"STR: {self.strength} ({fmt(self.str_mod)}) " +
                f"DEX: {self.dexterity} ({fmt(self.dex_mod)}) " +
                f"CON: {self.constitution} ({fmt(self.con_mod)}) " +
                f"INT: {self.intelligence} ({fmt(self.int_mod)}) " +
                f"WIS: {self.wisdom} ({fmt(self.wis_mod)}) " +
                f"CHA: {self.charisma} ({fmt(self.cha_mod)})\n" +
                f"Level 0 {self.alignment} {self.ancestry} {self.background}\n" + 
                f"{self.hit_points} hp | AC {self.armor_class} | Score: {fmt(score)}\n" +
                f"Melee attack: {fmt(self.str_mod)} | Ranged attack: {fmt(self.dex_mod)}\n" + 
                f"Talents: {self.talents}\n" +
                f"Languages: {self.languages}\n" +
                f"Gear: {self.gear}\n" +
                f"Empty gear slots: {self.gear_slots - len(self.gear)}")


chars = [Character() for i in range(4)]
for c in chars:
    print(c)

