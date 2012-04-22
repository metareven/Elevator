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
        self.IPs = ["localhost"]
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



    def send_job(self,job):
        """sends a list of buttonpresses to the next elevator, should be run in a seperate process"""
        msg = self.my_ip + job
        if self.next == self.my_ip:
            get_next()
        while not send(msg,self.next):
            get_next()

    def get_next(self):
        """fetches the next ip in line and sets it to self.next,skips itself"""
        for x,y in enumerate(self.IPs):
            if y == self.next:
                self.next = self.IPs[(x+1)%len(self.IPs)] #if self.IPs[(x+1)%len(self.IPs)]  != self.my_ip else self.IPs[(x+2)%len(self.IPs)]




    def send(self,message,ip,triesleft=TRIES):
        """sends message to ip and returns the number of characters you were able to send"""
        try:
            id = self.generate_id()
            to = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP SOCKET
            to.settimeout(self.TIMEOUT)
            to.connect((ip,self.port))
            res = to.send(message+id)
            to.close()
            #now lets check if they got the message
            check = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            check.settimeout(self.TIMEOUT)
            check.bind((self.my_ip,id))
            check.accept()
            #if accept() went through then we know the message got there
            return res
        except:
            return send(ip,triesleft-1) if triesleft>=0 else None

    def process_message(self,message):
        """processes a message"""
        temp = message.strip()
        temp = message.split("[")
        print temp
        ip = temp[0].strip()
        arr = temp[1].split("]")
        jobs = arr[0].split(",")
        _id = int(arr[1].strip())
        for job in jobs:
            (floor,direction) = job.split(" ")
            if self.ele.check_job(job):
                self.ele.add_job(floor,direction,self.elevatorlock)
            else:
                Process(target=send_job,args=(self,[job])).start()
        #let's "ack" that message
        for i in xrange(self.TRIES):
            try:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.settimeout(self.TIMEOUT)
                sock.connect((ip,_id))
                sock.close()
                break
            except:
                print "could not ack to " + ip + " on " +str(_id)
        return 1

    def accept(self):
        """listens for incoming connections and stuff"""
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.bind((self.my_ip,8154))
        server_socket.listen(len(self.IPs))
        while True:
            (sock,addr) = server_socket.accept()
            (ip,port) = addr
            print ip + " connected"
            #p = Process(target=TrafficHandler.receive_message,args=(sock,ip))
            #p.start()
            #p.join()
            #p = SocketProcess(1,TrafficHandler.receive_message,(self,1,ip))
            #p.start()
            TrafficHandler.receive_message(self,sock,ip)

    def receive_message(self,sock,ip,triesleft = TRIES):
        """receives a message from a socket"""
        sock.settimeout(TrafficHandler.TIMEOUT)
        res = TrafficHandler.process_message(self,sock.recv(1024))
        if not res:
            return self.receive_message(sock,ip,triesleft-1) if triesleft>=0 else None
        else:
            return res















def main():
    handler = TrafficHandler()
    handler.start()
    while True:
        time.sleep(1)
        try:
            s = socket.socket()
            #s.bind(("localhost",9876))
            s.connect((socket.getfqdn(),8154))
            s.send("0.0.0.0[1 1,2 1,3 1]1")
            s.close()
        except:
            print "crash =( "
    pass
if __name__ == '__main__':
    main()
