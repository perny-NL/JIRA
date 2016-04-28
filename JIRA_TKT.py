import JIRA_LLI

ISSUE_CLASS = False

if (ISSUE_CLASS):
    def filterIssueCustomDetails(item):
        res = {}
        for i in range(len(item)):
            values = []
            for j in range(len(item[i]["values"])):
                values.append(item[i]["values"][j])
            res[item[i]["customfieldId"]] = values
        return res

    def filterIssueDetails(item):
        res = []
        for i in range(len(item)):
            res.append(item[i]["id"])
        return res

    class Issue():
        def __init__(self, key, lli=None):
            if (lli is None):
                lli = JIRA_LLI.Jira_lli()
                lli.connect()
            self.fields = {}
            issue = lli.getIssue(key)
            self.retrieved = lli.getStoredServerTime()
            if (issue):
                self.fields = self.translateIssue(issue)

        def get(self, item):
            if (item in self.fields):
                return self.fields[item]
            else:
                self.lli.log("ERROR: '" + item + "' is not a valid field!")
                return ""
        
        def getFields(self):
            return self.fields

        def getLastUpdate(self):
            return self.retrieved

        def getCustomFields(self, id=""):
            if (id):
                if (id in self.getCustomFields().keys()):
                    return self.get("customFieldValues")[id]
                else:
                    self.lli.log("ERROR: '" + id + "' is not a valid custom field!")
                    return []
            else:
                return self.get("customFieldValues").keys()

        def isValid(self):
            if (self.getFields()):
                return True
            else:
                return False

        def translateIssue(self, issue):
            priority = issue["priority"]
            if (priority is None):
                priority = "6"
            res = {    "summary":issue["summary"].encode("utf-8"),
                    "priority":priority,
                    "customFieldValues":filterIssueCustomDetails(issue["customFieldValues"]) }
            for i in ["description","type","assignee","status","resolution","project","reporter","created","updated","key"]:
                res[i] = issue[i]
            for i in ["components","fixVersions","affectsVersions"]:
                res[i] = filterIssueDetails(issue[i])
            return res



class Jira_tkt():
    def __init__(self, obj):
        self.lli = obj
        self.issues_list = {}
        self.movedIssues = {}
        self.resetLists()
    
    def resetLists(self):
        self.customFields = {}
        self.issues_retrieved = []
        self.resetUpdatedList()

    def resetUpdatedList(self):
        self.issues_updated = {}

    def getIssue(self, key, force):
        if (key in self.movedIssues):
            return self.getIssue(self.movedIssues[key], force)
        if (force or (not self.exists(key))):
            if (ISSUE_CLASS):
                issue = Issue(key)
                fields = issue.getFields()
                self.customFields.update(issue.getCustomFields().keys())
            else:
                issue, moved = self.lli.getIssue(key)
                if (moved):
                    self.movedIssues[key] = moved
                    self.lli.log("Issue '" + key + "' has been moved to '" + moved + "'", True)
                    return self.getIssue(moved, force)
                if (not issue):
                    fields = {}
                    self.lli.log("This issue ('" + key + "') does not exist or you don't have permission to view it", True)
                else:
                    fields = self.translateIssue(issue)
            self.issues_list[key] = fields
        return self.issues_list[key]

    def issueExists(self, key, force=False):
        return (self.getIssue(key, force) != {})

    def setAllFields(self, key):
        None
