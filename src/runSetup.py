#!/usr/bin/env python

from ConfigParser import ConfigParser
from os import listdir
import json


def startSetup():
    config = ConfigParser()
    moduleList = listdir("modules")

    config.add_section("global")
    value = raw_input("Enter the JSON root folder to write the json files too : ")
    if value[-1] != "/":
        value += "/"
    config.set("global", "jsonRoot", value)

    modulesConfig = []

    for module in moduleList:
        if module == "__init__.py" or module[-3:] != ".py":
            continue
        loadedModule = __import__("modules." + module[:-3], fromlist=["*"])
        moduleConfig = loadedModule.startConfig(config)
        modulesConfig.append(moduleConfig)

    modulesConfigDict = {}
    modulesConfigDict["moduleList"] = modulesConfig
    configString = json.dumps(modulesConfigDict)
    modulesFile = open(config.get("global", "jsonRoot") + "modules.json", "w")
    modulesFile.write(configString)
    modulesFile.close()

    configFile = open("server.cfg", "w")
    config.write(configFile)
    configFile.close()

if __name__ == "__main__":
    startSetup()

