
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

# Case to test that activities are pushed to front and order is maintained
# Unless activity time is 20 less than previous one
case1 = [
    Activity('A', 20),
    Activity('B', 2),
    Activity('C', 25),
    Activity('D', 4)
]


# Case to test that activities with higher priority are scheduled over activities with lower priorities
# Notice that Activity D is selected instead of Activity F (both have same priority)
case2 = [
    Activity('A', 29, priority=5),
    Activity('B', 29, priority=2),
    Activity('C', 29, priority=5),
    Activity('D', 29, priority=3),
    Activity('E', 29, priority=1),
    Activity('F', 29, priority=3),
    Activity('G', 29, priority=2),
    Activity('H', 29, priority=4),
]



# Case to test grouped activities get scheduled in prefered slot 

case3 = [
    Activity('A', 7),
    Activity('B', 9, group=ActivityGroup.email),
    Activity('C', 3, group=ActivityGroup.email),
    Activity('D', 14),
    Activity('E', 9),
    Activity('F', 5, group=ActivityGroup.email),
]



# case = [
#     Activity('email client 1', 5, group=ActivityGroup.email),
#     Activity('email client 2', 2, group=ActivityGroup.email),
#     Activity('email friend', 1, group=ActivityGroup.email),
#     Activity('email brother', 15, group=ActivityGroup.email),
#     Activity('email sister', 25, group=ActivityGroup.email),
#     Activity('email mother', 15, group=ActivityGroup.email),
#     Activity('email employees', 4, group=ActivityGroup.email, startTime=100),

#     Activity('Work on project A', 10),
#     Activity('Work on project B', 20),
#     Activity('Work on project C', 4),
#     Activity('Work on project E', 3),
#     Activity('Work on project D', 6),

#     Activity('Call boss', 15, group=ActivityGroup.call),
#     Activity('Call mom', 30, group=ActivityGroup.call)
# ]






