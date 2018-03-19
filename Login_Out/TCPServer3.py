# coding: utf-8
import socket
import sys
from threading import Thread
from SocketServer import ThreadingMixIn 
from FTP_Server0 import *
#------------------------
# Default port numbers
#------------------------
# The PI (Protocol Intepreter) port generally deals with commands and reply messages. AKA Control Socket
# The DTP (Data Transfer Protocol) port generally is used for the transfer of data. AKA Data Socket
# The DTP can be changed.
#------------------------
PI_Port     = 12341
DTP_Port    = 12340
#Set up Server and PI_Socket

class PISocket(object):
    def __init__ (self, hostname, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SourceAddress  = (hostname, port)
        self.s.bind(self.SourceAddress)
        
    def changeServerAddress(self, address):
        self.SourceAddress = (address)
         
    def Disconnect(self):
        self.s.close()
    
    def runServer(self):
       # self.socket.bind(self.ServerAddress)
        self.s.listen(1)
        while True:
            print >>sys.stderr, 'Waiting for connection...'
            # socket, name, port
            connection, ClientAddr = self.s.accept() 
            print >>sys.stderr, 'Connection from: ', ClientAddr
            newthread = ClientPIThread(connection, ClientAddr)
            newthread.start()
        self.Disconnect()
# This class will handle all commands and return messages        
class ClientPIThread(Thread):
    def __init__(self, connection, ClientAddr):
        Thread.__init__(self)
        self.FTP_Server_Interface = FTP_Server_Interface(connection, ClientAddr)
        
    def run(self):
            # Continuously check commands from user
            self.FTP_Server_Interface.CommandProcessor() 
            
def DTPSocket(object):
    def __init__ (self, hostname, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerAddress   = (hostname, port)
        
    def changeServerAddress(self, address):
        self.ServerAddress = (address)
        self.Connect()
         
    def Connect(self):
        self.socket.connect(self.ServerAddress)
        
    def Disconnect(self):
        self.socket.close()
        
    def sendData(self, path):
        command = create_FTP_str(command,argument)
        print command
        self.socket.sendall(command.encode('UTF-8'))
        
    def receiveData(self):
        msg = self.socket.recv(8192).decode('UTF-8')
        print msg
        return msg
          
    
Server = PISocket('localhost', PI_Port)
Server.runServer()

    