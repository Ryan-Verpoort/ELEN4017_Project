import socket
import sys
import string

#from enum import Enum
#from parse import *
    
#class FTP_MODE(Enum):
FTP_MODE = {
    "Stream":"S"
}

# FTP_TYPE{}
    
# FTP_STU{}    

# FTP_MODE{}

DTP_Port    = 12345
MAX_FTP_CMD_STRING_LEN   =31
       
FTP_SM = {
"USER1":"331", # User name okay, need password.
"USER2":"332", # Need account for login.
"PASS1":"230", # User logged in, proceed.
"PASS2":"530", # Not logged in.
"QUIT":"221",  # Service closing control connection.
}

user="Tiny"
passwords="Paws"

FTP_COMMAND = {  
"USER": 1,            
"PASS": 2,
"QUIT": 3,        
}

#class FTP_COMMAND(Enum):
#    USER = auto() 
#    PASS = auto()
    
class FTP_Server_Interface(object):
    def __init__(self, connection, ClientAddr):
        self.connection         = connection
        self.ClientAddr         = ClientAddr
        self.DTP_Socket         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerAddressDTP   = ('localhost', DTP_Port)
        
        self.usernameFlag       = False
        self.loginFlag          = False
        self.quitFlag           = False
        self.dataInFlag         = False
        self.dataOutFlag        = False
        self.mode = 0
        self.stru = 0
        self.type = 0
        self.port = DTP_Port
    
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
           
            
    def QUIT(self):
        print 'quitting'
    	self.usernameFlag   = False
    	self.loginFlag      = False
        self.quitFlag       = True
        return FTP_SM["QUIT"]
    # Thread is gna be needed for sending/receiving data
    
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
            msg = self.connection.recv(8192).decode('UTF-8')
            #print msg
            cmd, argu = ParseFTPStringCommand(msg)
            if FTP_COMMAND[cmd] == FTP_COMMAND["USER"]:
                self.ServerMsg = self.USER(argu)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["PASS"]:
                self.ServerMsg = self.PASS(argu)
                continue
            elif FTP_COMMAND[cmd] == FTP_COMMAND["QUIT"]:
                self.ServerMsg = self.QUIT()
                break
            else:
                print "command not implemented"
                continue
        self.ServerReply()
        self.connection.close()
        self.DTP_Socket.close()
        
                 
    def ServerReply(self):
        if not self.ServerMsg =="":
            self.connection.sendall(self.ServerMsg.encode('UTF-8'))
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


    
    
    