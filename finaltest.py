from Main import loadFileConfig
from MyAgentChest import MyAgentChest
from MyAgentGold import MyAgentGold
from MyAgentStones import MyAgentStones
import numpy as np
env, lAg = loadFileConfig("env1.txt")
tresA = np.array(env.grilleTres)
trespos=list(zip(*np.where(tresA!=None)))
print(len(trespos))
def allfinished(agents):
    for i in agents:
        if(i.state!="End"):
            return False
    return True

chestagents=[]
for i in lAg.values():
    if(type(i)==MyAgentChest):
        chestagents.append(i)

goldagents=[]
for i in lAg.values():
    if(type(i)==MyAgentGold):
        goldagents.append(i)
stonesagents=[]
for i in lAg.values():
    if(type(i)==MyAgentStones):
        stonesagents.append(i)
if(len(stonesagents)>0):
    stonesagents[0].setup(True)
    for i in range(len(stonesagents)-1):
        stonesagents[i+1].setup()
if(len(goldagents)>0):
    goldagents[0].setup(True)
    for i in range(len(goldagents)-1):
        goldagents[i+1].setup()
if(len(chestagents)>0):
    chestagents[0].setup(True)
    for i in range(len(chestagents)-1):
        chestagents[i+1].setup()

for i in lAg.values():
    i.Begin()
while(not allfinished(lAg.values())):
    for i in lAg.values():
        print("agent problematique",i.id,i.path,(i.posX,i.posY),i.state,type(i),i.chestlist)
        i.step()

print("\n\n******* SCORE TOTAL : {}".format(env.getScore()))
