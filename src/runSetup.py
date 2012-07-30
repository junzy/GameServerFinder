#!/usr/bin/env python

from ConfigParser import *
from os import listdir

def setup():
    config = ConfigParser()
    moduleList = listdir("modules")

    for module in moduleList:
        loadedModule = __import__("modules." + module)
        loadedModule.startConfig()

    configFile = open("server.cfg", "w")
    config.write(configFile)
    configFile.close()

if __name__ == "__main__":
    setup()
