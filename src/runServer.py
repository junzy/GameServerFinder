#!/usr/bin/env python

from twisted.internet import reactor

import ConfigParser

def startServer():
    config = ConfigParser.ConfigParser()
    config.read(["server.cfg"])
    
    moduleList = os.listdir("modules")

    for module in moduleList:
        loadedModule = __import__("modules." + module)
        loadedModule.startModule(config)
    
    reactor.run()
    return

if __name__ == "main":
    startServer()
