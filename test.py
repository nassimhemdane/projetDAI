import itertools
from collections import deque
import re
import numpy as np
from igraph import *

from Main import *

env, lAg = loadFileConfig("env1.txt")

tresA = np.array(env.grilleTres)
trespos=list(zip(*np.where(tresA!=None)))
vertex = [i for i in range(len(trespos))]
edges = list(itertools.product(vertex, vertex))
for i,j in edges:
    if (i==j):
        edges.remove((i,j))
def dist(a,b):
    return float(abs(a[0]-b[0])+abs(a[1]-b[1]))

tresobj = []
for i in trespos:
    tresobj.append(tresA[i])
weighted_edges = [(a,b,dist(trespos[a],trespos[b])) for a,b in edges]
g = Graph()
g.add_vertices(len(vertex))
g.add_edges([(a,b) for a,b,c in weighted_edges])
g.vs["name"] = vertex
g.vs["obj"]=tresobj
g.vs["pos"] = trespos
g.es["weight"] = [c for a,b,c in weighted_edges]


def find(graph,a,b):
    k=0
    for i in graph.get_edgelist():
        if((i[0]==a and i[1]==b) or (i[0]==b and i[1]==a)):
            return k
        k=k+1
    return -1

def mst(graph,src):
    nvertex= len(graph.vs["name"])
    keys = [sys.maxsize] * nvertex
    mstL = [False] * nvertex
    keys[src] = 0
    parents = [None] * nvertex
    parents[src]= -1
    for j in range(nvertex):
        min = sys.maxsize
        for v in range(len(keys)):
            if keys[v] < min and mstL[v] == False:
                min = keys[v]
                u = v
        mstL[u]=True
        for i in range(len(keys)):
            if (mstL[i] == False and graph.es[find(graph, u, i)]["weight"] < keys[i] ):
                keys[i] = graph.es[find(graph, u, i)]["weight"]
                parents[i] = u
    return graph_from_parents(graph,parents),src

def graph_from_parents(graph,parents):
    tuples= []
    vertex = [i for i in range(len(graph.vs["name"]))]
    for i in range(len(parents)):
        if(parents[i]>=0):
            tuples.append((parents[i],i,graph.es[find(graph, parents[i], i)]["weight"]))
    g3= Graph()
    g3.add_vertices(len(parents))
    g3.add_edges([(a, b) for a, b, c in tuples])
    g3.es["weight"] = [c for a, b, c in tuples]
    g3.vs["name"] = vertex
    return g3

def iterative_dfs(graph, node):

    visited = []
    stack = deque()
    stack.append(node)

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.append(node)
            unvisited = []
            for i in range(len(g2.vs["name"])):
                if ((i not in visited) and find(graph, node, i) >= 0):
                    unvisited.append(i)
            stack.extend(unvisited)

    return visited

g2,s = mst(g,3)

def tourne(g,s):
    g2,s = mst(g,s)
    return g2.dfs(s)[0]

def score(gb,s):
    t = tourne(gb,s)
    sum = 0
    for i in range(len(t) - 1):
        sum = sum + gb.es[find(g, t[i], t[i + 1])]["weight"]

    sum = sum + gb.es[find(g, t[0], t[len(t)-1] )]["weight"]
    return sum
def scoret(gb,t, pos):
    posvertex = []
    for i in t:
        posvertex.append(gb.vs[i]["pos"])
    min = sys.maxsize
    imin = 0
    for i in range(len(posvertex)):
        if (dist(pos, posvertex[i]) < min):
            min = dist(pos, posvertex[i])
            imin = i
    sum = dist(pos,posvertex[imin])
    for i in range(len(t) - 1):
        sum = sum + gb.es[find(g, t[i], t[i + 1])]["weight"]

    #sum = sum + gb.es[find(g, t[0], t[len(t) - 1])]["weight"]
    return sum

#for i in range(len(vertex)):
    #print(score(g,i))



def bid_tour(graph,pos):
    posvertex = graph.vs["pos"]
    min=sys.maxsize
    imin=0
    for i in range(len(posvertex)):
        if(dist(pos,posvertex[i])<min):
            min=dist(pos,posvertex[i])
            imin = i
    tour= tourne(graph,imin)
    score = scoret(graph,tour,pos)
    return tour,score


def generate_alternatives(graph,path,pos):
    scores = {path[i]:graph.vs[path[i]]["pos"] for i in range(len(path))}
    alternatives = {}
    sorted_alt=[]
    idx=0
    max=scoret(graph, path, pos)
    for i in range(len(path)-1):
        pass
        for j in range(len(path)):
            alt = []
            for k in range(i+1):
                if(j+k<len(path)):
                    alt.append(path[j+k])
                else:
                    alt.append(path[j+k-len(scores)])
            sc = scoret(graph,alt,pos)
            alternatives[idx]=(alt,max-sc)
            sorted_alt.append((alt,max-sc))
            idx=idx+1
    alternatives[idx] = (path, 0)

    sorted_alt.append((path,0))
    sorted_alt.sort(key=lambda x:-x[1])
    return alternatives,sorted_alt

