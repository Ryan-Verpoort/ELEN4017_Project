#coding: utf-8
import sys
import socket
import os
from Directory import *
from threading import Thread

 
def create_FTP_str(Command, Argument=''):
    if Argument == '':
        Command = str(Command) + '\r\n'
    else:
        Command = str(Command) + ' ' + str(Argument) + '\r\n'
    #print Command
    return str(Command)
    

class Socket(object):
    def __init__ (self, Source_Name, Source_Port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SourceAddress  = (Source_Name, Source_Port)
        self.DestAddr =("",0)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Bind()

    def Connect(self):
        self.socket.connect(self.DestAddr)
    
    def Accept(self):
        self.connection, self.DestAddr = self.socket.accept()

    def Disconnect(self):
        self.socket.close()
    
    def Bind (self):
         self.socket.bind(self.SourceAddress)

    def setDestAddress(self, address):
        self.DestAddr = (address)

    def sendCommand(self, command, argument=''):
        Command = create_FTP_str(command,argument)
        print "C---------------------->S " + Command
        self.socket.sendall(Command)

    def serverResponse(self):
        msg = self.socket.recv(8192)
        print "C<----------------------S " + msg
        return msg

    # Active Mode 
    def sendData(self, File_Name, encoding="None"):
        UploadDir = DirectoryData("/User/Uploads/")
        UploadDir.placeFile(File_Name, self.connection, encoding)
        self.connection.shutdown(socket.SHUT_WR)
        self.connection.close()
        
    def receiveData(self, File_Name, encoding):
        DownloadDir = DirectoryData("/User/Downloads/")
        DownloadDir.getFile(File_Name, self.connection, encoding)
        self.connection.close()
            