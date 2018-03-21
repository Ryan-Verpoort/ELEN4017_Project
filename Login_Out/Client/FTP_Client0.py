import sys
import socket
import os
from TCPClient3 import *  
from Directory import *
# Class Containing all Client FTP commands 
''' TYPE - ASCII Non-print Image
         MODE - Stream
         STRUCTURE - File, Record
         COMMANDS - USER, QUIT, PORT,
                    TYPE, MODE, STRU,
                      for the default values
                    RETR, STOR,
                    NOOP.

      The default values for transfer parameters are:

         TYPE - ASCII Non-print
         MODE - Stream
         STRU - File'''
'''
FILE_EXTENSIONS = {
    "txt": "A",
    "png": "I",
    "mp4": "I",
    "Unrecognised": "N/A" 
}'''
FTP_TYPE = {
    "A": "UTF-8",
    "I": "None"
}

EXTENSION = {
    ".jpeg": "I",
    ".png" : "I",
    ".mp4" : "I",
    ".txt" : "A"
}

def getEncoding(File_Name):
    end=len(File_Name)
    extensionIndex = File_Name.find(".")
    extension = File_Name [extensionIndex:end]
    if extension in EXTENSION:
        return ENCODING[EXTENSION[extension]]
    print "Only Processing .jpeg .png .mp4 .txt"
    return ""

FTP_MODE = { "S": 1 }

FTP_STRU = { "F": 2 }

FTP_COMMAND = {  
    "USER": 1,            
    "PASS": 2,
    "QUIT": 3,
    "PORT": 4,
    "TYPE": 5,
    "MODE": 6,
    "STRU": 7,
    "RETR": 8,
    "STOR": 9,
    "LIST": 10,
    "HELP": 11,
    "NOOP": 12,
    "PASV": 13 
}

FTP_SM = {
"USER1":"331", # User name okay, need password.
"USER2":"332", # Need account for login.
"PASS1":"230", # User logged in, proceed.
"PASS2":"530", # Not logged in.
"QUIT" :"221", # Service closing control connection.
"OKAY" :"200", # Command okay.
"FAIL" :"500", # Syntax error, command unrecognized.
"DNE"  :"502", # Command not implemented.
"DATA" :"225", # Data connection open; no transfer in progress.
"DATAQ":"226", # Closing data connection. Success or abort.
"BPARA":"504", # Command not implemented for that parameter.
"BFILE":"550", # Requested file action not taken.
"BCON" : "425", # Can't open data connection."
"BTYPE": "451", # Requested action aborted: local error in processing.
"PASV" : "227" # Entering Passive Mode
}

DATA_FLOW = {
    "DOWNLOAD": 1,
    "UPLOAD": 2,
    "NONE": 3
}

Dest_PI_Port = 12341
Source_PI_Port = 12350

