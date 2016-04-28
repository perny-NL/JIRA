import os, sys, time, getpass, urllib2
from suds.client import Client
#import threading
from threading import Thread, Lock
import LOGGER, CONNECTIVITY

class Jira_lli:
    JIRA_SERVER = "http://jira.tomtomgroup.com/"
    # FOR TEST USE: "http://plsrvut-jir02/"
    def __init__(self, account="", password=""):
        self.className = "JIRA"
        self.logger = LOGGER.Logger(self.className)
        self.logger.addLog("warning", "[START]")

        self.auth = None
        self.account = ""
        self.password = ""
        self.serverTime = ""
        self.environment = ""
        self.max_num_issues = 400
        self.max_num_issues_freetext = 100
#        self.max_num_issues_filter = 1000
        self.max_num_issues_filter = 200
        self.client = Client(Jira_lli.JIRA_SERVER + "rpc/soap/jirasoapservice-v2?wsdl")
        self.logging = False
        self.log_file = None
        self.connect(account, password)
        self.mutex = Lock()
        #self.connectionPool = [self.jiraWrapper("login", self.account, self.password)]
    
    def __del__(self):
        self.logger.addLog("warning", "[END]")
        if (self.account):
            self.jiraWrapper("logout", self.account)
        if (self.logging):
            self.log_file.close()

    def setLogging(self, switch):
        self.logging = switch
        if (self.logging):
            self.log_file = open(self.className + ".log", "w")
        else:
            self.log_file.close()
    
    def log(self, message, show=False):
        if (show):
            print message
        if (self.logging):
            self.logger.addLog("warning", message)
            #self.log_file.write(message + "\n")
            #self.log_file.flush()

    def setMaxIssuesNumber(self, num):
        self.max_num_issues = num

    def getAccount(self):
        return self.account
    
    def getPassword(self):
        return self.password
    
    def releaseConnection(self, auth):
        self.connectionPool.append(auth)
    
    def getConnection(self, pool=False):
        if (pool and self.connectionPool):
            return self.connectionPool.pop()
        return self.jiraWrapper("login", self.account, self.password)

    def connect(self, account, password):
        connectivity = CONNECTIVITY.Connectivity(self.className + " (SOAP)", account, password)
        self.account, self.password = connectivity.getCredentials()
        try:
            self.auth = self.getConnection()
        except:
            self.log(self.className + " 'password' is not correct!", True)
            sys.exit()
    
    def getStoredServerTime(self):
        return self.serverTime
    
    def getServerTime(self, show=False):
        serverTime = self.jiraWrapper("getServerInfo")
        formatTime = serverTime["serverTime"]["serverTime"][:16].replace("T", " ")
        if (show):
            self.log("Server time: " + str(formatTime), True)
        return formatTime

    def getIssue(self, key):
        res = {}
        moved = ""
        try:
            res = self.jiraWrapper("getIssue", key)
        except:
            urlIssue = Jira_lli.JIRA_SERVER + "browse/" + key
            request = urllib2.Request(urlIssue)
            try:
                result = urllib2.urlopen(request)
                urlIssueMoved = result.geturl()
                moved = urlIssueMoved.split( "/" )[-1]
                if (moved == key):
                    moved = ""
            except:
                res = {}
        return res, moved

    def getRoles(self):
        res = {}
        try:
            rl = self.jiraWrapper("getProjectRoles")
        except:
            rl = []
            self.log("'getRolesInfo' failed!")
#        for i in range(len(rl)):
#            res[rl[i]["id"]] = {"name":rl[i]["name"], "description":rl[i]["description"]}
        return rl

    def getActors(self, role, projectId):
        try:
            res = self.jiraWrapper("getProjectRoleActors", role, projectId)
        except:
            res = []
#            self.log("Server time: " + str(formatTime))
        return res

    def getUser(self, account, **kwargs):
        try:
            info = self.jiraWrapper("getUser", account, **kwargs)
            res = {"name":info["fullname"], "email":info["email"]}
        except:
            res = {"name":"", "email":""}
            self.log("'getUser' failed!", account)
        return res

    def getProjectId(self, project):
        try:
            res = self.jiraWrapper("getProjectByKey", project)
            # can be also retrieved by "getProjects()"
        except:
            res = ""
            self.log("'getProjectId' failed!")
        return res

    def getProjects(self):
        res = {}
        try:
            prj = self.jiraWrapper("getProjectsNoSchemes")
        except:
            prj = []
            self.log("'getProjectsInfo' failed!")
        for i in range(len(prj)):
            res[prj[i]["id"]] = {"name":prj[i]["name"], "key":prj[i]["key"]}
