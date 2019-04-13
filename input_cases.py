from input_interfaces import ScheduleTime, BufferTime, Activity, ActivityGroup


# Activities to test model with

case = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'buffer-times': [
        BufferTime(12),
        BufferTime(20, 10)
    ],
    'activities' : [
        Activity('A', 16),
        Activity('B', 5),
        Activity('C', 10),
        Activity('Z', 10, startTime=70)
    ],
    'activity-groups': [],
    'disturbance-marked-times': []
}

# Case1 to Case6 - Test objective function's individual components
# Each case forces a single penalty component to produce a penalty

# Activity 'C' won't be fitted
# Expected objective score = (120 / 5) * 100 = 2400
case1 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'buffer-times': [],
    'activities' : [
        Activity('A', 50),
        Activity('B', 40),
        Activity('C', 90)
    ],
    'activity-groups': []
}

# Activity 'C' won't be fitted
# Expected objective score = (120 / 3) * 100 = 4000
case2 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities' : [
        Activity('A', 50, priority=3),
        Activity('B', 40, priority=3),
        Activity('C', 90, priority=3)
    ]
}

# Activities order will be changed : 
# 'B' will not be followed by 'C'
# Expected objective score = 1
case3 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities' : [
        Activity('A', 5, priority=3),
        Activity('B', 4, priority=3),
        Activity('C', 3, priority=3, startTime=5)
    ]
}

# Activities order will be changed :
# 'A' will not be followed by 'B'
# 'B' will not be followed by 'C'
# Expected objective score = 2
case4 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities' : [
        Activity('A', 10, priority=3),
        Activity('B', 5, priority=3, startTime=30),
        Activity('C', 30, priority=3, startTime=0),
    ]
}

# There will be a time gap of 10 min after A ends and B starts
# Expected objective score = (num_of_activities_after_B + 1) * (lag time of B) = 1 * 10 = 10
case5 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities' : [
        Activity('A', 10),
        Activity('B', 5, startTime=20)
    ]
}

# There will be a time gap of 10 min after A ends and B starts
# However, unlike case 5 there is 1 activity after B
# Expected objective score = (num_of_activities_after_B + 1) * (lag time of B) = 2 * 10 = 20
case6 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities' : [
        Activity('A', 10),
        Activity('B', 5, startTime=20),
        Activity('C', 15, startTime=25)
    ]
}

# There is 10 min lag time for activity A, activity B, and activity C
# Penalty for activity A = (num_of_activities_after_A + 1) * (lag time of A)=  3 * 10 = 30
# Penalty for activity B = (num_of_activities_after_B + 1) * (lag time of B) = 2 * 10 = 20
# Penalty for activity A = (num_of_activities_after_C + 1) * (lag time of C) = 1 * 10 = 10
# Expected objective score = 60
case7 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities' : [
        Activity('A', 10, startTime=10),
        Activity('B', 10, startTime=30),
        Activity('C', 10, startTime=50),
    ]
}

# Case to test that activities are pushed to front and order is maintained
# if no startTime or group is specified
case8 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'activities': [
        Activity('A', 15),
        Activity('B', 3),
        Activity('C', 20, priority=1),
        Activity('D', 7, priority=3),
        Activity('E', 10)
    ]
}



# Case to test that activities with higher priority are scheduled over activities with lower priorities
# Notice that Activity D is scheduled instead of Activity F 
# (both D and F have same priority and duration but D is defined before)
case9 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],

    'activity-groups': [],

    'activities': [
        Activity('A', 29, priority=2),
        Activity('B', 29, priority=2),
        Activity('C', 29, priority=1),
        Activity('D', 29, priority=3),
        Activity('E', 29, priority=1),
        Activity('F', 29, priority=3),
        Activity('G', 29, priority=2),
        Activity('H', 29, priority=2)
    ]
}

case10 = {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],

    'activity-groups': [
        ActivityGroup('email', 30, 80)
    ],

    'activities': [
        Activity('A', 10),
        Activity('B', 9, groupName='email'),
        Activity('C', 3, groupName='email'),
        Activity('D', 14),
        Activity('E', 9),
        Activity('F', 5, groupName='email'),
    ]
}

case11 = {}











