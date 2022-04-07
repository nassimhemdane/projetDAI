from transitions import Machine
import random

class ChestBehaviour(object):

    states= ["Init","WaitForOffer","WaitForResponse","BeginPlan"]
    def __init__(self,id):
        self.id=id
        self.chestList=[]
        self.machine =Machine(model=self,states=ChestBehaviour.states,initial="Init")
        self.machine.add_transition("Begin","Init","WaitForOffer")
        self.machine.add_transition("NegStep","WaitForOffer","WaitForResponse",conditions=["got_offer"])



