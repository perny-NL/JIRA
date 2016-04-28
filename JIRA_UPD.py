import sys

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
	res.update(getSingleDifference(a, b, "affectedVersion"))
#	res.update(getSingleDifference(a, b, "platform"))
	res.update(getSingleDifference(a, b, "component"))
	res.update(getSingleDifference(a, b, "status"))
	res.update(getSingleDifference(a, b, "resolution"))
	res.update(getSingleDifference(a, b, "fixVersion"))
	res.update(getSingleDifference(a, b, "project"))
	res.update(getSingleDifference(a, b, "reporter"))
	res.update(getSingleDifference(a, b, "created"))
#	res.update(getSingleDifference(a, b, "updated"))
##	res.update(getSingleDifference(a, b, "id"))
##	res.update(getSingleDifference(a, b, "attachmentNames"))
##	res.update(getSingleDifference(a, b, "duedate"))
##	res.update(getSingleDifference(a, b, "environment"))
##	res.update(getSingleDifference(a, b, "votes"))
	return res

class Jira_upd():
	def __init__(self):
		None
		
	def refreshIssues(self, keyList):
		if (type(keyList).__name__ == "list"):
			res = {}
			for i in range(len(keyList)):
				res[keyList[i]] = self.refreshIssue(keyList[i])
			return res
		else:
			print "'refreshIssues' can be only called on <list> otherwise call 'Update'"
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
		exec "b = self." + item
		if (b):
			str = "a = self.get" + item[:1].upper() + item[1:] + "Name(issue['" + item + "']"
			if item in ["type","component","fixVersion","affectedVersion"]:
				str += ", issue['project']"
			str += ")"
			exec str
#			print item, a, b
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
		for i in ["status","assignee","priority","resolution","type","component","fixVersion","affectedVersion"]:
			if (not self.templateContain(issue, i)):
				print "False"
				return False
		print "True"
		return True

	def templateExtraInfo(self, key, string, serverTime, value="updated", response="updateAuthor"):
		exec "items = self.fld.get" + string + "(key, True)"
		if (items and (str(items[-1][value])[:-3] >= serverTime)):
			return (items[-1][response], str(items[-1][value])[:-3])
		return ("", "")

	def refresh(self):
		if (not self.qry.getStoredQuery()):
			print "No query stored: impossible to call 'refresh()'!"
			#sys.exit()
			return
		if (self.qry.getStoredQuery() != self.qry.getQuery()):
			print "Query has been changed since last run: 'refresh()' cannot be called!"
			#sys.exit()
			return
		serverTime = self.lli.getStoredServerTime()
		query = self.getClause("project")
		query += " AND updated >= '" + serverTime + "'"
		issues = self.lli.getIssuesFromProject(query)
		return self.checkUpdatedIssues(issues, serverTime)
