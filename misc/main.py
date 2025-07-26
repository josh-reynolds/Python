import datetime

class Items:
    def __init__(self):
        self.name = ""
        self.section = ""
        self.quantity = 0

class Recipe:
    def __init__(self):
        self.name = ""
        self.ingredients = []

class ShoppingList:
    def __init__(self):
        self.items = []
        self.meal_plan = []
        self.date = datetime.date.today()

    def __repr__(self):
        result = f"{self.date.month}/{self.date.day}/{self.date.year}"
        result += f"\n{self.meal_plan}"
        result += f"\n{self.items}"
        return result

    def add_item(self, item):
        self.items.append(item)

    def add_meal(self, meal):
        self.meal_plan.append(meal)

sl = ShoppingList()
sl.add_meal("Lasagna")
sl.add_item("Milk")
print(sl)

# ----------------------------------------------------
# use cases:
#
# add items to list
#  - item database includes section data
# add recipes to list
#  - recipe database includes ingredient data
# adding new recipe/ingredient to list populates databases
# gather ingredient list for recipes on list
# gather par list
#  - par list built from saved history
# print list
# save list
# query saved lists for recipe frequency
# query saved lists for ingredient frequency

# workflow:
#  - start a new list
#  - automatically tagged with current date
#  - add recipes to meal plan
#  - if recipe in database, ingredients added to review list
#  - if recipe not in database, user inputs ingredients, then added to review list
#  - user presented with list of par + recipe items to review
#  - user can push review items to list, or exclude
#  - user can also directly add ingredients (with quantities)
#  - user can adjust quantity of items on the list
#  - if ingredient not in database, user adds section information
#  - on completion, user can print and/or save list
#  - backlog of previous lists works as history database
#  - can have reports showing most frequent recipes, etc.
#  - history data also informs par calculations
