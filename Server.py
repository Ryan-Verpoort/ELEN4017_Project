import socket
import threading
import os
import sys
from FileRW import *
import shutil

Port = 2500
Host = '127.0.0.1'

script_dir = os.getcwd()

LoginDetails = {"user": "123"}

        
FTP_TYPE = {
    "A": "UTF-8",
    "E": "cp500",
    "I": "None"
}

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# This class has the responsibilty of handling a clients connections to the server: 
#   -> control connection
#   -> data connection
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
        print script_dir
        self.ClientSocket = ClientSocket
        self.ClientAddress = ClientAddress
        self.DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.DataAddress = ("",0)
        self.Port = Port
        self.Host = Host
        self.UserPath = os.path.abspath(os.path.join(os.path.sep,script_dir,"ClientDatabase"))
        self.UserParentDir = os.path.abspath(os.path.join(os.path.sep,script_dir,"ClientDatabase"))
        #self.fsHandler = FileSocketHandler()
        
        self.type = FTP_TYPE["A"]
        # For User Login
        self.loginFlag = False
        self.usernameFlag = False
        self.username = ""
      
        print ('Connection request from address: ' + str(self.ClientAddress))
        
    # -----------------------------------
    # This function is the main entry for the thread and it does the following:
    #   -> constantly checks for the clients commands.
    #   -> splits the command into 2 strings
    #   -> checks if the commands been implemented
    #       - if true = execute
    #       - else = wait for next client command
    # -----------------------------------
    def run(self):
        ReplyMsg = "220 Welcome to Group 3's FTP server"
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
        while 1:
            Input = self.ClientSocket.recv(4096).decode('UTF-8')
            Command,Argument = self.InputArgument(Input)
            
            if Command == 'USER':
                self.USER(Argument)
                continue
                
            if Command == 'PASS':
                self.PASS(Argument)
                continue
                
            if Command == 'STOR':
                self.Receive_File(Argument)
                continue
            
            elif Command == 'RETR':
                self.Transmit_File(Argument)
                continue
            
            elif Command == 'PORT':
                print('502 Command not implemented.')
                continue
        
            elif Command == 'NOOP':
                self.NoAction(Command)
                continue
            
            elif Command == 'LIST':
                #print str(self.UserPath)
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
                print(self.UserPath)
                continue
            
            elif Command == 'MKD':
                self.MakeDirectory(Argument)
                continue
            
            elif Command == 'RMD':
                self.RemoveDirectory(Argument)
                continue
            
            elif Command == 'CDUP':
                self.ParentDirectory()
            
            elif Command == 'DELE':
                self.DeleteFile(Argument)
                continue
                
            elif Command == 'QUIT':
                self.ClientDisconnect()
                break
                
            else:
                self.ClientSocket.send('502 Command not implemented.')
                
        self.ClientSocket.close()
        
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
    # in- username:string
    # -----------------------------------
    # This function does the following:
    #   -> checks the username against the LoginDetails
    #   -> sets a username flag
    #   -> sends appropriate response to client
    # -----------------------------------
    def USER(self, username):
        # Check if username is good
        if username in LoginDetails.keys():
            self.username = username
            self.usernameFlag = True
            ReplyMsg = "331  User name okay, need password." 
        else: 
            self.usernameFlag = False
            ReplyMsg = "332 Need account for login."
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
    
    # -----------------------------------
    # in- password:string
    # -----------------------------------
    # This function does the following:
    #   -> checks the username against the LoginDetails
    #   -> sets a username flag
    #   -> sends appropriate response to client
    # -----------------------------------
    def PASS(self, password):
        if self.loginFlag or not self.usernameFlag:
            ReplyMsg = "451 Requested action aborted: local error in processing."
        elif (password == LoginDetails[self.username]):
            self.loginFlag = True
            ReplyMsg = "230 User logged in, proceed."
            self.UserPath = os.path.abspath(os.path.join(os.path.sep,self.UserPath,self.username))
            self.UserParentDir = os.path.abspath(os.path.join(os.path.sep,self.UserParentDir,self.username))
        else:
            ReplyMsg = "530 Not logged in."
        print str(self.UserParentDir)
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
        
    def getUserPath(self):
        print self.UserPath
    # -----------------------------------
    # in - File_Name:string
    # This function does the following:
    #   -> sends a reply to the client: that the data connection is ready
    #   -> stores the file received from the client
    #   -> closes the data connection
    #   -> sends a reply to the client: that the transfer was successful
    #   -> resets the type
    # -----------------------------------
    def Receive_File(self, File_Name):
        File_Name = str(File_Name).replace("\\","")
        File_Name = str(self.UserPath)+ '/' + File_Name
        ReadFromSocket(self.DataSocket, File_Name, self.type)
       
        self.type = FTP_TYPE["A"]
        self.DataSocket.close()
        
        Reply2 = '226 Successfully transferred \"' + File_Name + '\"\r\n'
        self.ClientSocket.send(Reply2.encode('UTF-8'))

        return
    
    def Transmit_File(self, File_Name):
        File_Name = str(File_Name).replace("\\","")
        File_Name = str(self.UserPath)+ '/'+str(File_Name)
        WriteToSocket(self.DataSocket, File_Name, self.type)
        
        self.type = FTP_TYPE["A"]
        self.DataSocket.close()
        
        Reply = '226 Successfully transferred \"' + File_Name + '\"\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        
        return
        
    # NOOP command returns 200 Ok
    def NoAction(self):
        Input = '200 OK'
        self.ClientSocket.send(Input.encode('UTF-8'))
        return
    
    #Not Working With Multiple Users
    #List all files and folders in current directory
    def CurrentFileDirectory(self):
        DirectoryName = os.path.basename(self.UserPath)
        Files = 'Files in Current Directory : \"' + DirectoryName + ''
        FileDirectory = os.listdir(self.UserPath)
        
        add = "\\"
        files = ""
        for i in FileDirectory:
            if str(i)[0] == ".":
                continue
            files = files +add+ str(i) + add+'\n'
       
        print files
        self.DataSocket.send(files.encode('UTF-8'))
        self.DataSocket.close()
        Reply = '226 Successfully transferred list of current working directory\"'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        #print(UserPath)
        return
        
    #Change the data type for file transfers
    def DataType(self,Type):
        #if true let user choose type
        if Type in FTP_TYPE:
            self.type = FTP_TYPE[Type]
            Reply = '200 Type set to ' + Type
        else:
            Reply = '400 Type ' + Type + ' not supported'
        print "Data"
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
    
    # Implement Passive Mode which initilises the socket to be used
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
        Message = ( '227 Entering Passive Mode (' + self.Host +',' + str(p1) + ',' +str(p2) + ')' )
        self.ClientSocket.send(Message.encode("UTF-8"))
        self.DataSocket, self.DataAddress = FileTransferSocket.accept()
        
        Message = ( '150 Connection accepted')
        self.ClientSocket.send(Message.encode("UTF-8"))
        
        FileTransferSocket.close()
        
    
    # Changes for all users needs to be fixed
    def ChangeDirectory(self,DirectoryName):
        DirectoryName = str(DirectoryName).replace("\\","")
        if os.path.isdir(self.UserPath+"/"+str(DirectoryName)):
            self.UserPath = os.path.abspath(os.path.join(os.path.sep,self.UserPath,DirectoryName))
            Reply = '250 CWD successful. \"' + DirectoryName + '\" is current directory.'
        else :
            Reply = '550 \"' + DirectoryName + '\"does not exsist.'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.getUserPath()
        return
    
    def MakeDirectory(self,DirectoryName):
        DirectoryName = str(DirectoryName).replace("\\","")
        os.mkdir(self.UserPath+"/"+DirectoryName)
        Reply = '257 \"' + DirectoryName + '\" created successfully'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.getUserPath()
        return
    
    def RemoveDirectory(self,DirectoryName):
        DirectoryName = str(DirectoryName).replace("\\","")
        shutil.rmtree(self.UserPath+"/"+DirectoryName) # Removes folder and all its contents
        #os.rmdir(DirectoryName)
        Reply = '250 \"' + DirectoryName + '\" deleted successfully.'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.getUserPath()
        return

    def ParentDirectory(self):
        self.UserPath = self.UserParentDir
        Reply = os.path.basename(self.UserPath)
        self.ClientSocket.send(Reply.encode('UTF-8')) 
        print(self.UserPath)
        return
    
    def DeleteFile(self,File_Name):
        File_Name = str(File_Name).replace("\\","")
        os.remove(File_Name)
        Reply = '250 \"' + File_Name + '\" deleted successfully.'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
    
    def ClientDisconnect(self):
        print('Client at address: ' + str(ClientAddress) + ' Disconnected')
        Reply = '221 Service closing control connection. \n' + self.username +' Logged out'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return

ControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ControlSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ControlSocket.bind((Host, Port))

while True:
    ControlSocket.listen(3)
    ControlConnection, ClientAddress = ControlSocket.accept()
    newthread = FTP_Client(ControlConnection,ClientAddress)
    newthread.start()