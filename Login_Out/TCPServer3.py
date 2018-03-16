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
PI_Port     = 12346  

#Set up Server and PI_Socket
PI_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerAddressPI = ('localhost', PI_Port)
PI_Socket.bind(ServerAddressPI)
PI_Socket.listen(4)

# This class will handle all commands and return messages        
class ClientPIThread(Thread):
    def __init__(self, connection, ClientAddr):
        Thread.__init__(self)
        self.FTP_Server_Interface = FTP_Server_Interface(connection, ClientAddr)
        
    def run(self):
            # Continuously check commands from user
            self.FTP_Server_Interface.CommandProcessor() 
            
    
            
while True:
    print >>sys.stderr, 'Waiting for connection...'
    # socket, name, port
    connection, ClientAddr = PI_Socket.accept() 
    print >>sys.stderr, 'Connection from: ', ClientAddr
    newthread = ClientPIThread(connection, ClientAddr)
    newthread.start()

