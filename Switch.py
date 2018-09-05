# Project 2 for OMS6250
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015


from Message import *
from StpSwitch import *

class Switch(StpSwitch):

    class TopoState(object):
        def __init__(self, switchID, neighbors):
            self.root = switchID
            self.distance = 0
            self.linksMap = {} #see dict comprehension {n: True for n in neighbors}
            for n in neighbors:
               self.linksMap[n] = [False, True]   #a list contain Y/N of pathThrough, and Y/N of activeLinks
            self.switchThrough = switchID #which switch do I go through to get to the root


    def __init__(self, idNum, topolink, neighbors):
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)

        #TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.
        self.state = Switch.TopoState(self.switchID, self.links)
        self.state.root = idNum

# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
    def send_initial_messages(self):
        #TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
	#      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)

        for id in self.links:
            self.send_message(Message(self.switchID, 0, self.switchID, id, False))

        return

    def send_messages(self):
        for id in self.links:
            pathThroughNeighbor = False
            if (self.state.switchThrough == id):
                pathThroughNeighbor = True
            #if self.state.linksMap[id][1]:
            self.send_message(Message(self.state.root,
                                   self.state.distance, self.switchID, id,
                                    pathThroughNeighbor))

    def process_message(self, message):
        #TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.
        # see 16:35

        # if the current switchID is greater than the root from the message, update
        # the root, distance to the root, activeLinks, and send new messages
        #resetTopo = False
        print(self.switchID, "switch", self.state.root, "state root ", message.root, ", message root", message.origin, "origin", message.distance, 'distance', self.state.switchThrough, 'switchThrough')
        self.state.linksMap[message.origin][0] = message.pathThrough
        if self.state.linksMap[message.origin][0]: #if path through set active
            self.state.linksMap[message.origin][1] = True

        #print("found a message that needs to be updated from", message.origin)
        if (self.state.root > message.root):
            #resetTopo = True
            self.state.root = message.root
            self.state.distance = message.distance + 1
            self.state.switchThrough = message.origin
            # send messages that the state has been updated
            for key in self.state.linksMap:
                #if neigh path through this switch
                if self.state.linksMap[key][0]:
                    self.state.linksMap[key][1] = True
                # if the neighbour is my switchthrough
                elif self.state.switchThrough == key:
                    self.state.linksMap[key][1] = True
                else:
                    self.state.linksMap[key][1] = False
            print "I get to the case where smaller root is found"
            self.send_messages()

        elif (self.state.root == message.root and self.state.distance > message.distance+1):
            self.state.distance = message.distance + 1
            # active link is next hop to the root
            # self.state.linksMap[message.origin] = [False, True]
            self.state.switchThrough = message.origin
            for key in self.state.linksMap:
                if (self.state.linksMap[key][0]):
                    self.state.linksMap[key][1] = True
                # if the neighbour is my switchthrough
                elif (self.state.switchThrough == key):
                    self.state.linksMap[key][1] = True
                else:
                    self.state.linksMap[key][1] = False
            # send messages that the state has been updated
            print "I get to the case where root is the same while distance is different"
            self.send_messages()

        elif (self.state.root == message.root and self.state.distance == message.distance + 1
              and message.origin < self.state.switchThrough):
            # active link is next hop to the root
            # self.state.linksMap[message.origin] = [False, True]
            self.state.switchThrough = message.origin
            for key in self.state.linksMap:
                if (self.state.linksMap[key][0]):
                    self.state.linksMap[key][1] = True
                elif (self.state.switchThrough == key):
                    self.state.linksMap[key][1] = True
                else:
                    self.state.linksMap[key][1] = False
            # send messages that the state has been updated
            print "I get to the case where root and distance are the same, while sender is a better path"
            self.send_messages()

        else:
            for key in self.state.linksMap:
                if (self.state.linksMap[key][0]):
                    self.state.linksMap[key][1] = True
                elif (self.state.switchThrough == key):
                    self.state.linksMap[key][1] = True
                else:
                    self.state.linksMap[key][1] = False


    def generate_logstring(self):
        #TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.

        logString = ""
        print self.switchID
        print self.state.linksMap
        for key in sorted(self.state.linksMap.keys()):
            if self.state.linksMap[key][1] == True: #active
                logString += str(self.switchID) + " - " + str(key) +", "
        logString = logString[:-2]

        return logString
