import sys

class Jira_qry():
    def __init__(self, obj):
        self.lli = obj
        self.reset()
    
    def reset(self):
        self.storedQuery = ""
        self.storedProject = []
        self.project = []
        self.id = []
        self.priority = []
        self.type = []
        self.resolution = []
        self.status = []
        self.reporter = []
        self.assignee = []
        self.components = []
        self.affectsVersions = []
        self.fixVersions = []
        self.customField = None
        self.labels = []
        self.createdDate = ""
        self.createdDateTo = ""
        self.createdComp = ""
        self.update = []
        self.updateDate = []
        self.projectExcl = False
        self.priorityExcl = False
        self.typeExcl = False
        self.resolutionExcl = False
        self.statusExcl = False
        self.reporterExcl = False
        self.assigneeExcl = False
        self.componentsExcl = False
        self.affectsVersionsExcl = False
        self.fixVersionsExcl = False
        self.customFieldExcl = False
        self.labelsExcl = False

    def setProject(self, project):
        if (type(project).__name__ == "str"):
            self.project = [project]
        else:
            self.project = project

    def setId(self, id):
        if (type(id).__name__ == "str"):
            self.id = [id]
        else:
            self.id = id

    def setPriority(self, priority=[], exclude=False):
        self.priorityExcl = exclude
        if (type(priority).__name__ == "str"):
            self.priority = [priority]
        else:
            self.priority = priority

    def setType(self, ttype=[], exclude=False):
        self.typeExcl = exclude
        if (type(ttype).__name__ == "str"):
            self.type = [ttype]
        else:
            self.type = ttype

    def setStatus(self, status=[], exclude=False):
        self.statusExcl = exclude
        if (type(status).__name__ == "str"):
            self.status = [status]
        else:
            self.status = status
    
    def setResolution(self, resolution=[], exclude=False):
        self.resolutionExcl = exclude
        if (type(resolution).__name__ == "str"):
            self.resolution = [resolution]
        else:
            self.resolution = resolution

    def setAssignee(self, assignee=[], exclude=False):
        self.assigneeExcl = exclude
        if (type(assignee).__name__ == "str"):
            self.assignee = [assignee]
        else:
            self.assignee = assignee

    def setReporter(self, reporter=[], exclude=False):
        self.reporterExcl = exclude
        if (type(reporter).__name__ == "str"):
            self.reporter = [reporter]
        else:
            self.reporter = reporter

    def setComponents(self, components=[], exclude=False):
        self.componentsExcl = exclude
        if (type(components).__name__ == "str"):
            self.components = [components]
        else:
            self.components = components

    def setAffectsVersions(self, affectsVersions=[], exclude=False):
        self.affectsVersionsExcl = exclude
        if (type(affectsVersions).__name__ == "str"):
            self.affectsVersions = [affectsVersions]
        else:
            self.affectsVersions = affectsVersions

    def setFixVersions(self, fixVersions=[], exclude=False):
        self.fixVersionsExcl = exclude
        if (type(fixVersions).__name__ == "str"):
            self.fixVersions = [fixVersions]
        else:
            self.fixVersions = fixVersions

    def setCustomField(self, id, values=[], exclude=False):
        self.customFieldExcl = exclude
        if (type(values).__name__ == "str"):
            self.customField = (id, [values])
        else:
            self.customField = (id, values)

    def setLabels(self, values=[], exclude=False):
        self.labelsExcl = exclude
        if (type(values).__name__ == "str"):
            self.labels = [values]
        else:
            self.labels = values

    def setUpdate(self, updateDate=[]):
        if (type(updateDate).__name__ == "str"):
            self.updateDate = [updateDate]
        else:
            self.updateDate = updateDate

    def setCreationDateBetween(self, creation1, creation2):
        self.createdDate = creation1
        self.createdDateTo = creation2

    def setCreationDate(self, creation, comparison="="):
        self.createdDate = creation
        self.createdComp = comparison

    def setLastUpdateDate(self, update=[]):
        if (type(update).__name__ == "str"):
            self.update = [update]
        else:
            self.update = update

    def setAffectedLike(self, affected):
        self.affectedLike = affected

    def setFixLike(self, fix):
        self.fixLike = fix
    
    # EXTENDED OPTIONS
    # project = NAVKIT AND key in ("NAVKIT-5172", "NAVKIT-5145")
    # project = NAVKIT AND labels in ("triaged")
    # project = NAVKIT AND (summary ~ "cam AND speed" OR description ~ "cam AND speed")

    def getProjectQuery(self):
        return self.project

    def getIdQuery(self):
        return self.id

#    def getCustomFieldQuery(self):
#        return self.customField

    def getComponentsQuery(self):
        return self.components

    def getCreationDateQuery(self):
        return self.creation

    def getLastUpdateDateQuery(self):
        return self.update

    def getPriorityQuery(self):
        return self.priority

    def getTypeQuery(self):
        return self.type

    def getStatusQuery(self):
        return self.status

    def getResolutionQuery(self):
        return self.resolution

    def getAssigneeQuery(self):
        return self.assignee

    def getReporterQuery(self):
        return self.reporter

    def getAffectsVersionsQuery(self):
        return self.affectsVersions

    def getFixVersionsQuery(self):
        return self.fixVersions

    def getClauseCreationDate(self):
        res = ""
        if (self.createdDate):
            if (self.createdDateTo):
                res += " AND (createdDate >= '" + self.createdDate + "' AND createdDate <= '" + self.createdDateTo + "')"
            else:
                res += " AND createdDate" + self.createdComp + "'" + self.createdDate + "'"
        return res
    
    def getClauseCustomField(self):
        res = ""
        if (self.customField is not None):
            res += " AND '" + self.customField[0] + "'"
            if (self.customFieldExcl):
                res += " not"
            res += " in ('"
            l = len(self.customField[1])
            for i in range(l):
                res += self.customField[1][i]
                if (i != (l - 1)):
                    res += "','"
            res += "')"
        return res
    
    def getClause(self, id):
        res = ""
        exec "list = self." + id
        if (list):
            if (id != "project"):
                res += " AND "
            if (id == "affectsVersions"):
                res += "affectedVersion"
            elif (id in ["components","fixVersions"]):
                res += id[:-1]
            else:
                res += id
            exec "excl = self." + id + "Excl"
            if (excl):
                res += " not"
            res += " in ("
            l = len(list)
            for i in range(l):
                res += "\"" + list[i] + "\""
                if (i != (l - 1)):
                    res += ","
            res += ")"
        return res

    def checkProjets(self):
        if (not self.project):
            self.lli.log("PROJECT(S) NOT SET", True)
            sys.exit()
    
    def getStoredQuery(self):
        return self.storedQuery
    
    def setStoredQuery(self, query):
        self.storedQuery = query
    
    def getQuery(self, key):
        self.checkProjets()
        query = ""
        for item in ["project","type","assignee","resolution","status","priority","components","affectsVersions","fixVersions","updateDate","labels"]:
            query += self.getClause(item)
        query += self.getClauseCustomField()
        query += self.getClauseCreationDate()
        if (key):
            query += " AND key > " + key
        return query
