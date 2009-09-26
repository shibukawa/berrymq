# -*- coding: utf-8 -*-

import netgrowl
import berrymq
from socket import AF_INET, SOCK_DGRAM, socket

class GrowlAdapter(object):
    def __init__(self, id_filter, application_name="berryMQ"):
        berrymq.regist_method(id_filter, self.listener)
        self.addr = ("localhost", netgrowl.GROWL_UDP_PORT)
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.application_name = application_name
        packet = netgrowl.GrowlRegistrationPacket(application_name)
        packet.addNotification()
        self.socket.sendto(packet.payload(), self.addr)

    def format(self, message):
        argstr = ", ".join([str(arg) for arg in message.args])
        kwargstr = ", ".join(["%s:%s" % (str(key), str(value))
                             for key, value in sorted(message.kwargs.items())])
        return "[%s], {%s}" % (argstr, kwargstr)
        
    def listener(self, message):
        desc = self.format(message)
        packet = netgrowl.GrowlNotificationPacket(
            self.application_name, title=message.id, description=desc)
        self.socket.sendto(packet.payload(), self.addr)
