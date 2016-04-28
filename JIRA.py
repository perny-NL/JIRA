import JIRA_QRY
import JIRA_LLI
#import JIRA_UPD
import JIRA_TKT
import JIRA_FLD
import JIRA_CLI
import JIRA_RST

import re
import os
import sys
import time
import getpass
from datetime import date, datetime, timedelta

def getSingleDifference(a, b, value):
    res = {}
    if (a[value] != b[value]):
        res[value] = (a[value], b[value])
    return res

def getDifference(a, b):
    res = {}
    res.update(getSingleDifference(a, b, "summary"))
    res.update(getSingleDifference(a, b, "description"))
    res.update(getSingleDifference(a, b, "priority"))
    res.update(getSingleDifference(a, b, "type"))
    res.update(getSingleDifference(a, b, "assignee"))
    res.update(getSingleDifference(a, b, "affectsVersions"))
    res.update(getSingleDifference(a, b, "components"))
    res.update(getSingleDifference(a, b, "status"))
    res.update(getSingleDifference(a, b, "resolution"))
    res.update(getSingleDifference(a, b, "fixVersions"))
    res.update(getSingleDifference(a, b, "project"))
    res.update(getSingleDifference(a, b, "reporter"))
    res.update(getSingleDifference(a, b, "created"))
#    res.update(getSingleDifference(a, b, "platform"))
#    res.update(getSingleDifference(a, b, "updated"))
##    res.update(getSingleDifference(a, b, "id"))
##    res.update(getSingleDifference(a, b, "attachmentNames"))
##    res.update(getSingleDifference(a, b, "duedate"))
##    res.update(getSingleDifference(a, b, "environment"))
##    res.update(getSingleDifference(a, b, "votes"))
    return res

def getTemplateId(func, name, value="name"):
    for k in func:
        if (func[k][value] == name):
            return k
    return ""

def getTemplateValue(func, k, value="name"):
    if (k in func):
        return str(func[k][value])
    else:
        return ""

class Jira:
    def __init__(self, account="", password=""):
        self.reset()
        self.projects = []
        self.lli = JIRA_LLI.Jira_lli(account, password)
        self.cli = JIRA_CLI.Jira_cli(self.lli.getAccount(), self.lli.getPassword())
        self.rst = JIRA_RST.Jira_rst(self.lli.getAccount(), self.lli.getPassword())
#        self.upd = JIRA_UPD.Jira_upd()
        self.qry = JIRA_QRY.Jira_qry(self.lli)
        self.tkt = JIRA_TKT.Jira_tkt(self.lli)
        self.fld = JIRA_FLD.Jira_fld(self.lli, self.cli, self.rst)
    
    def reset(self):
        self.users = {}
        self.projectId = {}
        self.roles = []
        self.custom_field = {}
    
    def setLogging(self, switch):
        self.lli.setLogging(switch)

    def log(self, message, show=False):
        self.lli.log(message, show)

    def setMaxIssuesNumber(self, num):
        self.lli.setMaxIssuesNumber(num)

    def getQuery(self, key=""):
        return self.qry.getQuery(key)

    def setQueryField(self, item, value):
        fun = item[0].capitalize() + item[1:]
        exec "self.qry.set" + fun + "(value)"
    
    def getQueryField(self, item):
        fun = item[0].capitalize() + item[1:]
        exec "ret = self.qry.get" + fun + "Query()"
        return ret
    
    def QUERY(self):
        return self.qry
    
    def resetQuery(self):
        self.qry.reset()
    
    def setProject(self, project):
        self.qry.setProject(project)
    
    def getServerTime(self):
        return self.lli.getStoredServerTime()

    def getServerTime2(self):
        return self.lli.getServerTime(True)

    def issueExists(self, key, force=False):
        return (self.tkt.issueExists(key, force))

    def getIssue(self, key, force=False):
        return self.tkt.getIssue(key, force)

    def showIssue(self, key):
        print self.lli.getIssue(key)

    def getAllIssues(self):
        return self.tkt.getAllIssues()
        
    def getIssuesRetrieved(self, update=False):
        return self.tkt.getIssuesRetrieved(update)

    def getNumIssuesRetrieved(self, update=False):
        return len(self.getIssuesRetrieved(update))

    def getIssuesUpdated(self):
        return self.tkt.getIssuesUpdated()

    def getNumIssuesUpdated(self):
        return self.tkt.getNumIssuesUpdated()

    def getProjectId(self, prj, forced=False):
        if (forced or (prj not in self.projectId)):
            self.projectId[prj] = self.lli.getProjectId(prj)
        return self.projectId[prj]
    
    def getRoles(self, forced=False):
        if (forced or (not self.roles)):
            self.roles = self.lli.getRoles()
        return self.roles
    
    def calculateAllUsers(self, prj, forced=False):
        if (forced or (prj not in self.users)):
            ProjectRoles = self.getRoles()
            for role in ProjectRoles:
                self.calculateUsersPerRole(prj, role, ["Observer"])
    
    def getUsers(self, prj):
        if (prj in self.users):
            return self.users[prj]
        else:
            return []
    
    def calculateUsersPerRole(self, prj, role, excl=[]):
