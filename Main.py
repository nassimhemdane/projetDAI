
from Environment import Environment
from MyAgentGold import  MyAgentGold
from MyAgentChest import MyAgentChest
from MyAgentStones import MyAgentStones
from Treasure import Treasure


def loadFileConfig(nameFile) :

    file = open(nameFile)
    lines = file.readlines()
    tailleEnv = lines[1].split()
    tailleX = int(tailleEnv[0])
    tailleY = int(tailleEnv[1])
    zoneDepot = lines[3].split()
    cPosDepot =  (int(zoneDepot[0]), int(zoneDepot[1]))
    dictAgent = dict()

    env = Environment(tailleX, tailleY, cPosDepot)
    cpt = 0

    for ligne  in lines[4:] :
        ligneSplit = ligne.split(":")
        if(ligneSplit[0]=="tres"): # new treasure
            if(ligneSplit[1]=="or"):
                env.addTreasure(Treasure(1, int(ligneSplit[4])), int(ligneSplit[2]), int(ligneSplit[3]))

            elif(ligneSplit[1]=="pierres"):
                tres = Treasure(2, int(ligneSplit[4]))
                env.addTreasure(tres, int(ligneSplit[2]), int(ligneSplit[3]))
        elif(ligneSplit[0]=="AG") : #new agent
            if(ligneSplit[1]=="or"):
                id = "agent" + str(cpt)
                agent = MyAgentGold(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt +1

            elif(ligneSplit[1]=="pierres"):
                id = "agent" + str(cpt)
                agent = MyAgentStones(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt + 1

            elif (ligneSplit[1] == "ouvr"):
                id = "agent" + str(cpt)
                agent = MyAgentChest(id, int(ligneSplit[2]), int(ligneSplit[3]), env)
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt = cpt + 1

    file.close()
    env.addAgentSet(dictAgent)

    return (env, dictAgent)


#def main():
#    env, lAg = loadFileConfig("env1.txt")
#    print(env)
#    for a in lAg.values() :
#        print(a)
#
#
#    #Exemple where the agents move and open a chest and pick up the treasure
#    lAg.get("agent0").move(7,4,7,3)
#    lAg.get("agent0").move(7, 3, 6, 3)
#    lAg.get("agent0").open()
#    print(env)
#    lAg.get("agent0").move(6, 3, 7, 3)
#    print(env)
#    lAg.get("agent4").move(6,7,6,6)
#    lAg.get("agent4").move(6, 6, 6, 5)
#    lAg.get("agent4").move(6, 5, 6, 4)
#    lAg.get("agent4").move(6, 4, 6, 3)
#    print(env)
#    lAg.get("agent4").load(env) # fail because agent4 has not the right type
#    lAg.get("agent4").move(6, 3, 7, 5) # fail because position (7,5) is not a neighbour of the current position
#    lAg.get("agent4").move(6, 3, 6, 2)
#    print(env)
#    lAg.get("agent2").move(5, 2, 5, 3)
#    lAg.get("agent2").move(5, 3, 6, 3)
#    lAg.get("agent2").load(env) # Success !
#    print(env)
#
#    #Example of unload tresor
#    lAg.get("agent2").move(6, 3, 5,2)
#    lAg.get("agent2").move(5, 2, 5, 1)
#    lAg.get("agent2").move(5, 1, 5, 0)
#    lAg.get("agent2").unload()
#    print(env)
#    #  Example where the agents communicate
#
#    lAg.get("agent2").send("agent4", "Hello !")
#    lAg.get("agent4").readMail()
#
#
#    ##############################################
#    ####### TODO #################################
#    ##############################################
#
#    # make the agents plan their actions (off-line phase)
#
#
#    # make the agents execute their plans
#
#
#
#    # print each agent's score
#
#
#    print("\n\n******* SCORE TOTAL : {}".format(env.getScore()))
#main()
#