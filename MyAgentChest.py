from MyAgentStones import *
from MyAgentGold import *
from MyAgent import MyAgent
from igraph import *
from transitions import Machine, State
import re
import itertools
import numpy as np
import random

from MyAgentStones import MyAgentStones
from util import *
#inherits MyAgent

class MyAgentChest(MyAgent) :
    states = ["Init", "WaitForOffer","WaitForResponse" , "BeginPlan"]
    states2 = ["Init","MakeOffer","WaitBids","BeginPlan"]
    def __init__(self, id, initX, initY, env,auctioneer=None):
        MyAgent.__init__(self, id, initX, initY, env)


    def setup(self,auctioneer=None):
        self.chestGraph = self.createChestGraph(self.env)
        self.negociating=True
        self.pathGraph=None
        self.lastmail = ""
        self.mystates=[]
        self.future_dest=None
        self.bid = None
        self.path=[]
        self.pathit=1
        self.resp = 0
        self.rmid=0
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
            self.machine = Machine(model=self, states=MyAgentChest.states, initial="Init")
            self.machine.add_transition("Begin", "Init", "WaitForOffer")
            self.machine.add_transition("NegStep", "WaitForOffer", "BeginPlan", conditions=["neg_end"], after=["begin_plan"])
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForResponse", after=["do_bid"],
                                        conditions=["got_offer"])
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForOffer")
            self.machine.add_transition("NegStep", "WaitForOffer", "WaitForOffer")
            self.machine.add_transition("NegStep", "WaitForResponse", "WaitForOffer",
                                        conditions=["got_response"], after=["update_chest_list"])
        else:
            self.machine = Machine(model=self, states=MyAgentChest.states2, initial="Init")
            self.machine.add_transition("NegStep", "BeginPlan", "BeginPlan")
            self.machine.add_transition("Begin", "Init", "MakeOffer", after=["create_bid_list"])
            self.machine.add_transition("NegStep", "MakeOffer", "BeginPlan", conditions=["bid_list_empty"],after=["begin_a_plan"])
            self.machine.add_transition("NegStep", "MakeOffer", "WaitBids", after=["make_offer"])
            self.machine.add_transition("NegStep", "WaitBids", "MakeOffer", conditions=["got_bids"],
                                        after=["compute_winner"])
            self.machine.add_transition("NegStep", "WaitBids", "WaitBids")

    def begin_plan(self):
        self.negociating = False
        idSender, textContent = self.readMail()
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
            plan = {}
            sum = dist(pos, self.pathGraph.vs[0]["pos"]) + 1
            plan[str(self.chestlist[tour[0]])] = str(sum)
            for i in range(len(tour) - 1):
                sum = sum + self.pathGraph.es[find(self.pathGraph, tour[i], tour[i + 1])]["weight"]
                plan[str(self.chestlist[tour[i + 1]])] = str(sum)
            for i in self.getstonesagents(self.env):
                self.send(i.id, "plan:" + str(plan))
            print("goldagents", self.getgoldagents(self.env))
            for i in self.getgoldagents(self.env):
                print("id", i.id)
                self.send(i.id, "plan:" + str(plan))

            self.create_my_plan(tour)
            self.machine.add_transition("ExecStep","BeginPlan",str((self.posX,self.posY)))
        else:
            self.machine.add_transition("ExecStep", "BeginPlan", "End", after="random_walk")
        self.machine.add_state("End")
        self.machine.add_transition("ExecStep", "End", "End", after="random_walk")

        pass

    def random_walk(self):
        can_slide = False
        for j in self.randompos():
            if (self.env.grilleAgent[j[0]][j[1]] == None):
                position = j
                can_slide = True
        if (can_slide):
            self.move(self.posX, self.posY, position[0], position[1])

    @property
    def domove(self):
        if(self.move(self.posX,self.posY,self.path[self.pathit][0],self.path[self.pathit][1])==1):
            return True
        else:
            can_slide=False
            position=None
            for j in self.randomposwr((self.path[self.pathit][0],self.path[self.pathit][1])):
                if(self.env.grilleAgent[j[0]][j[1]]==None):
                    position=j
                    can_slide=True
            if(can_slide):
                buff = str(position)+"o"+"{:.2f}".format(random.random())
                self.machine.add_state(buff)
                self.machine.add_transition("ExecStep",self.state,buff,conditions="domove",after="increment")
                self.path.insert(self.pathit,position)
                self.path.insert(self.pathit+1,(self.posX,self.posY))
                self.machine.add_transition("ExecStep",buff,self.state,conditions="rmove",after="increment")
            return False


    @property
    def rmove(self):
        print("ICI",self.id, type(self),self.path[self.pathit][0], self.path[self.pathit][1])
        if (self.move(self.posX, self.posY, self.path[self.pathit][0], self.path[self.pathit][1]) == 1):
            return True
        else:
            return False
    def randompos(self):
        pospos = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, 1), (0, -1), (-1, -1), (1, -1)]
        truepos = [(self.posX + a, self.posY + b) for a, b in pospos]
        theposs = []
        for i in truepos:
            if (i[0] > 0 and i[1] > 0 and i[0] < self.env.tailleX and i[1] < self.env.tailleY):
                theposs.append(i)
        random.shuffle(theposs)
        return theposs

    def randomposwr(self,notpos):
        pospos=[(1,0),(1,1),(0,1),(-1,0),(-1,1),(0,-1),(-1,-1),(1,-1)]
        truepos=[(self.posX+a,self.posY+b) for a,b in pospos]
        truepos.remove(notpos)
        theposs=[]
        for i in truepos:
            if(i[0]>0 and i[1]>0 and i[0]<self.env.tailleX and i[1]<self.env.tailleY):
                theposs.append(i)
        random.shuffle(theposs)
        return theposs



    def increment(self):
        self.pathit+=1

    def create_my_plan(self,tour):
        it=0
        lp=(self.posX, self.posY)
        lastpos = str(lp)
        self.path=[lastpos]
        self.machine.add_state(str(lastpos))
        for i in tour:
            dest=self.pathGraph.vs[i]["pos"]
            places = path(lp,dest)
            print(self.id,"path to ",i, places)
            self.path.extend(places)
            for j in places:
                buff =str(j) +str(it) + str(random.random())
                self.machine.add_state(buff)
                self.machine.add_transition("ExecStep",lastpos,buff,conditions="domove",after="increment")
                lp=j
                lastpos=buff
                it=it+1

            isopening="opened:"+str(lp) + str(random.random() + it)
            self.machine.add_state(isopening)
            self.machine.add_transition("ExecStep",lastpos,isopening,after="open")
            it = it + 1
            lastpos=isopening
        self.machine.add_state("End")
        self.machine.add_transition("ExecStep",lastpos,"End", after="random_walk")
        self.machine.add_transition("ExecStep","End","End", after="random_walk")




    def selfdestroy(self):
        self.env.grilleAgent[self.posX][self.posY]= None

    def getstonesagents(self,env):
        chestagents = []
        agentA = np.array(env.grilleAgent)
        for i in agentA:
            for j in i:
                if (type(j) == MyAgentStones):
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
        return chestagents

    def begin_a_plan(self):
        self.negociating = False
        for i in self.players:
            self.send(i.id,"endneg")
        self.pathGraph=self.chestGraph.subgraph(self.chestlist)
        if(len(self.chestlist)>0):
            posvertex = []
            for i in range(len(self.pathGraph.vs["name"])):
                posvertex.append(self.pathGraph.vs[i]["pos"])
            min = sys.maxsize
            imin = 0
            self.chestlist.sort()
            pos=(self.posX,self.posY)
            for i in range(len(posvertex)):
                if (dist(pos, posvertex[i]) < min):
                    min = dist(pos, posvertex[i])
                    imin = i

            tour = tourne(self.pathGraph,imin)
            plan = {}
            sum = dist(pos,self.pathGraph.vs[0]["pos"])+1
            plan[str(self.chestlist[tour[0]])]=str(sum)
            for i in range(len(tour) - 1):
                sum = sum + self.pathGraph.es[find(self.pathGraph, tour[i], tour[i + 1])]["weight"]
                plan[str(self.chestlist[tour[i+1]])]=str(sum)
            for i in self.getstonesagents(self.env):
                self.send(i.id,"plan:"+str(plan))
            print("goldagents",self.getgoldagents(self.env))
            for i in self.getgoldagents(self.env):
                print("id",i.id)
                self.send(i.id,"plan:"+ str(plan))
                ###create the plan
            self.create_my_plan(tour)
            self.machine.add_transition("ExecStep", "BeginPlan", str((self.posX, self.posY)))
        else:
            self.machine.add_transition("ExecStep", "BeginPlan", "End", after="random_walk")
        self.machine.add_state("End")
        self.machine.add_transition("ExecStep", "End", "End", after="random_walk")






    def printboi(self):
        print("---------printboi")
    def compute_winner(self):
        ml = self.chestlist.copy()
        if (ml == []):
            sc = dist((self.posX, self.posY), self.chestGraph.vs[self.myoffer]["pos"])
        else:
            ml.append(self.myoffer)
            sc = scoret(self.chestGraph, ml, (self.posX, self.posY))
        self.bid = self.myoffer
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



    @property
    def got_bids(self):
        self.bids= {}
        idSender,textContent = self.readMail()
        self.rmid+=1
        while(idSender!=None):
            bid=int(re.search("bid:(\d*)",textContent).groups()[0])
            self.bids[idSender]=bid
            self.nbbids = self.nbbids + 1
            idSender,textContent = self.readMail()
            self.rmid+=1
            print(self.id,"got bid:",bid)
        return (self.nbbids==len(self.players))


    def make_offer(self):
        self.myoffer= self.bid_list.pop()

        for i in self.players:
            self.send(i.id,"offer:"+str(self.myoffer))
    @property
    def bid_list_empty(self):
        return self.bid_list==[]

    def create_bid_list(self):
        self.bid_list = self.chestGraph.vs["name"]
        chestagents=self.getchestagents(self.env)
        self.players = []
        for k in chestagents:
            #print(k.id)
            if(k.id != self.id):
                self.players.append(k)
    def state(self):
        return self.machine.state
    def do_bid(self):
        vertex = int(re.search("offer:(\d*)",self.lastmail).groups()[0])
        print(self.id,"offer", vertex)
        ml = self.chestlist.copy()
        if (ml == []):
            sc = dist((self.posX,self.posY), self.chestGraph.vs[vertex]["pos"])
        else:
            ml.append(vertex)
            sc = scoret(self.chestGraph, ml, (self.posX,self.posY))
        self.bid =vertex
        print(sc)
        self.send(self.sender,"bid:" + str(sc))

    def update_chest_list(self):
        resp = self.resp
        if(resp==1):
            bid = self.bid
            self.chestlist.append(bid)


    @property
    def neg_end(self):
        idSender, textContent = self.readMail()
        self.mailBox.append((idSender,textContent))
        self.rmid+=1
        print("endneg",textContent)
        if(textContent!=None):
            if(re.match("endneg",textContent)):
                return True
        return False

    @property
    def got_response(self):

        idSender, textContent = self.readMail()
        self.rmid+=1
        if(textContent!=None):
            if(re.search("response:(\d*)",textContent)):
                print("heere",textContent)
                resp = int(re.search("response:(\d*)",textContent).groups()[0])
                self.resp=resp
                self.sender=idSender
                return True
        return False


    @property
    def got_offer(self):
        idSender, textContent=self.readMail()
        self.rmid += 1
        if(textContent!=None):
            if(re.match("offer:(\d*)",textContent)):
                self.lastmail=textContent
                self.sender= idSender
                print("got the offer",self.lastmail)
                return True
        print(self.id,"didnt get anu offer")
        return False


    def createChestGraph(self,env):
        tresA = np.array(env.grilleTres)
        trespos = list(zip(*np.where(tresA != None)))
        tresobj=[]
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
        g.vs["obj"]= tresobj
        g.es["weight"] = [c for a, b, c in weighted_edges]
        return g

    def getchestagents(self,env):
        chestagents = []
        agentA = np.array(env.grilleAgent)
        for i in agentA:
            for j in i:
                if (type(j) == MyAgentChest):
                    chestagents.append(j)
        print(chestagents)
        return chestagents


    # open a chest
    def open(self):
        self.env.open(self, self.posX, self.posY)

    # the agent do not hold some treasure
    def getTreasure(self):
        return 0

    def __str__(self):

        res = "agent Chest "+ self.id + " (" + str(self.posX) + " , " + str(self.posY) + ")"
        return res