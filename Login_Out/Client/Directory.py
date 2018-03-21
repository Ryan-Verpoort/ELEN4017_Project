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
        
    def placeFile(self, FileA, socket, Encode_Type):
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
        
        

    def getFile(self, FileA, socket, Encode_Type):
        File = open(self.path+FileA,'wb')
        if Encode_Type == "None":
            data = socket.recv(8192)
            while data:
                print "Receiving..."
                File.write(data)
                data = socket.recv(8192)
        else:
            data = socket.recv(8192).decode(Encode_Type)
            while data:
                print "Receiving..."
                File.write(data)
                data = socket.recv(8192).decode(Encode_Type)
        print "Done Receiving"
        
    #function for printing directory
    def List(self):
        listDir = os.listdir(self.path)
        return listDir


'''def getEncoding(File_Name):
    end=len(File_Name)
    extensionIndex = File_Name.find(".")
    extension = File_Name [extensionIndex:end]
    if extension in EXTENSION:
        return ENCODING[EXTENSION[extension]]
    print "Only accept .jpeg .png .mp4 .txt"
    return ""'''

    