#        projectId = self.lli.getProjectId(prj)
#        ProjectRoles = self.lli.getRoles()
#        for role in ProjectRoles:
        if (role["name"] not in excl):
            projectId = self.getProjectId(prj)
            actors = self.lli.getActors(role, projectId)
            if ("roleActors" in actors):
                for actor in actors["roleActors"]:
                    for user in actor["users"]:
                        self.getUser(user["name"], prj)
    
    def getProjects(self):
        return self.fld.getProjects()

    def getProjectKeyFromName(self, name):
        info = self.getProjects()
        for f in info.keys():
            if (info[f]["name"] == name):
                return str(info[f]["key"])
        return ""
    
    def getProjectName(self, id):
        info = self.getProjects()
        tmp = getTemplateValue(info, id)
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on ProjectName")
        return str(tmp)
    
    def getProjectKey(self, id):
        info = self.getProjects()
        tmp = getTemplateValue(info, id, "key")
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on ProjectKey")
        return str(tmp)

    def getFavouriteFilters(self):
        return self.fld.getFavouriteFilters()
    
    def getIssueCountForFilter(self, id):
        return self.fld.getIssueCountForFilter(id)
    
    def existsFilterCount(self, key):
        return self.fld.existsFilterCount(key)
    
    def getIssuesFromTextSearch(self, search):
        return self.lli.getIssuesFromTextSearch(search)

    def getIssuesFromTextSearchWithProject(self, prj, search, flag=0):
        return self.lli.getIssuesFromTextSearchWithProject(prj, search, flag)
    
    def getUser(self, account, prj="", **kwargs):
        if (prj):
            if (prj in self.users):
                if (account not in self.users[prj]):
                    self.users[prj].append(account)
            else:
                self.users[prj] = [account]
        return self.fld.getUser(account, **kwargs)
    
    def getEmail(self, account, prj=""):
        return self.getUser(account, prj)["email"]

    def getAssigneeId(self, name):
        return self.getUserAccount(name)
    
    def getAssigneeName(self, name):
        return self.getUser(name)["name"]
    
    def getUserName(self, account, prj="", **kwargs):
        return self.getUser(account, prj, **kwargs)["name"]

    def getUserAccount(self, name):
        if (name == "None"):
            return name
        info = self.fld.getAllUsers()
        for k in info.keys():
            if (info[k]["name"] == name):
                return k
        self.lli.log("Cannot find '" + name + "' in the users accounts")
        return ""

#    def getIssueId(self, key, force=False):
#        issue = self.getIssue(key, force)
#        return issue["id"]
    
    def getAssignee(self, key, encripted=False, force=False, **kwargs):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        if (encripted):
            return issue["assignee"]
        else:
            return self.getUserName(issue["assignee"], self.getProject(key, force), **kwargs)

    def getReporter(self, key, encripted=False, force=False, **kwargs):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        if (encripted):
            reporter = issue["reporter"]
            if (not reporter):
                return "Unknown"
            else:
                return reporter
        else:
            return "Unknown"