def IRU(alternatives):
    pass
    iru_alt = []
    for i in alternatives:
        iru_alt.append((alternatives[i][0],alternatives[i][1],len(alternatives-i)))
    return iru_alt

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
def value_offer(myalt,oalt):
    vof=[]
    for i in myalt:
        p=1
        for alt in oalt:
            palt =0
            ilt=0
            it = 0
            lj=[]
            for j in alt:
                if(len(intersection(j[0],i[0]))==0):
                    palt=palt+ pow((len(alt)-it +1),20)*j[1]
                    ilt=ilt+pow((len(alt)-it +1),20)
                    lj.append(j)
                it=it+1
            if(ilt>0):
                palt = palt/ilt
            #print(lj,palt)
            p=p*palt
        vof.append((i[0],i[1],i[1]*p))
    vof.sort(key=lambda x:-p)
    return vof

def bid_vertex(graph,mylist,mypos,vertex):
    ml=mylist.copy()
    if(ml==[]):
        sc=dist(mypos,graph.vs[vertex]["pos"])
    else:
        ml.append(vertex)
        sc = scoret(graph,ml,mypos)
    return sc

def getchestagents(env):
    chestagents = []
    agentA = np.array(env.grilleAgent)
    for i in agentA:
        for j in i:
            if(type(j)==MyAgentChest):
                chestagents.append(j)
    return chestagents

#print(bid_tour(g,(0,0)))

sc = scoret(g,[1,4],(0,0))

agents= [(7,4),(9,9),(1,2)]
chestL=list(g.vs["name"])
agentchest = [[], [], []]
for i in chestL:
    ag=0
    maxsc=100000
    for j in range(len(agents)):
        sc=bid_vertex(g,agentchest[j],agents[j],i)
        if(sc<maxsc):
            ag=j
            maxsc=sc
    agentchest[ag].append(i)




#ag1=chestagents[0]
#ag2=chestagents[1]
#ag3=chestagents[2]
#gag1=goldagents[0]
#gag2=goldagents[1]
#sag1=stonesagents[0]
#sag2=stonesagents[1]
#sag1.setup()
#sag2.setup(True)
#gag1.setup()
#gag2.setup(True)
#ag1.setup()
#ag2.setup(True)
#ag3.setup()
#print(getchestagents(env))
#ag1.Begin()
#ag2.Begin()
#ag3.Begin()
#gag1.Begin()
#gag2.Begin()
#sag1.Begin()
#sag2.Begin()
##ag2.send(ag1.id,"plan:"+str({"0": 12.3, "2": 3.4, "6": 12.4}))#

#while(ag1.state!="BeginPlan" or ag2.state!="BeginPlan" or ag3.state!="BeginPlan" or
#      gag1.state!="BeginPlan" or gag2.state!="BeginPlan" or
#        sag1.state!="BeginPlan" or sag2.state!="BeginPlan" ):
#    if(ag1.state!="BeginPlan"):
#        ag1.NegStep()
#        print(ag1.id, ag1.state)
#    if(ag2.state!="BeginPlan"):
#        ag2.NegStep()
#        print(ag2.id,ag2.state)
#    if (ag3.state != "BeginPlan"):
#        ag3.NegStep()
#        print(ag3.id, ag3.state)
#    if (gag1.state != "BeginPlan"):
#        gag1.NegStep()
#        print(gag1.id, gag1.state)
#    if (gag2.state != "BeginPlan"):
#        gag2.NegStep()
#        print(gag2.id, gag2.state)
#    if (sag1.state != "BeginPlan"):
#        sag1.NegStep()
#        print(sag1.id, sag1.state)
#    if (sag2.state != "BeginPlan"):
#        sag2.NegStep()
#        print(sag2.id, sag2.state)#

#print(ag1.id,"plan",ag1.chestlist)
#print(ag2.id,"plan",ag2.chestlist)
#print(ag3.id,"plan",ag3.chestlist)
#print(gag1.id,"plan",gag1.chestlist)
#print(gag2.id,"plan",gag2.chestlist)
#print(sag1.id,"plan",sag1.chestlist)
#print(sag2.id,"plan",sag2.chestlist)
#lpo=2
#while(ag1.state!="End" or ag2.state!="End" or ag3.state!="End" or gag1.state!="End" or gag2.state!="End" or
#    sag1.state!="End" or sag2.state!="End"):
#    lpo+=1
#    if(env.grilleAgent[4][10]==None or env.grilleAgent[4][10]==4):
#        if(lpo % 3 == 0):
#            env.grilleAgent[4][10] = 4
#        else:
#            env.grilleAgent[4][10] = None
#    if(ag1.state!="End"):
#        ag1.ExecStep()
#        print(ag1.id,type(ag1) ,(ag1.posX,ag1.posY),ag1.state)
#    if(ag2.state!="End"):
#        ag2.ExecStep()
#        print(ag2.id, type(ag2) ,(ag2.posX, ag2.posY), ag2.state)
#    if (ag3.state != "End"):
#        ag3.ExecStep()
#        print(ag3.id, type(ag3) ,(ag3.posX, ag3.posY), ag3.state)
#    if (gag1.state != "End"):
#        gag1.ExecStep()
#        print(gag1.id,type(gag1) , (gag1.posX, gag1.posY), gag1.state)
#    if (gag2.state != "End"):
#        gag2.ExecStep()
#        print(gag2.id, type(gag2) , (gag2.posX, gag2.posY), gag2.state)
#    if (sag1.state != "End"):
#        sag1.ExecStep()
#        print(sag1.id, type(sag1), (sag1.posX, sag1.posY), sag1.state)
#    if (sag2.state != "End"):
#        sag2.ExecStep()
#        print(sag2.id, type(sag2), (sag2.posX, sag2.posY), sag2.state)


print("\n\n******* SCORE TOTAL : {}".format(env.getScore()))



