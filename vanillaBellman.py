import threading
import socket
import sys
import copy
import pickle
import time

class Server(threading.Thread):
    def run(self):
        global ownName, ownPort, DVTableNeighbours, nT, ownLinksCosts, DVT, change, ownLinksHop
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("127.0.0.1", int(sys.argv[2])))
        timeout = []
        while True:
            msg, cli = s.recvfrom(2048)
            data = pickle.loads(msg)
            if data[0] == "KEEP-ALIVE":
                nT[data[1]] = time.time()
            elif data[0] == "COST-CHANGE":
                ownLinksCosts[data[1]] = data[2]
                for m in ownLinksHop:
                    if ownLinksHop[m] == data[1]:
                        DVT[m] = float("inf")
                BellmanFord()
            else:
                DVTableNeighbours[data[0]] = data[1]
                print "Recieved " + str(data[1]) + " From " + data[0]
                BellmanFord()
            for i in nT:
                temp = time.time()
                if temp - nT[i] > 12:
                    print i, "timed out"
                    ownLinksCosts[i] = float("inf")
                    DVT[i] = float("inf")
                    DVTableNeighbours.pop(i, None)
                    DVTableNeighbours = {}
                    for j in ownLinksHop:
                        if ownLinksHop[j] == i:
                            DVT[j] = float("inf")
                    timeout.append(i)
                    BellmanFord()
                    change = 1
            for j in range(len(timeout)):
                nT.pop(timeout[j], None)
                del timeout[j]
                j = j - 1
                

class Broadcast(threading.Thread):
    def run(self):
        global ownLinksPorts, change, ownLinksHop, ownName
        while True:
            if change == 1:
                change = 0
                global DVT
                modDVT = {}
                client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                for i in ownLinksPorts:
                    modDVT = copy.deepcopy(DVT)
                    for j in ownLinksHop:
                        if ownLinksHop[j] == i:
                            modDVT[j] = float("inf")
                    data = [ownName, modDVT]
                    packet = pickle.dumps(data)
                    client.sendto(packet, ("127.0.0.1",ownLinksPorts[i]))
                    #print "SENT " + str(data) + " to " + i + " at " + str(ownLinksPorts[i])

class KeepAlive(threading.Thread):
    def run(self):
        global ownLinksPorts, ownName
        k = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = ["KEEP-ALIVE", ownName]
        packet = pickle.dumps(data)
        while True:
            for i in ownLinksPorts:
                k.sendto(packet, ("127.0.0.1", ownLinksPorts[i]))
            time.sleep(10)

def BellmanFord():
    global ownLinksCosts, change, ownLinksHop, DVTableNeighbours, DVT, N, ownName

    print "I am Router " + ownName
    for x in N:
        temp = []
        hoptemp = {}
        if x in ownLinksCosts:
            temp.append(ownLinksCosts[x])
            hoptemp[ownLinksCosts[x]] = x
        for y in DVTableNeighbours:
            temp.append(ownLinksCosts[y] + DVTableNeighbours[y][x])
            hoptemp[(ownLinksCosts[y] + DVTableNeighbours[y][x])] = y
        old = copy.copy(DVT[x])
        if len(temp) == 0:
            temp.append(old)
        #hoptemp[old] = ownLinksHop[x]
        DVT[x] = min(temp)
        try:
            ownLinksHop[x] = hoptemp[DVT[x]]
        except:
            print hoptemp, ownLinksHop
        if old != DVT[x]:
            change = 1
    for q in DVT:
                print "Least cost path to " + q + ": " + ownLinksHop[q] + " and the cost is " + str(DVT[q])
    #DVTableNeighbours = {}
            

N = ["A", "B", "C", "D", "E", "F"]
ownLinksCosts = {}
ownLinksPorts = {}
ownLinksHop = {}
ownName = str(sys.argv[1])
ownPort = int(sys.argv[2])
DVTableNeighbours = {}
DVT = {}
nT = {}

config = open(str(sys.argv[3]), "r")
hostCount = int(config.readline())
ownLinksCosts[ownName] = float(0)
ownLinksHop[ownName] = ownName
for x in range(hostCount):
    line = config.readline()
    configList = line.split()
    name = configList[0]
    cost = float(configList[1])
    portno = int(configList[2])
    ownLinksCosts[name] = cost
    ownLinksPorts[name] = portno
    ownLinksHop[name] = name

for x in N:
    if x in ownLinksCosts:
        DVT[x] = ownLinksCosts[x]
    else:
        DVT[x] = float("inf")

#print DVT

change = 1

ServerThread = Server()
BroadcastThread = Broadcast()
KeepaliveThread = KeepAlive()

ServerThread.start()
BroadcastThread.start()
KeepaliveThread.start()

ServerThread.join()
BroadcastThread.join()
KeepaliveThread.join()
