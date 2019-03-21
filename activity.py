
class ActivityGroup:
    ActivityGroups = 2
    start = {}
    end = {}

    email = 'email'
    start[email] = 30
    end[email] = 80

    call = 'call'
    start[call] = 60
    end[call] = 80




class Activity:
    def __init__(self, name, duration, startTime=None, group=None, priority=5):
        self.name = name
        self.duration = duration
        self.startTime = startTime
        self.group = group
        self.priority = priority





# Activities to test model with

# Case to test activities of equal low priority, no groups defined
# Test for getActivitiyNotPresentPenalty1 and getActivitiyNotPresentPenalty2 to see the difference between the 2 penalty functions
case1 = [
    Activity('A', 39),
    Activity('B', 39),
    Activity('C', 39),
    Activity('D', 29),
    Activity('E', 29),
    Activity('F', 29),
    Activity('G', 29),
    Activity('H', 59),
    Activity('I', 59)
]


case2 = [
    Activity('A', 7),
    Activity('B', 9),
    Activity('C', 3),
    Activity('D', 14),
    Activity('E', 9),
    Activity('F', 5),
]






