import itertools
import sys

from MyAgent import MyAgent
import numpy as np

from igraph import *
from transitions import Machine, State
import re
import json
import random
from util import *


#inherits MyAgent

class MyAgentStones(MyAgent):
    states = ["Init", "WaitForOffer", "WaitForResponse", "ValidatePlan", "BeginPlan"]
    states2 = ["Init", "MakeOffer", "WaitBids", "ValidatePlan", "BeginPlan"]
    def __init__(self, id, initX, initY, env, capacity):
        MyAgent.__init__(self, id, initX, initY, env)
        self.stone = 0
        self.backPack = capacity

    def setup(self, auctioneer=None):
        self.actbackpack=0
        self.negociating=True
        self.chestGraph= self.createChestGraph(self.env)
        chests= self.chestGraph.vs["pos"]
        tresA = np.array(self.env.grilleTres)
        goldchest=[]
        for i in range(len(chests)):
            if(tresA[chests[i]].type==2):
                goldchest.append(i)
        self.goldGraph=self.chestGraph.subgraph(goldchest)
        self.constraints= {}
        for i in self.goldGraph.vs["name"]:
            self.constraints[i]=-1

        self.pathGraph = None
        self.lastmail = ""
        self.bid = None
        self.resp = 0
        self.path = []
        self.pathit = 1
        if (auctioneer == None):
            self.auctioneer = False
        else:
            self.auctioneer = auctioneer
        self.bid_list = []
        self.players = []
        self.sender = 0
        self.nbbids = 0
        self.myoffer = None
        self.winner = None
        self.chestlist = []
        if (not self.auctioneer):
            self.machine = Machine(model=self, states=MyAgentStones.states, initial="Init")
            self.machine.add_transition("NegStep", "ValidatePlan", "BeginPlan",conditions=["updated_constraints"], after=["begin_plan"])
            self.machine.add_transition("NegStep", "ValidatePlan", "ValidatePlan", conditions=["got_chest_plan"],
                                        after=["update_plan"])
            self.machine.add_transition("NegStep", "ValidatePlan", "ValidatePlan")
            self.machine.add_transition("NegStep", "BeginPlan", "BeginPlan")
            self.machine.add_transition("Begin", "Init", "WaitForOffer")
            self.machine.add_transition("NegStep", "WaitForOffer", "ValidatePlan", conditions=["neg_end"])
            self.machine.add_transition("NegStep", "WaitForOffer","WaitForOffer",conditions=["got_chest_plan"],after=["update_plan"])
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForResponse", after=["do_bid"],
                                        conditions=["got_offer"])
            self.machine.add_transition("NegStep","BeginPlan","BeginPlan")
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForOffer")
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForOffer")
            self.machine.add_transition("NegStep", "WaitForResponse", "WaitForOffer",
                                        conditions=["got_response"], after=["update_chest_list"])
        else:
            self.machine = Machine(model=self, states=MyAgentStones.states2, initial="Init")
            self.machine.add_transition("NegStep", "BeginPlan", "BeginPlan")
            self.machine.add_transition("Begin", "Init", "MakeOffer", after=["create_bid_list"])
            self.machine.add_transition("NegStep", "MakeOffer", "ValidatePlan", conditions=["bid_list_empty"], after=["end_neg"])
            self.machine.add_transition("NegStep", "ValidatePlan", "BeginPlan", conditions=["updated_constraints"],after=["begin_a_plan"])
            self.machine.add_transition("NegStep", "ValidatePlan", "ValidatePlan", conditions=["got_chest_plan"],
                                        after=["update_plan"])
            self.machine.add_transition("NegStep", "ValidatePlan", "ValidatePlan")
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForOffer", conditions=["got_chest_plan"],
                                        after=["update_plan"])
            self.machine.add_transition("NegStep", "MakeOffer", "WaitBids", after=["make_offer"])
            self.machine.add_transition("NegStep", "WaitBids", "MakeOffer", conditions=["got_bids"],
                                        after=["compute_winner"])
            self.machine.add_transition("NegStep", "WaitBids", "WaitBids")

    def end_neg(self):
        for i in self.players:
            self.send(i.id, "endneg")

    @property
    def domove(self):
        if (self.move(self.posX, self.posY, self.path[self.pathit][0], self.path[self.pathit][1]) == 1):
            return True
        else:
            can_slide = False
            position = None
            for j in self.randomposwr((self.path[self.pathit][0], self.path[self.pathit][1])):
                if (self.env.grilleAgent[j[0]][j[1]] == None):
                    position = j
                    can_slide = True
            if (can_slide):
                buff = str(position) + "o" + "{:.2f}".format(random.random())
                self.machine.add_state(buff)
                self.machine.add_transition("ExecStep", self.state, buff, conditions="domove", after="increment")
                self.path.insert(self.pathit, position)
                self.path.insert(self.pathit + 1, (self.posX, self.posY))
                self.machine.add_transition("ExecStep", buff, self.state, conditions="rmove", after="increment")
            return False

    @property
    def rmove(self):
        print("ICI",self.id,type(self) ,self.path[self.pathit][0], self.path[self.pathit][1])
        if (self.move(self.posX, self.posY, self.path[self.pathit][0], self.path[self.pathit][1]) == 1):
            return True
        else:
            return False

    def randomposwr(self, notpos):
        pospos = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, 1), (0, -1), (-1, -1), (1, -1)]
        truepos = [(self.posX + a, self.posY + b) for a, b in pospos]
        truepos.remove(notpos)
        theposs = []
        for i in truepos:
            if (i[0] > 0 and i[1] > 0 and i[0] < self.env.tailleX and i[1] < self.env.tailleY):
                theposs.append(i)
        random.shuffle(theposs)
        return theposs
    def randompos(self):
        pospos = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, 1), (0, -1), (-1, -1), (1, -1)]
        truepos = [(self.posX + a, self.posY + b) for a, b in pospos]
        theposs = []
        for i in truepos:
            if (i[0] > 0 and i[1] > 0 and i[0] < self.env.tailleX and i[1] < self.env.tailleY):
                theposs.append(i)
        random.shuffle(theposs)
        return theposs

    def increment(self):
        self.pathit += 1

    def create_my_plan(self, tour):
        it = 0
        act_bag = 0
        lp = (self.posX, self.posY)
        lastpos = str(lp)
        self.path = [lastpos]
        self.machine.add_state(str(lastpos))
        for i in tour:
            dest = self.pathGraph.vs[i]["pos"]
            quant = self.pathGraph.vs[i]["obj"].value
            if (act_bag != 0):
                act_bag = act_bag + quant
                if (act_bag <= self.backPack):
                    places = path(lp, dest)
                    print(self.id, "path to ", i, places)
                    self.path.extend(places)
                    for j in places:
                        buff =str(j) + str(it)+ "{:.2f}".format(random.random())
                        self.machine.add_state(buff)
                        self.machine.add_transition("ExecStep", lastpos, buff, conditions="domove",
                                                    after="increment")
                        lp = j
                        lastpos = buff
                        it = it + 1
                    isopening = "loading:" + str(lp) + str(random.random() + it)
                    self.machine.add_state(isopening)
                    self.machine.add_transition("ExecStep", lastpos, isopening, after="load")
                    it=it+1
                    lastpos = isopening
                else:
                    places1 = path(lp, self.env.posUnload)
                    self.path.extend(places1)
                    for j in places1:
                        buff=str(j) + str(it)+ "{:.2f}".format(random.random())
                        self.machine.add_state(buff)
                        self.machine.add_transition("ExecStep", lastpos, buff, conditions="domove",
                                                    after="increment")
                        lp = j
                        lastpos = buff
                        it = it + 1
                    isopening = "unloading:" + str(lp) + str(random.random()+it)
                    self.machine.add_state(isopening)
                    self.machine.add_transition("ExecStep", lastpos, isopening, after="unload")
                    it=it+1
                    places2 = path(self.env.posUnload, dest)
                    lastpos = isopening
                    print(self.id, "path to ", i, places1, places2)
                    self.path.extend(places2)
                    for j in places2:
                        buff = str(j) + str(it)+ "{:.2f}".format(random.random())
                        self.machine.add_state(buff)
                        self.machine.add_transition("ExecStep", lastpos, buff, conditions="domove",
                                                    after="increment")
                        lp = j
                        lastpos = buff
                        it = it + 1
                    isopening = "puting:" + str(lp) + str(random.random() + it)
                    self.machine.add_state(isopening)
                    self.machine.add_transition("ExecStep", lastpos, isopening, after="load")
                    it=it+1
                    lastpos = isopening
                    act_bag = 0
            else:
                act_bag = quant
                places = path(lp, dest)
                print(self.id, "path to ", i, places)
                self.path.extend(places)
                for j in places:
                    buff =str(j) + str(it)+ "{:.2f}".format(random.random())
                    self.machine.add_state(buff)
                    self.machine.add_transition("ExecStep", lastpos, buff, conditions="domove",
                                                after="increment")
                    lp = j
                    lastpos = buff
                    it = it + 1
                isopening = "puting:" + str(lp) + str(random.random() +it )
                self.machine.add_state(isopening)
                self.machine.add_transition("ExecStep", lastpos, isopening, after="load")
                self.machine.add_transition("ExecStep", lastpos, isopening, after="load")
                lastpos = isopening
        placesf = path(lp, self.env.posUnload)
        self.path.extend(placesf)
        for j in placesf:
            buff = str(j) + str(it)+ "{:.2f}".format(random.random())
            self.machine.add_state(buff)
            self.machine.add_transition("ExecStep", lastpos, buff, conditions="domove",
                                        after="increment")
            lp = j
            lastpos = buff
            it = it + 1
        isopening = "unloading:" + str(lp) + str(random.random()+it)
        self.machine.add_state(isopening)
        self.machine.add_transition("ExecStep", lastpos, isopening, after="unload")
        it=it+1
        lastpos = isopening
        self.machine.add_state("End")
        self.machine.add_transition("ExecStep", lastpos, "End", after="random_walk")
        self.machine.add_transition("ExecStep", "End", "End", after="random_walk")


    def selfdestroy(self):
        self.env.grilleAgent[self.posX][self.posY]= None

    def begin_plan(self):
        self.negociating=False
        self.pathGraph = self.chestGraph.subgraph(self.chestlist)
        if(len(self.chestlist)>0):
            posvertex = []
            for i in range(len(self.pathGraph.vs["name"])):
                posvertex.append(self.pathGraph.vs[i]["pos"])
            min = sys.maxsize
            imin = 0
            self.chestlist.sort()
            pos = (self.posX, self.posY)
            for i in range(len(posvertex)):
                if (dist(pos, posvertex[i]) < min):
                    min = dist(pos, posvertex[i])
                    imin = i

            tour = tourne(self.pathGraph, imin)
            if (len(tour) > 0):
                ###create the plan
                self.create_my_plan(tour)
                self.machine.add_transition("ExecStep", "BeginPlan", str((self.posX, self.posY)))
        else:
            self.machine.add_transition("ExecStep", "BeginPlan", "End", after="random_walk")
        self.machine.add_state("End")
        self.machine.add_transition("ExecStep", "End", "End", after="random_walk")
        pass

    @property
    def got_bids(self):
        self.bids = {}
        idSender, textContent = self.readMail()
        retmails = []
        while (idSender != None):
            if (re.search("bid:(\d*)", textContent)):
                bid = int(re.search("bid:(\d*)", textContent).groups()[0])
                self.bids[idSender] = bid
                self.nbbids = self.nbbids + 1
                idSender, textContent = self.readMail()
                print(self.id, "got bid:", bid)
            else:
                retmails.append((idSender, textContent))
                idSender, textContent = self.readMail()
        for i in retmails:
            self.mailBox.append(i)
        return (self.nbbids == len(self.players))



    def compute_winner(self):
        vertex = self.myoffer
        vobj = self.goldGraph.vs.select(name=vertex)["obj"][0]
        sc=sys.maxsize
        if (vobj.value <= self.backPack):
            ml = self.chestlist.copy()
            if (ml == []):
                sc = dist((self.posX, self.posY), self.goldGraph.vs.select(name=vertex)["pos"][0])
            else:
                ml.append(vertex)
                sc = scoretwc(self.goldGraph, ml, (self.posX, self.posY), self.env.posUnload, self.backPack)
            self.bid = self.myoffer
        print(self.id, "i bid:",sc )
        max=sc
        idwinner=self.id
        for i in self.bids.keys():
            if(self.bids[i]<max):
                max=self.bids[i]
                idwinner=i
        if(idwinner==self.id):
            self.chestlist.append(self.myoffer)
            for j in self.bids.keys():
                self.send(j,"response:0")
        else:
            for j in self.bids.keys():
                if(j==idwinner):
                    self.send(j,"response:1")
                else:
                    self.send(j,"response:0")
        print(self.id,"winner is!!:",idwinner, "with score:", max , "vs",sc)
        self.bids={}
        self.myoffer=None
        self.nbbids=0

    def make_offer(self):
        self.myoffer= self.bid_list.pop()
        for i in self.players:
            self.send(i.id,"offer:"+str(self.myoffer))

    def random_walk(self):
        can_slide = False
        for j in self.randompos():
            if (self.env.grilleAgent[j[0]][j[1]] == None):
                position = j
                can_slide = True
        if (can_slide):
            self.move(self.posX, self.posY, position[0], position[1])


    def begin_a_plan(self):
        self.negociating=False
        for i in self.players:
            self.send(i.id,"endneg")
        self.pathGraph = self.chestGraph.subgraph(self.chestlist)
        if(len(self.chestlist)>0):
            posvertex = []
            for i in range(len(self.pathGraph.vs["name"])):
                posvertex.append(self.pathGraph.vs[i]["pos"])
            min = sys.maxsize
            imin = 0
            self.chestlist.sort()
            pos = (self.posX, self.posY)
            for i in range(len(posvertex)):
                if (dist(pos, posvertex[i]) < min):
                    min = dist(pos, posvertex[i])
                    imin = i

            tour = tourne(self.pathGraph, imin)
            if (len(tour) > 0):
                ###create the plan
                self.create_my_plan(tour)
                self.machine.add_transition("ExecStep", "BeginPlan", str((self.posX, self.posY)))
        else:
            self.machine.add_transition("ExecStep", "BeginPlan", "End", after="random_walk")
        self.machine.add_state("End")
        self.machine.add_transition("ExecStep","End","End", after="random_walk")

    def create_bid_list(self):
        self.bid_list = self.goldGraph.vs["name"]
        goldagents = self.getstonesagents(self.env)
        self.players = []
        for k in goldagents:
            # print(k.id)
            if (k.id != self.id):
                self.players.append(k)

    @property
    def bid_list_empty(self):
        return self.bid_list == []

    @property
    def updated_constraints(self):
        for i in self.constraints.items():
            if(float(i[1])<0):
                return False
        return True

    @property
    def got_response(self):
        idSender, textContent = self.readMail()
        if (textContent != None):
            if (re.search("response:(\d*)", textContent)):
                resp = int(re.search("response:(\d*)", textContent).groups()[0])
                self.resp = resp
                self.sender = idSender
                return True
        return False

    def update_chest_list(self):
        resp = self.resp
        if (resp == 1):
            bid = self.bid
            self.chestlist.append(bid)

    def do_bid(self):
        vertex = int(re.search("offer:(\d*)", self.lastmail).groups()[0])
        print(self.id, "offer", vertex)
        vobj = self.goldGraph.vs.select(name=vertex)["obj"][0]
        if(vobj.value<=self.backPack):
            ml = self.chestlist.copy()
            if (ml == []):
                sc = dist((self.posX, self.posY), self.goldGraph.vs.select(name=vertex)["pos"][0])
            else:
                ml.append(vertex)
                sc = scoretwc(self.goldGraph, ml, (self.posX, self.posY),self.env.posUnload,self.backPack)
            self.bid = vertex
            self.send(self.sender, "bid:" + str(sc))
        else:
            self.send(self.sender,"bid:" + str(sys.maxsize))


    @property
    def got_offer(self):
        idSender, textContent = self.readMail()
        if (textContent != None):
            if (re.match("offer:(\d*)", textContent)):
                self.lastmail = textContent
                self.sender = idSender
                print("got the offer", self.lastmail)
                return True
        print(self.id, "didnt get any offer")
        return False

    @property
    def got_chest_plan(self):
        idSender, textContent = self.readMail()
        if (textContent != None):
            self.mailBox.append((idSender, textContent))
            print("gotchesplan mail",textContent,self.mailBox)
            if (re.match("plan:.*", textContent)):
                return True
        return False

    @property
    def neg_end(self):
        idSender, textContent = self.readMail()
        self.mailBox.append((idSender, textContent))
        print("negend",textContent)
        if (textContent != None):
            if (re.match("endneg", textContent)):
                idSender, textContent = self.readMail()
                return True
        return False

    def update_plan(self):
        print("i update the plan")
        idSender, textContent = self.readMail()
        resp = re.search("plan:(.*)", textContent).groups()[0]
        resp=resp.replace("\'", "\"")
        convertedDict = json.loads(resp)
        for i in convertedDict.keys():
            if int(i) in self.constraints.keys():
                print("convertedicit[i]",convertedDict[i])
                self.constraints[int(i)]=float(convertedDict[i])

    def getstonesagents(self,env):
        chestagents = []
        agentA = np.array(env.grilleAgent)
        for i in agentA:
            for j in i:
                if (type(j) == MyAgentStones):
                    chestagents.append(j)
        print(chestagents)
        return chestagents

    def creatGoldGraph(self,env):
        tresA = np.array(env.grilleTres)
        trespos = list(zip(*np.where(tresA != None)))
        ntrespos=[]
        for i in trespos:
            if(tresA[i].type==1):
                ntrespos.append(i)
        trespos=ntrespos
        vertex = [i for i in range(len(trespos))]
        edges = list(itertools.product(vertex, vertex))
        for i, j in edges:
            if (i == j):
                edges.remove((i, j))
        weighted_edges = [(a, b, dist(trespos[a], trespos[b])) for a, b in edges]
        g = Graph()
        g.add_vertices(len(vertex))
        g.add_edges([(a, b) for a, b, c in weighted_edges])
        g.vs["name"] = vertex
        g.vs["pos"] = trespos
        g.es["weight"] = [c for a, b, c in weighted_edges]
        return g

    def createChestGraph(self, env):
        tresA = np.array(env.grilleTres)
        trespos = list(zip(*np.where(tresA != None)))
        tresobj = []
        for i in trespos:
            tresobj.append(tresA[i])
        vertex = [i for i in range(len(trespos))]
        edges = list(itertools.product(vertex, vertex))
        for i, j in edges:
            if (i == j):
                edges.remove((i, j))
        weighted_edges = [(a, b, dist(trespos[a], trespos[b])) for a, b in edges]
        g = Graph()
        g.add_vertices(len(vertex))
        g.add_edges([(a, b) for a, b, c in weighted_edges])
        g.vs["name"] = vertex
        g.vs["pos"] = trespos
        g.vs["obj"] = tresobj
        g.es["weight"] = [c for a, b, c in weighted_edges]
        return g

    def getchestagents(self,env):
        chestagents = []
        agentA = np.array(env.grilleAgent)
        for i in agentA:
            for j in i:
                if (type(j) == MyAgentChest.MyAgentChest):
                    chestagents.append(j)
        print(chestagents)
        return chestagents

    def getgoldagents(self,env):
        chestagents = []
        agentA = np.array(env.grilleAgent)
        for i in agentA:
            for j in i:
                if (type(j) == MyAgentGold):
                    chestagents.append(j)
        print(chestagents)
        return chestagents

    # return quantity of precious stones collected and not unloaded yet
    def getTreasure(self):
        return self.stone

    # unload precious stones in the pack back at the current position
    def unload(self):
        self.env.unload(self)
        self.stone = 0

    #return the agent's type
    def getType(self):
        return 2

    # load the treasure at the current position
    def load(self):
        self.env.load(self)

    # add some precious stones to the backpack of the agent (quantity t)
    # if the quantity exceeds the back pack capacity, the remaining is lost
    def addTreasure(self, t):
        if(self.stone + t <= self.backPack) :
            self.stone = self.stone + t
        else :
            self.stone = self.backPack

    def __str__(self):
        res ="agent Stone "+ self.id + " ("+ str(self.posX) + " , " + str(self.posY) + ")"
        return res