#            description = "..."
#            issueSecurityScheme = None
#            lead = "dleckie"
#            notificationScheme = None
#            permissionScheme = None
#            projectUrl = None
#            url = "http://vlieg.intra.local/browse/WILDWOOD"
        return res

    def getVersionsList(self, project):
        res = {}
        resReleased = {}
        try:
            ver = self.jiraWrapper("getVersions", project)
        except:
            ver = []
            self.log("'getVersions(" + project + ")' failed!")
        for i in range(len(ver)):
            res[ver[i]["id"]] = {"name":(ver[i]["name"]).encode("utf-8"), "released":ver[i]["released"]}
#            archived = False
#            releaseDate = None
#            sequence = 1
        return res

    def getComponentsList(self, project):
        res = {}
        try:
            comp = self.jiraWrapper("getComponents", project)
        except:
            comp = []
            self.log("'getComponents(" + project + ")' failed!")
        for i in range(len(comp)):
            res[comp[i]["id"]] = {"name":(comp[i]["name"]).encode("utf-8")}
        return res

    '''
TYPE
images/icons/issuetypes/blank.png
#images/icons/issuetypes/bug.png
images/icons/issuetypes/defect.png
images/icons/issuetypes/documentation.png
images/icons/issuetypes/epic.png
images/icons/issuetypes/exclamation.png
images/icons/issuetypes/genericissue.png
images/icons/issuetypes/health.png
#images/icons/issuetypes/improvement.png
images/icons/issuetypes/newfeature.png
images/icons/issuetypes/requirement.png
images/icons/issuetypes/sales.png
images/icons/issuetypes/subtask.png
#images/icons/issuetypes/task.png
images/icons/issuetypes/undefined.png
images/icons/TECHOPS/cab.gif
images/icons/TECHOPS/calendarevent.gif
images/icons/TECHOPS/incident.gif
images/icons/TECHOPS/problem.gif
images/icons/TECHOPS/servicerequest.gif
images/icons/tt_design.gif
images/icons/tt_testcase.gif
#images/icons/tt_userstory.gif
SUB-TYPE
#images/icons/issuetypes/subtask_alternate.png
PRIORITY
#images/icons/priorities/blocker.png
#images/icons/priorities/major.png
#images/icons/priorities/critical.png
#images/icons/priorities/trivial.png
#images/icons/priorities/minor.png
#images/icons/tt_priority_undetermined.gif
STATUS
#images/icons/statuses/closed.png
images/icons/statuses/document.png
images/icons/statuses/down.png
#images/icons/statuses/generic.png
images/icons/statuses/information.png
#images/icons/statuses/inprogress.png
#images/icons/statuses/needinfo.png
#images/icons/statuses/open.png
#images/icons/statuses/reopened.png
#images/icons/statuses/resolved.png
images/icons/statuses/trash.png
images/icons/statuses/up.png
#images/icons/statuses/visible.png
    '''
    def getTypesList(self):
        res = {}
        try:
            type = self.jiraWrapper("getIssueTypes")
        except:
            type = []
            self.log("'getTypeSupport' failed!")
        for i in range(len(type)):
            res[type[i]["id"]] = {"name":type[i]["name"], "icon":str(type[i]["icon"]).replace(Jira_lli.JIRA_SERVER, "")}
#              description = "Analysis of CR/PR Automotive"
#              subTask = False
        return res

    def getSubTypesList(self, project):
        res = {}
#        try:
        projectId = self.jiraWrapper("getProjectByKey", project)["id"]
        subtype = self.jiraWrapper("getSubTaskIssueTypesForProject", projectId)
#        except:
#            subtype = []
#            self.log("'getSubTypeSupport' failed!")
        for i in range(len(subtype)):
            res[subtype[i]["id"]] = {"name":subtype[i]["name"], "icon":str(subtype[i]["icon"]).replace(Jira_lli.JIRA_SERVER, "")}
#              description = "The sub-task of the issue"
#              subTask = True
        return res

    def getPrioritiesList(self):
        res = {}
        try:
            pri = self.jiraWrapper("getPriorities")
        except:
            pri = []
            self.log("'getPriorities' failed!")
        for i in range(len(pri)):
            res[pri[i]["id"]] = {"name":pri[i]["name"], "icon":str(pri[i]["icon"]).replace(Jira_lli.JIRA_SERVER, "")}
