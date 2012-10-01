#!/usr/bin/env python

from ConfigParser import ConfigParser
from os import listdir

def startSetup():
    config = ConfigParser()
    moduleList = listdir("modules")
    
    config.add_section("global")
    value = raw_input("Enter the JSON root folder to write the json files too : ")
    config.set("global", "jsonRoot", value)
    
    for module in moduleList:
        if module == "__init__.py" or module[-3:] != ".py":
            continue
        loadedModule = __import__("modules." + module[:-3], fromlist=["*"])
        loadedModule.startConfig(config)

    configFile = open("server.cfg", "w")
    config.write(configFile)
    configFile.close()

if __name__ == "__main__":
    startSetup()
