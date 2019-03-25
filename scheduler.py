import collections
import time
from ortools.sat.python import cp_model

from activity import ActivityGroup
from activity import case1, case2, case3, case4, case5, case6, case7, case8, case9, case10, case11


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
        # Extra variables to pass to solution printer
        self.extraVariables = {}


    class ScheduleTasksSolutionsPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, activityVars, objVar, extraVariables):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._activity_vars = activityVars
            self._obj_var = objVar
            self._solution_count = 0
            self._extra_variables = extraVariables

        # Override callback method to print solutions
        def OnSolutionCallback(self):
            self._solution_count += 1

            print('Obj Value: ', self.Value(self._obj_var), '\n')
            sortedActivities = sorted(self._activity_vars, key=lambda act: self.Value(act.start))
            for activityVar in sortedActivities:
                if self.Value(activityVar.isPresent):
                    print('At ' + str(self.Value(activityVar.start)) +
                        '\tfor: ' + str(activityVar.data.duration) +
                        '\t\tpriority: ' + str(activityVar.data.priority) +
                        '\t' + activityVar.data.name)
            print()
            for activityVar in sortedActivities:
                if not self.Value(activityVar.isPresent):
                    print('At ' + str(self.Value(activityVar.start)) +
                        '\tfor: ' + str(activityVar.data.duration) +
                        '\t\tpriority: ' + str(activityVar.data.priority) +
                        '\t' + activityVar.data.name + '\t\tNot fitted')
            print('**************************')

        def solutionCount(self):
            return self._solution_count


    def solve(self):
        # Creates solution printer callback to be passed to solver
        solutionPrinter = self.ScheduleTasksSolutionsPrinter(self.activityVars, self.objVar, self.extraVariables)
        # solve
        # status = self.solver.SearchForAllSolutions(self.model, solutionPrinter)

        start = time.time()
        status = self.solver.SolveWithSolutionCallback(self.model, solutionPrinter)
        end = time.time()

        # Print status and num of solutions
        print('Status = %s' % self.solver.StatusName(status))
        print('Number of solutions found: %i' % solutionPrinter.solutionCount())
        print('Time Taken: ', round(end-start, 3), 'seconds')

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
                    end = self.model.NewIntVar(groupStartTime, groupEndTime, 'end ' + activity.name)
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

        # Main objective function that penalizes unwanted behavior
        # OR-Tools library will minimize this function to find the optimal solution
        self.objVar = self.cpObjectiveFunction()
        self.model.Minimize(self.objVar)


    def cpObjectiveFunction(self):
        finalObjVar = 0

        # Adding penalty to activities for not being present
        activitiesNotPresentPenalty = self.getActivitiesNotPresentPenalty()
        finalObjVar += 100 * activitiesNotPresentPenalty

        # Adding penalty to activities which switch order
        activitiesOrderChangedPenalty = self.getActivitiesOrderChangedPenalty()
        finalObjVar += activitiesOrderChangedPenalty

        # Adding penalty for activities for not starting immediately after the next one
        activitiesNotPushedFrontPenalty = self.getActivitiesInBetweenGapsPenalty()
        finalObjVar += activitiesNotPushedFrontPenalty

        return finalObjVar

    def getActivitiesNotPresentPenalty(self):
        # Weighted penalties by priority (lower priority number == greater penalty)
        return sum([(int(120 / actVar.data.priority) * (1 - actVar.isPresent)) for actVar in self.activityVars])
        # Weighted penalties by priority (lower priority number == greater penalty) and duration
        # return sum([(int(120 / actVar.data.priority) * (1 - actVar.isPresent) * actVar.data.duration) for actVar in self.activityVars])

    def getActivitiesOrderChangedPenalty(self):
        nextElementBefore = []
        for i in range(0, len(self.activityVars) - 1):
            nextActStartDif = self.model.NewIntVar(-self.endScheduleTime, self.endScheduleTime, '')
            self.model.Add(nextActStartDif == self.activityVars[i].start - self.activityVars[i+1].start)
            nextActStartDifPosIndicator = self.getPositiveIndicatorForVariable(nextActStartDif, -self.endScheduleTime, self.endScheduleTime)
            nextActStartDifPosIndicatorIfActPresent = self.model.NewIntVar(0, 1, '')
            self.model.AddProdEquality(nextActStartDifPosIndicatorIfActPresent, [nextActStartDifPosIndicator, self.activityVars[i].isPresent])
            nextElementBefore.append(nextActStartDifPosIndicatorIfActPresent)
        return sum(nextElementBefore)

    def getPositiveIndicatorForVariable(self, var, varLb, varUb):
        ub = int(max(abs(varLb), abs(varUb)))
        varAbs = self.model.NewIntVar(0, ub, '')
        self.model.AddAbsEquality(varAbs, var)
        doubleOrNothing = self.model.NewIntVar(0, int(2 * ub), '')
        self.model.Add(doubleOrNothing == varAbs + var)
        doubleIndicator = self.model.NewIntVar(0, 2, '')
        avoidZero = self.model.NewIntVar(1, ub, '')
        self.model.AddMaxEquality(avoidZero, [varAbs, 1])
        self.model.AddDivisionEquality(doubleIndicator, doubleOrNothing, avoidZero)
        indicator = self.model.NewIntVar(0, 1, '')
        self.model.AddDivisionEquality(indicator, doubleIndicator, 2)
        return indicator

    # Get the sum of gaps between each activity intervals (to be used as penalty for objective function minimization)
    def getActivitiesInBetweenGapsPenalty(self):
        # actStartAndPreviousActEndDifs will contain lag time for each activity - free time between one activity and the next
        actStartAndPreviousActEndDifs = []
        # Each iteration of the loop determines the lag time for that activity
        # In Short - For each activity (actVar), the algorithm calculates the difference: 
        # d = (actVar.start - actVar2.end) where actVar2 is all the other activities
        # The lagtime will be equal to the minimum of all these positive differences
        # lagtime = min( d for all d > 0 )
        for actVar in self.activityVars:
            # Array that will contain all the difference d = (actVar - actVar2) if d > 0
            actStartAndAllActsEndDifs = []
            # Array that will contain bool indicating whether actVar2 comes after actVar
            # Sum of this array will be used as weight for lag time
            # This will push activities in reducing lag time with previous activity rather than the next activity
            act2AfterAct = []
            # Add start time to this array which will be the lag time if this is the first activity
            actStartAndAllActsEndDifs.append(actVar.start)
            for actVar2 in self.activityVars:
                if not actVar == actVar2:
                    # Define variable a with constraint a == -(actVar - actVar2)
                    act1StartAct2EndDif = self.model.NewIntVar(-self.endScheduleTime, self.endScheduleTime, '')
                    self.model.Add(act1StartAct2EndDif == actVar.start - actVar2.end)
                    # Also define (-a) necessary for subsequent steps
                    act2EndAct1StartDif = self.model.NewIntVar(-self.endScheduleTime, self.endScheduleTime, '')
                    self.model.Add(act2EndAct1StartDif == -act1StartAct2EndDif)
                    # Define bool variable b such that b = 1 iff -a > 0
                    # In other words, b = 1 iff a >= 0
                    # Or, more importantly b = 0 iff (actVar - actVar2) < 0
                    act1StartAct2EndDifNegIndicator = self.getPositiveIndicatorForVariable(act2EndAct1StartDif, -self.endScheduleTime, self.endScheduleTime)
                    act2AfterAct.append(act1StartAct2EndDifNegIndicator)
                    # Define variable m
                    #                   = 0 if (actVar - actVar2) >= 0
                    #                   = 2 * self.endScheduleTime if (actVar - actVar2) < 0
                    doubleEndScheduleOrNothing = self.model.NewIntVar(0, 2*self.endScheduleTime, '')
                    self.model.AddProdEquality(doubleEndScheduleOrNothing, [act1StartAct2EndDifNegIndicator, 2*self.endScheduleTime])
                    # Define variable n = (actVar - actVar2) + m
                    #                   = (actVar - actVar2)    if (actVar - actVar2) >= 0
                    #                   > self.endScheduleTime  if (actVar1 - actVar2) < 0
                    act1StartAct2EndDifIfPositive = self.model.NewIntVar(0, 2*self.endScheduleTime, '')
                    self.model.Add(act1StartAct2EndDifIfPositive == act1StartAct2EndDif + doubleEndScheduleOrNothing)
                    # Finally the variable we want:
                    # Define p = n * actVar.isPresent
                    #                   = (actVar - actVar2)    if (actVar - actVar2) >= 0 and actVar.isPresent == 1
                    #                   > self.endScheduleTime  if (actVar - actVar2) <  and actVar.isPresent == 1
                    #                   = 0                     if actVar.isPresent == 0
                    act1StartAct2EndDifIfPositiveAndPresent = self.model.NewIntVar(0, 2*self.endScheduleTime, '')
                    self.model.AddProdEquality(act1StartAct2EndDifIfPositiveAndPresent, [act1StartAct2EndDifIfPositiveAndPresent, actVar.isPresent])
                    # Append to array that will contain all p's to later minimize
                    actStartAndAllActsEndDifs.append(act1StartAct2EndDifIfPositive)
            # define variable s = minimum(all p and startTime )
            # In other words s = minimum of actVar - actVar2 such that (actVar - actVar2 > 0)
            # So s is the lag time for this activity actVar
            actStartAndPreviousActEndDif = self.model.NewIntVar(0, self.endScheduleTime, '')
            self.model.AddMinEquality(actStartAndPreviousActEndDif, actStartAndAllActsEndDifs)
            # We define the weight w = sum(act2 such that act2 > 0)
            actNumOfActsAfter = self.model.NewIntVar(0, len(self.activityVars), '')
            self.model.Add(actNumOfActsAfter == 1 + sum(act2AfterAct))
            # Multiply s and w to obtain weighted lag time, which is basically the penalty for this activity
            actStartAndPreviousActEndDifWeighted = self.model.NewIntVar(0, len(self.activityVars)*self.endScheduleTime, '')
            self.model.AddProdEquality(actStartAndPreviousActEndDifWeighted, [actStartAndPreviousActEndDif, actNumOfActsAfter])
            actStartAndPreviousActEndDifs.append(actStartAndPreviousActEndDifWeighted)
        return sum(actStartAndPreviousActEndDifs)


# For now, one time unit is 5 min so 12 units / hour
# Time period is 10 hours
scheduleTimeUnits = 120

scheduler = ScheduleTasks(scheduleTimeUnits)

scheduler.addActivities(case10)

scheduler.solve()



