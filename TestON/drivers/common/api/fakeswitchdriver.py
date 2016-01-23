import sys
sys.path.append("../")
from drivers.common.apidriver import API

import socket
import time

import random
import pexpect
import struct
import fcntl
import os
import signal
import re
import binascii

import scapy.all as scapy

import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.fakedevice as fakedevice

import testutils
timeout = 30

class FakeSwitchDriver(API):


    def __init__(self):
        super(API, self).__init__()
	self.swList = []
	self.DEBUG = 1
	self.config = message.ofp_switch_config
        self.config.flags = 0
        self.config.miss_send_len = 128

    def connect(self,**connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        self.name = self.options['name']
        self.controllerIP = self.options['controllerIP']
        self.controllerPort = self.options['controllerPort']
        connect_result = super(API,self).connect()
        self.logFileName = main.logdir+"/"+self.name+".session"
        return main.TRUE

    def createSwitch(self, **kwargs):
	if self.DEBUG:
            print "Begin createSwitch"
        print "Connecting switch to controller: " + self.controllerIP +":" + self.controllerPort
        self.sw = fakedevice.FakeSwitch(name='switch0', host=self.controllerIP, port=int(self.controllerPort))
        self.dpid = kwargs.get('dpid', random.randint(1,1000000))
        self.nPorts = kwargs.get('nPorts', 1)
        self.ports = []
        for dataport in range(self.nPorts):
                self.ports.append(dataport)
	self.swList.append(self.sw)
	if self.DEBUG:
            print "End createSwitch"

    def startSwitch(self):
	if self.DEBUG:
            print "Begin startSwitch"
	self.send_msg = message.hello().pack()
	if self.DEBUG:
            print "Sending Hello"
	self.sw.send(self.send_msg)
	self.sw.start()
	if self.DEBUG:
            print "end startSwitch"
   
    def getswList(self):
	return self.swList

    def receiver(self):
        '''
        Parses new messages
        Returns parsed of_msg 
        '''

        if self.DEBUG:
            print "Starting reciever"
        self.sw.msg_cond.acquire()
        if len(self.sw.msgs) == 0 :     # assumes wakeup by notify() -- no stampeed!
            self.sw.msg_cond.wait(timeout)
        if len(self.sw.msgs) == 0 :
            return None    # timed out
        m = self.sw.msgs.pop(0)
        self.sw.msg_cond.release()

        parsedM = parse.of_message_parse(m)
        if self.DEBUG:
            oftype = parsedM.header.type
            print "\n\nNew message from controller:"
            print parsedM
            print "OpenFlow Message type: " + str(oftype)
            print "Recieved raw: \n"+ testutils._b2a(m)
            print "Recieved parsed: \n" + testutils._pktParse(m)
            print "Returning from receiver"
        return parsedM

    def handshake_loop(self, pktCount=20):
        '''
        Completes the OpenFlow handshake
        '''
        count = 0
        while count < pktCount: 
            count += 1
            parsedM = self.receiver()
            if parsedM == None:
                return False
            oftype = parsedM.header.type
            if oftype == 0:
            #Hello
                main.log.debug( "Hello received" )
                exp = message.hello().pack()
                if self.DEBUG:
                    print "Expected: \n"+ testutils._b2a(exp) 
                    print testutils._pktParse(exp)
            elif oftype == 1:
            #Error
                main.log.debug( "Error received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 2:
            #echo Request
                main.log.debug( "Echo Request received" )
                self.echo( parsedM )
                '''
                reply = message.echo_reply()
                reply.data = parsedM.data
                print reply.data
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                self.sw.send(send_msg)
                main.log.debug( "Echo Reply sent" )
                if self.DEBUG:
                    print "Sent: \n"+ testutils._b2a(send_msg) 
                    print testutils._pktParse(send_msg)
                '''
                break
            elif oftype == 3:
            #Echo Reply
                main.log.debug( "Echo Reply received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 4:
            #Vendor
                main.log.debug( "Vendor received" )
                #I dont know this one, and ONOS wont show switch in the topo until it responds to this
                #This may be Nicira vendor extensions
                if self.DEBUG:
                    if parsedM.data:
                        print "data: " + parsedM.data
                reply = message.error()
                reply.code = ofp.OFPBRC_BAD_VENDOR
                reply.type = ofp.OFPET_BAD_REQUEST
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.log.debug( "Bad Vendor sent" )
                print "Got a Vendor message, send \"Bad Vendor\" message to controller"
                self.sw.send(send_msg)
                if self.DEBUG:
                    print "Sent: \n"+ testutils._b2a(send_msg) 
                    print testutils._pktParse(send_msg)
            elif oftype == 5:
            #Features Request
                main.log.debug( "Features Request received" )
                reply = testutils.genFeaturesReply(ports=self.ports, dpid=self.dpid)
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                self.sw.send(send_msg)
                main.log.debug( "Features Reply sent" )
                print "Sent switch_features to controller"
                if self.DEBUG:
                    print "Sent: \n"+ testutils._b2a(send_msg) 
                    print testutils._pktParse(send_msg)

            elif oftype == 6:
            #features Reply
                main.log.debug( "Features Reply received" )
                print "doing nothing with this packet"
                pass#NOTE: Switch shouldn't see this

            elif oftype == 7:
             #get_config_request
                main.log.debug( "Get Config Request received" )
                reply = message.get_config_reply()
                reply.flags = self.config.flags
                reply.miss_send_len = self.config.miss_send_len
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                self.sw.send(send_msg)
                main.log.debug( "Get Config Reply sent" )
                if self.DEBUG:
                    print "Sent: \n"+ testutils._b2a(send_msg) 
                    print testutils._pktParse(send_msg)
            elif oftype == 8:
            #get config reply
                main.log.debug( "Get Config Reply recieved" )
                print "doing nothing with this packet"
                pass#NOTE: Switch shouldn't see this

            elif oftype == 9:
                #set_config
                main.log.debug( "Set Config received" )
                self.config.flags = parsedM.flags
                self.config.miss_send_len = parsedM.miss_send_len
            elif oftype == 10:
            #Packet in
                main.log.debug( "Packet in received" )
                print "doing nothing with this packet"
                pass#NOTE: Switch shouldn't see this
            elif oftype == 11:
            #flow removed
                main.log.debug( "Flow Removed received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 12:
            #Port status
                main.log.debug( "Port Status received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 13:
            #packet out
                main.log.debug( "Packet Out received" )
                if self.DEBUG:
                    if parsedM.data:
                        print "data: " + testutils._b2a(parsedM.data)
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 14:
            #flow mod
                main.log.debug( "Flow Mod received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 15:
            #port mod
                main.log.debug( "Port Mod received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            elif oftype == 16:
            #stats request
                main.log.debug( "Stats Request received" )
                self.stats_reply( parsedM )
            elif oftype == 17:
            #stats reply
                main.log.debug( "Stats Reply received" )
                print "doing nothing with this packet"
                pass#Switch shouldn't be receiving this
            elif oftype == 18:
            #barrier request
                main.log.debug( "Barrier Request received" )
                reply = message.barrier_reply()
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                self.sw.send(send_msg)
                main.log.debug( "Barrier Reply sent" )
                if self.DEBUG:
                    print "Sent: \n"+ testutils._b2a(send_msg) 
                    print testutils._pktParse(send_msg)
            elif oftype == 19:
            #barrier reply
                main.log.debug( "Barrier Reply received" )
                print "doing nothing with this packet"
                pass#TODO: implement
            else: 
                main.log.error( "GOT UNKNOWN OFTYPE" )
                print "doing nothing with this packet"
            #print testutils._b2a(m)
            #print m.type()
            #print testutils._pktParse(m)
                
	if self.DEBUG:
            print "End handshake"
    
    def echo(self, parsedM):
        '''
        Echo Function handles of echo messages
        '''
        if parsedM.header.type == 2:
        #echo Request
            reply = message.echo_reply()
            reply.data = parsedM.data
            main.log.info( reply.data )
            reply.header.xid = parsedM.header.xid
            send_msg = reply.pack()
            self.sw.send(send_msg)
            main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" +
                            testutils._pktParse(send_msg) )
        else:
            #Error
            #TODO: implement this
            return

    def stats_reply(self, parsedM):
        '''
        This function handles responding to stats requests
        '''
        #TODO: respond with real data for stats?
        #Check for the type of stats request
        if parsedM.type == ofp.OFPST_DESC:
            reply = message.desc_stats_reply()
            desc = ofp.ofp_desc_stats()
            desc.mfr_desc = "Jon Hall Switches"
            desc.hw_desc = "Fake Switch"
            desc.sw_desc = "1.0"
            desc.serial_num = "1"
            desc.dp_desc = "A Switch... or is it?"
            reply.stats.append( desc )
        elif parsedM.type == ofp.OFPST_FLOW:
            reply = message.flow_stats_reply()
        elif parsedM.type == ofp.OFPST_AGGREGATE:
            reply = message.aggregate_stats_reply()
        elif parsedM.type == ofp.OFPST_TABLE:
            reply = message.table_stats_reply()
        elif parsedM.type == ofp.OFPST_PORT:
            reply = message.port_stats_reply()
        elif parsedM.type == ofp.OFPST_QUEUE:
            reply = message.queue_stats_reply()
        else:
            # should be vendor only
            #TODO: implement?
            reply = message.ofp_stats_reply()
        reply.header.xid = parsedM.header.xid
        reply.flags = 0
        send_msg = reply.pack()
        self.sw.send(send_msg)
        main.log.debug( "Stats Reply sent" )
        main.log.warn( reply.show() )
        main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) +
                        "\n" + testutils._pktParse(send_msg) )
    '''
    def disconnect(self):
        #for cont in self.contList:
        #    cont.set_dead()
        for sw in self.swList:
            sw.set_dead()
        return main.TRUE
    '''
