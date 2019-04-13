import collections
import time
from ortools.sat.python import cp_model


class ScheduleTasks:

    def __init__(self, userData):
        self.userData = userData
        # Initialize OR-Tools model and solver
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # Set overall time interval inside of which all activities must be scheduled
        self.startScheduleTime = userData['schedule-time'][0].startTime
        self.endScheduleTime = userData['schedule-time'][0].endTime

        # Create container for activity variables
        self.activityVars = []
        # Container for activity variables which will be charged negative penalty for being present
        self.secondChoiceActivityVars = []
        # This variable will contain model's objective variable which will be used to find the optimal solution
        self.objectiveScoreVar = None
        # Container to store extra variables to pass to solution printer
        self.extraVariables = {}

        # Finally create the actual model variables and constraints
        self._addActivities()


    class ScheduleTasksSolutionsPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, activityVars, objScoreVar, extraVariables):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._activity_vars = activityVars
            self._obj_score_var = objScoreVar
            self._solution_count = 0
            self._extra_variables = extraVariables

        # Override callback method to print solutions
        def OnSolutionCallback(self):
            self._solution_count += 1

            for key, var in self._extra_variables.items():
                print(key, ': ', self.Value(var))

            print('Objective Score: ', self.Value(self._obj_score_var), '\n')
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
        solutionPrinter = self.ScheduleTasksSolutionsPrinter(self.activityVars, self.objectiveScoreVar, self.extraVariables)
        # solve
        # status = self.solver.SearchForAllSolutions(self.model, solutionPrinter)

        start = time.time()
        status = self.solver.SolveWithSolutionCallback(self.model, solutionPrinter)
        end = time.time()

        # Print status and num of solutions
        print('Status = %s' % self.solver.StatusName(status))
        print('Number of solutions found: %i' % solutionPrinter.solutionCount())
        print('Time Taken: ', round(end-start, 3), 'seconds')

    def _addActivities(self):
        # create group dictionary to easily access group by name
        activityGroupsByName = {}
        for group in self.userData['activity-groups']:
            activityGroupsByName[group.name] = group
        # Separate high and low disturbance times
        highDisturbanceTimes = [dis for dis in self.userData['disturbance-marked-times'] if dis.disturbance == 'high']
        lowDisturbanceTimes = [dis for dis in self.userData['disturbance-marked-times'] if dis.disturbance == 'low']

        # creating on the fly class to store activity variables
        ActivityVar = collections.namedtuple('ActivityVars', 'start, end, interval, isPresent, data')

        # Add buffer constraints
        buffers = self.userData['buffer-times']
        for buffer in buffers:
            self._addBuffer(buffer, ActivityVar)

        # Add activity data to OR-tools model
        activities = self.userData['activities']

        for activity in activities:
            # 1 - If Activity Start time is given
            if activity.startTime is not None:
                self._addActivityWithStartTime(activity, ActivityVar)
            else:
                self._addActivityWithoutStartTime(
                    activity,
                    activityGroupsByName,
                    highDisturbanceTimes,
                    lowDisturbanceTimes,
                    ActivityVar
                )

        # Ensure no activities overlap
        intervalVars = [activityVar.interval for activityVar in self.activityVars]
        self.model.AddNoOverlap(intervalVars)

        # Ensure no Priority n activities are scheduled if all Priority (n-1) activities are not scheduled
        self._addPriorityConstraint()

        # Main objective function that penalizes unwanted behavior
        # OR-Tools library will minimize this function to find the optimal solution
        self.objectiveScoreVar = self._cpObjectiveFunction()
        self.model.Minimize(self.objectiveScoreVar)

    def _addBuffer(self, buffer, ActivityVar):
        if buffer.startTime is not None:
            start = buffer.startTime
            end = buffer.startTime + buffer.duration
        else:
            start = self.model.NewIntVar(self.startScheduleTime, self.endScheduleTime, 'start ' + buffer.name)
            end = self.model.NewIntVar(self.startScheduleTime, self.endScheduleTime, 'end ' + buffer.name)

        isPresent = self.model.NewBoolVar('is present ' + buffer.name)
        interval = self.model.NewOptionalIntervalVar(start, buffer.duration, end, isPresent, 'interval ' + buffer.name)

        # Store newly created model variables for later access
        buffer.priority = 1
        bufferVar = ActivityVar(start=start, end=end, interval=interval, isPresent=isPresent, data=buffer)
        self.activityVars.append(bufferVar)

    def _addActivityWithStartTime(self, activity, ActivityVar):
        start = activity.startTime
        end = activity.startTime + activity.duration
        isPresent = self.model.NewBoolVar('is present ' + activity.name)
        # Optional interval for soft constraint
        interval = self.model.NewOptionalIntervalVar(start, activity.duration, end, isPresent, 'interval ' + activity.name)
        # Store newly created model variables for later access
        activityVar = ActivityVar(start=start, end=end, interval=interval, isPresent=isPresent, data=activity)
        self.activityVars.append(activityVar)

    def _addActivityWithoutStartTime(self, activity, activityGroupsByName, highDisturbanceTimes, lowDisturbanceTimes, ActivityVar):
        
        # Interval if group
        if activity.groupName is not None:
            group = activityGroupsByName[activity.groupName]
            start = self.model.NewIntVar(group.startTime, group.endTime, 'start ' + activity.name)
            end = self.model.NewIntVar(group.startTime, group.endTime, 'end ' + activity.name)
        # Interval if no group
        else:
            start = self.model.NewIntVar(self.startScheduleTime, self.endScheduleTime, 'start ' + activity.name)
            end = self.model.NewIntVar(self.startScheduleTime, self.endScheduleTime, 'end ' + activity.name)

        isPresent = self.model.NewBoolVar('is present ' + activity.name)
        # Optional interval for soft constraint
        interval = self.model.NewOptionalIntervalVar(start, activity.duration, end, isPresent, 'interval ' + activity.name)
        # Store newly created model variables for later access
        activityVar = ActivityVar(start=start, end=end, interval=interval, isPresent=isPresent, data=activity)
        self.activityVars.append(activityVar)
        if activity.groupName is None:
            self.secondChoiceActivityVars.append(activityVar)

        # Make more intervals using disturbed high/low times
        if not activity.attentionRequired == 2:
            # Array to use to ensure only one of these multiple intervals is fitted
            allIsPresents = [isPresent]
            if activity.attentionRequired == 1:
                for disTime in lowDisturbanceTimes:
                    start2 = self.model.NewIntVar(disTime.startTime, disTime.endTime, '')
                    end2 = self.model.NewIntVar(disTime.startTime, disTime.endTime, '')
                    isPresent2 = self.model.NewBoolVar('is present ' + activity.name)
                    # Optional interval for soft constraint
                    interval2 = self.model.NewOptionalIntervalVar(start2, activity.duration, end2, isPresent2, 'interval ' + activity.name)
                    # Store newly created model variables for later access
                    activityVar2 = ActivityVar(start=start2, end=end2, interval=interval2, isPresent=isPresent2, data=activity)
                    self.activityVars.append(activityVar2)
                    allIsPresents.append(isPresent2)
                    if activity.groupName is not None:
                        self.secondChoiceActivityVars.append(activityVar2)

            if activity.attentionRequired == 3:
                for disTime in highDisturbanceTimes:
                    start2 = self.model.NewIntVar(disTime.startTime, disTime.endTime, '')
                    end2 = self.model.NewIntVar(disTime.startTime, disTime.endTime, '')
                    isPresent2 = self.model.NewBoolVar('is present ' + activity.name)
                    # Optional interval for soft constraint
                    interval2 = self.model.NewOptionalIntervalVar(start2, activity.duration, end2, isPresent2, 'interval ' + activity.name)
                    # Store newly created model variables for later access
                    activityVar2 = ActivityVar(start=start2, end=end2, interval=interval2, isPresent=isPresent2, data=activity)
                    self.activityVars.append(activityVar2)
                    allIsPresents.append(isPresent2)
                    if activity.groupName is not None:
                        self.secondChoiceActivityVars.append(activityVar2)
            # Make sure at most only 1 of any of these intervals is fitted
            self.model.Add(sum(allIsPresents) <= 1)
    
    def _addPriorityConstraint(self):
        self.model.Add
        nbuffers = len([act for act in self.userData['buffer-times']])
        npriority1Activities = len([act for act in self.userData['activities'] if act.priority == 1])
        npriority2Activities = len([act for act in self.userData['activities'] if act.priority == 2])
        # npriority3Activities = len([act for act in self.userData['activities'] if act.priority == 3])

        priority1sPresent = self.model.NewIntVar(0, npriority1Activities, '')
        priority1sPresentSummed = sum([actVar.isPresent for actVar in self.activityVars if actVar.data.priority == 1])
        self.model.Add(priority1sPresent == priority1sPresentSummed)
        self.extraVariables['1present'] = priority1sPresentSummed

        # priority2sPresent = self.model.NewIntVar(0, npriority2Activities, '')
        # priority2sPresentSummed = sum([actVar.isPresent for actVar in self.activityVars if actVar.data.priority == 2])
        # self.model.Add(priority2sPresent == priority2sPresentSummed)
        # # priority2sPresent = sum([actVar.isPresent for actVar in self.activityVars if actVar.data.priority == 2])
        # # priority3sPresent = sum([actVar.isPresent for actVar in self.activityVars if actVar.data.priority == 3])

        # priority1sNotPresent = self.model.NewIntVar(0, npriority1Activities, '')
        # self.model.Add(priority1sNotPresent == nbuffers + npriority1Activities - priority1sPresent)
        # priority2sNotPresent = self.model.NewIntVar(0, npriority2Activities, '')
        # self.model.Add(priority2sNotPresent == npriority2Activities - priority2sPresent)

        # toBeZero12 = self.model.NewIntVar(0, 0, '')
        # self.model.AddProdEquality(toBeZero12, [priority1sNotPresent, priority2sPresent])
        # # self.model.Add(toBeZero12 == 0)

        # # toBeZero13 = self.model.NewIntVar(0, 0, '')
        # # self.model.AddProdEquality(toBeZero13, [priority1sNotPresent, priority3sPresent])
        # # self.model.Add(toBeZero13 == 0)

        # # toBeZero23 = self.model.NewIntVar(0, 0, '')
        # # self.model.AddProdEquality(toBeZero23, [priority2sNotPresent, priority3sPresent])
        # # self.model.Add(toBeZero23 == 0)

        

    def _cpObjectiveFunction(self):
        finalObjVar = 0

        # Adding penalty to activities for not being present
        activitiesNotPresentPenalty = self.getActivitiesNotPresentPenalty()
        finalObjVar += 1200 * activitiesNotPresentPenalty

        # # Adding penalty to activities for being fitted to lesser wanted options
        # activitiesFittedToSecondChoiceTimesPenalty = self.getActivitiesFittedToSecondChoiceTimesPenalty()
        # finalObjVar += 120 * activitiesFittedToSecondChoiceTimesPenalty

        # # Adding penalty to activities which switch order
        # activitiesOrderChangedPenalty = self.getActivitiesOrderChangedPenalty()
        # finalObjVar += activitiesOrderChangedPenalty

        # Adding penalty for activities for not starting immediately after the next one
        activitiesNotPushedFrontPenalty = self.getActivitiesInBetweenGapsPenalty()
        finalObjVar += activitiesNotPushedFrontPenalty

        return finalObjVar

    def getActivitiesNotPresentPenalty(self):
        # penaltyByPriority = {
        #     1: 14400,
        #     2: 120,
        #     3: 1
        # }
        # # Weighted penalties by priority (lower priority number == greater penalty)
        # return sum(
        #     [(int(penaltyByPriority[int(actVar.data.priority)]) * (1 - actVar.isPresent))
        #                 for actVar in self.activityVars]
        # )
        return sum( [(1 - actVar.isPresent) for actVar in self.activityVars] )

    def getActivitiesFittedToSecondChoiceTimesPenalty(self):
        return sum([act.isPresent for act in self.secondChoiceActivityVars])


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




