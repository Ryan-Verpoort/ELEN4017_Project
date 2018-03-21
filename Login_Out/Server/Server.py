from threading import Thread
from SocketServer import ThreadingMixIn 
from FTP_Server0 import *

class Server(object):
    def __init__ (self, hostname, port):
        self.socket = Socket(hostname, port)
        
    def changeServerAddress(self, address):
        self.SourceAddress = (address)
         
    def runServer(self):
       # self.socket.bind(self.ServerAddress)
        self.socket.socket.listen(5)
        while True:
            print >>sys.stderr, 'Waiting for connection...'
            # socket, name, port
            self.socket.Accept() 
            newthread = ClientPIThread(self.socket.connection, self.socket.DestAddr)
            newthread.start()
        self.socket.Disconnect()
    
# This class will handle all commands and return messages        
class ClientPIThread(Thread):
    def __init__(self, connection, ClientAddr):
        Thread.__init__(self)
        self.FTP_Server_Interface = FTP_Server_Interface(connection, ClientAddr)
        
    def run(self):
            # Continuously check commands from user
            self.FTP_Server_Interface.CommandProcessor() 
            print "End of Thread"
            
server = Server('localhost', PI_Port)
server.runServer()