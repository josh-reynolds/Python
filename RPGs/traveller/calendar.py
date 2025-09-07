class Calendar:
    def __init__(self):
        self.current_date = ImperialDate(1,1105)
        self.observers = []

    @property
    def day(self):
        return self.current_date.day

    @day.setter
    def day(self, value):
        self.current_date.day = value
        if self.current_date.day >= 366:
            self.current_date.day = self.day - 365
            self.year += 1
        for observer in self.observers:
            observer.notify(self.current_date)

    @property
    def year(self):
        return self.current_date.year

    @year.setter
    def year(self, value):
        self.current_date.year = value
        for observer in self.observers:
            observer.notify(self.current_date)

    #def plus_day(self):
        #self.day += 1

    def plus_week(self):
        self.day += 7

    # For longer intervals, we will need to make sure
    # repeating events execute multiple times to catch up

    #def plus_month(self):
        #self.day += 28

    #def plus_year(self):
        #self.year += 1

    def __repr__(self):
        return f"{self.current_date}"

    def add_observer(self, observer):
        self.observers.append(observer)

class ImperialDate:
    def __init__(self, day, year):
        self.day = day
        self.year = year
        if self.day > 365:
            self.day -= 365
            self.year += 1

    def __repr__(self):
        return f"{self.day:03.0f}-{self.year}"

    def __eq__(self, other):
        return self.day == other.day and self.year == other.year

    def __gt__(self, other):
        return self.year > other.year or (self.day > other.day and
                                          self.year == other.year)

    def __ge__(self, other):
        return self == other or self > other

    def __sub__(self, other):
        return self.day - other.day

    def copy(self):
        return ImperialDate(self.day, self.year)

# We'll use the standard Imperial calendar, though that didn't
# yet exist in Traveller '77
# year is 365 consecutively numbered days
# date displayed as DDD-YYYY
# seven day weeks and four week months are used to refer to
# lengths of time, but rarely to establish dates
# (of course fun math, 7 * 4 * 12 = 336, so we are missing
# 29 days - but since week/month are really just durations
# it shouldn't matter)

# right now we only have refreshing the cargo depot weekly as an
# event, but there will be more:
#    * monthly loan payment
#    * annual maintenance
#    * monthly crew salaries
#    * daily berthing fees for extended stays
# other operational costs might better be handled as resource modeling:
#    * fuel
#    * life support

# also need to advance the calendar while in-system
# RAW says that ships typically take two trips per month:
# each jump is one week, and they spend a week buying & selling
# cargo, finding passengers, and on shore leave

# two approaches:
#    * give each action a cost in days
#    * advance the calendar only on jump and liftoff (the latter
#        perhaps with a message like 'you spent a week on Yorbund')

# for the former, does it add up to about a week? and do we want the
# player to be fiddling with time as well as money and space?
#    * to/from jump point - 1 day each
#    * to/from orbit - no time, don't want to privilege highport
#    * buy cargo (and load into ship) - 1 day
#    * sell cargo (and load into ship) - 1 day
#    * find passengers (and embark) - 1 day
#    * find freight (and load into ship) - 1 day
#    * listing hold/depot contents - no time
#    * refuelling - no time at port, 1 day to skim 
#    * recharging life support?
#    * financial transactions - no time
#
# easily 6-7 days if the player does all activities
# but if they want to go fast, jump in, skim fuel, jump out - just
# one day? or even no delay if they have reserve fuel.
