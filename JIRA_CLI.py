import os, re, sys, getpass
import LOGGER, CONNECTIVITY

class Jira_cli:
    CLI_VERSION = "3.4.0"
    SERVER_STRING = "http://vlieg.intra.local"
#    PATH_JAR = "jira-cli-" + CLI_VERSION + "\\lib"
    PATH_JAR = "D:\mapr_ct-devenv_prep_windows\Tools\PyTools\Modules\jira-cli-" + CLI_VERSION + "\\lib"
    JAR_FILE = "jira-cli-" + CLI_VERSION + ".jar"

    def __init__(self, account, password):
        self.className = self.__class__.__name__.upper()
        self.account = account
        self.password = password
        self.token = False
        self.login = "token.txt"
        self.logger = LOGGER.Logger(self.className)
        self.logger.addLog("warning", "[START]")
    
    def __del__(self):
        self.logger.addLog("warning", "[END]")
        output = "logout.txt"
        if (self.token):
            os.system(self.wrapper("logout", output))
            os.remove(output)
            os.remove(self.login)

    def getAccount(self):
        return self.account

    def getPassword(self):
        return self.password

    def getConnection(self):
        self.token = True
        os.system(self.wrapper("login", self.login))
        with open(self.login) as f:
            data = f.read()
        return data

    def updateLabels(self, key, labels):
        values = " ".join(labels)
        os.system(self.wrapper("updateLabels", key, values))
    
    def updateAssignee(self, key, assignee):
        os.system(self.wrapper("updateAssignee", key, assignee))
    
    def getLabels(self, key):
        output = "q.txt"
        os.system(self.wrapper("getLabels", key, output))
        with open(output) as f:
            data = f.read()
        os.remove(output)
        return re.search("Labels.*:(.*)", data).group(1).strip().split()
    
    def wrapper(self, func, *args):
        res = "java -jar " + os.path.join(Jira_cli.PATH_JAR, Jira_cli.JAR_FILE) + " -a "
        if (func == "login"):
            return res + "login -u " + self.getAccount() + " -p " + self.getPassword() + " -s " + Jira_cli.SERVER_STRING + " > " + args[0]
        if (not self.token):
            self.auth = self.getConnection()
        if (func == "logout"):
            res += "logout -l < " + self.login + " -p \"\" -s " + Jira_cli.SERVER_STRING + " > " + args[0]
        elif (func == "getLabels"):
            res += "getIssue --issue \"" + args[0] + "\" --outputFormat 2 -u " + self.getAccount() + " -p " + self.getPassword() + " -s " + Jira_cli.SERVER_STRING + " -f " + args[1]
        elif (func == "updateLabels"):
            res += "updateIssue --issue \"" + args[0] + "\" --labels \"" + args[1] + "\" -p \"\" -s " + Jira_cli.SERVER_STRING + " -l < " + self.login
        elif (func == "updateAssignee"):
            res += "updateIssue --issue \"" + args[0] + "\" --assignee \"" + args[1] + "\" -p \"\" -s " + Jira_cli.SERVER_STRING + " -l < " + self.login
        return res
