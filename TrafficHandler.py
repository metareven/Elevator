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
from .python_heis_driver import elevator as el

"""TODO
--------------------------------------------------------------------------------
    the elevator has to wait for an ack / syn ack after sending a message instead of just responding
    ----------------------------------------------------------------------------
"""


class SocketProcess(Process):
    def __init__(self,socket,fun,args):
        super(SocketProcess,self).__init__()
        self.socket = socket
        self.fun = fun
        self.args = args
        self.is_stop = Event()
        self.is_stop.clear()

    def run(self):
        self.fun(*self.args)



class TrafficHandler:
    TRIES = 5
    TIMEOUT = 0.2

    def __init__(self):
        self.IPs = ["localhost"]
        self.my_ip = socket.getfqdn()
        self.port = 8154
        self.elevator = el.Elevator()
        self.elevatorlock = Lock()
        for i in xrange(len(self.IPs)):
            if self.IPs[i] == self.my_ip:
                self.next = self.IPs[(i+1)%len(self.IPs)] #the next IP in the sequence
                self.previous = self.IPs[(i-1)%len(self.IPs)] #the previous IP in the sequence


    def respond(self,message,ip,triesleft=TRIES):
        """processes the message and responds to ip"""
        if not message:
            return None

        if not self.previous in message:
            #if someone else is sending us messages, our previous must have DCed
            self.previous = message.split("[")[0].strip()


        if  "[syn ack]" in message:
            return 1  #do nothing, the ack has been received and all is well
        try:
            to = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            to.settimeout(TrafficHandler.TIMEOUT)
            to.connect((ip,self.port))
            if "[ack]" in message:
                to.send(self.my_ip + "[syn ack]")
            else:
                process_message(message)
                to.send(self.my_ip + "[ack]")
            to.close()
            return 1
        except:
            return respond(message,ip,triesleft-1) if triesleft>=0 else None

    def start(self):
        """starts the TrafficHandler"""
        p = Process(target=TrafficHandler.accept,args=(self,))
        p.start()

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
            to = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP SOCKET
            to.connect((ip,self.port))
            res = to.send(message)
            to.close()
            return res
        except:
            return send(ip,triesleft-1) if triesleft>=0 else None

    def process_message(self,message):
        """processes a message"""
        temp = message.strip()
        temp = message.split("[")
        print temp
        ip = temp[0].strip()
        temp[1] = temp[1].replace("]","")
        jobs = temp[1].split(",")
        for job in jobs:
            (floor,direction) = job
            if self.elevator.check_job(job):
                self.elevator.add_job(floor,direction,self.elevatorlock)
            else:
                Process(target=send_job,args=(self,[job])).start()
        #TODO: send the floors to the elevator, let the elevator see if it
        # wants these floors and then either add them to itself or send them
        # onwards
        return 1

    def accept(self):
        """listens for incoming connections and stuff"""
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.bind((self.my_ip,8154))
        server_socket.listen(len(self.IPs))
        print "server initialized"
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
            s.send("0.0.0.0[hei,paa,deg]")
            s.close()
        except:
            print "crash =( "
    pass
if __name__ == '__main__':
    main()
