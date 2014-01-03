#! /usr/bin/env python
# coding=utf-8

import logging
import logging.handlers
import os
import json

from ConfigParser import ConfigParser
from twisted.internet import reactor

__all__ = ['restart_server', 'start_server', 'stop_server', 'start_config']

logger = logging.getLogger('main')


def restart_server(config_file_name, log_file_name):
    stop_server()
    start_server(config_file_name, log_file_name)


def stop_server():
    if logger.isEnabledFor(logging.INFO):
        logger.info("Stopping Server")
    reactor.stop()


def start_server(config_file_name, log_file_name):
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(name)s:%(lineno)d %(levelname)-8s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
    handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=10 * 1024 * 1024, backupCount=5)

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    if logger.isEnabledFor(logging.INFO):
        logger.info("Starting Server")

    config_file = open(config_file_name)
    config = ConfigParser()
    config.readfp(config_file)

    module_list = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    for module in module_list:
        if module == "__init__.py" or module[-3:] != ".py" or module[:4] == 'main':
            continue
        if logger.isEnabledFor(logging.INFO):
            logger.info("Loading module: modules." + module[:-3])
        loaded_module = __import__("pygamescanner." + module[:-3], fromlist=["*"])
        loaded_module.start_module(config)

    reactor.run()


def start_config(config_file_name):
    config = ConfigParser()
    config.add_section("global")

    value = raw_input("Enter the JSON root folder to write the json files too : ")
    if len(value) == 0:
        value = '../www/JSON'
    elif value[-1] != "/":
        value += "/"
    config.set("global", "json_root", value)

    modules_config = []

    module_list = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    for module in module_list:
        if module == "__init__.py" or module[-3:] != ".py" or module[:4] == 'main':
            continue
        loaded_module = __import__("pygamescanner." + module[:-3], fromlist=["*"])
        module_config = loaded_module.start_config(config)
        modules_config.append(module_config)

    modules_config_dict = dict()
    modules_config_dict["module_list"] = modules_config
    config_string = json.dumps(modules_config_dict)
    modules_file = open(config.get("global", "json_root") + "modules.json", "w")
    modules_file.write(config_string)
    modules_file.close()

    config_file = open(config_file_name, "w")
    config.write(config_file)
    config_file.close()
