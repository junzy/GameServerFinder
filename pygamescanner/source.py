#! /usr/bin/env python
# coding=utf-8

import struct
import time
import json
import logging
import os
import socket

from netaddr import IPNetwork
from netaddr.core import AddrFormatError
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from pygamescanner.util.packet import Packet
from pygamescanner.util.lan import get_all_broadcast_address

module_name = 'source'
module_title = 'Source'


class Source(DatagramProtocol):
    def __init__(self):
        # packet info
        self.packet_size = 1400
        self.whole_packet = -1
        self.split_packet = -2

        # a2s_info
        self.a2s_info_query_byte = ord('T')
        self.a2s_info_query_str = 'Source Engine Query'
        self.a2s_info_reply_byte = ord('I')

        # a2s_player
        self.a2s_player_query_byte = ord('U')
        self.a2s_player_reply_byte = ord('D')

        # a2s_rules
        self.a2s_rules_query_byte = ord('V')
        self.a2s_rules_reply_byte = ord('E')

        # a2s_challenge
        self.a2s_challenge_query_byte = -1
        self.a2s_challenge_reply_byte = ord('A')

        self.server_dict = {}
        self.last_send_time = 0
        self.logger = logging.getLogger(module_name)

        # Define the defaults
        self.json_root = "../www/JSON/"
        self.ip_ranges = [IPNetwork("10.1.33.0/24"), IPNetwork("10.1.34.0/24")]
        self.port_list = [27015]
        self.ping_delay = 10.0
        self.module_enabled = True

    def load_config(self, config):
        module_enabled = config.get("cs", "module_enabled")
        if module_enabled.lower() == "false":
            self.module_enabled = False
            return
        else:
            self.json_root = config.get("global", "json_root")
            self.module_enabled = True

        ip_ranges = config.get("cs", "ip_ranges")
        if ip_ranges:
            ip_ranges = json.loads(ip_ranges)
            self.ip_ranges = []
            for ip_range in ip_ranges:
                self.ip_ranges.append(IPNetwork(ip_range))

        port_list = config.get("cs", "port_list")
        if port_list:
            self.port_list = json.loads(port_list)

        ping_delay = config.get("cs", "ping_delay")
        if ping_delay:
            self.ping_delay = float(ping_delay)

    def start_crawler(self):
        if self.module_enabled:
            reactor.listenUDP(0, self)
            self.server_pinger()

    def server_pinger(self):
        try:
            file_pointer = open(os.path.abspath(self.json_root) + "/cs.json", 'w')
            file_pointer.write(json.dumps(self.server_dict))
            file_pointer.close()

            keys = self.server_dict.keys()
            current_time = time.time()
            for key in keys:
                if (current_time - self.server_dict[key]["lastTS"]) > (self.ping_delay + 1):
                    del self.server_dict[key]

            keys = self.server_dict.keys()
            for key in keys:
                ip_address, port = key.split(":")
                self.server_dict[key]["lastTS"] = time.time()
                self.server_dict[key]["latency"] = "CHECKING"
                self.send_a2s_info(ip_address, port)

            counter = 0
            for ip_range in self.ip_ranges:
                ip_list = list(ip_range[1:-1])
                for ip_address in ip_list:
                    for port in self.port_list:
                        self.send_a2s_info(str(ip_address), port)
                    if counter == 64:
                        time.sleep(0.1)
                        counter = 0
                    counter += 1
        except socket.error as e:
            pass
        except Exception as e:
            if self.logger.isEnabledFor(logging.ERROR):
                self.logger.error(e)
        finally:
            reactor.callLater(self.ping_delay, self.server_pinger)

    def datagramReceived(self, server_response, server_info):
        try:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("Packet received: \n" + server_response)

            packet = Packet(server_response)

            first_long = packet.get_long()
            first_byte = packet.get_byte()

            if first_long == -1 and (first_byte == ord('m') or first_byte == ord('I')):
                self.recv_a2s_info(server_response, server_info)
                return

            if first_byte == self.a2s_challenge_reply_byte:
                self.recv_a2s_challenge(server_response, server_info)
                return

            if first_byte == self.a2s_player_reply_byte:
                self.recv_a2s_player(server_response, server_info)
                return

            print ' '.join(('%#04x' % ord(c) for c in server_response))
        except Exception as e:
            if self.logger.isEnabledFor(logging.ERROR):
                self.logger.error(e)

    def send_a2s_info(self, host, port):
        packet = Packet()
        packet.put_long(self.whole_packet)
        packet.put_byte(self.a2s_info_query_byte)
        packet.put_string(self.a2s_info_query_str)
        self.transport.write(packet.getvalue(), (host, port))

    def recv_a2s_info(self, packet, (host, port)):
        if (str(host) + ":" + str(port)) in self.server_dict and \
                self.server_dict[(str(host) + ":" + str(port))]["latency"] == "CHECKING":
            self.server_dict[(str(host) + ":" + str(port))]["latency"] = \
                int((time.time() - self.server_dict[(str(host) + ":" + str(port))]["lastTS"]) * 1000)
        else:
            self.server_dict[(str(host) + ":" + str(port))] = {}
            self.server_dict[(str(host) + ":" + str(port))]["latency"] = "Unknown"
            self.server_dict[(str(host) + ":" + str(port))]["lastTS"] = time.time()
            self.server_dict[(str(host) + ":" + str(port))]["challenge"] = None

        packet = Packet(packet)
        packet.get_long()
        self.server_dict[(str(host) + ":" + str(port))]['type'] = chr(packet.get_byte())
        if self.server_dict[(str(host) + ":" + str(port))]['type'] == "I":
            self.server_dict[(str(host) + ":" + str(port))]['version'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['serverName'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['map'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['gameDir'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['gameDesc'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['appid'] = packet.get_short()
            self.server_dict[(str(host) + ":" + str(port))]['numPlayers'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['maxPlayers'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['numBots'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['dedicated'] = chr(packet.get_byte())
            self.server_dict[(str(host) + ":" + str(port))]['os'] = chr(packet.get_byte())
            self.server_dict[(str(host) + ":" + str(port))]['passworded'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['secure'] = chr(packet.get_byte())
            self.server_dict[(str(host) + ":" + str(port))]['gameVersion'] = packet.get_string()

            try:
                edf = packet.get_byte()
                self.server_dict[(str(host) + ":" + str(port))]['edf'] = edf

                if edf & 0x80:
                    self.server_dict[(str(host) + ":" + str(port))]['port'] = packet.get_short()
                if edf & 0x10:
                    self.server_dict[(str(host) + ":" + str(port))]['steamid'] = packet.get_long_long()
                if edf & 0x40:
                    self.server_dict[(str(host) + ":" + str(port))]['specPort'] = packet.get_short()
                    self.server_dict[(str(host) + ":" + str(port))]['specName'] = packet.get_string()
                if edf & 0x20:
                    self.server_dict[(str(host) + ":" + str(port))]['gameID'] = packet.get_string()
            except struct.error:
                pass

        else:
            self.server_dict[(str(host) + ":" + str(port))]['gameIP'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['serverName'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['map'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['gameDir'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['gameDesc'] = packet.get_string()
            self.server_dict[(str(host) + ":" + str(port))]['numPlayers'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['maxPlayers'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['version'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['dedicated'] = chr(packet.get_byte())
            self.server_dict[(str(host) + ":" + str(port))]['os'] = chr(packet.get_byte())
            self.server_dict[(str(host) + ":" + str(port))]['passworded'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['isMod'] = packet.get_byte()
            self.server_dict[(str(host) + ":" + str(port))]['secure'] = chr(packet.get_byte())
            self.server_dict[(str(host) + ":" + str(port))]['numBots'] = packet.get_byte()

            if self.server_dict[(str(host) + ":" + str(port))]['isMod'] == 1:
                self.server_dict[(str(host) + ":" + str(port))]['URLInfo'] = packet.get_string()
                self.server_dict[(str(host) + ":" + str(port))]['URLDL'] = packet.get_string()
                self.server_dict[(str(host) + ":" + str(port))]['nul'] = packet.get_byte()
                self.server_dict[(str(host) + ":" + str(port))]['modVersion'] = packet.get_long()
                self.server_dict[(str(host) + ":" + str(port))]['modSize'] = packet.get_long()
                self.server_dict[(str(host) + ":" + str(port))]['svOnly'] = packet.get_byte()
                self.server_dict[(str(host) + ":" + str(port))]['CIDLL'] = packet.get_byte()

        self.send_a2s_player(host, port)

    def send_a2s_player(self, host, port):
        if self.server_dict[(str(host) + ":" + str(port))]['challenge'] is None:
            self.send_a2s_challenge(host, port)
            return

        packet = Packet()
        packet.put_long(self.whole_packet)
        packet.put_byte(self.a2s_player_query_byte)
        packet.put_long(self.server_dict[(str(host) + ":" + str(port))]['challenge'])
        self.transport.write(packet.getvalue(), (host, port))

    def recv_a2s_player(self, packet, (host, port)):
        packet = Packet(packet)
        packet.get_long()
        packet.get_byte()
        num_players = packet.get_byte()

        self.server_dict[(str(host) + ":" + str(port))]['players'] = []

        try:
            for _ in xrange(num_players):
                player = dict()
                player['index'] = packet.get_byte()
                player['name'] = packet.get_string()
                player['kills'] = packet.get_long()
                player['time'] = packet.get_float()
                self.server_dict[(str(host) + ":" + str(port))]['players'].append(player)
        except struct.error:
            pass

    def send_a2s_challenge(self, host, port):
        packet = Packet()
        packet.put_long(self.whole_packet)
        packet.put_byte(self.a2s_player_query_byte)
        packet.put_long(self.a2s_challenge_query_byte)
        self.transport.write(packet.getvalue(), (host, port))

    def recv_a2s_challenge(self, packet, (host, port)):
        packet = Packet(packet)
        packet.get_long()
        packet.get_byte()
        self.server_dict[(str(host) + ":" + str(port))]['challenge'] = packet.get_long()
        self.send_a2s_player(host, port)


def start_config(config):
    module_config = dict()
    module_config["module_name"] = module_name
    module_config["module_title"] = module_title

    config.add_section(module_config["module_name"])
    while True:
        value = raw_input("Would you like the scanner for Source to be activated? (Y/N) :")
        if value.lower() in ['y', 'yes']:
            config.set(module_config["module_name"], "module_enabled", "true")
            break
        elif value.lower() in ['n', 'no']:
            config.set(module_config["module_name"], "module_enabled", "false")
            return module_config
        else:
            print "Please enter either y(es) or n(o)"

    print "Please enter the IP ranges to be scanned. In the form subnet/mask, eg. 10.1.1.0/24. Blank input to stop :"
    ip_ranges = []
    while True:
        if len(ip_ranges) == 0:
            value = raw_input("Enter IP range/Blank to use default : ")
        else:
            value = raw_input("Enter IP range : ")
        value = value.strip()
        if value == "":
            if len(ip_ranges) < 1:
                ip_ranges = get_all_broadcast_address()
            config.set(module_config["module_name"], "ip_ranges", json.dumps(ip_ranges))
            break
        else:
            try:
                IPNetwork(value)
                ip_ranges.append(value)
            except ValueError:
                print value, "is not a valid IP range"
            except AddrFormatError:
                print value, "is not a valid IP range"

    print "Please enter the ports to scan on each host. Press enter to use default. Enter 0 to stop :"
    port_list = []
    while True:
        value = raw_input("Enter port no. : ")
        value = value.strip()
        if value == "":
            if 27015 not in port_list:
                port_list.append(27015)
            config.set(module_config["module_name"], "port_list", json.dumps(port_list))
            break
        elif value == "0":
            config.set(module_config["module_name"], "port_list", json.dumps(port_list))
            break
        else:
            try:
                test = int(value)
                if 0 < test < 65536:
                    port_list.append(value)
                else:
                    print "Please enter a value between 0 and 65535"
            except ValueError:
                print value, "is not a valid number. Please enter a value between 0 and 65535"

    print "Please enter the delay for checking the server. Between 1 and 3600 Seconds :"
    while True:
        value = raw_input("Enter delay : ")
        try:
            test = int(value)
            if 1 <= test <= 3600:
                config.set(module_config["module_name"], "ping_delay", value)
                break
            else:
                print "Please enter a number between 1 and 3600"
        except ValueError:
            print value, "is not a valid number. Please enter a number between 1 and 3600"
    return module_config


def start_module(config):
    logger = logging.getLogger(module_name)
    if logger.isEnabledFor(logging.INFO):
        logger.info("Starting Source Module")
    crawler = Source()
    crawler.load_config(config)
    crawler.start_crawler()


if __name__ == "__main__":
    start_module(None)
    reactor.run()

__all__ = ["Source", "start_config", "start_module"]
