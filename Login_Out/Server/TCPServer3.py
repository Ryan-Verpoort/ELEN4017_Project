# coding: utf-8
import socket
import sys
import os
from threading import Thread
from SocketServer import ThreadingMixIn 
from Directory import *
#------------------------
# Default port numbers
#------------------------
# The PI (Protocol Intepreter) port generally deals with commands and reply messages. AKA Control Socket
# The DTP (Data Transfer Protocol) port generally is used for the transfer of data. AKA Data Socket
# The DTP can be changed.
#------------------------
PI_Port     = 12341
DTP_Port    = 12340
            
class Socket(object):
    def __init__ (self, Source_Name, Source_Port):
        if isinstance(Source_Name, str):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.SourceAddress  = (Source_Name, Source_Port)
            self.DestAddr =("",0)
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.Bind()
        else:
            self.socket = Source_Name #socket will be passed here
    
    def Accept(self):
        self.connection, self.DestAddr = self.socket.accept()
        
    def Connect(self):
        self.socket.connect(self.DestAddr)
        
    def Disconnect(self):
        #self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
    
    def Bind (self):
        self.socket.bind(self.SourceAddress)

    def setDestAddress(self, address):
        self.DestAddr = (address)
        
    def sendReply(self, ServerMsg):
        if not ServerMsg =="":
            self.socket.sendall(ServerMsg)
            print "C<-----------------------S "+ ServerMsg
        ServerMsg = ""
        return

    def receiveCommand(self):
        msg = self.socket.recv(8192)
        print "C----------------------->S "+ msg
        return msg

    def sendData(self, File_Name, username,  Encoding_Type):
        UploadDir = DirectoryData("/ClientDatabase/"+username+"/")
        print UploadDir.path
        UploadDir.retrFile(File_Name, self.socket, Encoding_Type)
        self.socket.close()
        
    def receiveData(self, File_Name, username,  Encoding_Type):
        
        DownloadDir = DirectoryData("/ClientDatabase/"+username+"/")
        print DownloadDir.path
        DownloadDir.storeFile(File_Name, self.socket, Encoding_Type)
        self.socket.close()
        #self.Disconnect()
    
