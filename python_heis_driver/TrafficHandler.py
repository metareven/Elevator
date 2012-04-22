#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Lars
#
# Created:     13.04.2012
# Copyright:   (c) Lars 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
from multiprocessing import *
import socket
import time
import threading
#import elevator

"""TODO
--------------------------------------------------------------------------------

    ----------------------------------------------------------------------------
"""


class SocketProcess(Process):
    def __init__(self, func,args):
        super(SocketProcess,self).__init__()
        self.func = func
        self.args = args
        self.is_stop = Event()
        self.is_stop.clear()

    def run(self):
        self.func(*self.args)

class SocketThread (threading.Thread):
    def __init__(self, func,args):
        self.func = func
        self.args = args
        threading.Thread.__init__(self)

    def run(self):
        self.func(*self.args)



class TrafficHandler:
    TRIES = 5
    TIMEOUT = 0.2

    def __init__(self):
        self.IPs = ["Laks","Laks"]
        self.my_ip = socket.getfqdn()
        self.port = 8154
        #self.ele = elevator.Elevator()
        self.elevatorlock = Lock()
        self.idlock = Lock()
        self.messageid = 0
        for i in xrange(len(self.IPs)):
            if self.IPs[i] == self.my_ip:
                self.next = self.IPs[(i+1)%len(self.IPs)] #the next IP in the sequence
                self.previous = self.IPs[(i-1)%len(self.IPs)] #the previous IP in the sequence

    def start(self):
        """starts the TrafficHandler"""
        #p = Process(target=TrafficHandler.accept,args=(1,))
        #p.start()
       #p2 = SocketThread(func=TrafficHandler.accept,args=(1,))
        #p2.start()
        p3 = SocketProcess(func=TrafficHandler.accept,args=(self,))
        p3.start()

    def generate_id(self):
        self.idlock.acquire()
        temp = self.messageid
        self.messageid = 3000+((self.messageid+1)%1000)
        self.idlock.release()
        return self.messageid



    def send_job(self,job):
        """sends a list of buttonpresses to the next elevator, should be run in a seperate process"""
        msg = self.my_ip + "[" + job[1] + "]"
        target = self.next
        res = self.send(msg,self.next,self.TRIES)
        while not res:
            #print "was not able to send"
            res = self.send(msg,self.next,self.TRIES)
            target = self.get_next()

    def get_next(self):
        """fetches the next ip in line"""
        for x,y in enumerate(self.IPs):
            if y == self.next:
                return self.IPs[(x+1)%len(self.IPs)] #if self.IPs[(x+1)%len(self.IPs)]  != self.my_ip else self.IPs[(x+2)%len(self.IPs)]




    def send(self,message,ip,triesleft):
        """sends message to ip and returns the number of characters you were able to send"""
        _id = self.generate_id()
        try:
            to = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP SOCKET
            to.settimeout(self.TIMEOUT + 1)
            print "trying to connect to " + ip + " on" + self.port
            to.connect((ip,self.port))
            print "done connecting"
            res = to.send(message+str(_id))
            counter = 0
            while True:
                try:
                    if(counter > self.TRIES):
                        print "returning none"
                        return None
                    print "waiting for ack " + str(counter)
                    counter += 1
                    time.sleep(self.TIMEOUT)
                    to.recv(1024)
                except:
                    time.sleep(0.1)
                    print "did not get acked"
            to.send("ackack")
            print "managed to ackack"
            """
            to.close()
            #now lets check if they got the message
            check = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            check.settimeout(self.TIMEOUT)
            check.bind((self.my_ip,_id))
            print "waiting for ack"
            check.accept()
            print "ack received"
            #if accept() went through then we know the message got there
            """
            return res
        except:
            if triesleft < 0:
                return None
            else:
                print "tries left " + str(triesleft)
                tr = triesleft-1
                return self.send(ip,tr,triesleft-1)

    def process_message(self,message):
        """processes a message"""
        temp = message.strip()
        if not message:
            return 0
        print "------------.-.-.-.-.-.-"
        print temp
        print "--------------.-.-.-.-.-."

        temp = message.split("[")
        ip = temp[0].strip()
        arr = temp[1].split("]")
        jobs = arr[0].split(",")
        _id = int(arr[1].strip())
        for job in jobs:
            (floor,direction) = job.split(" ")
            if False: # self.ele.check_job(job):
                self.ele.add_job(floor,direction,self.elevatorlock)
            else:
                temppros = SocketProcess(func=self.send_job,args=((floor,job),))
                temppros.start()
        #let's "ack" that message
        """
        for i in xrange(self.TRIES):
            try:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.settimeout(self.TIMEOUT)
                #print "ip " + ip
                #print "id" + str(_id)
                sock.connect((ip,_id))
                sock.close()
                #print "managed to ack"
                break
            except:
                #print "could not ack to " + ip + " on " +str(_id)
                pass
        """
        return 1

    def accept(self):
        """listens for incoming connections and stuff"""
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.bind((self.my_ip,8154))
        server_socket.listen(len(self.IPs))
        while True:
            (sock,addr) = server_socket.accept()
            (ip,port) = addr
            TrafficHandler.receive_message(self,sock,ip)

    def receive_message(self,sock,ip,triesleft = TRIES):
        """receives a message from a socket"""
        ackacked = False;
        sock.settimeout(TrafficHandler.TIMEOUT)
        #process the message
        processcounter = 0
        res = TrafficHandler.process_message(self,sock.recv(1024))
        while not res:
            res = TrafficHandler.process_message(self,sock.recv(1024))
            processcounter += 1
            if processcounter > self.TRIES:
                return None
        print "doen processing"
        counter = 0
        nomessagecount = 0
        while not ackacked:
            sock.send("ack")
            print "sending ack"
        #wait for the ack-ack
            try:
                 sock.recv(1024)
                 ackacked = True
            except:
                time.sleep(0.1)
                counter += 1
                if counter > self.TRIES:
                    return None
        print "done recving"


        """
        if not res:
            return self.receive_message(sock,ip,triesleft-1) if triesleft>=0 else None
        else:
            return res
        """















def main():
    handler = TrafficHandler()
    handler.start()
    s = socket.socket()
    #s.bind(("localhost",9876))
    s.connect((socket.getfqdn(),8154))
    s.send(socket.getfqdn() + "[1 1]"+str(3100))
    s.close()

if __name__ == '__main__':
    main()
