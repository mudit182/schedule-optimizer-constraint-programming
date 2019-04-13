from input_interfaces import createInputShell, ScheduleTime, BufferTime, Activity, ActivityGroup


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
        # Activity('A', 16, startTime=30, priority=1),
        Activity('B', 5, priority=2),
        Activity('C', 10, groupName='email', priority=1),
        Activity('D', 5, groupName='interview'),
        Activity('Z', 10, startTime=70, priority=1)
    ],
    'activity-groups': [
        ActivityGroup('email', 40, 60),
        ActivityGroup('interview', 40, 80)
    ],
    'disturbance-marked-times': []
}



# In case of conflicting activities, only 1 gets scheduled
case1 = createInputShell()
case1['activities'] = [
    Activity('A', 10, startTime=30),
    Activity('B', 5, startTime=30)
]


# In case of conflicting activities times, events with higher priority get scheduled
# Start time fixed
case2 = createInputShell()
case2['activities'] = [
    Activity('A', 10, startTime=30, priority=3),
    Activity('B', 5, startTime=30, priority=1),
    Activity('C', 2, startTime=30, priority=2),
]



# In case of more activities than available time, events with higher priority get scheduled
# No Start time provided
case3 = createInputShell()
case3['activities'] = [
    Activity('A', 70, priority=3),
    Activity('B', 30, priority=1),
    Activity('C', 30, priority=2),
]



# Higher priority activities get scheduled over lower priority ones 
case4 = createInputShell()
case4['activities'] = [
    Activity('A', 10, priority=3),
    Activity('B', 30, priority=1),
    Activity('C', 20, priority=2),
    Activity('D', 50, priority=3),
    Activity('E', 5, priority=1),
    Activity('F', 10, priority=1),
    Activity('G', 15, priority=2),
    Activity('H', 25, priority=3),
    Activity('I', 20, priority=1)
]



# In case of priority 1 activities not being scheduled, no priority 2 or 3 activities are scheduled
case5 = createInputShell()
case5['activities'] = [
    Activity('A', 50, priority=1),
    Activity('B', 40, priority=1),
    Activity('C', 50, priority=1),
    Activity('D', 20, priority=2),
    Activity('E', 10, priority=2),
    Activity('F', 10, priority=3),
]




# In case of priority 2 activities not being scheduled, no priority 3 activities are scheduled
case6 = createInputShell()
case6['activities'] = [
    Activity('A', 10, priority=1),
    Activity('B', 20, priority=1),
    Activity('C', 50, priority=2),
    Activity('D', 60, priority=2),
    Activity('B', 70, priority=2),
    Activity('E', 10, priority=3),
]


# Only priority 2 activities are provided they are scheduled normally
case7 = createInputShell()
case7['activities'] = [
    Activity('A', 10, priority=2),
    Activity('B', 20, priority=2),
]



# Only priority 3 activities are provided they are scheduled normally
case7 = createInputShell()
case7['activities'] = [
    Activity('A', 10, priority=3),
    Activity('B', 20, priority=3),
]



# Only priority 1 and 3 activities are provided they are scheduled normally
case7 = createInputShell()
case7['activities'] = [
    Activity('A', 10, priority=1),
    Activity('B', 20, priority=3),
    Activity('C', 30, priority=3),
]



# Activities with groupName is scheduled inside group's alloted time
case8 = createInputShell()
case8['activities'] = [
    Activity('A', 10, groupName='email'),
    Activity('B', 5, groupName='email'),
]
case8['activity-groups'] = [
    ActivityGroup('email', 40, 60),
]



# Activities with groupName is scheduled inside group's alloted time
# Activities that cannot fit inside alloted group time are not scheduled
case9 = createInputShell()
case9['activities'] = [
    Activity('A', 10, groupName='email'),
    Activity('B', 5, groupName='email'),
    Activity('C', 20, groupName='email'),
]
case9['activity-groups'] = [
    ActivityGroup('email', 40, 60),
]



# Multiple groups and also activities without groups
# Activities with groupName is scheduled inside group's alloted time
# Activities that cannot fit inside alloted group time are not scheduled
case9 = createInputShell()
case9['activities'] = [
    Activity('A', 10, groupName='email'),
    Activity('B', 5, groupName='email'),
    Activity('C', 20, groupName='email'),
    Activity('D', 15, groupName='interview'),
    Activity('E', 15, groupName='interview'),
    Activity('F', 45, groupName='interview'),
    Activity('G', 5),
    Activity('H', 15),
]
case9['activity-groups'] = [
    ActivityGroup('email', 40, 60),
    ActivityGroup('interview', 50, 90),
]