Dest_DTP_Port = 12330
Source_DTP_Port = 9999
class FTP_Client_Interface(object):

    def __init__ (self):
        self.PI_Socket = Socket(getNetworkIp(), Source_PI_Port)
        self.PI_Socket.setDestAddress(("localhost", Dest_PI_Port))
        self.PI_Socket.Connect()
        self.Port = 12345 # The Client will always have two ports, so that the two sockets can run in parallel
        self.DestAddr = ("",0)
        
        self.serverFlag = False
        self.usernameFlag = False
        self.loginFlag = False
        self.quitFlag = False
        self.portFlag = False
        self.transferFlag = False
        self.typeFlag = False
        self.passiveFlag = False
        
        self.dataFlow = DATA_FLOW["NONE"]
        self.type = FTP_TYPE["A"]
        self.mode = FTP_MODE["S"]
        self.stru = FTP_STRU["F"]
        self.ServerMsg = ""
        
    def FTP_Connect(self):
        self.PI_Socket.setDestAddress(("localhost",Dest_PI_Port))
        self.PI_Socket.Connect()
        
    def FTP_Disconnect(self):
        self.PI_Socket.Disconnect()
        print "Closing Socket..."
        
    def FTP_Login(self):
        command = "USER"
        self.USER(command)
        command = "PASS"
        self.PASS(command)
        if self.loginFlag:
            return True
        else:
            return False
            
    def TYPE(self,command):
        #if true let user choose type
        if self.typeFlag:
            encode = raw_input('Type: ')
            encode = encode.upper()
            if encode in FTP_TYPE:
                self.type = FTP_TYPE[encode]
            else:
                self.type = FTP_TYPE["A"]
                print "type argument not implemented-- Setting to default type"
            self.PI_Socket.sendCommand(command, encode)
            msg = self.PI_Socket.serverResponse()
            
    def USER (self, command):
        username = raw_input('Username: ' )
        self.PI_Socket.sendCommand(command, username)
        msg = self.PI_Socket.serverResponse()
        if msg[0:3] == FTP_SM["USER1"]:
            print "Username right\n"
            self.usernameFlag = True
        else:
            self.usernameFlag = False
    
    def PASS (self, command):
        count = 3
        while count>0:
            password = raw_input('Password: ' )
            if self.usernameFlag == False:
                self.QUIT("QUIT")
                print "Invalid Credentials..."
                return
			
            self.PI_Socket.sendCommand(command, password)
            msg = self.PI_Socket.serverResponse()
            if msg[0:3] == FTP_SM["PASS1"]:
                self.loginFlag = True
                print "Logged In"
                break
            else:
                count = count-1
                print "Attempts Left: "+ str(count)
        if count == 0:
            self.QUIT("QUIT")
    
    def PORT(self, command):
        if self.portFlag:
            newPort = raw_input('NewPort: ' )
            self.Port = int (newPort)
        else:
            newPort = self.Port
            
        ipstring = getNetworkIp()
        Host = socket.inet_aton(ipstring)
        
        p1 = int(newPort)/256
        p2 = int(newPort)%256
        print p1
        print p2
        p1 = chr(p1)
        p2 = chr(p2)
        NewAddress = Host[0] + ',' +Host[1] +','+ Host[2] +','+ Host[3] + ',' + p1+ ',' +p2
        self.PI_Socket.sendCommand(command, NewAddress)
        print NewAddress
        msg = self.PI_Socket.serverResponse()
        if msg[0:3] == FTP_SM["OKAY"]:
            self.transferFlag = True
        else:
            self.transferFlag = False
    
    
    def PASV(self, command):
        
        self.PI_Socket.sendCommand(command)
        Reply = self.PI_Socket.serverResponse()
        if not Reply[0:3] == FTP_SM["PASV"]:
            return
        print(Reply)
        start = Reply.find('(')
        end = Reply.find(')')
        address= Reply[start+1:end]
        address = address.split(",")
        print address
        Host = address[0]+ address[1]+ address[2]+ address[3]
        host = socket.inet_ntoa(Host)
        port = ord(address[4])*256 + ord(address[5])
        print('New host Data Connection: ' + str(host))
        print('New port Data Connection: ' + str(port))
        
        self.DestAddr=(host, port)
        
        
    def LIST(self,command):
        # Enter PASV
        # self.PASV("PASV")
        self.PI_Socket.sendCommand(command)
        DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        msg = self.PI_Socket.serverResponse()
        if msg[0:3] == FTP_SM["DATA"]:
            print self.DestAddr
            DataSocket.connect(self.DestAddr)
            asd = DataSocket.recv(8192).decode("UTF-8")
        msg = self.PI_Socket.serverResponse()
        if msg[0:3] == FTP_SM["DATAQ"]:
            DataSocket.close()
        
    def STOR(self, command):
        # 1. check if file exists
        # 2. check if file has the correct type for encoding
        # 2. set connection up
        # 3. send data to server once server has connected
        # 4. check if upload successful
        # ------- 1 -----------
        
        File_Name = raw_input('File Name: ')
        File_Name = File_Name
        UploadDir = DirectoryData("/User/Uploads/")
        if not UploadDir.FileExists(File_Name):
            self.transferFlag = False
            return
        
        self.PORT("PORT")
        self.TYPE("TYPE")
        if self.transferFlag and (not self.serverFlag): 
            self.transferFlag = False # only one transfer at a time
            self.dataFlow = DATA_FLOW["UPLOAD"]
            DataSocket = Socket(getNetworkIp(), self.Port)
            DataSocket.socket.listen(1)
            # ------- 2 -----------    
            self.PI_Socket.sendCommand(command, File_Name)
            # Check if server connected successfully
            msg = self.PI_Socket.serverResponse()
            if msg[0:3] == FTP_SM["DATA"]:
                # ------- 3 -----------
                DataSocket.Accept()
                self.serverFlag = True
                DataSocket.sendData(File_Name, self.type)   
            else:
                DataSocket.Disconnect()
                return
            DataSocket.Disconnect()
        
        # Check if server has disconnected
        # ------- 4 -----------
        msg = self.PI_Socket.serverResponse() # should be closed
        self.serverFlag = False
        self.dataFlow = DATA_FLOW["NONE"]
        self.typeFlag = False
        self.type = FTP_TYPE["A"]
        if msg[0:3] == FTP_SM["DATAQ"]:
            self.serverFlag = False
              
        
    def RETR(self, command):
        # 1. check if file exists
        # 2. check if file ext is appropriate for encoding type
        # 3. set connection up 
        # 4. send data to server once server has connected
        # 5. close connection
        
        # ------- 1 ----------- 
        File_Name = raw_input('File Name: ')
    
        # ------- 2 ----------- 
        self.PORT("PORT")
        self.TYPE("TYPE")
      
        if self.transferFlag and not self.serverFlag: 
            
            self.transferFlag = False # only one transfer at a time
            self.dataFlow = DATA_FLOW["DOWNLOAD"]
            # start listening for server
            DataSocket = Socket(getNetworkIp(), self.Port)
            DataSocket.socket.listen(1)
            # ------- 1 ----------- 
            # ------- 2 ----------- 
            # ------- 3 ----------- 
            self.PI_Socket.sendCommand(command, File_Name)
            msg = self.PI_Socket.serverResponse()
            if msg[0:3] == FTP_SM["DATA"]:
                # ------- 3 ----------- 
                DataSocket.Accept()
                self.serverFlag = True
                DataSocket.receiveData(File_Name, self.type)
            else:
                self.serverFlag = False
                DataSocket.Disconnect()
                return
            DataSocket.Disconnect()
        # ------- 4 -----------   
        msg = self.PI_Socket.serverResponse() # should be closed
        self.serverFlag = False
        self.dataFlow = DATA_FLOW["NONE"]
        self.typeFlag = False
        self.type = FTP_TYPE["A"]
        if msg[0:3] == FTP_SM["DATAQ"]:
            self.serverFlag = False
        
    def NOOP(self,command):
        self.PI_Socket.sendCommand(command)
        msg = self.PI_Socket.serverResponse()
        return
        
    def QUIT (self, command):
        self.PI_Socket.sendCommand(command)
        msg = self.PI_Socket.serverResponse()
        print msg
        if msg[0:3] == FTP_SM["QUIT"]:
            print "Disconnected"
            self.loginFlag = False
            self.usernameFlag = False
            self.quitFlag = True
         
            
    def CommandProcessor(self):
        # This function takes in 
        
        while not self.quitFlag:
            #print "SF %r UF %r, LF %r, QF %r, PF %r, TF %r" %(self.serverFlag, self.usernameFlag,self.loginFlag,self.quitFlag,self.portFlag,self.transferFlag)
            cmd = Input()
            #print "CMD: "+cmd
            if cmd in FTP_COMMAND:
                if FTP_COMMAND[cmd] == FTP_COMMAND["USER"]:
                    self.USER(cmd)
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["PASS"]:
                    self.PASS(cmd)
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["PORT"]:
                    self.portFlag = True
                    self.PORT(cmd)
                    self.portFlag = False
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["PASV"]:
                    self.PASV(cmd)
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["LIST"]:
                    self.LIST(cmd)
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["STOR"]:
                    self.STOR(cmd)
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["RETR"]:
                    self.RETR(cmd)
                    continue
                elif FTP_COMMAND[cmd] == FTP_COMMAND["NOOP"]:
                    self.NOOP(cmd)
                    continue
                    
                elif FTP_COMMAND[cmd] == FTP_COMMAND["QUIT"]:
                    self.QUIT(cmd)
                    break
                elif FTP_COMMAND[cmd] == FTP_COMMAND["TYPE"]:
                    self.typeFlag = True
                    self.TYPE(cmd)
                    self.typeFlag = False
                    continue
            else:
                print "Bad command"
                self.PI_Socket.sendCommand(cmd)
                msg = self.PI_Socket.serverResponse()
                continue 
    
        #print "oopsie"
        #self.PI_Socket.Disconnect()
                

#-------------------------------------
#            Input(self)
#-------------------------------------
# out: list of strings (command, arg)
# -> Takes in the clients commandline
# -> Splits the commandLine
# -> Upper cases the command
#-------------------------------------
def Input(): 
    command = raw_input('CMD: ' )
    command = command.upper()
    return (command) 

#-----------------------------------------------
# Function getNetworkIP()
#-----------------------------------------------
# - out: str of local machines IP
# -> connects online to a server
#-----------------------------------------------
def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
    
