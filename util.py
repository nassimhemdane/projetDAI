import sys

from MyAgentChest import *
import numpy as np

from igraph import *


def dist(a, b):
    p=path(a,b)
    return len(p)

def find(graph,a,b):
    k=0
    for i in graph.get_edgelist():
        if((i[0]==a and i[1]==b) or (i[0]==b and i[1]==a)):
            return k
        k=k+1
    return -1






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
        sum = sum + gb.es[find(gb, t[i], t[i + 1])]["weight"]

    return sum

def scoretwc(gb,t,pos,out,capacity):
    posvertex = []
    actc=0
    tid=[]
    min = sys.maxsize
    imin = 0
    for i in range(len(gb.vs["name"])):
        if(gb.vs[i]["name"] in t):
            tid.append(i)
    subg = gb.subgraph(tid)
    for i in range(len(tid)):
        posvertex.append(subg.vs[i]["pos"])
    for i in range(len(posvertex)):
        if (dist(pos, posvertex[i]) < min):
            min = dist(pos, posvertex[i])
            imin = i
    tour=tourne(subg,imin)
    actc = actc + subg.vs.select(name=subg.vs[tour[0]]["name"])["obj"][0].value
    if(actc<=capacity):
        sum = dist(pos,posvertex[0])
    else:
        sum = dist(pos,out) + dist(out,posvertex[0])

    for i in range(len(tour) - 1):
        actc = actc + subg.vs.select(name=subg.vs[tour[i+1]]["name"])["obj"][0].value
        if(actc<=capacity):
            sum = sum + subg.es[find(subg, tour[i], tour[i + 1])]["weight"]
        else:
            sum= sum+ dist(subg.vs[tour[i]]["pos"],out) + dist(out,subg.vs[tour[i+1]]["pos"])

    return sum

def tourne(g,s):
    g2,s = mst(g,s)
    return g2.dfs(s)[0]

def tournewc(g,s,c):
    g2,s = mstwc(g,s,c)
    return g2.dfs(s)[0]


def path(pos1,pos2):
    path=[]
    distx = pos2[0]-pos1[0]
    disty = pos2[1]-pos1[1]
    relativx=abs(distx)-abs(disty)
    relativy=abs(disty)-abs(distx)
    if(distx!=0):
        stepx= distx/abs(distx)
    else:
        stepx=0
    if(disty!=0):
        stepy=disty/abs(disty)
    else:
        stepy=0
    px=pos1[0]
    py=pos1[1]
    for i in range(relativx):
        px=px+stepx
        path.append((int(px),int(py)))
    for i in range(relativy):
        py = py+stepy
        path.append((int(px),int(py)))
    for i in range(min(abs(distx),abs(disty))):
        px = px + stepx
        py = py + stepy
        path.append((int(px), int(py)))
    return path

def mst(graph,src):
    nvertex= len(graph.vs["name"])
    keys = [sys.maxsize] * nvertex
    mstL = [False] * nvertex
    print("nvertex",nvertex)
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

def mstwc(graph,src,constraints):
    nvertex= len(graph.vs["name"])
    actc=[0]*nvertex
    keys = [sys.maxsize] * nvertex
    mstL = [False] * nvertex
    keys[src] = 0
    parents = [None] * nvertex
    parents[src]= -1
    actc[src]=0
    for j in range(nvertex):
        min = sys.maxsize
        for v in range(len(keys)):
            if max(keys[v],keys[v]+(constraints[v]-actc[v])) < min and mstL[v] == False:
                min = max(keys[v],keys[v]+(constraints[v]-actc[v]))
                u = v
        mstL[u]=True
        actc[u]=actc[parents[u]]+keys[u]
        for i in range(len(keys)):
            if (mstL[i] == False and graph.es[find(graph, u, i)]["weight"] < keys[i] ):
                keys[i] = graph.es[find(graph, u, i)]["weight"]
                parents[i] = u
    return graph_from_parents(graph,parents),src

