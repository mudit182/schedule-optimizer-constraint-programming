import collections
from ortools.sat.python import cp_model

from activity import ActivityGroup
# from activity import case1
from activity import case2



class ScheduleTasks:

    def __init__(self, timeUnits):
        # Fix period over which optimization must
        self.startScheduleTime = 0
        self.endScheduleTime = timeUnits
        # Create variables array
        self.activityVars = []
        self.objVar = None
        # Creates the model
        self.model = cp_model.CpModel()
        # Creates the solver
        self.solver = cp_model.CpSolver()


    class ScheduleTasksSolutionsPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, activityVars, objVar):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._activity_vars = activityVars
            self._obj_var = objVar
            self._solution_count = 0

        # Override callback method to print solutions
        def OnSolutionCallback(self):
            self._solution_count += 1
            
            print('Obj Value: ', self.Value(self._obj_var), '\n')
            sortedActivities = sorted(self._activity_vars, key=lambda act: self.Value(act.start))
            for activityVar in sortedActivities:
                if self.Value(activityVar.isPresent):
                    print('At ' + str(self.Value(activityVar.start)) +
                        '\t\t\tfor: ' + str(activityVar.data.duration) +
                        '\t\tpriority: ' + str(activityVar.data.priority) + '\t\tpresent: ' + str(self.Value(activityVar.isPresent)) +
                        '\t\t' + activityVar.data.name)
            print()
            for activityVar in sortedActivities:
                if not self.Value(activityVar.isPresent):
                    print('Not fitted:\t\t' + 'At: ' + str(self.Value(activityVar.start)) +
                        '\t\tpriority: ' + str(activityVar.data.priority) + '\t\tpresent: ' + str(self.Value(activityVar.isPresent)) +
                        '\t\t' + activityVar.data.name)
            print('**************************')

        def solutionCount(self):
            return self._solution_count


    def solve(self):
        # Creates solution printer callback to be passed to solver
        solutionPrinter = self.ScheduleTasksSolutionsPrinter(self.activityVars, self.objVar)
        # solve
        # status = self.solver.SearchForAllSolutions(self.model, solutionPrinter)
        status = self.solver.SolveWithSolutionCallback(self.model, solutionPrinter)

        # Print status and num of solutions
        print('Status = %s' % self.solver.StatusName(status))
        print('Number of solutions found: %i' % solutionPrinter.solutionCount())

    def addActivities(self, activities):
        # creating on the fly class to store activity variables
        ActivityVar = collections.namedtuple('ActivityVars', 'start, end, interval, isPresent, data')

        for _, activity in enumerate(activities):

            # Priority 1 - If Activity Start time is given
            if activity.startTime is not None:
                start = activity.startTime
                end = activity.startTime + activity.duration
            else:
                # Priority 2 - Put activity inside activity group's prefered slot
                if activity.group is not None:
                    groupStartTime, groupEndTime = ActivityGroup.start[activity.group], ActivityGroup.end[activity.group]
                    start = self.model.NewIntVar(groupStartTime, groupEndTime, 'start ' + activity.name)
                    end = self.model.NewIntVar(groupEndTime, groupEndTime, 'end ' + activity.name)
                # If no start time or group time, let activity float anywhere in the entire schedule time period
                else:
                    start = self.model.NewIntVar(self.startScheduleTime, self.endScheduleTime, 'start ' + activity.name)
                    end = self.model.NewIntVar(self.startScheduleTime, self.endScheduleTime, 'end ' + activity.name)

            isPresent = self.model.NewBoolVar('is present ' + activity.name)
            interval = self.model.NewOptionalIntervalVar(start, activity.duration, end, isPresent, 'interval ' + activity.name)

            activityVar = ActivityVar(start=start, end=end, interval=interval, isPresent=isPresent, data=activity)
            self.activityVars.append(activityVar)

        intervalVars = [activityVar.interval for activityVar in self.activityVars]
        self.model.AddNoOverlap(intervalVars)

        self.objVar = self.cpObjectiveFunction()
        self.model.Minimize(self.objVar)

        self.model.Add(self.activityVars[0].isPresent == 1)
        self.model.Add(self.activityVars[1].isPresent == 1)



    def cpObjectiveFunction(self):
        finalObjVar = 0

        # Adding penalty to activities for not being present
        activitiesNotPresentPenalty = sum([(self.getActivitiyNotPresentPenalty1(actVar)) for actVar in self.activityVars])
        finalObjVar += activitiesNotPresentPenalty

        # Adding penalty for activities for not being pushed towards the front
        activitiesNotPushedFrontPenalty = self.getActivitiesNotPushedFrontPenalty()
        # finalObjVar += activitiesNotPushedFrontPenalty

        # Adding penalty to activities which switch order
        activitiesOrderChangedPenalty = self.getActivitiesOrderChangedPenalty()
        # finalObjVar += activitiesOrderChangedPenalty

        return finalObjVar



    def getActivitiyNotPresentPenalty1(self, activityVar):
        # Weighted penalties by priority (lower priority number == greater penalty)
        return int(120 / activityVar.data.priority) * (activityVar.isPresent)

    def getActivitiyNotPresentPenalty2(self, activityVar):
        # Also weighted for duration (2 short duration activities should have equal added penalty as one long duration activity's penalty)
        return int(120 / activityVar.data.priority) * self.model.Negated(activityVar.isPresent) * activityVar.data.duration

    def getActivitiesNotPushedFrontPenalty(self):
        # The further the activity start time, the bigger the penalty
        return sum([actVar.start for actVar in self.activityVars])

    def getActivitiesOrderChangedPenalty(self):
        AreBeforeNeighbor = []
        for i in range(len(self.activityVars) - 1):
            isBeforeItsNeighbor = self.model.NewBoolVar(str(i) + ' before ' + str(i+1))
            self.model.Add(isBeforeItsNeighbor == self.activityVars[i].start < self.activityVars[i+1].start)
            AreBeforeNeighbor.append(isBeforeItsNeighbor)
        return sum([(isBeforeItsNeighbor)  for isBeforeItsNeighbor in AreBeforeNeighbor])





# For now, one time unit is 5 min so 12 units / hour
# Time period is 10 hours
scheduleTimeUnits = 120

scheduler = ScheduleTasks(scheduleTimeUnits)


# givenActivities = [
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

scheduler.addActivities(case2)

scheduler.solve()



