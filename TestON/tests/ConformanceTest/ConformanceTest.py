'''
	
     TestON is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 2 of the License, or
     (at your option) any later version.

     TestON is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.


'''
class ConformanceTest :

    def __init__(self) :
        self.default = ''
        self.DEBUG = True

    def CASE1(self,main) :

        import time
        main.log.report("Beginning Openflow controller conformance Tests")
        main.case("Starting controller")
        #main.Controller1.stop()
        #main.Controller1.start()
        # TODO: Assert here
        main.case("Testing Controller compatibility")
	
        main.log.warn("Make sure your controller is running and listening for Switch connections!")

        main.step("Start fake switch")
        main.FakeSwitch1.createSwitch()
        main.FakeSwitch1.startSwitch()
        # TODO: Assert here

        main.step("Openflow handshake with switch")
        main.FakeSwitch1.handshake_loop()
        # TODO: Assert here

        # TODO: if handshake fails, exit test early

    def CASE2(self,main):
        import drivers.common.api.testutils as testutils
        import drivers.common.api.oftest.message as message
        main.FakeSwitch1.createSwitch()
        main.FakeSwitch1.startSwitch() #includes Hello's
        main.case("CONF 1.1 - Features Request")
        main.step("Connecting to switch")
        #main.FakeSwitch1.handshake_loop()
        fruit = main.FALSE
        count = 0
        while count < 10:
            parsedM = main.FakeSwitch1.receiver()
            if parsedM == None:
                main.log.error("Did not receive a message")
                break
            if parsedM.header.type == 5:
            #Features Request
                reply = testutils.genFeaturesReply(ports=main.FakeSwitch1.ports, dpid=main.FakeSwitch1.dpid)
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                main.log.info( "Sent switch_features to controller" )
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )
                fruit = main.TRUE
                #TODO: parsedM has no data/body attribute. Is this checked or ignored by oftest?
                break
            elif parsedM.header.type == 2:
            #echo Request
                reply = message.echo_reply()
                reply.data = parsedM.data
                main.log.info( "Echo Request Body:" + reply.data )
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )
            count = count + 1
        utilities.assert_equals(expect=main.TRUE,actual=fruit,
                onpass="Controller sends Features Request on connect",
                onfail="Did not receive a Features Request message")
                
    def CASE3(self,main):
        import drivers.common.api.testutils as testutils
        import drivers.common.api.oftest.message as message
        main.FakeSwitch1.createSwitch()
        main.FakeSwitch1.startSwitch() #includes Hello's
        main.case("CONF 1.2 - Set Config")
        #NOTE: The purpose of this is to see how a controller tries to set switch configs.
        #       This test is limited by controller api's

        #NOTE: Currently we are only testing the default configuration for conformance

        #TODO: automate setting possible switch configurations
        main.step("Checking default's for switch config")
        #main.FakeSwitch1.handshake_loop()
        fruit = main.FALSE
        count = 0
        while count < 10:
            parsedM = main.FakeSwitch1.receiver()
            if parsedM == None:
                main.log.error("Did not receive a message")
                break
            if parsedM.header.type == 9:
                #set_config
                #TODO: check flags and miss_send_len values
                miss_send_len_check = main.FALSE
                if (int(parsedM.miss_send_len) >= 0 and int(parsedM.miss_send_len) <= 65535):
                    main.FakeSwitch1.config.miss_send_len = parsedM.miss_send_len
                    miss_send_len_check = main.TRUE
                else:
                    miss_send_len_check = main.FALSE
                    main.log.error("Miss_Send_Length is incorrect")
                    
                    
                    
                flags_check = main.FALSE
                if (int(parsedM.flags) >= 0 and int(parsedM.flags) <= 65535):
                    #TODO CHECK which values for flags are defined
                    # possibly defined in the structures file
                    main.FakeSwitch1.config.flags = parsedM.flags
                    flags_check = main.TRUE
                else:
                    main.log.error("Flags is incorrect")
                    
                if flags_check == main.TRUE and miss_send_len_check == main.TRUE:
                    fruit = main.TRUE
            elif parsedM.header.type == 2:
            #echo Request
                reply = message.echo_reply()
                reply.data = parsedM.data
                main.log.debug( reply.data )
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )
            elif parsedM.header.type == 5:
            #Features Request
                #nPorts=4
                #ports = []
                #for dataport in range(nPorts):
                #        ports.append(dataport)
                reply = testutils.genFeaturesReply(ports=main.FakeSwitch1.ports, dpid=main.FakeSwitch1.dpid)
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                main.log.info( "Sent switch_features to controller" )
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )

            if fruit == main.TRUE:
                break
            count = count + 1
        utilities.assert_equals(expect=main.TRUE,actual=fruit,
                onpass="Understood Controller's default set config",
                onfail="Did not receive a set config message from the controller")
         
    def CASE4(self,main):
        import drivers.common.api.testutils as testutils
        import drivers.common.api.oftest.message as message
        main.FakeSwitch1.createSwitch()
        main.FakeSwitch1.startSwitch() #includes Hello's
        main.case("CONF 1.3 - get config request")
        #TODO Make an API request if available

        main.step("Scanning for Get Config request")
        #main.FakeSwitch1.handshake_loop()
        fruit = main.FALSE
        count = 0
        while count < 10:
            parsedM = main.FakeSwitch1.receiver()
            if parsedM == None:
                main.log.error("Did not receive a message")
                break
            if parsedM.header.type == 7:
             #get_config_request
                reply = message.get_config_reply()
                reply.flags = main.FakeSwitch1.config.flags
                reply.miss_send_len = main.FakeSwitch1.config.miss_send_len
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.log.info( "Sending Get Config Reply" )
                main.FakeSwitch1.sw.send(send_msg)
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )
                fruit = main.TRUE
                #TODO: parsedM has no data/body attribute. Is this checked or ignored by oftest?
                break
            elif parsedM.header.type == 2:
            #echo Request
                reply = message.echo_reply()
                reply.data = parsedM.data
                main.log.debug( reply.data )
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )
            elif parsedM.header.type == 5:
            #Features Request
                reply = testutils.genFeaturesReply(ports=main.FakeSwitch1.ports, dpid=main.FakeSwitch1.dpid)
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                main.log.info( "Sent switch_features to controller" )
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) ) 
             

            count = count + 1
        utilities.assert_equals(expect=main.TRUE,actual=fruit,
                onpass="Received get config request from controller",
                onfail="Did not receive a get config request from the controller")
         
    def CASE5(self,main):
        import drivers.common.api.testutils as testutils
        import drivers.common.api.oftest.message as message
        main.FakeSwitch1.createSwitch()
        main.FakeSwitch1.startSwitch() #includes Hello's
        main.case("CONF 1.4a - Flow mod: proactive add")
        #NOTE this test is limited by controller API's
        main.step("Addign a flow to the switch")
        main.FakeSwitch1.handshake_loop()
        fruit = main.FALSE
        #TODO: For values in flow mod fields, loop through controller api to send flow mods to the switch and check if values sent = values told to controller
        #NOTE controller doesnt have to use add
        #NOTE what happens when you input wrong values to the controller
        #TODO check type of flow mod
        #TODO check buffer_id
        #TODO check cookie
        count = 0
        while count < 10:
            parsedM = main.FakeSwitch1.receiver()
            if parsedM == None:
                main.log.error("Did not receive a message")
                break
            if parsedM.header.type == 14:
             #flow_mod

                fruit = main.TRUE
                break
            elif parsedM.header.type == 2:
            #echo Request
                reply = message.echo_reply()
                reply.data = parsedM.data
                main.log.info( reply.data )
                reply.header.xid = parsedM.header.xid
                send_msg = reply.pack()
                main.FakeSwitch1.sw.send(send_msg)
                if main.FakeSwitch1.DEBUG:
                    main.log.debug( "Sent: \n"+ testutils._b2a(send_msg) + "\n" + testutils._pktParse(send_msg) )
            count = count + 1
        utilities.assert_equals(expect=main.TRUE,actual=fruit,
                onpass="Recieved Flow Mod: add from the controller",
                onfail="Incorrect flow mod message from the controller")
         
