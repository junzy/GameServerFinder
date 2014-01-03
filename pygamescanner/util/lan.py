#! /usr/bin/env python
# coding=utf-8

import netifaces
import netaddr
import socket


def get_all_broadcast_address():
    broadcast_address_list = []
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        if socket.AF_INET in addresses:
            ip_info = addresses[socket.AF_INET][0]
            address = ip_info['addr']
            netmask = ip_info['netmask']
            network_address = netaddr.IPNetwork('%s/%s' % (address, netmask))
            broadcast_address = netaddr.IPNetwork('%s/%s' % (network_address.network, netmask))
            if not str(broadcast_address).startswith('127'):
                broadcast_address_list.append(str(broadcast_address))

__all__ = ['get_all_broadcast_address']