#        issue = self.lli.getIssue(key)
#        print issue
#        print self.issues_list[key]
#        self.issues_list[key][field] = value

    def setField(self, key, field, value):
        if (key not in self.issues_list):
            return
        if (field[:12] == "customfield_"):
            res = self.issues_list[key]["customFieldValues"]
            for k in res:
                if (k == field):
                    res[k] = [value]
            self.issues_list[key]["customFieldValues"] = res
        elif (field in ["affectsVersions", "fixVersions", "components"]):
            self.issues_list[key][field] = value
        else:
            self.issues_list[key][field] = str(value)
    
    def exists(self, key, where=""):
        if (not where):
            return True if (key in self.issues_list) else False
        elif (where == "retrieved"):
            return True if (key in self.issues_retrieved) else False
        else:
            return True if (key in self.issues_updated) else False
    
    def addRetrievedIssues(self, issues, project=False):
        res = {}
        self.resetLists()
        for i in range(len(issues)):
            key = issues[i]["key"]
            self.issues_list[key] = self.translateIssue(issues[i])
            self.issues_retrieved.append(key)
            if (project):
                res[self.issues_list[key]["project"]] = ""
        if (project):
            return res.keys()

    def addUpdatedIssue(self, key, issue, diff):
        self.issues_list[key] = issue
        self.issues_updated[key] = diff

    def addRetrievedIssueAfterUpdated(self, key, remove=False):
        if (remove):
            self.lli.log("REMOVING: " + key)
            self.issues_retrieved.remove(key)
        else:
            self.lli.log("ADDING: " + key)
            self.issues_retrieved.append(key)

    def getAllIssues(self):
        return self.issues_list
    
    def getIssuesRetrieved(self, update=False):
        if (update):
            return sorted(self.issues_updated.keys(), key=lambda issue:int(issue[issue.index("-")+1:]), reverse=True)
        else:
            return sorted(self.issues_retrieved, key=lambda issue:int(issue[issue.index("-")+1:]), reverse=True)
    
    def getNumIssuesUpdated(self):
        count = 0
        for key in self.issues_updated.keys():
            if (key in self.issues_retrieved):
                count += 1
        return len(self.issues_updated), count
    
    def getIssuesUpdated(self):
        return self.issues_updated
    
    def lastUpdate(self, key=""):
        if (not key):
            return self.lli.getStoredServerTime()
        elif (not self.exists(key)):
            return self.lli.getServerTime()
        else:
            issue = self.issues_list[key]
            return issue["retrieved"]
    
    def getCustomFields(self):
        return self.customFields
    
    def addCustomFieldsValues(self, item):
        id = item["customfieldId"]
        val = item["values"]
        if (id in self.customFields):
            temp = self.customFields[id][:]
        else:
            temp = []
        for v in val:
            if (v not in temp):
                temp.append(v.encode("ascii", "replace"))
        self.customFields[id] = temp
        return temp
    
    def listIssueCustomDetails(self, items):
        res = {}
        for item in items:
            val = self.addCustomFieldsValues(item)
            res[item["customfieldId"]] = item["values"] # val
        return res

    def listIssueDetails(self, item):
        res = []
        for i in item:
            res.append(str((i["id"]).encode("utf-8")))
        return res

    def __Unicode2Ascii(self, value):
        return unicode(value.encode("utf-8"), "utf-8")
    
    def __None2EmptyString(self, value, default=""):
        return default if (value is None) else value
    
    def translateIssue(self, issue):
        summary = self.__Unicode2Ascii(issue["summary"])
        assignee = self.__None2EmptyString(issue["assignee"], "None")
        resolution = self.__None2EmptyString(issue["resolution"])
        priority = self.__None2EmptyString(issue["priority"], "0")
        description = self.__Unicode2Ascii(self.__None2EmptyString(issue["description"]))
        return {
            "summary":summary,
            "priority":priority,
            "assignee":assignee,
            "resolution":resolution,
            "description":description,
            "retrieved":self.lastUpdate(),
            "key":issue["key"],
            "type":issue["type"],
            "status":issue["status"],
            "project":issue["project"],
            "created":issue["created"],
            "updated":issue["updated"],
            "reporter":issue["reporter"],
            "components":self.listIssueDetails(issue["components"]),
            "fixVersions":self.listIssueDetails(issue["fixVersions"]),
            "affectsVersions":self.listIssueDetails(issue["affectsVersions"]),
            "customFieldValues":self.listIssueCustomDetails(issue["customFieldValues"])
#            "id":issue["id"],
#            "votes":issue["votes"],
#            "duedate":issue["duedate"],
#            "environment":issue["environment"],
#            "attachmentNames":self.listIssueDetails(issue["attachmentNames"])
        }