#            color = "#cc0000"
#            description = "Blocks development and/or testing work, production could not run."
        return res

    def getStatusesList(self):
        res = {}
        try:
            sta = self.jiraWrapper("getStatuses")
        except:
            sta = []
            self.log("'getStatuses' failed!")
        for i in range(len(sta)):
            res[sta[i]["id"]] = {"name":sta[i]["name"], "icon":str(sta[i]["icon"]).replace(Jira_lli.JIRA_SERVER, "")}
#            description = "The issue is open and ready for the assignee to start work on it."
        return res

    def getResolutionsList(self):
        res = {}
        try:
            temp = self.jiraWrapper("getResolutions")
        except:
            temp = []
            self.log("'getResolutions' failed!")
        for i in range(len(temp)):
            res[temp[i]["id"]] = {"name":temp[i]["name"]}
#            icon = None                
#             description = "A fix for this issue is checked into the tree and tested."
        return res

    def getDependencies(self, key, **kwargs):
        res = []
        try:
            links = self.jiraWrapper("getIssueLinks", key, **kwargs)
        except:
            links = []
            self.log("'getIssueLinks(" + key + ")' failed!")
        for i in range(len(links)):
            destination = links[i]["destinationKey"]
            if (key == destination):
                destination = links[i]["sourceKey"]
                direction = False
            else:
                direction = True
            type = links[i]["type"]
            res.append({"destination":destination, "type":type, "direction":direction})
#            id = 179988
        return res
    
    def getAttachments(self, key):
        res = []
        try:
            attachments = self.jiraWrapper("getAttachmentsFromIssue", key)
        except:
            attachments = []
            self.log("'getAttachmentsFromIssue(" + key + ")' failed!")
        for i in range(len(attachments)):
            res.append({"author":attachments[i]["author"], "created":attachments[i]["created"], "filename":attachments[i]["filename"], "id":attachments[i]["id"]})
#            filesize = 64501
#            id = "309544"
#            mimetype = "image/jpeg"
            #http://vlieg.intra.local/secure/attachment/378604/Screenshot.png
        return res

    def getWorklogs(self, key, forced=False):
        res = []
        try:
            worklogs = self.jiraWrapper("getWorklogs", key)
        except:
            worklogs = []
            self.log("'getWorklogs(" + key + ")' failed!")
        for i in range(len(worklogs)):
            res.append({"author":worklogs[i]["author"], "created":worklogs[i]["created"], "startDate":worklogs[i]["startDate"],
                        "timeSpent":worklogs[i]["timeSpent"], "timeSpentInSeconds":worklogs[i]["timeSpentInSeconds"],
                        "updateAuthor":worklogs[i]["updateAuthor"], "updated":worklogs[i]["updated"]})
#            comment = None
#            groupLevel = None
#            id = "232058"
#            roleLevelId = None
        return res
    
    def getComments(self, key, **kwargs):
        res = []
        try:
            comments = self.jiraWrapper("getComments", key, **kwargs)
        except:
            comments = []
            self.log("'getComments(" + key + ")' failed!")
        for i in range(len(comments)):
            res.append({"author":comments[i]["author"], "created":comments[i]["created"], "body":comments[i]["body"].encode("utf-8"),
                        "updateAuthor":comments[i]["updateAuthor"], "updated":comments[i]["updated"]})
#            id = "894536"
#            groupLevel = None
#            roleLevel = None
        return res

    def getTransitions(self, key):
        res = []
        try:
            transitions = self.jiraWrapper("getTransitions", key)
        except:
            transitions = []
            self.log("'getTransitions(" + key + ")' failed!")
        for i in range(len(transitions)):
            res.append({"executor":transitions[i]["executor"], "status":transitions[i]["status"], "when":transitions[i]["when"]})
#            id = 2823991
#            key = "NGL-789"
        return res

    def getHistory(self, key):
        #https://jira.atlassian.com/browse/JRA-27692
        res = []
        try:
            history = self.jiraWrapper("getHistory", key)
        except:
            history = []
            self.log("'getHistory(" + key + ")' failed!")
        for i in range(len(history)):
            changes = []
            for j in range(len(history[i]["changes"])):
                name = history[i]["changes"][j]["name"]
                value = history[i]["changes"][j]["value"]
                if (value is None):
                    if (name == "resolution"):
                        value = "Unresolved"
                    elif (name == "assignee"):
                        value = "None"
                    else:
                        value = ""
                else:
                    value = value.encode("utf-8")
                changes.append({"name":name, "values":value})
            res.append({"changes":changes, "executor":history[i]["executor"], "when":history[i]["when"]})
