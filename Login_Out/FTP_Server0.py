import socket
import sys
import string

#from enum import Enum
#from parse import *
    
#class FTP_MODE(Enum):
FTP_MODE = {
    "Stream":"S"
}

FTP_TYPE = {
    "ASCII": "A",
    "NON-PRINT": "N"
}

FTP_MODE = { "STREAM": "S" }

FTP_STRU = { "FILE": "F" }

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
    "NOOP": 12 
}
       
FTP_SM = {
"USER1":"331", # User name okay, need password.
"USER2":"332", # Need account for login.
"PASS1":"230", # User logged in, proceed.
"PASS2":"530", # Not logged in.
"QUIT":"221",  # Service closing control connection.
"OKAY":"200",  # Command okay.
"FAIL":"500",  # Syntax error, command unrecognized.
"DNE" :"502"   # Command not implemented.
}

user="Tiny"
passwords="Paws"

DTP_Port    = 12345
MAX_FTP_CMD_STRING_LEN   =31

class FTP_Server_Interface(object):
    def __init__(self, connection, ClientAddr):
        self.connection         = connection
        self.ClientAddr         = ClientAddr
        self.DestinationAddr    = ClientAddr
        self.usernameFlag       = False
        self.loginFlag          = False
        self.quitFlag           = False
        self.transferFlag       = False
        self.connectionFlag     = False
        
        self.type = FTP_TYPE["ASCII"]
        self.mode = FTP_MODE["STREAM"]
        self.stru = FTP_STRU["FILE"]
    
        self.ServerMsg = ""
        self.path = "" 
           
    def USER(self, username):
        if (username == user):
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
        address = address.split(",")
        Host = address[0]+ address[1]+ address[2]+ address[3]
        host = socket.inet_ntoa(Host)
        port = ord(address[4])*256 + ord(address[5])
        Addr = (host, port)
        self.DestinationAddr = Addr
        return FTP_SM["OKAY"]
    
    def STOR(self):
        return FTP_SM["OKAY"]
        
    def RETR(self):
        return FTP_SM["OKAY"]
        
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
            self.ServerReply()
            msg = self.connection.recv(8192)
            #print msg
            cmd, argu = ParseFTPStringCommand(msg)
            if FTP_COMMAND[cmd] == FTP_COMMAND["USER"]:
                self.ServerMsg = self.USER(argu)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["PASS"]:
                self.ServerMsg = self.PASS(argu)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["PORT"]:
                self.ServerMsg = self.PORT(argu)
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
                print "command not implemented"
                self.ServerMsg = FTP_SM["DNE"]
                continue
                
        self.ServerReply()
        self.connection.close()
        
        
    def ServerReply(self):
        if not self.ServerMsg =="":
            self.connection.sendall(self.ServerMsg)
            print self.ServerMsg
        self.ServerMsg = ""
        
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
    print command + arg
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


    
    
    