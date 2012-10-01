#!/usr/bin/env python

from twisted.internet import reactor
from ConfigParser import ConfigParser
from os import listdir

def startServer():
    config = ConfigParser()
    config.read(["server.cfg"])
    
    moduleList = listdir("modules")
    
    for module in moduleList:
        if module == "__init__.py" or module[-3:] != ".py":
            continue
        loadedModule = __import__("modules." + module[:-3], fromlist=["*"])
        loadedModule.startModule(config)
    
    reactor.run()

if __name__ == "__main__":
    startServer()
