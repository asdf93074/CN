import socket as so
import sys
import pickle
import time
import copy
from threading import Thread

def server():
    global neighboursCosts, nT, change, costTable, ownLinks
    timeout = []
    s = so.socket(so.AF_INET, so.SOCK_DGRAM)
    s.bind(('127.0.0.1', int(sys.argv[2])))
    while 1:
        msg, cli = s.recvfrom(1024) 
        newData = pickle.loads(msg)
        if newData[0] != sys.argv[1]:
            if newData[1] == "KEEP-ALIVE":
                nT[newData[0]] = time.time()
            elif newData[0] == "COST-CHANGE":
                ct1 = ownLinks[newData[1]][0]
                ownLinks[newData[1]][0] = newData[2]
                ct = findNeighbour(newData[1],costTable)
                if costTable[ct][1] > ownLinks[newData[1]][0]:
                    costTable[ct][1] = ownLinks[newData[1]][0]
                    for i in range(len(costTable)-1):
                        if len(costTable[i + 1][3]) == 2 and costTable[i + 1][0] != newData[1]:
                            if costTable[i + 1][3][1] == newData[1]:
                                costTable[i + 1][1] = costTable[i + 1][1] - ct1 + ownLinks[newData[1]][0]
                    change = 1
            else:
                neighboursCosts[newData[0]] = newData
                bellford()
        for x in nT:
            temp = time.time()
            if temp - nT[x] > 11:
                costTable[findNeighbour(x, costTable)][1] = float("inf")
                print x, "timed out"
                timeout.append(x)
                change = 1
        for i in range(len(timeout)):
            nT.pop(timeout[i], None)
    
def broadcast():
    global change, ownLinks
    modTable = []
    while True:
        if change == 1:
            change = 0
            c = so.socket(so.AF_INET, so.SOCK_DGRAM)
            global costTable
            for i in range(len(costTable)-1):
                modTable = copy.deepcopy(costTable)
                #print modTable
                for d in range(len(costTable)-1):
                    if len(modTable[d + 1][3]) == 2:
                        if modTable[d + 1][3][1] == costTable[i+1][0]:
                            modTable[d + 1][1] = float("inf")
                #print "SENDING " + str(modTable) + " TO " + costTable[i + 1][0]
                packet = pickle.dumps(modTable)
                c.sendto(packet, ('127.0.0.1',costTable[i+1][2]))
                #print "END"

def timers():
    global nT, costTable, change, ownLinks
    timeout = []
    while 1:
        for x in nT:
            temp = time.time()
            if temp - nT[x] > 11:
                costTable[findNeighbour(x, costTable)][1] = float("inf")
                print x, "timed out"
                timeout.append(x)
                change = 1
        for i in range(len(timeout)):
            nT.pop(timeout[i], None)

def keepalive():
    global ownLinks
    k = so.socket(so.AF_INET, so.SOCK_DGRAM)
    p = [sys.argv[1], "KEEP-ALIVE"]
    pd = pickle.dumps(p)
    while 1:
        for i in ownLinks:
            k.sendto(pd, ('127.0.0.1', ownLinks[i][1]))
        time.sleep(10)

def bellford():
    global costTable, neighboursCosts, change
    print "I am Router " + sys.argv[1]
    for x in neighboursCosts:
        for y in range(len(neighboursCosts[x]) - 1):
            y = y + 1
            if neighboursCosts[x][y][0] != sys.argv[1] and x != sys.argv[1]:
                t = findNeighbour(neighboursCosts[x][y][0], costTable)
                p = findNeighbour(x, costTable)
                if p != 0:
                    if t != 0:
                        if costTable[t][3][1] == x:
                            costTable[t][1] = costTable[p][1] + neighboursCosts[x][y][1]
                        else:
                            try:
                                if costTable[p][1] + neighboursCosts[x][y][1] < costTable[t][1]:
                                    costTable[t][1] = costTable[p][1] + neighboursCosts[x][y][1]
                                    costTable[t][3] = costTable[0] + x
                                    change = 1
                            except:
                                print x, costTable
                    else:
                        change = 1
                        costTable.append([str(neighboursCosts[x][y][0]),float(costTable[p][1] + neighboursCosts[x][y][1]),
                                          int(neighboursCosts[x][y][2]),str(costTable[0]+x)])
    for z in range(len(costTable) - 1):
        print "Least cost path to router " + costTable[z + 1][0] + ": " + str(costTable[z + 1][3]) + " and the cost is " + str(costTable[z + 1][1])
      
def minValue(a, b):
    if a < b:
        return a
    else:
        return b

def findNeighbour(NID, Table):
    for i in range(len(Table) - 1):
        if Table[i + 1][0] == NID:
            return i + 1
    return 0

change = 1
neighboursCosts = {}
costTable = []
ownLinks = {}
nT = {}
costTable.append(sys.argv[1])
config = open(str(sys.argv[3]), "r")
count = int(config.readline())
for x in range(count):
    line = config.readline()
    configList = line.split()
    ownLinks[configList[0]] = [float(configList[1]),int(configList[2]),str(costTable[0]) + str(configList[0])]
    costTable.append([str(configList[0]),float(configList[1]),int(configList[2]),str(costTable[0]) + str(configList[0])])

costTable.append([str(sys.argv[1]),float(0),int(sys.argv[2]),str(sys.argv[1])])

ST = Thread(target=server)
sys.stdout.flush()
Broad = Thread(target=broadcast)
sys.stdout.flush()
keep = Thread(target=keepalive)
sys.stdout.flush()
#timeOut = Thread(target=timers)
#bell = Thread(target=bellford)
#sys.stdout.flush()

ST.start()
Broad.start()
keep.start()
#timeOut.start()

ST.join()
Broad.join()
keep.join()
#timeOut.join()