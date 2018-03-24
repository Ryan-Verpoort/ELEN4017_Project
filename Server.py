import socket
import threading
import os
import sys

Port = 2500
Host = '127.0.0.1'

script_dir = os.getcwd()

#TypeList to determine what typeof data encoding to be used
LoginDetails = {"user": "123"}

class FTP_Threading(threading.Thread):
    
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
        
        self.TypeList = [True,False,False]
        # For User Login
        self.loginFlag = False
        self.usernameFlag = False
        self.username = ""
      
        print ('Connection request from address: ' + str(self.ClientAddress))
        
    
    def run(self):
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
        
    #Formatting of Input arguments for server to decide what must be done
    def InputArgument(self,Input):
        SpacePosition = Input.find(' ')
        #Look for Space determine if command has arguments
        if(SpacePosition != -1):
            Command = Input[0:SpacePosition]
            End = Input.find('\r\n')
            Argument = Input[SpacePosition+1:End]
        else:
            End = Input.find('\r\n')
            Command = Input[0:End]
            Argument = ''
        return Command,Argument
    
    def USER(self, username):
        # Check if username is good
        if username in LoginDetails.keys():
            self.username = username
            self.usernameFlag = True
            ReplyMsg = "331  User name okay, need password.\r\n" 
        else: 
            self.usernameFlag = False
            ReplyMsg = "332 Need account for login.\r\n"
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
                
    def PASS(self, password):
        if self.loginFlag or not self.usernameFlag:
            ReplyMsg = "451 Requested action aborted: local error in processing.\r\n"
        elif (password == LoginDetails[self.username]):
            self.loginFlag = True
            
            ReplyMsg = "230 User logged in, proceed.\r\n"
            self.UserPath = os.path.abspath(os.path.join(os.path.sep,self.UserPath,self.username))
            self.UserParentDir = os.path.abspath(os.path.join(os.path.sep,self.UserParentDir,self.username))
        else:
            ReplyMsg = "530 Not logged in.\r\n"
        print str(self.UserParentDir)
        self.ClientSocket.send(ReplyMsg.encode('UTF-8'))
        
            
    #Recive a File From Client
    def Receive_File(self, File_Name):
        #Determine Type of data transfer
        if(self.TypeList[0] == True):
            Encode_Type = 'UTF-8'
        elif(self.TypeList[1]==True):
            Encode_Type = 'cp500'
        print "storing file"
        
        Reply1 = ("225 Data connection open; no transfer in progress.\r\n")
        self.ClientSocket.send(Reply1.encode('UTF-8'))
        #Store files in a folder stuff to see if files are being placed correctly
        File_Name = self.UserPath+ '/' + File_Name
        if(self.TypeList[2] == True):
            ReceivedData = self.DataSocket.recv(8192)
            File =  open(File_Name,'wb')
            
            while ReceivedData:
                print "Receiving..."
                File.write(ReceivedData)
                ReceivedData =self.DataSocket.recv(8192)
        else:
            ReceivedData = self.DataSocket.recv(8192).decode(Encode_Type)
            File =  open(File_Name,'wb')
            
            while ReceivedData:
                print "Receiving..."
                File.write(ReceivedData)
                ReceivedData = self.DataSocket.recv(8192).decode(Encode_Type)
        File.close()
        Reply2 = '226 Successfully transferred \"' + File_Name + '\"'
        self.DataSocket.close()
        self.ClientSocket.send(Reply2.encode('UTF-8'))
        
        
        for i in xrange(0, len(self.TypeList)):
            self.TypeList[i] = False
        self.TypeList[0] = True
        return
    
    def Transmit_File(self, File_Name):
        # Check if file exists
        if(self.TypeList[0] == True):
            Encode_Type = 'UTF-8'
        elif(self.TypeList[1]==True):
            Encode_Type = 'cp500'
        
        print str(self.UserPath+ '/'+str(File_Name))  
        TransmittedFile = open(self.UserPath+ '/'+str(File_Name),'rb')
        
        Reply1 = ("225 Data connection open; no transfer in progress.\r\n")
        self.ClientSocket.send(Reply1.encode('UTF-8'))
        
        if(self.TypeList[2]==True):
            Reading = TransmittedFile.read(8192)
            while (Reading):
                self.DataSocket.send(Reading)
                Reading = TransmittedFile.read(8192)
        else:
            Reading = TransmittedFile.read(8192).encode(Encode_Type)
            while (Reading):
                self.DataSocket.send(Reading)
                Reading = TransmittedFile.read(8192).encode(Encode_Type)
                
        TransmittedFile.close()
        Reply = '226 Successfully transferred \"' + File_Name + '\"\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        self.DataSocket.close()
        
        for i in xrange(0, len(self.TypeList)):
            self.TypeList[i] = False
        self.TypeList[0] = True
        return
        
    #NOOP command returns 200 Ok
    def NoAction(self):
        Input = '200 OK'
        self.ClientSocket.send(Input.encode('UTF-8'))
        return
    
    #Not Working With Multiple Users
    #List all files and folders in current directory
    def CurrentFileDirectory(self):
        DirectoryName = os.path.basename(self.UserPath)
        Files = 'Files in Current Directory : \"' + DirectoryName + '\r\n'
        FileDirectory = os.listdir(self.UserPath)
        
        files = ""
        for i in FileDirectory:
            files = files + str(i) + '\n'
       
        print files
        self.DataSocket.send(files.encode('UTF-8'))
        self.DataSocket.close()
        #self.DataSocket, self.DataAddress = FileTransferSocket.accept()
        #ReplyCode = ("225 Data connection open; no transfer in progress.\r\n")
        Reply = '226 Successfully transferred list of current working directory\"\r\n'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        #print(UserPath)
        return
        
    #Change the data type for file transfers
    def DataType(self,Type):
        for i in xrange(0, len(self.TypeList)):
            self.TypeList[i] = False
        if(Type == 'A'):
            self.TypeList[0] = True
        elif(Type == 'E'):
            self.TypeList[1] = True
        elif(Type == 'I'):
            self.TypeList[2] = True
        else:
            Reply = '400 Type ' + Type + ' not supported'
            self.ClientSocket.send(Reply)
            return
        Reply = '200 Type set to ' + Type
        self.ClientSocket.send(Reply)
        print(Reply)
        return
    
    #Implement Passive Mode which initilises the socket to be used
    def PassiveMode(self):
        FileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        FileTransferSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        FileTransferSocket.bind(('0.0.0.0', 0))
        FileTransferSocket.listen(1)
        DataPort = FileTransferSocket.getsockname()[1]
        #print DataPort
        #DataPort is a value of 256 get remainder    
        p2 = DataPort % 256
        #Subtract remainder to ensure its a multiple of 256
        p1 = (DataPort -p2)/256
        
        #Replace dots with commas to meet standards
        self.Host = self.Host.replace('.',',')
        
        Message = ( '227 Entering Passive Mode (' + self.Host +',' + str(p1) + ',' +str(p2) + ')\r\n' )
        self.ClientSocket.send(Message.encode("UTF-8"))
        #self.DataSocket, self.DataAddress
        #ReplyCode = ('150 File status okay about to open data connection.\r\n')
        #self.ClientSocket.send(ReplyCode.encode('UTF-8'))
        
        self.DataSocket, self.DataAddress = FileTransferSocket.accept()
        #ReplyCode = ("225 Data connection open; no transfer in progress.\r\n")
        
        #self.ClientSocket.send(ReplyCode.encode('UTF-8'))
        FileTransferSocket.close()
        #return DataConnection, DataAddress
    
    # Changes for all users needs to be fixed
    def ChangeDirectory(self,DirectoryName):
        if os.path.isdir(DirectoryName):
            self.UserPath = os.path.abspath(os.path.join(os.path.sep,UserPath,DirectoryName))
            Reply = '250 CWD successful. \"' + DirectoryName + '\" is current directory.'
        else :
            Reply = '550 \"' + DirectoryName + '\"does not exsist.'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
    
    def MakeDirectory(self,DirectoryName):
        os.mkdir(DirectoryName)
        Reply = '257 \"' + DirectoryName + '\" created successfully'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return
    
    def RemoveDirectory(self,DirectoryName):
        os.rmdir(DirectoryName)
        Reply = '250 \"' + DirectoryName + '\" deleted successfully.'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return

    def ParentDirectory(self):
        self.UserPath = script_dir
        Reply = os.path.basename(self.UserPath)
        self.ClientSocket.send(Reply.encode('UTF-8')) 
        print(self.UserPath)
        return
    
    def DeleteFile(self,File_Name):
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
    newthread = FTP_Threading(ControlConnection,ClientAddress)
    newthread.start()