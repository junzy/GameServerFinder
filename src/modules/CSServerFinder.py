#!/usr/bin/env python

import struct, socket, time, json, traceback, StringIO
from netaddr import IPNetwork
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

PACKETSIZE=1400

WHOLE=-1
SPLIT=-2

# A2S_INFO
A2S_INFO = ord('T')
A2S_INFO_STRING = 'Source Engine Query'
A2S_INFO_REPLY = ord('I')

# A2S_PLAYER
A2S_PLAYER = ord('U')
A2S_PLAYER_REPLY = ord('D')

# A2S_RULES
A2S_RULES = ord('V')
A2S_RULES_REPLY = ord('E')

# S2C_CHALLENGE
CHALLENGE = -1
S2C_CHALLENGE = ord('A')

class SourceQueryPacket(StringIO.StringIO):
    # putting and getting values
    def putByte(self, val):
        self.write(struct.pack('<B', val))

    def getByte(self):
        return struct.unpack('<B', self.read(1))[0]

    def putShort(self, val):
        self.write(struct.pack('<h', val))

    def getShort(self):
        return struct.unpack('<h', self.read(2))[0]

    def putLong(self, val):
        self.write(struct.pack('<l', val))

    def getLong(self):
        return struct.unpack('<l', self.read(4))[0]

    def getLongLong(self):
        return struct.unpack('<Q', self.read(8))[0]

    def putFloat(self, val):
        self.write(struct.pack('<f', val))

    def getFloat(self):
        return struct.unpack('<f', self.read(4))[0]

    def putString(self, val):
        self.write(val + '\x00')

    def getString(self):
        val = self.getvalue()
        start = self.tell()
        end = val.index('\0', start)
        val = val[start:end]
        self.seek(end+1)
        return val

