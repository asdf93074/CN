import sys
from socket import *
import pickle

sock = socket(AF_INET, SOCK_DGRAM)

l = {}
names = []

for i in range(len(sys.argv)-1):
    f = open(sys.argv[i + 1], "r")
    d = int(f.readline())
    l[sys.argv[i+1][6]] = {}
    for j in range(d):
        c = f.readline()
        data = c.split()
        l[sys.argv[i+1][6]][data[0]] = float(data[1])
        
for i in l:
    names.append([i])
    
table = {'A':5000, 'B':5001, 'C':5002, 'D':5003, 'E':5004, 'F':5005}
while 1:
    print "-----------------------------------------------------------"
    print "What would you like to do?"
    print "1. Change cost of link"
    print "2. Print cost of each link"
    c = int(raw_input())
    if c == 1:
        a = raw_input("First node: ")
        b = raw_input("Second node: ")
        d = raw_input("Please enter the new cost: ")
        d = float(d)
        try:
            l[a][b] = d
            l[b][a] = d
            data = ["COST-CHANGE", b, d]
            packet = pickle.dumps(data)
            sock.sendto(packet, ("127.0.0.1", table[a]))
            data = ["COST-CHANGE", a, d]
            packet = pickle.dumps(data)
            sock.sendto(packet, ("127.0.0.1", table[b]))
        except:
            print "Wrong link entered."
        print "-----------------------------------------------------------\n"
    elif c == 2:
        for i in l:
            for j in l[i]:
                print i, "to", j," = ", l[i][j]
        print "-----------------------------------------------------------\n"
