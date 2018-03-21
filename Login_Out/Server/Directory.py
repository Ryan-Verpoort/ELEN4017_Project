import sys
import os
import socket as s
#550 Requested action not taken.
#File unavailable (e.g., file not found, no access).

class DirectoryData(object):
    def __init__ (self, path):
        self.path = os.getcwd()+path
        
    def FileExists(self, fileA):
        print "Checking if file exists"
        listDir = self.List()
        for fileX in listDir:
            if fileX == fileA:
                print fileA+" exists"
                return True
        return False
        
    def retrFile(self, FileA, socket, Encode_Type):
        File = open (self.path+FileA,'rb')
        if Encode_Type == "None":
            Reading = File.read(8192)
            while Reading:
                print "Sending..."
                socket.send(Reading)
                Reading = File.read(8192)
        else:
            File = open (self.path+FileA,'rb')
            print self.path+FileA
            Reading = File.read(8192).encode(Encode_Type)
            while Reading:
                print "Sending..."
                socket.send(Reading)
                Reading = File.read(8192).encode(Encode_Type)
                
        File.close()
        print "Finished sending."

    def storeFile(self, FileA, socket, Encode_Type):
        print "storing " + FileA 
        print "encoding " + Encode_Type 
        File = open(self.path+FileA,'wb')
        if Encode_Type == "None":
            data = socket.recv(8192)
            
            while data:
                print "Receiving1..."
                File.write(data)
                data = socket.recv(8192)
        else:
            data = socket.recv(8192).decode(Encode_Type)
            
            while data:
                print "Receiving2..."
                File.write(data)
                print "Receiving2.1.."
                data = socket.recv(8192).decode(Encode_Type)  
                print "Receiving2.2.."
        print "Done Receiving"
        File.close()
        
    #function for printing directory
    def List(self):
        listDir = os.listdir(self.path)
        return listDir
        