#            key = "NAVKIT-2579"
#            id = 4208153
        return res
    
#    def getSavedFilters(self): # Deprecated - same as getFavouriteFilters
#        return self.jiraWrapper("getSavedFilters")
    
    def getFavouriteFilters(self):
        res = {}
        try:
            filters = self.jiraWrapper("getFavouriteFilters")
        except:
            filters = []
            self.log("'getFavouriteFilters' failed!")
        for i in range(len(filters)):
            res[filters[i]["id"]] = {"author":filters[i]["author"], "name":filters[i]["name"]}
#        description = None
#        project = None
#        xml = None
        return res
    
    def getIssueCountForFilter(self, id):
        try:
            filterscount = self.jiraWrapper("getIssueCountForFilter", id)
        except:
            filterscount = 0
            self.log("'getIssueCountForFilter('" + id + ")' failed!")
        return filterscount
    
    def getIssuesFromFilter(self, filterId):
        return self.jiraWrapper("getIssuesFromFilterWithLimit", filterId)

    def getIssuesFromTextSearch(self, search): # SEARCH IN SUMMARY, DESCRIPTION AND COMMENTS
        return self.jiraWrapper("getIssuesFromTextSearchWithLimit", search)
    
    def getIssuesFromTextSearchWithProject(self, prj, search, flag): # SEARCH IN SUMMARY, DESCRIPTION AND COMMENTS
        if (flag == 0):
            return self.jiraWrapper("getIssuesFromTextSearchWithProject", [prj], search)
        elif (flag == 1):
            return self.jiraWrapper("getIssuesFromTextSearchWithProject", [prj], " AND ".join(search))
        else:
            return self.jiraWrapper("getIssuesFromTextSearchWithProject", [prj], " OR ".join(search))
    
    def getLabels(self, key): # NOT IMPLEMENTED
        # ALTERNATIVE: "... AND labels in (1,2,3)"
        # updateIssue("NGL-777", [{"id":"labels", "values":["1", "2", "3"]}])
        res = []
        try:
            labels = self.jiraWrapper("getLabels", key)
        except:
            labels = []
            self.log("'getLabels' failed!")
        for i in range(len(labels)):
            res.append({"???":labels[i]["???"]})
        return res
    
    def getResolutionDateByKey(self, key): # NOT USED
        return self.jiraWrapper("getResolutionDateByKey", key)

    def getFieldsForEdit(self, key): # NOT USED
        return self.jiraWrapper("getFieldsForEdit", key)

    def getCustomFields(self): # ONLY FOR ADMINISTRATORS
        return self.jiraWrapper("getCustomFields")

    def getAvailableActions(self, key):
        return self.jiraWrapper("getAvailableActions", key)
    
    def getFieldsForAction(self, key, actionId):
        return self.jiraWrapper("getFieldsForAction", key, actionId)
    
