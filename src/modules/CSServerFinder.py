#!/usr/bin/env python

import struct, socket, time, json, traceback
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

class CSServerCrawler(DatagramProtocol):
    def startProtocol(self):
        try:
            self.A2A_PING = "i"
            self.A2S_SERVERQUERY_GETCHALLENGE = ""
            self.A2S_INFO = ""
            self.A2S_PLAYER = ""
            self.A2S_RULES = ""
            self.serverDict = {}
            
        except Exception as e:
            print (e)
            traceback.print_exc()

    def loadConfig(config):
        return

    def serverPinger (self):
        try:
            self.dbCursor.execute('delete from cs')
            self.dbConnection.commit()
            self.jsonString = [{'serverIP':u'Server IP' , 'serverPort':u'Port', 'serverName':u'Server Name', 'serverMapName':u'Map', 'serverType':u'Type', 'serverGameName':u'Game Name', 'serverPlayer':u'Players', 'serverPlayerMax':u'Max Players', 'serverLatency':u'Latency'}]
            filePointer = open("../JSON/cs.json", 'w')
            filePointer.write(json.dumps(self.jsonString))
            filePointer.close()
            self.lastSendTime = time.time()
            for self.ipAddr in self.ipRanges:
                for i in xrange(2, 254):
                    self.transport.write(self.magicString, (self.ipAddr % i, self.dstPort))
        except Exception as e:
                print(e)
                traceback.print_exc()

    def startCrawler():
        self.pingerTask = LoopingCall(self.serverPinger)
        self.pingerTask.start("PINGER REPEAT TIME")
        return

    def datagramReceived (self, serverResponse, (host, port)):
        try:
            serverLatency = int((time.time() - self.lastSendTime)*1000)
            serverResponseList = serverResponse.split("\0")
            if len(serverResponseList) < 6 :
                return
            serverIP, serverPort = serverResponseList[0].split("m")[1].split(":")
            serverName = serverResponseList[1]
            serverMapName = serverResponseList[2]
            serverType = serverResponseList[3]
            serverGameName = serverResponseList[4]
            serverPlayer = ord(serverResponseList[5][0])
            serverPlayerMax = ord(serverResponseList[5][1])

#            print ("Server Found" +
#                   "\n\tServer Name : " + serverName +
#                   "\n\tServer IP : " + serverIP + ":" + serverPort +
#                   "\n\tMap Name : " + serverMapName +
#                   "\n\tType : " + serverType +
#                   "\n\tPlayers : " + str(serverPlayer) + "/" + str(serverPlayerMax) +
#                   "\n\tLatency : " + str(serverLatency) + "\n")

            self.jsonString = [dict((self.dbCursor.description[i][0], value) for i, value in enumerate(row)) for row in self.dbCursor.fetchall()]
            self.jsonString.insert(0, {'serverIP':u'Server IP' , 'serverPort':u'Port', 'serverName':u'Server Name', 'serverMapName':u'Map', 'serverType':u'Type', 'serverGameName':u'Game Name', 'serverPlayer':u'Players', 'serverPlayerMax':u'Max Players', 'serverLatency':u'Latency'})
            filePointer = open("../JSON/cs.json", 'w')
            filePointer.write(json.dumps(self.jsonString))
            filePointer.close()
        except Exception as e:
            print(e)
            traceback.print_exc()

def startModule(config):
    crawler = CSServerFinder()
    crawler.loadConfig(config)
    crawler.startCrawler()
    reactor.listenUDP(0, crawler)

def startConfig(config):
    config.add_section("CS")
    value = raw_input("Would you like the scanner for CS to be activated? (Y/N) :")
    while value not in ["Y", "N"]:
       value = raw_input("Please answer with with a (Y/N) :")
    if value == "Y":
        config.set("CS", "bool", "true")
    else :
        config.set("CS", "bool", "false")

if __name__ == "__main__":
    startModule(None)
    reactor.run()
