

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