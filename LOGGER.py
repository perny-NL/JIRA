import os, logging

class Logger:
    def __init__(self, className=""):
        self.logger = logging.getLogger(className + "Log")
#        self.handler = logging.FileHandler(os.path.join("\\", "tmp", className + ".log"))
        self.handler = logging.FileHandler(os.path.join(os.getcwd(), className + ".log"))
        self.handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        self.logger.addHandler(self.handler) 
        self.setLevel("DEBUG")
#        self.logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    def __del__(self):
        self.handler.flush()
        self.logger.removeHandler(self.handler)
        #FIXED ON PYTHON 2.7
        #self.handler.close()
        #http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run
    
    def setLevel(self, level):
        exec "item = logging." + level
        self.logger.setLevel(item)
    
    def addLog(self, level, message):
        exec "self.logger." + level + "('" + message + "')"
