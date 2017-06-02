from socket import *
import pickle

sock = socket(AF_INET, SOCK_DGRAM)
table = {'A':5000, 'B':5001, 'C':5002, 'D':5003, 'E':5004, 'F':5005}
while 1:
    print "What would you like to do?"
    print "1. Change cost of link"
    c = raw_input()
    if c == 1:
        a = raw_input("First node: ")
        b = raw_input("Second node: ")
        d = raw_input("Please enter the new cost: ")
        d = int(d)
        data = [["COST-CHANGE"], b, d]
        packet = pickle.dumps(data)
        sock.sendto(packet, ("127.0.0.1", table[a]))
        data = [["COST-CHANGE"], a, d]
        packet = pickle.dumps(data)
        sock.sendto(packet, ("127.0.0.1", table[b]))
        