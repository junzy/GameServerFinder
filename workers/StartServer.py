import ConfigParser


def start():
    config = ConfigParser.ConfigParser()
    config.read(["server.cfg"])
    return

if __name__ == "main":
    start()
