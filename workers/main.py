#!/usr/bin/env python
from twisted.internet import reactor

from CSServerFinder import CSServerFinder

if __name__ == "__main__":
    print ("Staring Servers")
    reactor.listenUDP(0, CSServerFinder())
    reactor.run()
