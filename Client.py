import socket
import os
import sys
import select
from FileRW import *
script_dir = os.path.dirname(__file__)

        
FTP_TYPE = {
    "A": "UTF-8",
    "E": "cp500",
    "I": "None"
}

EXTENSION = {
    ".jpg": "I",
    ".png" : "I",
    ".mp4" : "I",
    ".txt" : "A",
    ".avi": "I"
}

'''

    For each class, include a brief description, author and date of last modification
    For each method, include a description of its purpose, functions, parameters and results
'''
# Return the appropriate encoding type for the extension on File_Name 
def getType(File_Name):
    # ---------------------
    File_Name = str(File_Name).replace("\\","")
    end=len(File_Name)
    extensionIndex = File_Name.find(".")
    extension = File_Name [extensionIndex:end]
    if extension in EXTENSION:
        string = EXTENSION[extension]
        print string
        return string
    print "Only Processing .jpeg .png .mp4 .txt .avi" 
    
    #ftp.drivehq.om
    #username = abctest321
    #password = 321abc
    
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# class Client
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# This class has the responsibilty of handling the client's and the server's inputs.
# In essence it acts as an interface between the two.
#
# It is also responsible for establishing a control and data connection.
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
class Client(object):
    def __init__(self):
        # information needed for the gui
        self.ControlConnectionFlag = False
        self.DataConnectionFlag = False
        self.LoginFlag = False
        self.username = ""
        self.server_reply = ""
        self.command = ""
        # FTP information
        self.Port = 2500#21#2500
        self.Host = '127.0.0.1'#'ftp.drivehq.com'#'127.0.0.1'  #'66.220.9.50'#'ftp.dlptest.com' #'ftp.mirror.ac.za'
        self.type = FTP_TYPE["A"]
        self.ControlSocket = socket.socket()
        self.DataSocket = socket.socket()
        self.DataAddress = ("",0)
        # Client directory paths for upload/download
        self.UserPath = os.path.abspath(os.path.join(os.path.sep,script_dir,"Local_Client_Files"))
        self.DataHost =""
        self.DataPort = 0
        print str(self.UserPath)

    def __del__(self):
        self.Disconnect()
        self.ControlSocket.close()
    
    # -----------------------------------
    # function FTPCommand
    # -----------------------------------
    # in- Command, Argument
    # -----------------------------------
    # This function does the following: 
    #   -> combines the two input strings
    #   -> sends it to the server
    #   -> waits for server reply
    # -----------------------------------
    def FTPCommand(self,Command,Argument=""):
        if Argument == '':
            self.command=str(Command) + '\r\n'
        else:
            self.command = str(Command) + ' ' + str(Argument) + '\r\n'
        self.sendCommand()
        self.getServerReply()
    
    # checks connection and sees if there is data before getting server reply 
    def getServerReply(self):
        try:
            self.server_reply = self.ControlSocket.recv(8192).decode('UTF-8')
            print "C<-----------S "+self.server_reply
        except:
            print "Server did not reply"
            
    # checks connection before sending command
    def sendCommand(self):
        try:
            self.ControlSocket.send(self.command.encode('UTF-8'))
            print "C----------->S "+ self.command
        except:
            print "Not connected to server. Please Disconnect"
    # -----------------------------------
    # function USER
    # -----------------------------------
    # in- user
    # -----------------------------------
    # This function does the following: 
    #   -> sends FTP Command == USER (user) to server
    #   -> if username is not authorized then QUIT
    # -----------------------------------
    def USER (self, user, command="USER", ):
        self.FTPCommand(command, user)
        if self.server_reply[0:1] == "5" :
            self.Disconnect()
            sys.exit()
  
    # sends FTP Command == PASS (password) to server
    def PASS (self,  password, command="PASS"):
        self.FTPCommand(command, password)
     
    # -----------------------------------
    # function Authenticate
    # -----------------------------------
    # This function does the following: 
    #   -> waits for server response and sets Login Flag
    # -----------------------------------
    def Authenticate(self):
        if self.server_reply[0] == "2":
            print "authentication success"
            self.LoginFlag = True
        else:
            self.LoginFlag = False
            
  
    # sends FTP Command == RETR (File_Name) to server
    def Receive_File(self, File_Name):
        File_Name = str(File_Name).replace("\\","")
        self.FTPCommand('RETR', File_Name)
        
        if not self.server_reply[0] == '5':
            File_Name = str(self.UserPath)+ '/' + File_Name
            ReadFromSocket(self.DataSocket, File_Name, self.type)
            
        self.CloseDataConnection()
        
    # sends FTP Command == STOR (File_Name) to server
    def Transmit_File(self, File_Name):
        self.FTPCommand('STOR',File_Name)
    
        if not self.server_reply[0] == '5':
            File_Name = str(self.UserPath)+ '/' + str(File_Name)
            WriteToSocket(self.DataSocket, File_Name, self.type)
            
        self.DataSocket.shutdown(socket.SHUT_WR)
        self.CloseDataConnection()
    
    # sends FTP Command == NOOP to server
    def NoAction(self):
        ServerReply = FTPCommand('NOOP','')

    # -----------------------------------
    # function File Directory
    # -----------------------------------
    # out- list of files in servers current directory
    # -----------------------------------
    # This function does the following: 
    #   -> sends FTP Command == LIST to server
    # -----------------------------------
    def FileDirectory(self):
        
        self.FTPCommand('LIST') 
        
        if self.server_reply[0] == "1" or self.server_reply[0] == "2":
            DataReply = self.DataSocket.recv(4096).decode('UTF-8')
            DataReply = DataReply
            DataReply = DataReply.split('\n')
            
        self.CloseDataConnection()
        return DataReply
    
    # -----------------------------------
    # function passiveMode
    # -----------------------------------
    # This function does the following: 
    #   -> send FTP Command == PASV to server
    #   -> receives a host name and port
    #   -> connects to data connection
    # -----------------------------------
    def passiveMode(self):
        self.FTPCommand('PASV')
        Reply = self.server_reply 
        Reply = Reply.replace(".",",")
        start = Reply.find('(')
        end   = Reply.find(')')
        Reply = Reply[start+1:end]
        Reply = Reply.split(',')

        self.DataHost = str(Reply[0]) + '.'+ str(Reply[1]) +'.'+ str(Reply[2]) +'.'+ str(Reply[3])
        self.DataPort = (int(Reply[4])*256) + int(Reply[5])
        self.DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.DataSocket.connect((self.DataHost,self.DataPort))
    
    # This function receives the server reply
    # which says that the data connection is closed
    def CloseDataConnection(self):
        self.getServerReply()
        self.DataConnectionFlag = False
        self.DataSocket.close()
        self.type = FTP_TYPE["A"]
    
    # -----------------------------------
    # function Help
    # -----------------------------------
    # FTP COMMAND == HELP
    # This function does the following:
    #   -> asks the server for a list of implemented commands
    # -----------------------------------
    def GetHelp(self):
        self.FTPCommand('HELP')
        
    # send FTP COMMAND == CWD (DirectoryName)to server
    def ChangeDirectory(self,DirectoryName ):
        self.FTPCommand('CWD', DirectoryName)
        self.getServerReply()
    
     # send FTP COMMAND == MKD (DirectoryName) to server
    def MakeDirectory(self, DirectoryName ):
        self.FTPCommand('MKD',DirectoryName)
    
    # send FTP COMMAND == RMD (DirectoryName)to server
    def RemoveDirectory(self, DirectoryName ):
        self.FTPCommand('RMD', DirectoryName)
        
    # send FTP COMMAND == CDUP to server
    def ParentDirectory(self):
        self.FTPCommand('CDUP','')
    
    # send FTP COMMAND == DELE (File_Name) to server
    def DeleteFile(self, File_Name):
        self.FTPCommand('DELE', File_Name)

    # send FTP COMMAND == TYPE (Type) to server
    def DataType(self, Type):
        if Type in FTP_TYPE:
            self.type = FTP_TYPE[Type]
            
        else:
            self.type = FTP_TYPE["A"]
            print "type argument not implemented-- Setting to default type"
        self.FTPCommand("TYPE",Type)
        
    # send FTP COMMAND == QUIT to server
    def Disconnect(self):
        self.ControlConnectionFlag = False
        self.FTPCommand('QUIT')
    
    # establish control connection with the server
    def Connect(self):
        self.ControlSocket = socket.socket()
        self.ControlSocket.connect((self.Host,self.Port))
        self.ControlSocket.settimeout(10.0)
        self.getServerReply()
        self.ControlConnectionFlag = True
