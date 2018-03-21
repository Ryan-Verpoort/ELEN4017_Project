import socket
import sys
import string
import random

from TCPServer3 import *

EXTENSION = {
    ".jpeg": "I",
    ".png" : "I",
    ".mp4" : "I",
    ".txt" : "A"
}

FTP_TYPE = {
    "A": "UTF-8",
    "I": "None"
}
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
"USER1":"331 User name okay, need password." ,
"USER2":"332 Need account for login." ,
"PASS1":"230 User logged in, proceed.",
"PASS2":"530 Not logged in.",
"QUIT" :"221 Service closing control connection",
"OKAY" :"200 Command okay.",
"FAIL" :"500 Syntax error, command unrecognized.",
"DNE"  :"502 Command not implemented.",
"DATA" :"225 Data connection open; no transfer in progress.",
"DATAQ":"226 Closing data connection. Success or abort.",
"BPARA":"504 Command not implemented for that parameter.",
"BFILE":"550 Requested file action not taken.",
"BCON" :"425 Can't open data connection.",
"BTYPE":"451 Requested action aborted: local error in processing.",
"PASV1" :"227 Entering Passive Mode"
}


user="Tiny"
passwords="Paws"

Source_DTP_Port    = 12330
MAX_FTP_CMD_STRING_LEN   =31

def getEncoding(File_Name):
    end=len(File_Name)
    extensionIndex = File_Name.find(".")
    extension = File_Name [extensionIndex:end]
    if extension in EXTENSION:
        return FTP_TYPE[EXTENSION[extension]]
    print "Only Processing .jpeg .png .mp4 .txt"
    return ""
    
