
def createInputShell():
    return {
    'schedule-time': [
        ScheduleTime(0, 120)
    ],
    'buffer-times': [],
    'activity-groups': [],
    'activities' : [],
    'disturbance-marked-times': []
}


class ScheduleTime:
    def __init__ (self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime


class BufferTime:
    def __init__ (self, duration, startTime=None):
        self.name = 'Buffer'
        self.duration = duration
        self.startTime = startTime
        self.priority = 1


class Activity:
    def __init__(self, name, duration, startTime=None, groupName=None, priority=3, attentionRequired=2):
        self.name = name
        self.duration = duration
        self.startTime = startTime
        self.groupName = groupName
        self.priority = priority
        self.attentionRequired = attentionRequired


class ActivityGroup:
    def __init__(self, name, startTime, endTime):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime


# disturbance is a string either 'high' or 'low'
class DisturbanceMarkedTimes:
    def __init__(self, disturbance, startTime, endTime):
        self.disturbance = disturbance
        self.startTime = startTime
        self.endTime = endTime
