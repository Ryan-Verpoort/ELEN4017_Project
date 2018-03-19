#coding: utf-8
import sys
import socket
import os
from threading import Thread

 
def create_FTP_str(Command, Argument=''):
    if Argument == '':
        Command = str(Command) + '\r\n'
    else:
        Command = str(Command) + ' ' + str(Argument) + '\r\n'
    #print Command
    return str(Command)
    
# The user-process default data port is the same as the control connection port (i.e., U)
def PISocket(object):
    def __init__ (self, hostname, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerAddress   = (hostname, port)
        
    def setServerAddress(self, address):
        self.ServerAddress = (address)
        self.Connect()
         
    def Connect(self):
        self.socket.connect(self.ServerAddress)
        
    def Disconnect(self):
        self.socket.close()
        
    def sendCommand(self, command):
        print command
        self.socket.sendall(command.decode('UTF-8'))
        
    def serverResponse(self):
        msg = self.socket.recv(8192).encode('UTF-8')
        print msg
        return msg
    
class Socket(object):
    def __init__ (self, Source_Name, Source_Port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SourceAddress  = (Source_Name, Source_Port)
        self.DestAddr =()
        #self.Bind()

    def Connect(self):
        self.socket.connect(self.DestAddr)
    
    def Disconnect(self):
        self.socket.close()
    
    def Bind (self):
         self.socket.bind(self.SourceAddress)

    def setDestAddress(self, address):
        self.DestAddr = (address)

    def sendCommand(self, command, argument=''):
        Command = create_FTP_str(command,argument)
        print Command
        self.socket.sendall(Command)

    def serverResponse(self):
        msg = self.socket.recv(8192)
        print msg
        return msg

    # Active Mode 
    def sendData(self, TransmittedFile, encoding):
        # Waiting for connection
        conn, Address = self.socket.accept()
        # Create file we wish to download
        # Receive data from connection
        # Write received data into created file
        if(encoding == "I"):
            Reading = TransmittedFile.read(8192)
            while (Reading):
                conn.send(Reading)
                Reading = TransmittedFile.read(8192)
        else:
            Reading = TransmittedFile.read(8192).encode(encoding)
            while (Reading):
                FileTransferSocket.send(Reading)
                Reading = TransmittedFile.read(8192).encode(encoding)
        TransmittedFile.close()
        conn.close()
    # Active Mode  
    def receiveData(self, file, encoding):
        # waiting for connection
        conn, Address = self.socket.accept()
        File_Name = '\Docs\\'+file
        # Open file we wish to upload
        # Write data to connection
        if(encoding == "I"):
            ReceivedData = FileTransferSocket.recv(8192)
            File =  open(File_Name,'wb')    
            while RecievedData:
                File.write(RecievedData)
                ReceivedData = FileTransferSocket.recv(8192)
        else:
            ReceivedData = FileTransferSocket.recv(8192).decode(encoding)
            File =  open(File_Name,'wb')            
            while RecievedData:
                File.write(RecievedData)
                ReceivedData = FileTransferSocket.recv(8192).decode(encoding)
        File.close()
        conn.close()
        