#        201-03-10: Changed this part to return "Unknown" when a user is not defined in Jira.
#                   The getUserName should be able to handle it but it fails and causes 
#                   the extraction process to stop.
#        if (encripted):
#            return issue["reporter"]
#        else:
#            return self.getUserName(issue["reporter"], self.getProject(key, force), **kwargs)

    def getProject(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        return issue["project"]
    
    def getSummary(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        return issue["summary"]

    def getDescription(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        return issue["description"]

    def getCreated(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        return str(issue["created"])

    def getUpdated(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        return str(issue["updated"])

    def getRetrieved(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        return issue["retrieved"]

    def getAssignees(self, prj):
        self.calculateAllUsers(prj)
        return self.getUsers(prj)
    
    def isReleaseVersion(self, version, project):
        tmp = self.getVersionsList(project)
        for i in tmp:
            if (tmp[i]["name"] == version):
                return tmp[i]["released"]
        self.lli.log("Version '" + version + "' not found!")
        return False
    
    def getVersionsList(self, project, released=False, force=False):
        return self.fld.getVersionsList(project, released, force)
    
    def getVersionsId(self, name, project, released=False, force=False):
        info = self.getVersionsList(project, released, force)
        if (type(name).__name__ == "str"):
            tmp = getTemplateId(info, name)
            if (not tmp):
                self.lli.log("name=" + name + " not present for Versions")
            return str(tmp)
        else:
            res = []
            for i in range(len(name)):
                tmp = getTemplateId(info, name[i])
                if (not tmp):
                    self.lli.log("name=" + name[i] + " not present for Versions")
                else:
                    res.append(str(tmp))
            return res

    def getAffectsVersionsId(self, name, project, released=False):
        return self.getVersionsId(name, project, released)

    def getFixVersionsId(self, name, project, released=False):
        return self.getVersionsId(name, project, released)

    def getVersionsName(self, id, project, released=False, force=False):
        info = self.getVersionsList(project, released, force)
        res = []
        for i in range(len(id)):
            tmp = getTemplateValue(info, id[i])
            if (not tmp):
                self.lli.log("key=" + str(id[i]) + " not present on VersionName")
            else:
                res.append(tmp)
        return res

    def getAffectsVersionsName(self, id, project, released=False):
        return self.getVersionsName(id, project, released)
    
    def getFixVersionsName(self, id, project, released=False):
        return self.getVersionsName(id, project, released)

    def getAffectsVersions(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        if (encripted):
            return issue["affectsVersions"]
        else:
            return self.getVersionsName(issue["affectsVersions"], self.getProject(key, force), force)
    
    def getFixVersions(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        if (encripted):
            return issue["fixVersions"]
        else:
            return self.getVersionsName(issue["fixVersions"], self.getProject(key, force), force)
    
    def getComponentsList(self, project, force=False):
        return self.fld.getComponentsList(project, force)
    
    def getComponentsId(self, name, project, force=False):
        info = self.getComponentsList(project, force)
        if (type(name).__name__ == "str"):
            tmp = getTemplateId(info, name)
            if (not tmp):
                self.lli.log("name=" + name + " not present for Components")
            return str(tmp)
        else:
            res = []
            for i in range(len(name)):
                tmp = getTemplateId(info, name[i])
                if (not tmp):
                    self.lli.log("name=" + name[i] + " not present for Components")
                else:
                    res.append(str(tmp))
            return res
    
    def getComponentsName(self, id, project, force=False):
        info = self.getComponentsList(project, force)
        res = []
        for i in range(len(id)):
            tmp = getTemplateValue(info, id[i])
            if (not tmp):
                self.lli.log("key=" + str(id[i]) + " not present on ComponentName")
            else:
                res.append(tmp)
        return res

    def getComponents(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        project = self.getProject(key, force)
        if (not issue):
            return []
        if (encripted):
            return issue["components"]
        else:
            return self.getComponentsName(issue["components"], project, force)
    
    def getAllTypesList(self, project, force=False):
        return self.fld.getCombinedTypesList(project, force)
    
    def getMinimalTypesList(self, project="", force=False):
        return self.fld.getMinimalTypesList(project, force)
    
    def getSubTypesList(self, project, force=False):
        return self.fld.getSubTypesList(project, force)
    
    def getTypesList(self, force=False):
        return self.fld.getTypesList(force)
    
    def getTypeId(self, name, project="", force=False):
        info = self.getAllTypesList(project, force)
        tmp = getTemplateId(info, name)
        if (not tmp):
            self.lli.log("name=" + name + " not present for Types")
        return str(tmp)
    
    def getTypeName(self, id, project="", force=False):
        info = self.getAllTypesList(project, force)
        tmp = getTemplateValue(info, id)
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on TypeName")
        return str(tmp)
    
    def getTypeIcon(self, id, project="", force=False):
        info = self.getAllTypesList(project, force)
        tmp = getTemplateValue(info, id, "icon")
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on TypeIcon")
        return str(tmp)

    def getType(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        if (encripted):
            return issue["type"]
        else:
            return self.getTypeName(issue["type"], self.getProject(key, force), force)
    
    def getPrioritiesList(self, force=False):
        return self.fld.getPrioritiesList(force)
    
    def getPriorityId(self, name, force=False):
        info = self.getPrioritiesList(force)
        tmp = getTemplateId(info, name)
        if (not tmp):
            self.lli.log("name=" + name + " not present for Priorities")
        return str(tmp)
    
    def getPriorityName(self, id, force=False):
        if (id == "0"):
            return "None"
        else:
            info = self.getPrioritiesList(force)
            tmp = getTemplateValue(info, id)
            if (not tmp):
                self.lli.log("key=" + str(id) + " not present on PriorityName")
            return str(tmp)
    
    def getPriorityIcon(self, id, force=False):
        info = self.getPrioritiesList(force)
        tmp = getTemplateValue(info, id, "icon")
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on PriorityIcon")
        return str(tmp)

    def getPriority(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        if (encripted):
            return issue["priority"]
        else:
            return self.getPriorityName(issue["priority"], force)
#            return self.getPriorityName(issue.get("priority"), force)
    
    def getStatusesList(self, force=False):
        return self.fld.getStatusesList(force)

    def getMinimalStatusesList(self, force=False):
        return self.fld.getMinimalStatusesList(force)

    def getStatusId(self, name, force=False):
        info = self.getStatusesList(force)
        tmp = getTemplateId(info, name)
        if (not tmp):
            self.lli.log("name=" + name + " not present for Statuses")
        return str(tmp)
    
    def getStatusName(self, id, force=False):
        info = self.getStatusesList(force)
        tmp = getTemplateValue(info, id)
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on StatusName")
        return str(tmp)
    
    def getStatusIcon(self, id, force=False):
        info = self.getStatusesList(force)
        tmp = getTemplateValue(info, id, "icon")
        if (not tmp):
            self.lli.log("key=" + str(id) + " not present on StatusIcon")
        return str(tmp)

    def getStatus(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        if (encripted):
            return issue["status"]
        else:
            return self.getStatusName(issue["status"], force)
    
    def getResolutionsList(self, force=False):
        return self.fld.getResolutionsList(force)
    
    def getResolutionId(self, name, force=False):
        if (name == "Unresolved"):
            return ""
        info = self.getResolutionsList(force)
        tmp = getTemplateId(info, name)
        if (not tmp):
            self.lli.log("name=" + name + " not present for Resolutions")
        return str(tmp)
    
    def getResolutionName(self, id, force=False):
        if (not id):
            return "Unresolved"
        else:
            info = self.getResolutionsList(force)
            tmp = getTemplateValue(info, id)
            if (not tmp):
                self.lli.log("key=" + str(id) + " not present on ResolutionName")
            return str(tmp)

    def getResolution(self, key, encripted=False, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return ""
        if (encripted):
            return "Unresolved" if (not issue["resolution"]) else issue["resolution"]
        else:
            return self.getResolutionName(issue["resolution"], force)

    def export(self, file, listOfIssue=[]):
        try:
            f = open(file, "w")
            f.write("Type,Priority,Key,Status,Resolution,Summary,Assignee,AffectsVersions,FixVersions,Components,Reporter,Created,Updated\n")
            issues = listOfIssue if (listOfIssue) else self.getIssuesRetrieved()
            for key in issues:
                line = self.getType(key) + ","
                line += self.getPriority(key) + ","
                line += key + ","
                line += self.getStatus(key) + ","
                line += self.getResolution(key) + ","
                line += self.getSummary(key).replace("\n"," ").replace(",",";").encode("ascii", "replace") + ","
                line += self.getAssignee(key).encode("ascii", "replace") + ","
                line += str(self.getAffectsVersions(key)).replace(",",";") + ","
                line += str(self.getFixVersions(key)).replace(",",";") + ","
                line += str(self.getComponents(key)).replace(",",";") + ","
                line += self.getReporter(key).encode("ascii", "replace") + ","
                line += self.getCreated(key) + ","
                line += self.getUpdated(key) + "\n"
                f.write(line)
            f.close()
            return len(issues)
        except:
            self.lli.log("Please, close file '" + file + "' and run export again", True)
        return -1

    def existsCustomFieldValues(self, value):
        for k, v in self.custom_field.iteritems():
            if (v == value):
                return k
        return None
    
    def setCustomFieldValuesList(self, items):
        for k, v in items.iteritems():
            if (k in self.custom_field):
                self.lli.log("Warning: substituting value '" + self.custom_field[k] + "' with '" + v + "' for custom field '" + k + "'")
            self.setCustomFieldValues(k, v)
    
    def setCustomFieldValues(self, id, value):
        self.custom_field[id] = value
    
    def getCustomFields(self):
        return self.tkt.getCustomFields()
    
    def getCustomFieldValues(self, key, field="", force=False):
        res = []
        issue = self.getIssue(key, force)
        if (issue):
            tmp = issue["customFieldValues"]
            if (field):
                fieldKey = self.existsCustomFieldValues(field)
                fieldId = field if (fieldKey is None) else fieldKey
                if (fieldId in tmp):
                    res = tmp[fieldId]
                else:
                    self.lli.log("Issue '" + key + "' doesn't have a custom field '" + field + "'")
            else:
                res = tmp.keys()
        return res
    
    def getLinksList(self):
        return ["Cloners","Duplicate","Dependency","Contains","Cause","Relates?","Relation"]
    
    def type2Show(self, type, direction):
        if (direction):
            match = {    "Cloners":"Cloned to","Duplicate":"Duplicates","Dependency":"Blocks","Contains":"Contains",
                        "Cause":"Causes","Relates?":"Maybe relates to","Relation":"Is related to"}
        else:
            match = {    "Cloners":"Is a clone of","Duplicate":"Is duplicated by","Dependency":"Depends on","Contains":"Is part of",
                        "Cause":"Is caused by","Relates?":"Is maybe related to","Relation":"Relates to"}
        return match[type]

    def getDependencies(self, key, force=False, **kwargs):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        return self.fld.getDependencies(key, force, **kwargs)

    def existsDependencies(self, key):
        return self.fld.existsDependencies(key)
    
    def getSubTasks(self, key, force=False):
        res = []
        info = self.getDependencies(key, force)
        for i in range(len(info)):
            if (info[i]["type"] == "jira_subtask_link"):
                res.append({"destination":info[i]["destination"], "direction":info[i]["direction"]})
        return res

    def getLinks(self, key, force=False):
        res = []
        info = self.getDependencies(key, force)
        for i in range(len(info)):
            if (info[i]["type"] != "jira_subtask_link"):
                res.append({"destination":info[i]["destination"], "type":info[i]["type"], "direction":info[i]["direction"]})
        return res

    def getLinksWithInfo(self, key, force=False):
        res = []
        links = self.getLinks(key, force)
        history = self.getHistory(key, force)
        for l in links:
            k = l["destination"]
            for h in sorted(history, reverse=True):
                for j in h["changes"]:
                    if ((j["name"] == "Link") and (j["values"][-len(k):] == k)):
                        res.append({"destination":k, "direction":l["direction"], "type":l["type"], 
                                    "when":h["when"], "executor":h["executor"]})
                        break
        self.lli.log(res)
    
    def setAssignee(self, key, assignee, interface="soap"):
        current = self.getAssignee(key)
        if (current == assignee):
            print "Assignee '" + self.getAssignee(key) + "' already present."
            return True
        if (interface == "soap"):
            self.updateIssue(key, "assignee", [assignee], True)
        elif (interface == "cli"):
            self.cli.updateAssignee(key, assignee)
        assignee_new = self.getAssignee(key, True)
        if (assignee != assignee_new):
            return False
        return True

    def addLabel(self, key, label, interface="soap"):
        labels = self.getLabels(key)
        if (label in labels):
            print label + " already present."
            return True
        labels.append(label)
        if (interface == "soap"):
            self.updateIssue(key, "labels", labels, True)
        elif (interface == "cli"):
            self.cli.updateLabels(key, labels)
        labels_new = self.getLabels(key, True)
        if (label not in labels_new):
            return False
        return True

    def removeLabel(self, key, label, interface="soap"):
        labels = self.getLabels(key)
        if (label not in labels):
            print label + " not present."
            return True
        labels.remove(label)
        if (interface == "soap"):
            self.updateIssue(key, "labels", labels, True)
        elif (interface == "cli"):
            self.cli.updateLabels(key, labels)
        labels_new = self.getLabels(key, True)
        if (label in labels_new):
            return False
        return True
    
    def existsLabels(self, key):
        return self.fld.existsLabels(key)
    
    def getComments(self, key, force=False, **kwargs):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        return self.fld.getComments(key, force, **kwargs)

    def getWorklogs(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        return self.fld.getWorklogs(key, force)

    def getAttachments(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        return self.fld.getAttachments(key, force)
    
    def getTransitionsInfo(self, key, force=False):
        first_action = timedelta(0)
        first_closure = timedelta(0)
        num_closures = 0 # only when is set to "Done"
        open_time = timedelta(0)
        close_time = timedelta(0)
        active_time = timedelta(0) # open, not "On Hold" or "Waiting for informations"
        last_close = timedelta(0)
        still_open = False
        trans = self.getTransitions(key, force)
        if (trans):
            if (len(trans) > 1):
                first_action += trans[1]["when"] - trans[0]["when"]
            if (self.getStatus(key) in ["Open", "Reopened", "In Progress"]):
                still_open = True
            last_open = trans[0]["when"]
            last_active = last_open
            flag = True
            flag_closed = True
            for item in trans:
                status = item["status"]
                if (status in ["Open", "Reopened", "In Progress"]):
                    if (flag):
                        open_time += item["when"] - last_open
                    else:
                        close_time += item["when"] - last_close
                    last_open = item["when"]
                    flag = True
                else:
                    if (status == "Done"):
                        num_closures += 1
                    if (flag_closed):
                        flag_closed = False
                        first_closure += item["when"] - trans[0]["when"]
                    if (status not in ["Waiting for information from user", "On Hold"]): # "In Testing"
                        active_time += item["when"] - last_active
                    last_active = item["when"]
                    if (flag):
                        open_time += item["when"] - last_open
                    else:
                        close_time += item["when"] - last_close
                    last_close = item["when"]
                    flag = False
            gap = datetime.today() - trans[-1]["when"]
            if (still_open):
                active_time += gap
                open_time += gap
            if (self.getStatus(key) != "Done"):
                close_time += gap
        return {
            "first_action":first_action,
            "first_closure":first_closure,
            "num_closures":num_closures,
            "open_time":open_time,
            "close_time":close_time,
            "active_time":active_time,
            "still_open":still_open
        }
    
    def getTransitions(self, key, force=False):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        reporter = self.getReporter(key, True, force)
        created = datetime.strptime(self.getCreated(key, force), "%Y-%m-%d %H:%M:%S")
        return self.fld.getTransitions(key, reporter, created, force)
    
    def getHistory(self, key, force=False, interface="rest"):
        # SOAP interface doesn't support 'getHistory' anymore after upgrading to JIRA 5.2!
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        return self.fld.getHistory(key, force, interface)
    
    def getLabels(self, key, force=False, interface="cli"):
        issue = self.getIssue(key, force)
        if (not issue):
            return []
        return self.fld.getLabels(key, force, interface)
    
    def setAllFields(self, key):
        self.tkt.setAllFields(key)
    
    def setField(self, key, field, value):
        self.tkt.setField(key, field, value)
    
    def getSpecificActions(self, key, action):
        res = 0
        available = self.getAvailableActions(key)
        for item in available:
            if (item["name"] == action):
                res = item["id"]
                break
        return res
    
    def getAvailableActions(self, key):
        res = []
        temp = self.lli.getAvailableActions(key)
        if (temp):
            for i in range(len(temp)):
                res.append({"id":temp[i]["id"], "name":temp[i]["name"]})
        return sorted(res)
    
    def getFieldsForAction(self, key, actionId):
        res = []
        temp = self.lli.getFieldsForAction(key, actionId)
        if (temp):
            for i in range(len(temp)):
                res.append({"id":temp[i]["id"], "name":temp[i]["name"]})
        return sorted(res, reverse=True)
    
    def updateIssueList(self, key, items, force=False):
        res = []
        for i in items:
            res.append({i:items[i]})
        return self.lli.updateIssue(key, res)
    
    def listIssueDetails(self, item):
        res = []
        for i in item:
            res.append(str(self.Unicode2Ascii(i["id"])))
        return res

    def Unicode2Ascii(self, value):
        return unicode(value.encode("utf-8"), "utf-8")

    def updateIssue(self, key, item, values, force=False): # 'values' should be always a list!
        if (item == "type"):
            field = "issuetype"
        elif (item == "affectsVersions"):
            field = "versions"
        else:
            field = item
        if (values == ["None"]):
            values = [None]
        if (force):
            res = self.lli.updateIssue(key, [{field:values}])
            if (not res):
                check_val = None
            elif (item == "labels"):
                real_value = values
                check_val = real_value
            elif (item in ["affectsVersions", "fixVersions", "components"]):
                real_value = values
                check_val = self.listIssueDetails(res[item])
            else:
                real_value = values[0]
                if (item not in res):
                    check_val = None
                else:
                    check_val = res[item]
            if (check_val != real_value):
                return None
            elif (item == "labels"):
                return ""
            else:
                self.setField(key, item, real_value)
                if (check_val is None):
                    return "None"
                else:
                    return check_val
        else:
            getFun = item[0].capitalize() + item[1:]
            if (item[:12] == "customfield_"):
                val_old = self.getCustomFieldValues(key, item)
                val_new = self.getCustomFieldValues(key, item)
            elif (item == "summary"):
                val_old = self.getSummary(key)
                val_new = self.getSummary(key, True)
            else:
                exec "val_old = self.get" + getFun + "(\"" + key + "\", True)"
                exec "val_new = self.get" + getFun + "(\"" + key + "\", True, True)"
            if (val_new == val_old):
                return self.updateIssue(key, item, values, True)
            return val_new

    def progressWorkflowAction(self, key, action, values=[]):
        return self.lli.progressWorkflowAction(key, action, values)
    
    def refreshRetrievedIssues(self):
        return self.upd.refreshIssues(self.tkt.getIssuesRetrieved())

    def refreshIssues(self, keyList):
        if (type(keyList).__name__ == "list"):
            res = {}
            for i in range(len(keyList)):
                res[keyList[i]] = self.refreshIssue(keyList[i])
            return res
        else:
            self.lli.log("'refreshIssues' can be only called on <list> otherwise call 'Update'", True)
            sys.exit()

    def refreshIssue(self, key):
        if (self.tkt.exists(key)):
            issue = self.getIssue(key)
        else:
            issue = {}
            res = {"new":""}
        updated_issue = self.getIssue(key, True)
        if (issue):
            res = getDifference(updated_issue, issue)
        return res

    def templateContain(self, issue, item):
        exec "b = self.qry." + item
        if (b):
            str = "a = self.get" + item[:1].upper() + item[1:] + "Name(issue['" + item + "']"
            if item in ["type","components","fixVersions","affectsVersions"]:
                str += ", issue['project']"
            str += ")"
            exec str
#            print item, a, b
            if (type(a).__name__ == "NoneType"):
                return False
            elif ((type(a).__name__ == "str") or (type(a).__name__ == "Text")):
                if (a not in b):
                    return False
            else:
                for i in range(len(a)):
                    if (a[i] not in b):
                        return False
        return True
 
    def isIssueBelonging(self, issue):
        # "platform","summary","description","reporter","created","updated"
        # "project"
        for i in ["status","assignee","priority","resolution","type","components","fixVersions","affectsVersions"]:
            if (not self.templateContain(issue, i)):
                self.lli.log("False")
                return False
        self.lli.log("True")
        return True

    def templateExtraInfo(self, key, string, serverTime, value="updated", response="updateAuthor"):
        exec "items = self.get" + string + "(key, True)"
        if (items and (str(items[-1][value])[:-3] >= serverTime)):
            return (items[-1][response], str(items[-1][value])[:-3])
        return ("", "")

    def refresh(self):
        if (not self.qry.getStoredQuery()):
            self.lli.log("No query stored: impossible to call 'refresh()'!", True)
            #sys.exit()
            return {}
        if (self.qry.getStoredQuery() != self.getQuery()):
            self.lli.log("Query has been changed since last run: 'refresh()' cannot be called!", True)
            #sys.exit()
            return {}
        serverTime = self.getServerTime()
        query = self.qry.getClause("project")
        query += " AND updated >= '" + serverTime + "'"
        issues = self.lli.getIssuesFromProject(query)
        return self.checkUpdatedIssues(issues, serverTime)

    def checkUpdatedIssues(self, issues, serverTime):
        self.tkt.resetUpdatedList()
        for i in range(len(issues)):
            diff = {}
            key = issues[i]["key"]
            self.lli.log(key)
            issue = self.tkt.translateIssue(issues[i])
            if (not self.tkt.exists(key)):
                self.lli.log(str(issue["created"])[:-3] + " " + serverTime)
                if (str(issue["created"])[:-3] >= serverTime):
                    diff["created"] = issue["created"]
                if (self.isIssueBelonging(issue)):
                    self.tkt.addRetrievedIssueAfterUpdated(key)
                    if ("created" not in diff):
                        diff["reopened"] = ""
                self.lli.log(str(diff))
            else:
                old_issue = self.getIssue(key)
                diff = getDifference(old_issue, issue)
                # TO DO: improve this part (done like this for performance purpose)
                retrieve_all_fields_on_update = False
                if (retrieve_all_fields_on_update):
                    (user, time) = self.templateExtraInfo(key, "Comments", serverTime)
                    if user:
                        diff["comment"] = (user, time)
                    (user, time) = self.templateExtraInfo(key, "Worklogs", serverTime)
                    if user:
                        diff["worklog"] = (user, time)
                    (user, time) = self.templateExtraInfo(key, "Attachments", serverTime, "created", "author")
                    if user:
                        diff["attachment"] = (user, time)
                    (user, time) = self.templateExtraInfo(key, "Transitions", serverTime, "when", "executor")
                    if user:
                        diff["transition"] = (user, time)
                    link = self.getLinks(key)
                    if (link != self.getLinks(key, True)):
                        diff["link"] = ""
                else:
                    self.fld.reset(key)
                self.lli.log(str(diff))
                if (self.isIssueBelonging(issue)):
                    if (not self.tkt.exists(key, "retrieved")):
                        self.tkt.addRetrievedIssueAfterUpdated(key)
                else:
                    if (self.tkt.exists(key, "retrieved")):
                        self.tkt.addRetrievedIssueAfterUpdated(key, True)
            self.tkt.addUpdatedIssue(key, issue, diff)
        return self.getIssuesUpdated()
    
    def getStoredQuery(self):
        return self.qry.getStoredQuery()
    
    def retrieveIssues(self, key=""):
        self.qry.setStoredQuery(self.getQuery(key))
        self.lli.log("QUERY: " + self.getStoredQuery(), True)
        issues = self.lli.getIssuesFromProject(self.getStoredQuery())
        self.tkt.addRetrievedIssues(issues)
        return self.getIssuesRetrieved()
    
    def retrieveFilteredIssues(self, id):
        filters = self.getFavouriteFilters()
        #self.lli.log("FILTER: " + filters[id]["name"], True)
        issues = self.lli.getIssuesFromFilter(id)
        projects = self.tkt.addRetrievedIssues(issues, True)
#        return self.tkt.getIssuesRetrieved(), projects
        return projects
    
    def getLinksRecursively(self, key, threshold=-1):
        result = {}
        to_analize = [key]
        while (to_analize):
#            print len(result), len(to_analize)
            if (len(result) == threshold):
                break
            x = to_analize[0]
            to_analize = to_analize[1:]
            self.getIssue(x)
            dependency = self.getLinks(x)
            list = []
            for i in range(len(dependency)):
                p = dependency[i]["destination"]
                list.append((p, dependency[i]["type"], dependency[i]["direction"]))
                if ((p not in to_analize) and (p not in result)):
                    to_analize.append(p)
            result[x] = list
        return result
    
#    def getIssuesFromProjectLink(self):
#        timer = startClock()
#        for k in self.all_issues.keys():
#            self.getLinks(k)
#        stopClock(timer, "linked issues")
#    
#    def getNotificationSchemes(self):
#        return self.lli.getNotificationSchemes()
#
#    def getAssociatedNotificationSchemes(self, projectRole):
#        return self.lli.getAssociatedNotificationSchemes(projectRole)

    def addComment(self, key, comment):
        return self.lli.addComment(key, comment)
    
    def chekIssues(self):
        for k in self.all_issues.keys():
            self.chekIssue(k)

    def chekLinkedIssues(self):
        for k in self.linkedIssues.keys():
            self.chekLinkedIssue(k)

    def chekIssue(self, key):
        self.bug = "0"
        self.closed = "0"
        self.affected = "1"
        self.platform = "0"
        self.link = "0"
#        issue = self.getIssue(key)
        info = {}
        if (self.getType(key) == "Bug"):
            if (self.getPriority(key) == "Undetermined"):
                info["priority"] = "missing"
            if (not self.getAffectsVersions(key)):
                info["affectsVersions"] = "missing"
            elif (len(self.getAffectsVersions(key)) > 1):
                if (self.affected == "1"):
                    info["affectsVersions"] = "too_many"
            if (not self.getComponents(key)):
                info["components"] = "missing"
            if (self.getResolution(key) == "Unresolved"): # Open, Reopened, InProgress
                if (self.getAssignee(key) == "None"):
                    info["assignee"] = "missing"
                if (self.getStatus(key) == "Reopened"):
                    if (self.getFixVersions(key)):
                        info["fixVersions"] = "too_many"
        '''
            elif (self.closed == "0"): # closed
                if (issue["resolution"] == self.getResolutionId("Fixed")):
                    if (issue["status"] == self.getStatusId("Ready For Testing")):
                        if (not issue["fixVersion"]):
                            info.append("missing_fix_version")
                        elif (len(issue["fixVersion"]) > 1):
                            info.append("too_many_fix")
#                        elif (issue["fixVersion"][0][0:3] != "NEXT"):
#                            info.append("fix_should_be_next")
                    elif (issue["status"] == self.getStatusId("Done")):
                        if (issue["assignee"] is not None):
                            info.append("presence_assignee")
                        if (not issue["fixVersion"]):
                            info.append("missing_fix_version")
                        elif (len(issue["fixVersion"]) > 1):
                            info.append("too_many_fix")
#                        elif (issue["fixVersion"][0] == "NEXT-BUILD"):
#                            info.append("fix_not_correct")
                else: #Won't fix, Duplicate, Incomplete, Cannot reproduce, Not a bug
                    if (issue["status"] == self.getStatusId("Ready For Testing")):
                        if (issue["fixVersion"]):
                            info.append("presence_fix_version")
                    elif (issue["status"] == self.getStatusId("Done")):
                        if (issue["assignee"] is not None):
                            info.append("presence_assignee")
                        if (issue["fixVersion"]):
                            info.append("presence_fix_version")
        elif (self.bug == "0"): #anything else but a bug
#            if (not issue["platform"]):
#                if (self.plaform == "1"):
#                    info.append("missing_platform")
            if (issue["priority"] == self.getPriorityId("Undetermined")):
                info.append("missing_priority")
            if (not issue["affectedVersion"]):
                info.append("missing_affected")
            elif (len(issue["affectedVersion"]) > 1):
                if (self.affected == "1"):
                    info.append("too_many_affected")
            if (not issue["components"]):
                info.append("missing_component")
            if (issue["resolution"] == self.getResolutionId("")): #Open, Reopened, InProgress
                if (issue["assignee"] is None):
                    info.append("missing_assignee")
            elif (self.closed == "0"): # closed
                if (issue["resolution"] == self.getResolutionId("Fixed")):
                    if (issue["status"] == self.getStatusId("Ready For Testing")):
                        if (not issue["fixVersion"]):
                            info.append("missing_fix_version")
                        elif (len(issue["fixVersion"]) > 1):
                            info.append("too_many_fix")
#                        elif (issue["fixVersion"][0] != "NEXT-BUILD"):
#                            info.append("fix_should_be_next")
                    elif (issue["status"] == self.getStatusId("Done")):
                        if (issue["assignee"] is not None):
                            info.append("presence_assignee")
                else: #Won't fix, Duplicate, Incomplete, Cannot reproduce, Not a bug
                    if (issue["status"] == self.getStatusId("Ready For Testing")):
                        if (issue["fixVersion"]):
                            info.append("presence_fix_version")
                    elif (issue["status"] == self.getStatusId("Done")):
                        if (issue["assignee"] is not None):
                            info.append("presence_assignee")
                        if (issue["fixVersion"]):
                            info.append("presence_fix_version")
        '''
#        if (info):
#            self.faulty_issues[key] = info
        return info

    def chekLinkedIssue(self, key):
        link_info = self.linkedIssues[key]
        details = []
        flag = False
        for i in range(len(link_info)):
            k = link_info[i]["linked"]
            v = link_info[i]["type"]
            linked_issue = self.getIssue(k)
            if ((self.getIssue(key)["resolution"] == self.getResolutionId("")) and
                (linked_issue["resolution"] != self.getResolutionId("")) and (v == "Cloners")):
                flag = True
            details.append((k, v, self.getResolutionName(linked_issue["resolution"]), "set_issue_ready_for_testing"))
#        if (flag):
#            self.faulty_linked_issues[key] = details

    def detailedBugs(self, list, prj=""):
        res = {}
        bugs = {}
        external_bugs = {}
        integrations = {}
        for i in range(len(list)):
            prj_in_jira = list[i][:list[i].index("-")]
            if (prj_in_jira == prj):
                if (list[i] not in bugs):
                    issue = self.getIssue(list[i])
                    if (issue):
                        bugs[list[i]] = (issue["summary"], self.getRStatuses()[issue["status"]], self.getResolutions()[issue["resolution"]]["name"])
            elif (prj_in_jira == prj+"IR"):
                if (list[i] not in integrations):
                    issue = self.getIssue(list[i])
                    if (issue):
                        integrations[list[i]] = (issue["summary"], self.getRStatuses()[issue["status"]], self.getResolutions()[issue["resolution"]]["name"])
            else:
                if (list[i] not in external_bugs):
                    issue = self.getIssue(list[i])
                    if (issue):
                        external_bugs[list[i]] = (issue["summary"], self.getRStatuses()[issue["status"]], self.getResolutions()[issue["resolution"]]["name"])
        res["bugs"] = bugs
        res["external_bugs"] = external_bugs
        res["integrations"] = integrations
        return res
