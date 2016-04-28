import os, sys, getpass

class Connectivity:
    def __init__(self, id="", account="", password="", server=""):
        self.account = account
        self.password = password
        self.server = server
        self.linux = True
        try:
            account_tmp = os.environ.get("USER")
            if (account_tmp is None):
                self.linux = False
                account_tmp = os.environ["USERNAME"]
        except:
            account_tmp = None
        if (not account):
            if (not account_tmp):
                print "USERNAME not found!"
                sys.exit()
            self.account = account_tmp
        if (not password):
            file_pswrd = os.path.join(os.getcwd(), "pswrd")
            file_path = os.path.join(os.getcwd(), "pswrd_path.txt")
            if (os.path.exists(file_pswrd)):
                f = open(file_pswrd, "r")
                password = f.read()
                f.close()
                self.password = password
            elif (os.path.exists(file_path)):
                f = open(file_path, "r")
                password_path = f.read()
                f.close()
                if (not os.path.exists(password_path)):
                    print "File '" + password_path + "' doesn't exists!"
                    sys.exit()
                f = open(password_path, "r")
                password = f.read()
                f.close()
                self.password = password
            else:
                self.password = getpass.getpass("Enter " + id + " password for <" + self.account + ">: ")

    def getCredentials(self):
        return self.account, self.password
    
    def getServer(self):
        return self.server
    
    def getPlatform(self):
        return self.linux
    
