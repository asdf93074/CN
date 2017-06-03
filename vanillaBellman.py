import threading
import socket
import sys
import copy

class Server(threading.Thread):
    def run(self):
        global ownName, ownPort, DVTableNeighbours
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("127.0.0.1", sys.argv[2]))
        while True:
            msg, cli = s.recvfrom(2048)
            data = pickle.loads(msg)
            if data[0] == "KEEP-ALIVE":
            elif data[0] == "COST-CHANGE"
            else:
                DVTableNeighbours[data[0]] = data[1]
                BellmanFord()

class Broadcast(threading.Thread):
    def run(self):
        global ownLinksPorts, change, ownLinksHop
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
                    packet = pickle.dumps(modDVT)
                    client.sendto(packet, ("127.0.0.1",ownLinksPorts[i]))

def BellmanFord():
    global ownLinksCosts, change, ownLinksHop, DVTableNeighbours, DVT, N

    temp = []
    for x in N:
        for y in DVTableNeighbours:
            if x in ownLinksCosts:
                temp.append(ownLinksCosts[x])
            temp.append(ownLinksCosts[y] + DVTableNeighbours[y][x])
        old = DVT[x]
        DVT[x] = min(temp)
        if old != DVT[x]:
            change = 1

N = ["A", "B", "C", "D", "E", "F"]
ownLinksCosts = {}
ownLinksPorts = {}
ownLinksHop = {}
ownName = str(sys.argv[1])
ownPort = int(sys.argv[2])
DVTableNeighbours = {}
DVT = {}
change = 1

config = open(str(sys.argv[3]), "r")
hostCount = int(config.readline())
ownLinksCosts[ownName] = float(0)
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