class FTP_Server_Interface(object):
    def __init__(self, connection, ClientAddr):
        self.PI_Socket= Socket(connection, 0)
        self.PI_Socket.setDestAddress(ClientAddr)
        self.DestAddr = ClientAddr #Default
        #self.connection         = connection #PI
        #self.DestAddr           = ClientAddr #PI
        
        self.usernameFlag       = False
        self.loginFlag          = False
        self.quitFlag           = False
        self.transferFlag       = False
        self.portFlag           = False
        self.connectionFlag     = False
        
        self.type = FTP_TYPE["A"]
        self.mode = FTP_MODE["S"]
        self.stru = FTP_STRU["F"]
    
        self.ServerMsg = ""
        self.username = ""

    def TYPE(self,Type):
        #if true let user choose type
        if Type in FTP_TYPE:
            self.type = FTP_TYPE[Type]
            return FTP_SM["OKAY"]
        else:
            return FTP_SM["BPARA"]
            #504 Command not implemented for that parameter.

    def USER(self, username):
        if (username == user):
            self.username = username
            self.usernameFlag = True
            return FTP_SM["USER1"]
        else: 
            self.usernameFlag = False
            return FTP_SM["USER2"] 
                
    def PASS(self, password):
        if (password == passwords and self.usernameFlag):
            self.usernameFlag   = True
            self.loginFlag      = True
            return FTP_SM["PASS1"]
        else:
            return FTP_SM["PASS2"]
    #-----------------------------------------------
    # Port(self,address)
    #-----------------------------------------------
    # in = address "h1, h2, h3, h4, p1, p2"
    # This function does the following:
    # -> Gets the local IP of the client
    # -> Converts it into a . format
    # -> Converts the port number
    # -> Changes the socket address
    #-----------------------------------------------
    def PORT(self, address):
        self.portFlag = False
        address = address.split(",")
        Host = address[0]+ address[1]+ address[2]+ address[3]
        host = socket.inet_ntoa(Host)
        port = ord(address[4])*256 + ord(address[5])
        Addr = (host, port)
        self.DestAddr = Addr
        self.portFlag = True
        self.transferFlag = True
        return FTP_SM["OKAY"]
    
    #Implement Passive Mode which initilises the socket to be used
    def PASV(self):
        Source_DTP_Port = random.randint(10000,20000)
        ipstring = getNetworkIp()
        Host = socket.inet_aton(ipstring)
        p2 = int(Source_DTP_Port)%256
        p1 = int(Source_DTP_Port)/256
        #p2 = int(Source_DTP_Port-p1)%256
        print "Actual: "+str (Source_DTP_Port)+" Sent: " +str(p1*256 +p2)
        print p1
        print p2
        p1 = chr(p1)
        p2 = chr(p2)
        NewAddress = Host[0] + ',' +Host[1] +','+ Host[2] +','+ Host[3] + ',' + p1+ ',' +p2
        
        msg= FTP_SM["PASV1"]+ " ("+NewAddress+")"
        print msg 
        return msg
        
    def STOR(self, fileName):
        # 1. Check if ext and type match
        enc = getEncoding(fileName)
        if not enc==self.type:
            return FTP_SM["BTYPE"]
        
        # 2. Set up connect and store received data
        Data_Socket = Socket('', DTP_Port)
        Data_Socket.setDestAddress(self.DestAddr)
        print "We r storing!"
        
        if  self.transferFlag and not self.connectionFlag and self.portFlag:
            Data_Socket.Connect()
            self.connectionFlag = True
            self.PI_Socket.sendReply(FTP_SM["DATA"])
            Data_Socket.receiveData(fileName, self.username, self.type)
        else:
            Data_Socket.Disconnect()
            return FTP_SM["BCON"]
        # 3. Disconnect son
        Data_Socket.Disconnect()
        self.transferFlag = False
        self.connectionFlag = False
        self.type = FTP_TYPE["A"]
        return FTP_SM["DATAQ"]
            
    def RETR(self, fileName):
        # 1. Check if file exists
     
        UploadDir = DirectoryData("/ClientDatabase/"+self.username+"/")
        if not UploadDir.FileExists(fileName):
            self.transferFlag = False
            return FTO_SM["BFile"]
        
        # 2. Check if ext and type match
        enc = getEncoding(fileName)
        if not enc==self.type:
            return FTP_SM["BTYPE"]
        # 3. Connecting to Client
        Data_Socket = Socket('', Source_DTP_Port)
        Data_Socket.setDestAddress(self.DestAddr)
        
        if  self.transferFlag and not self.connectionFlag and self.portFlag:
            Data_Socket.Connect()
            self.connectionFlag = True
            self.PI_Socket.sendReply(FTP_SM["DATA"])
            Data_Socket.sendData(fileName, self.username, self.type)
        else:
            Data_Socket.Disconnect()
            return FTP_SM["BCON"]
        # 3. Close Connection   
        Data_Socket.Disconnect()
        self.transferFlag = False
        self.connectionFlag = False
        self.type = FTP_TYPE["A"]
        return FTP_SM["DATAQ"]
        
    def LIST(self, pathName="null"):
        #self.PASV()
        DataSocket = Socket(getNetworkIp() , Source_DTP_Port)
        print "listening..."
        DataSocket.socket.listen(1)
        self.PI_Socket.sendReply(FTP_SM["DATA"])
        DataSocket.Accept()
        print "accepted"
        #self.PI_Socket.sendReply(FTP_SM["DATA"])
        if pathName == "null":
            FileDirectory = DirectoryData("/ClientDatabase/"+self.username+"/")
        else: 
            FileDirectory= DirectoryData("/ClientDatabase/"+self.username+"/"+pathName)
        fd = FileDirectory.List()
        
        Files=""
        for i in fd:
            Files = Files + str(i) + '\n'
        DataSocket.connection.sendall(Files).encode("UTF-8")
        DataSocket.connection.close()
        DataSocket.close()
        print "closing"
        return FTP_SM["DATAQ"]
        
    def QUIT(self):
        print 'quitting'
    	self.usernameFlag   = False
    	self.loginFlag      = False
        self.quitFlag       = True
        return FTP_SM["QUIT"]
        
    # Thread is gna be needed for sending/receiving data
    def NOOP(self):
        return FTP_SM["OKAY"]
    #-----------------------------------------------
    # Function CommandProcessor(connection, server):
    #-----------------------------------------------
    # - in: IP socket connection and FTP_Server_Interface
    # This function does the following:
    # -> receives command from client
    # -> parses the received string
    # -> executes the command using the FTP_Server_Interface 
    # -> sets server message
    #-----------------------------------------------        
    def CommandProcessor(self):
        
        while not self.quitFlag:
            if True:
                self.PI_Socket.sendReply(self.ServerMsg)
                msg = self.PI_Socket.receiveCommand()
                cmd, argu = ParseFTPStringCommand(msg)
                if cmd in FTP_COMMAND:
                    if FTP_COMMAND[cmd] == FTP_COMMAND["USER"]:
                        self.ServerMsg = self.USER(argu)
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["PASS"]:
                        self.ServerMsg = self.PASS(argu)
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["PORT"]:
                        self.ServerMsg = self.PORT(argu)
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["PASV"]:
                        self.ServerMsg = self.PASV()
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["TYPE"]:
                        self.ServerMsg = self.TYPE(argu)
                        continue
                        
                    if FTP_COMMAND[cmd] == FTP_COMMAND["LIST"]:
                        self.ServerMsg = self.LIST(argu)
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["STOR"]:
                        self.ServerMsg = self.STOR(argu)
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["RETR"]:
                        self.ServerMsg = self.RETR(argu)
                        continue
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["QUIT"]:
                        self.ServerMsg = self.QUIT()
                        break
                        
                    elif FTP_COMMAND[cmd] == FTP_COMMAND["NOOP"]:
                        self.ServerMsg = self.NOOP()
                        continue
                        
                else:  
                    self.ServerMsg = FTP_SM["DNE"]
                    continue
                
        print "moo1"
        self.PI_Socket.sendReply(self.ServerMsg)
        self.PI_Socket.Disconnect()
        
#-----------------------------------------------
# Function ParseFTPStringCommand(FTP_CMD_str)
#-----------------------------------------------
# - in: command string from client
# - out: string command and string argument
# This function does the following:
# -> parses the input string to split the command and arguments
#-----------------------------------------------
def ParseFTPStringCommand(FTP_CMD_str):
    string = FTP_CMD_str[0:MAX_FTP_CMD_STRING_LEN]
    string = remove_all('\r\n', string)
    if (len(string) > 4):
        command, arg = string.split(" ")
    else:
        command = string
        arg = ''
    #print command + arg
    return (command, arg)

#-----------------------------------------------
# Function remove_all(substr, str)
#-----------------------------------------------
# - in: two strings --> substr, str  
# - out: str
# This function does the following:
# -> removes the substring from the main string
#-----------------------------------------------
def remove_all(substr, str):
    index = 0
    length = len(substr)
    while string.find(str, substr) != -1:
        index = string.find(str, substr)
        str = str[0:index] + str[index+length:]
    return str

#-----------------------------------------------
# Function getNetworkIP()
#-----------------------------------------------
# - out: str of local machines IP
#-----------------------------------------------
def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
    
    
    
    