#    def getDefaultRoleActors(self) : # ??????
#        return 1

    def updateIssue(self, key, items):
        res = []
        for i in items:
            id = i.keys()[0]
            val = [] if (i[id] == ["None"]) else i[id]
            res.append({"id":id, "values":val})
        return self.jiraWrapper("updateIssue", key, res)
        
    def addComment(self, key, comment):
        return self.jiraWrapper("addComment", key, comment)
    
    def progressWorkflowAction(self, key, action, values):
        return self.jiraWrapper("progressWorkflowAction", key, action, values)
    
    def getNotificationSchemes(self): # ONLY FOR ADMINISTRATORS
        return self.jiraWrapper("getNotificationSchemes")

    def getAssociatedNotificationSchemes(self, projectRole): # ONLY FOR ADMINISTRATORS
        return self.jiraWrapper("getAssociatedNotificationSchemes", projectRole)

    def getIssuesFromProject(self, query):
        return self.jiraWrapper("getIssuesFromJqlSearch", query)

    
    
    
    
    def stillConnected(self):
        self.client.service.getIssuesFromJqlSearch(self.auth, "updated >= now()", self.max_num_issues)
        try:
            self.client.service.getIssuesFromJqlSearch(self.auth, "updated >= now()", self.max_num_issues)
        except:
            self.log("{stillConnected} Reconnecting...", True)
            self.auth = self.jiraWrapper("login", self.account, self.password)

    def requestWithReconnect(self, fun, *args):
        # INFO: "getHistory" has been removed by JIRA 5.2
        # INFO: using "getTransitions" the call is failing but 'result' is correctly filled
        '''
        if (len(args) == 0):
            tmp = "-"
        else:
            tmp = args[0]
        print "result = self.client.service." + fun + "(" + tmp + ")"
        exec "result = self.client.service." + fun + "(self.auth, *args)"
        '''
        try:
            exec "result = self.client.service." + fun + "(self.auth, *args)"
        except:
            print "Errore inatteso:", sys.exc_info()[0]
            print "Function is: ", fun 
            self.log("{requestWithReconnect} Reconnecting...", True)
            self.auth = self.jiraWrapper("login", self.account, self.password)
            exec "result = self.client.service." + fun + "(self.auth, *args)"
        return result

    def getIssuesFromFilterRecursive(self, filterId, offset=0):
       # self.stillConnected()
        try:
            result = self.client.service.getIssuesFromFilterWithLimit(self.auth, filterId, offset, self.max_num_issues_filter)
        except:
            print "SOME PROBLEM RETRIEVING ISSUES WITH THIS FILTER!"
            result = []
        if (len(result) == self.max_num_issues_filter):
            os.write(1,".")
            result += self.getIssuesFromFilterRecursive(filterId, offset + len(result))
        return result

    def getIssuesRecursive(self, query):
        self.stillConnected()
        result = self.client.service.getIssuesFromJqlSearch(self.auth, query, self.max_num_issues)
        try:
            result = self.client.service.getIssuesFromJqlSearch(self.auth, query, self.max_num_issues)
        except:
            self.logger.addLog("warning", "Problem retrieving issue with " + "query" + ".")
            print "SOME PROBLEM RETRIEVING ISSUES WITH THIS QUERY!"
            result = []
        if (len(result) == self.max_num_issues):
            os.write(1,".")
            result += self.getIssuesRecursive(query + " AND id < " + result[-1]["id"])
        return result

    def jiraWrapper(self, func, *args, **kwargs):
        if (func in ["login", "logout"]):
            exec "result = self.client.service." + func + "(*args)"
        else:
            if (func in ["getIssuesFromJqlSearch", "getIssuesFromFilterWithLimit", "getIssuesFromTextSearchWithLimit", "getIssuesFromTextSearchWithProject"]):
                self.serverTime = self.getServerTime(True)
                timer = time.clock()
                if (func == "getIssuesFromTextSearchWithProject"):
                    result = self.client.service.getIssuesFromTextSearchWithProject(self.auth, args[0], self.max_num_issues)
                elif (func == "getIssuesFromTextSearchWithLimit"):
                    result = self.client.service.getIssuesFromTextSearchWithLimit(self.auth, args[0], self.max_num_issues_freetext)
                elif (func == "getIssuesFromFilterWithLimit"):
                    try:
                       result = self.getIssuesFromFilterRecursive(args[0])
                    except:
                       self.logger.addLog("warning", "JiraWrapper: Error Retrieving Filtered Issues")
                       result= []
                else: # (func == "getIssuesFromJqlSearch")
                    result = self.getIssuesRecursive(args[0])
                self.log("Retrieving " + str(len(result)) + " issues took %.6f seconds" % (time.clock() - timer), True)
            else:
                if ("jira_request" in kwargs):
                    self.mutex.acquire()
                    auth = self.getConnection(True)
#                    self.stillConnected(auth)
                    try:
                        exec "result = self.client.service." + func + "(auth, *args)"
                    except:
                        self.log("Reconnecting...", True)
                        auth = self.jiraWrapper("login", self.account, self.password)
                        exec "result = self.client.service." + func + "(auth, *args)"
#                    self.releaseConnection(auth)
                    self.mutex.release()
                else:
                    result = self.requestWithReconnect(func, *args)
                if ((func == "getComments") and (result is None)):
                    self.logger.addLog("warning", "Problem retrieving 'comments' on '" + args[0] + "'")
                    result = [{"author":"mapr","body":"PROBLEM RETRIEVING COMMENTS","created":"2012-12-21 00:00:00","groupLevel":"","id":"","roleLevel":"","updateAuthor":"","updated":""}]
        return result