class CSServerFinder(DatagramProtocol):
    def __init__(self):
        try:
            self.loadDefaults()
            self.serverDict = {}
            self.lastSendTime = 0
        except Exception as e:
            print (e)
            traceback.print_exc()
            
    def loadDefaults(self):
        self.jsonRoot = "../www/JSON/"
        self.ipRanges = [IPNetwork("10.1.33.0/24"), IPNetwork("10.1.34.0/24")]
        self.portList = [27015]
        self.pingDelay = 10.0
        self.moduleEnabled = True
    
    def loadConfig(self, config):
        moduleEnabled = config.get("cs", "moduleEnabled")
        if moduleEnabled == "False" :
            self.moduleEnabled = False
            return
        else :
            self.jsonRoot = config.get("global", "jsonRoot")
            self.moduleEnabled = True
            
        ipRanges = config.get("cs", "ipRanges")
        if ipRanges :
            ipRanges = json.loads(ipRanges)
            self.ipRanges = []
            for ipRange in ipRanges:
                self.ipRanges.append(IPNetwork(ipRange))
            
        portList = config.get("cs", "portList")
        if portList :
            self.portList = json.loads(portList)
            
        pingDelay = config.get("cs", "pingDelay")
        if pingDelay :
            self.pingDelay = float(pingDelay)

    def startCrawler(self):
        if self.moduleEnabled :
            reactor.listenUDP(0, self)
            self.pingerTask = LoopingCall(self.serverPinger)
            self.pingerTask.start(self.pingDelay)

    def serverPinger(self):
        try:
            filePointer = open(self.jsonRoot + "cs.json", 'w')
            filePointer.write(json.dumps(self.serverDict))
            filePointer.close()
            
            for keys in self.serverDict:
                if time.time() - self.serverDict[keys]["lastTS"] > 20:
                    del self.serverDict[key]
            print self.serverDict
            
            self.lastSendTime = time.time()
            counter = 0
            for ipRange in self.ipRanges:
                ipList = list(ipRange[1:-1])
                for ipAddr in ipList:
                    for port in self.portList:
                        if(((str(ipAddr) + ":" + str(port)) in self.serverDict)) :
                            self.serverDict[(str(ipAddr) + ":" + str(port))]["lastTS"] = time.time()
                        self._send_A2S_INFO(str(ipAddr), port)
                    if counter == 64:
                        time.sleep(0)
                        counter = 0
                    counter += 1
        except Exception as e:
                print(e)
                traceback.print_exc()

    def datagramReceived(self, serverResponse, serverInfo):
        try:
            packet = SourceQueryPacket(serverResponse)
            firstLong = packet.getLong()
            firstByte = packet.getByte()
            if firstLong == -1 and (firstByte == ord('m') or firstByte == ord('I')):
                self._recv_A2S_INFO(serverResponse, serverInfo)
                return
            
            if firstByte == S2C_CHALLENGE:
                self._recv_A2S_CHALLENGE(serverResponse, serverInfo)
                return
            
            if firstByte == A2S_PLAYER_REPLY:
                self._recv_A2S_PLAYER(serverResponse, serverInfo)
                return
            
            print ' '.join(('%#04x' % ord(c) for c in serverResponse))
        except Exception as e:
            print(e)
            traceback.print_exc()
    
    def _send_A2S_INFO(self, host, port):
        packet = SourceQueryPacket()
        packet.putLong(WHOLE)
        packet.putByte(A2S_INFO)
        packet.putString(A2S_INFO_STRING)
        self.transport.write(packet.getvalue(), (host, port))
    
    def _recv_A2S_INFO(self, packet, (host, port)):
        if (str(host) + ":" + str(port)) in self.serverDict:
            self.serverDict[(str(host) + ":" + str(port))]["latency"] = int((time.time() - self.serverDict[(str(host) + ":" + str(port))]["lastTS"])*1000)
        else :
            self.serverDict[(str(host) + ":" + str(port))] = {}
            self.serverDict[(str(host) + ":" + str(port))]["latency"] = int((time.time() - self.lastSendTime)*1000)
            self.serverDict[(str(host) + ":" + str(port))]["lastTS"] = time.time()
            self.serverDict[(str(host) + ":" + str(port))]["challenge"] = None

        packet = SourceQueryPacket(packet)
        discard = packet.getLong()
        self.serverDict[(str(host) + ":" + str(port))]['type'] = chr(packet.getByte())
        if self.serverDict[(str(host) + ":" + str(port))]['type'] == "I":
            self.serverDict[(str(host) + ":" + str(port))]['version'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['serverName'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['map'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['gameDir'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['gameDesc'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['appid'] = packet.getShort()
            self.serverDict[(str(host) + ":" + str(port))]['numPlayers'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['maxPlayers'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['numBots'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['dedicated'] = chr(packet.getByte())
            self.serverDict[(str(host) + ":" + str(port))]['os'] = chr(packet.getByte())
            self.serverDict[(str(host) + ":" + str(port))]['passworded'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['secure'] = chr(packet.getByte())
            self.serverDict[(str(host) + ":" + str(port))]['gameVersion'] = packet.getString()
            
            try:
                edf = packet.getByte()
                self.serverDict[(str(host) + ":" + str(port))]['edf'] = edf

                if edf & 0x80:
                    self.serverDict[(str(host) + ":" + str(port))]['port'] = packet.getShort()
                if edf & 0x10:
                    self.serverDict[(str(host) + ":" + str(port))]['steamid'] = packet.getLongLong()
                if edf & 0x40:
                    self.serverDict[(str(host) + ":" + str(port))]['specPort'] = packet.getShort()
                    self.serverDict[(str(host) + ":" + str(port))]['specName'] = packet.getString()
                if edf & 0x20:
                    self.serverDict[(str(host) + ":" + str(port))]['gameID'] = packet.getString()
            except:
                pass

        else :
            self.serverDict[(str(host) + ":" + str(port))]['gameIP'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['serverName'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['map'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['gameDir'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['gameDesc'] = packet.getString()
            self.serverDict[(str(host) + ":" + str(port))]['numPlayers'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['maxPlayers'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['version'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['dedicated'] = chr(packet.getByte())
            self.serverDict[(str(host) + ":" + str(port))]['os'] = chr(packet.getByte())
            self.serverDict[(str(host) + ":" + str(port))]['passworded'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['isMod'] = packet.getByte()
            self.serverDict[(str(host) + ":" + str(port))]['secure'] = chr(packet.getByte())
            self.serverDict[(str(host) + ":" + str(port))]['numBots'] = packet.getByte()
            
            if self.serverDict[(str(host) + ":" + str(port))]['isMod'] == 1:
                self.serverDict[(str(host) + ":" + str(port))]['URLInfo'] = packet.getString()
                self.serverDict[(str(host) + ":" + str(port))]['URLDL'] = packet.getString()
                self.serverDict[(str(host) + ":" + str(port))]['nul'] = packet.getByte()
                self.serverDict[(str(host) + ":" + str(port))]['modVersion'] = packet.getLong()
                self.serverDict[(str(host) + ":" + str(port))]['modSize'] = packet.getLong()
                self.serverDict[(str(host) + ":" + str(port))]['svOnly'] = packet.getByte()
                self.serverDict[(str(host) + ":" + str(port))]['CIDLL'] = packet.getByte()
            
        self._send_A2S_PLAYER(host, port)
            
    def _send_A2S_PLAYER(self, host, port):
        if self.serverDict[(str(host) + ":" + str(port))]['challenge'] == None:
            self._send_A2S_CHALLENGE(host, port)
            return
        
        packet = SourceQueryPacket()
        packet.putLong(WHOLE)
        packet.putByte(A2S_PLAYER)
        packet.putLong(self.serverDict[(str(host) + ":" + str(port))]['challenge'])
        self.transport.write(packet.getvalue(), (host, port))

    def _recv_A2S_PLAYER(self, packet, (host, port)):
        packet = SourceQueryPacket(packet)
        discard = packet.getLong()
        discard = packet.getByte()
        numPlayers = packet.getByte()
        
        self.serverDict[(str(host) + ":" + str(port))]['players'] = []
        
        try:
            for i in xrange(numPlayers):
                player = {}
                player['index'] = packet.getByte()
                player['name'] = packet.getString()
                player['kills'] = packet.getLong()
                player['time'] = packet.getFloat()
                self.serverDict[(str(host) + ":" + str(port))]['players'].append(player)
        except:
            pass

    def _send_A2S_CHALLENGE(self, host, port):
        packet = SourceQueryPacket()
        packet.putLong(WHOLE)
        packet.putByte(A2S_PLAYER)
        packet.putLong(CHALLENGE)
        self.transport.write(packet.getvalue(), (host, port))
        
    def _recv_A2S_CHALLENGE(self, packet, (host, port)):
        packet = SourceQueryPacket(packet)
        discard = packet.getLong()
        discard = packet.getByte()
        self.serverDict[(str(host) + ":" + str(port))]['challenge'] = packet.getLong()
        self._send_A2S_PLAYER(host, port)

def startConfig(config):
    moduleConfig = {}
    moduleConfig["moduleName"] = "cs"
    moduleConfig["moduleTitle"] = "CS"
    moduleConfig["defaultEnabled"] = "true"
    moduleConfig["refreshTime"] = "10"
    
    config.add_section("cs")
    while True:
        value = raw_input("Would you like the scanner for Counter Strike to be activated? (Y/N) :")
        if value == "Y" or value == "y" :
            config.set("cs", "moduleEnabled", "true")
            break
        elif value == "N" or value == "n" :
            config.set("cs", "moduleEnabled", "false")
            return moduleConfig
        else :
            print "Please enter either Y or N"
    
    print "Please enter the IP ranges to be scanned. In the form subnet/mask, eg. 10.1.1.0/24. Blank input to stop :"
    ipRanges = []
    while True:
        value = raw_input("Enter IP range : ")
        if value == "":
            config.set("cs", "ipRanges", json.dumps(ipRanges))
            break
        try:
            test = IPNetwork(value)
            ipRanges.append(value)
        except:
            print value, "is not a valid IP range"
            
    print "Please enter the ports to scan on each host. Press enter to use default. Enter 0 to stop : "
    portList = []
    while True:
        value = raw_input("Enter port no. : ")
        if value == "":
            portList.append(27015)
            config.set("cs", "portList", json.dumps(portList))
            break
        elif value == "0":
            config.set("cs", "portList", json.dumps(portList))
            break
        else :
            try :
                test = int(value)
                if test < 65536 and test > 0 :
                    portList.append(value)
                else :
                    print "Please enter a value between 0 and 65535"
            except:
                print value, "is not a valid number"
    
    print "Please enter the delay for checking the server. Between 1 and 3600 Seconds :"
    while True:
        value = raw_input("Enter delay : ")
        try :
            test = int(value)
            if test >= 1 and test <= 3600:
                config.set("cs", "pingDelay", value)
                moduleConfig["refreshTime"] = value
                break
            else :
                print "Please enter a number between 1 and 3600"
        except :
            print value, "is not a valid number"
    return moduleConfig

def startModule(config):
    crawler = CSServerFinder()
    crawler.loadConfig(config)
    crawler.startCrawler()

if __name__ == "__main__":
    startModule(None)
    reactor.run()
