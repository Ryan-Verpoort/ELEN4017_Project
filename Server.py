import socket
import threading
import os
import sys
import shutil

from FileRW import *

Port = 2500
Host = '192.168.0.101'
#127.0.0.1'

#script_dir = os.path.dirname(__file__) #for some reason, the server doesn't like this :/
script_dir = os.getcwd()
LoginDetails = {"user": "123", "userKay":"123"}

        
FTP_TYPE = {
    "A": "UTF-8",
    "E": "cp500",
    "I": "None"
}

FTP_HELP_RESPONSE = { 
    "USER\n",
    "PASS\n",
    "PASV\n",
    "STOR\n",
    "RETR\n",
    "LIST\n",
    "TYPE\n",
    "CWD\n",
    "MKD\n",
    "RMD\n",
    "CDUP\n",
    "DELE\n",
    "QUIT\n"
}


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# class FTP_Client
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# This class has the responsibilty of handling a clients connections to the server: 
#   -> control connection (receives commands and sends server replies)
#   -> data connection (sends and receives data)
#
# Multiple FTP_Client threads can be run in parallel, which is created by the main server socket.
#
# On a side note:
#       We have made our FTP server run in a purely passive mode.
#       This means that the client always connects to the server.
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

class FTP_Client(threading.Thread):
    
    def __init__(self,ClientSocket,ClientAddress):
        threading.Thread.__init__(self)
        self.ClientSocket = ClientSocket
        self.ClientAddress = ClientAddress
        self.DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.DataAddress = ("",0)
        self.Port = Port
        self.Host = Host
        self.UserPath = os.path.abspath(os.path.join(os.path.sep,script_dir,"ClientDatabase"))
        self.UserParentDir = os.path.abspath(os.path.join(os.path.sep,script_dir,"ClientDatabase"))
        self.type = FTP_TYPE["A"]
        # For User Login
        self.loginFlag = False
        self.usernameFlag = False
        self.username = ""
        self.quitFlag = False
        #print self.UserPath
        print ('Connection request from address: ' + str(self.ClientAddress))
        
    # -----------------------------------
    # function run
    # -----------------------------------
    # This function is the main entry for the thread and it does the following:
    #   -> constantly checks for the clients commands.
    #   -> splits the command into 2 strings
    #   -> checks if the commands been implemented
    #       - if true = execute
    #       - else = wait for next client command
    # -----------------------------------
    def run(self):
        ReplyMsg = "220 Welcome to Group 3's FTP server.\r\n"
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
        while not self.quitFlag:
            Input = self.ClientSocket.recv(4096).decode('UTF-8')
            Command,Argument = self.InputArgument(Input)
            
            if Command == 'USER':
                self.USER(Argument)
                continue
                
            if Command == 'PASS':
                self.PASS(Argument)
                continue
                
            if self.loginFlag: 
                if Command == 'STOR':
                    self.Receive_File(Argument)
                    continue
            
                elif Command == 'RETR':
                    self.Transmit_File(Argument)
                    continue
        
                elif Command == 'NOOP':
                    self.NoAction()
                    continue
            
                elif Command == 'LIST':
                    self.CurrentFileDirectory()
                    continue
            
                elif Command == 'TYPE':
                    self.DataType(Argument)
                    continue
                
                elif Command == 'PASV':
                    self.PassiveMode()
                    continue
                
                elif Command == 'CWD':
                    self.ChangeDirectory(Argument)
                    continue
            
                elif Command == 'MKD':
                    self.MakeDirectory(Argument)
                    continue
            
                elif Command == 'RMD':
                    self.RemoveDirectory(Argument)
                    continue
            
                elif Command == 'CDUP':
                    self.ParentDirectory()
                    continue
            
                elif Command == 'PWD':
                    self.PrintWorkingDirectory()
                    continue

                elif Command == 'DELE':
                    self.DeleteFile(Argument)
                    continue
                
                elif Command == 'QUIT':
                    self.ClientDisconnect()
                    continue
                
                elif Command == 'HELP':
                    self.HELP()
                    continue
                
                else:
                    self.ClientSocket.send('502 Command not implemented.\r\n')
            else:
                Reply = "530 Please login with USER and PASS.\r\n"
                self.ClientSocket.send(Reply.encode('UTF-8'))
        self.ClientSocket.close()
    # -----------------------------------
    # function InputArgument
    # -----------------------------------
    # in- Input which is a string
    # out- Command, Argument which are both strings
    # -----------------------------------
    # This function does the following: 
    #   -> splits up the command line
    # -----------------------------------
    def InputArgument(self,Input):
        
        SpacePosition = Input.find(' ')
        if(SpacePosition != -1):
            Command = Input[0:SpacePosition]
            End = Input.find('\r\n')
            Argument = Input[SpacePosition+1:End]
        else:
            End = Input.find('\r\n')
            Command = Input[0:End]
            Argument = ''
        return Command,Argument
    
    # -----------------------------------
    # function USER
    # -----------------------------------
    # in- username:string
    # -----------------------------------
    # This function does the following:
    #   -> checks the username against the LoginDetails
    #   -> sets a username flag
    # -----------------------------------
    def USER(self, username):
        # Check if username is good
        if username in LoginDetails.keys():
            self.username = username
            self.usernameFlag = True
            ReplyMsg = "331  User name okay, need password.\r\n" 
        else: 
            self.usernameFlag = False
            self.quitFlag = True
            ReplyMsg = "530 Need an account. No anonymous users allowed. \r\n"
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
    
    # -----------------------------------
    # function PASS
    # -----------------------------------
    # in- password:string
    # -----------------------------------
    # This function does the following:
    #   -> checks the username against the LoginDetails
    #   -> sets a username flag 
    # -----------------------------------
    def PASS(self, password):
        if self.loginFlag or not self.usernameFlag:
            ReplyMsg = "530 Not logged in.\r\n"
        elif (password == LoginDetails[self.username]):
            self.loginFlag = True
            ReplyMsg = "230 User logged in, proceed.\r\n"
            self.UserPath = os.path.abspath(os.path.join(os.path.sep,self.UserPath,self.username))
            self.UserParentDir = os.path.abspath(os.path.join(os.path.sep,self.UserParentDir,self.username))
        else:
            ReplyMsg = "530 Not logged in.\r\n"
        print str(self.UserParentDir)
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
    
    def getUserPath(self):
        print self.UserPath # user to print the path
        
    
    # -----------------------------------
    # function Receive_File
    # -----------------------------------
    # in - File_Name:string
    # -----------------------------------
    # FTP COMMAND == STOR 
    # This function does the following:
    #   -> stores the file received from the client in the path specified for the user
    #   -> resets the type
    # -----------------------------------
    def Receive_File(self, File_Name):
        File_Name = str(File_Name).replace("\\","")
        path = os.path.abspath(os.path.join(os.path.sep,self.UserPath,File_Name))
        File_Name = str(path)
        ReadFromSocket(self.DataSocket, File_Name, self.type)
       
        self.type = FTP_TYPE["A"]
        self.DataSocket.close()
        
        Reply2 = '226 Successfully transferred \"' + File_Name + '\"\r\n'
        self.ClientSocket.send(Reply2.encode('UTF-8'))

        return
    
    # -----------------------------------
    # function Transmit_File
    # -----------------------------------
    # FTP COMMAND == RETR
    # in - File_Name:string
    # This function does the following:
    #   -> sends the requested file to the client
    #   -> resets the type
    # -----------------------------------
    def Transmit_File(self, File_Name):
        File_Name = str(File_Name).replace("\\","")
        path = os.path.abspath(os.path.join(os.path.sep,self.UserPath,File_Name))
        File_Name = str(path)
        WriteToSocket(self.DataSocket, File_Name, self.type)
        
        self.type = FTP_TYPE["A"]
        self.DataSocket.close()
        
        Reply = '226 Successfully transferred \"' + File_Name + '\"\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        
        return
    # -----------------------------------
    # FTP COMMAND == NOOP 
    # -----------------------------------
    # This function does nothing! 
    # -----------------------------------
    def NoAction(self):
        Input = '200 OK\r\n'
        self.ClientSocket.send(Input.encode('UTF-8'))
        return
    
    # -----------------------------------
    # function CurrentFileDirectory
    # -----------------------------------
    # FTP COMMAND == LIST
    # This function does the following:
    #   -> list all files and folders in current directory.
    #   -> sends the list to the client through the data connection.
    # -----------------------------------
    def CurrentFileDirectory(self):
        DirectoryName = os.path.basename(self.UserPath)
        Files = 'Files in Current Directory : \"' + DirectoryName
        FileDirectory = os.listdir(self.UserPath)
        
        #add = "\\"
        files = ""
        for i in FileDirectory:
            if str(i)[0] == ".":
                continue
            files = files + str(i)+'\n'
       
        #print files
        self.DataSocket.send(files.encode('UTF-8'))
        self.DataSocket.close()
        Reply = '226 Successfully transferred list of current working directory.\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        #print(UserPath)
        return

    # -----------------------------------
    # function DataType
    # -----------------------------------
    # in - Type:string (A,E,I)
    # -----------------------------------
    # FTP COMMAND == TYPE
    # This function does the following:
    #   -> sets the type for the next data transmission
    # -----------------------------------
    def DataType(self,Typez):
        #if true let user choose type
        if str(Typez) in FTP_TYPE:
            self.type = FTP_TYPE[Typez]
            Reply = '200 Type set to ' + Typez +'\r\n'
        else:
            Reply = '400 Type ' + Typez + ' not supported\r\n'
        #print "Data"
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
    
    # -----------------------------------
    # function PassiveMode
    # -----------------------------------
    # FTP COMMAND == PASV
    # This function does the following:
    #   -> Initilises the data connection socket to be used
    #   -> Sends socket information to client
    # -----------------------------------
    def PassiveMode(self):
        FileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        FileTransferSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        FileTransferSocket.bind(('0.0.0.0', 0))
        FileTransferSocket.listen(1)
        DataPort = FileTransferSocket.getsockname()[1]
        
        #DataPort is a value of 256 get remainder    
        p2 = DataPort % 256
        #Subtract remainder to ensure its a multiple of 256
        p1 = (DataPort -p2)/256
        
        self.Host = self.Host.replace('.',',')
        Message = ( '227 Entering Passive Mode (' + self.Host +',' + str(p1) + ',' +str(p2) + ')' +'\r\n' )
        self.ClientSocket.send(Message.encode("UTF-8"))
        self.DataSocket, self.DataAddress = FileTransferSocket.accept()
        
        Message = ( '150 Connection accepted\r\n')
        self.ClientSocket.send(Message.encode("UTF-8"))
        
        FileTransferSocket.close()
        
    # FTP COMMAND == CWD
    def ChangeDirectory(self,DirectoryName):
        DirectoryName = str(DirectoryName).replace("\\","")
        DirectoryName = str(DirectoryName).replace("/","")
        path = os.path.abspath(os.path.join(os.path.sep,self.UserPath,DirectoryName))
        #print path
        if os.path.isdir(path):
            self.UserPath = path
            Reply = '250 CWD successful. \"' + DirectoryName + '\" is current directory.\r\n'
        else :
            Reply = '550 \"' + DirectoryName + '\"does not exsist.\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.getUserPath()
        return
    
    # FTP COMMAND == MKD
    def MakeDirectory(self,DirectoryName):
        DirectoryName = str(DirectoryName).replace("\\","")
        DirectoryName = str(DirectoryName).replace("/","")
        path = os.path.abspath(os.path.join(os.path.sep,self.UserPath,DirectoryName))
        os.mkdir(path)
        Reply = '257 \"' + DirectoryName + '\" created successfully\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.getUserPath()
        return
    
    # FTP COMMAND == RMD
    def RemoveDirectory(self,DirectoryName):
        DirectoryName = str(DirectoryName).replace("\\","")
        DirectoryName = str(DirectoryName).replace("/","")
        path = os.path.abspath(os.path.join(os.path.sep,self.UserPath,DirectoryName))
        shutil.rmtree(path) # Removes folder and all its contents
        #os.rmdir(DirectoryName)
        Reply = '250 \"' + DirectoryName + '\" deleted successfully.\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.getUserPath()
        return
    
    # FTP COMMAND == CDUP
    # Changes the users cwd to the parent directory
    def ParentDirectory(self):
        self.UserPath = self.UserParentDir
        Reply = "250 "+os.path.basename(self.UserPath)+ " is your current working directory\r\n "
        self.ClientSocket.send(Reply.encode('UTF-8')) 
        #print(self.UserPath)
        return

    #FTP COMMAND == PWD
    #Prints current working directory
    def PrintWorkingDirectory(self):
        Path = os.path.basename(self.UserPath)
        Reply = '257 '+ Path +'\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
        
    # FTP COMMAND == DELE
    def DeleteFile(self,File_Name):
        File_Name = str(File_Name).replace("\\","")
        File_Name = str(File_Name).replace("/","")
        path = os.path.abspath(os.path.join(os.path.sep,self.UserPath,File_Name))
        os.remove(path)
        Reply = '250 \"' + File_Name + '\" deleted successfully.\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
    
    # FTP COMMAND == QUIT
    def ClientDisconnect(self):
        print('Client at address: ' + str(ClientAddress) + ' Disconnected')
        Reply = '221 Service closing control connection. \n' + self.username +' Logged out\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.quitFlag = True
        return
        
    # -----------------------------------
    # function Help
    # -----------------------------------
    # FTP COMMAND == HELP
    # This function does the following:
    #   -> sends the user the implemented server commands
    # -----------------------------------
    def HELP(self):
        Reply = "214 The following commands are recognised:\r\n"
        for helps in FTP_HELP_RESPONSE:
            Reply = Reply +  helps
        Reply = Reply + "214 HELP command successful.\r\n"
        self.ClientSocket.send(Reply.encode('UTF-8'))
    
            
# The main server control socket listens for new connections and creates threads
ControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ControlSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ControlSocket.bind((Host, Port))

while True:
    ControlSocket.listen(3)
    ControlConnection, ClientAddress = ControlSocket.accept()
    newthread = FTP_Client(ControlConnection,ClientAddress)
    newthread.start()