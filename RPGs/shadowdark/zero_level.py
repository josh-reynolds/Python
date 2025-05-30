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

        self.melee_attack = self.str_mod
        self.melee_damage = 0              # STR does not add to damage per RAW
        self.ranged_attack = self.dex_mod
        self.ranged_damage = 0             # DEX does not add to damage per RAW

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
            self.ranged_attack += 1
        elif self.ancestry == "Goblin":
            self.talents.append("Keen Senses")
            self.languages.append("Goblin")
        elif self.ancestry == "Half-orc":
            self.talents.append("Mighty")
            self.languages.append("Orcish")
            self.melee_attack += 1
            self.melee_damage += 1
        elif self.ancestry == "Halfling":
            self.talents.append("Stealthy")
        elif self.ancestry == "Human":
            self.talents.append("Ambitious")
            self.languages.append(choice(languages))

        self.gear = []
        n = randint(1,4)
        for i in range(n):
            self.gear.append(choice(gear))
        self.gear_slots = (max(10, self.strength))

        self.attacks = []
        md = f"{fmt(self.melee_damage)}" if self.melee_damage > 0 else ""
        melee_damage_string = "1d4" + md + " damage"
        rd = f"{fmt(self.ranged_damage)}" if self.ranged_damage > 0 else ""
        ranged_damage_string = "1d4" + rd + " damage"

        for item in self.gear:
            if item == "Dagger":
                mod = max(self.melee_attack, self.ranged_attack)  # Finesse weapon
                self.attacks.append(f"Dagger (melee close range) {fmt(mod)} / " 
                                    + melee_damage_string)
                self.attacks.append(f"Dagger (thrown near range) {fmt(mod)} / " 
                                    + ranged_damage_string)
            elif item == "Shortbow & 5 arrows":
                self.attacks.append(f"Shortbow (shoot far range) {fmt(self.ranged_attack)} / " 
                                    + ranged_damage_string)
            elif item == "Club":
                self.attacks.append(f"Club (melee close range) {fmt(self.melee_attack)} / " 
                                    + melee_damage_string)

        self.name = choice(names[self.ancestry])

    def __repr__(self):
        dash_len = 76 - len(self.name)
        score = self.str_mod + self.dex_mod + self.con_mod + self.int_mod + self.wis_mod + self.cha_mod
        output = f"{self.name} {'=' * dash_len}\n"
        output += f"STR: {self.strength} ({fmt(self.str_mod)}) "
        output += f"DEX: {self.dexterity} ({fmt(self.dex_mod)}) "
        output += f"CON: {self.constitution} ({fmt(self.con_mod)}) "
        output += f"INT: {self.intelligence} ({fmt(self.int_mod)}) "
        output += f"WIS: {self.wisdom} ({fmt(self.wis_mod)}) "
        output += f"CHA: {self.charisma} ({fmt(self.cha_mod)})\n"
        output += f"Level 0 {self.alignment} {self.ancestry} {self.background}\n" 
        output += f"{self.hit_points} hp | AC {self.armor_class} | Score: {fmt(score)}\n"
        output += f"Melee attack: {fmt(self.melee_attack)} / {fmt(self.melee_damage)} | "
        output += f"Ranged attack: {fmt(self.ranged_attack)} / {fmt(self.ranged_damage)}\n"

        if len(self.attacks) > 0:
            for line in self.attacks:
                output += " - " + line + "\n"

        output += f"Talents: {self.talents}\n"
        output += f"Languages: {self.languages}\n"
        output += f"Gear: {self.gear}\n"
        output += f"Empty gear slots: {self.gear_slots - len(self.gear)}"

        return output


chars = [Character() for i in range(4)]
for c in chars:
    print(c)
    print("\n")

