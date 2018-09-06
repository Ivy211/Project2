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
            #assume the root is itself, and therefore the path through is false
            self.send_message(Message(self.switchID, 0, self.switchID, id, False))

        return

    def send_messages(self):
        for id in self.links:
            # if the neighbour is not the switch through, self doesn't need to path through to be true
            pathThroughNeighbor = False
            if (self.state.switchThrough == id):
                pathThroughNeighbor = True

            # the following if statement is commented out since we not only need to send out messages to neighbours where activelinks are
            # true, but also need to actually send to all neighbours.
            # The reason is for instance there is a switch 6, which needs 7 to go to root 1. The active link between 6 and 7 were set to false
            # at a certain point since when 7 sends the initial message to 6, 6 believes it has a better root (6), and therefore didn't update its root
            # and set the active link to 7 as false. When 7 receives message and realizes there's a better root (1) exists, it deactivated the
            # link to 6. However, if we don't send a message to 6 in this case, 6 will never know a better root (1) exist.
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

        print(self.switchID, "switch", self.state.root, "state root ", message.root, ", message root", message.origin, "origin", message.distance, 'distance', self.state.switchThrough, 'switchThrough')
        self.state.linksMap[message.origin][0] = message.pathThrough

        # if state finds a better root, update root, distance, switchThrough, resetTopo, and send a message
        if (self.state.root > message.root):
            self.state.root = message.root
            self.state.distance = message.distance + 1
            self.state.switchThrough = message.origin
            # send messages that the state has been updated
            self.resetTopo()
            print "I get to the case where smaller root is found"
            self.send_messages()

        # if state finds a better route (shorter distance) to go the root, update distance, switchThrough, resetTopo, and send a message
        elif (self.state.root == message.root and self.state.distance > message.distance+1):
            self.state.distance = message.distance + 1
            self.state.switchThrough = message.origin
            self.resetTopo()
            # send messages that the state has been updated
            print "I get to the case where root is the same while distance is different"
            self.send_messages()

        # if state finds a better route (same distance but the neighbor has shorter ID) to go the root, update distance, switchThrough, resetTopo, and send a message
        elif (self.state.root == message.root and self.state.distance == message.distance + 1
              and message.origin < self.state.switchThrough):
            # active link is next hop to the root
            # self.state.linksMap[message.origin] = [False, True]
            self.state.switchThrough = message.origin
            self.resetTopo()
            # send messages that the state has been updated
            print "I get to the case where root and distance are the same, while sender is a better path"
            self.send_messages()

        #else just reset the topo to update the status of pathrough, and activeLinks based on the new information
        else:
            self.resetTopo()

    #this method is designed to reset the status of linksMap for state. [0] is pathThrough, [1] is activeLinks.

    def resetTopo(self):
        for key in self.state.linksMap:
            # if path through is true, active link has to be true
            if self.state.linksMap[key][0]:
                self.state.linksMap[key][1] = True
            # if the neighbour is my switchthrough, active link has to be true
            elif self.state.switchThrough == key:
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

        #the key has to be sorted to generate sorted trees

        for key in sorted(self.state.linksMap.keys()):
            if self.state.linksMap[key][1] == True: #active
                logString += str(self.switchID) + " - " + str(key) +", "
        logString = logString[:-2]

        return logString
