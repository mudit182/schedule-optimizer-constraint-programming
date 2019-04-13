

# For scheduler class to be used as a component in the objective function

    # def getactivitiesNotPushedFrontPenalty(self):
    #     # # Push activities as forward as possible
    #     breakBeforeActivities = []
    #     for i, actVar in enumerate(self.activityVars):
    #         actStartEndDifs = []
    #         actStartEndDifs.append(actVar.start)
    #         for actVar2 in self.activityVars:
    #             startEndDif = actVar.start - actVar2.end
    #             actStartEndDifs.append(startEndDif)
    #         breakBeforeAct = self.model.NewIntVar(0, self.endScheduleTime, 'break before ' + str(i))
    #         breakBeforeActivities.append(breakBeforeAct)
    #     return sum(breakBeforeActivities)

    # def getactivitiesNotPushedBackPenalty(self):
    #     # Push activities as forward as possible
    #     breakBeforeActivities = []
    #     for i, actVar in enumerate(self.activityVars):
    #         actStartEndDifs = []
    #         actStartEndDifs.append(self.endScheduleTime - actVar.end)
    #         for actVar2 in self.activityVars:
    #             startEndDif = actVar.start - actVar2.end
    #             actStartEndDifs.append(startEndDif)
    #         breakBeforeAct = self.model.NewIntVar(0, self.endScheduleTime, 'break before ' + str(i))
    #         breakBeforeActivities.append(breakBeforeAct)
    #     return sum(breakBeforeActivities)

    # def getActivitiesStartTimeBackPenalty(self):
    #     # The further the activity start time, the bigger the penalty
    #     presentIntervalsStart = []
    #     for actVar in self.activityVars:
    #         isPresentStart = self.model.NewIntVar(0, self.endScheduleTime, '')
    #         self.model.AddProdEquality(isPresentStart, [actVar.start, actVar.isPresent])
    #         presentIntervalsStart.append(isPresentStart)
    #     return sum([start for start in presentIntervalsStart])



    # def getActivitiesNotPresentPenalty(self):
    #     penaltyByPriority = {
    #         1: 14400,
    #         2: 120,
    #         3: 1
    #     }
    #     # Weighted penalties by priority (lower priority number == greater penalty)
    #     return sum(
    #         [(int(penaltyByPriority[int(actVar.data.priority)]) * (1 - actVar.isPresent))
    #                     for actVar in self.activityVars]
    #     )