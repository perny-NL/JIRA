import json
#import xml.etree.ElementTree as ET
import os, re, sys, getpass
from datetime import datetime, timedelta
import urllib2, base64
import LOGGER, CONNECTIVITY

class Jira_rst:
    #REST API: https://developer.atlassian.com/display/JIRADEV/JIRA+REST+API+Example+-+Query+issues
    #HOW TO RETRIEVE HISTORY: https://jira.atlassian.com/browse/JRA-27692
    #EXAMPLE: http://vlieg.intra.local/rest/api/2/search?jql=key=PYRA-57&expand=changelog
    SERVER_STRING = "http://vlieg.intra.local/rest/api/2/"

    def __init__(self, account, password):
        self.className = self.__class__.__name__.upper()
        self.account = account
        self.password = password
        self.auth = base64.encodestring('%s:%s' % (self.account, self.password))[:-1]
        self.logger = LOGGER.Logger(self.className)
        self.logger.addLog("warning", "[START]")
    
    def __del__(self):
        self.logger.addLog("warning", "[END]")

    def getAccount(self):
        return self.account

    def getPassword(self):
        return self.password

    def getIssue(self, key):
        return self.wrapper("getIssue", key)
    
    def getHistory(self, key):
        return self.wrapper("getHistory", key)
        
    def wrapper(self, func, *args):
        query = Jira_rst.SERVER_STRING + "search?jql=key=" + args[0]
        if (func == "getHistory"):
            query += "&expand=changelog"
        request = urllib2.Request(query)
        request.add_header("Authorization", "Basic %s" % self.auth)
        file =  urllib2.urlopen(request)
        xml = file.read()
        obj = json.loads(xml)
        if (func == "getHistory"):
            res = []
            tmp = obj["issues"][0]["changelog"]["histories"]
            for item in tmp:
                when = datetime.strptime(item["created"][:-9], "%Y-%m-%dT%H:%M:%S")
                changes = []
                for item2 in item["items"]:
                    name = item2["field"]
                    #fromString = "NONE" if (item2["fromString"] is None) else item2["fromString"][:20]
                    value = item2["toString"]
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
                res.append({"changes":changes, "executor":item["author"]["name"], "when":when})
            return res
        else:
            print obj
        return ""
