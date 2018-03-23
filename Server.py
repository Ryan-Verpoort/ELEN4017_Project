import socket
import threading
import os

Port = 2500
Host = '127.0.0.1'
script_dir = os.path.dirname(__file__)

#TypeList to determine what typeof data encoding to be used
TypeList = [True,False,False]

class FTP_Threading(threading.Thread):
    
    def __init__(self,ClientSocket,ClientAddress):
        threading.Thread.__init__(self)
        self.ClientSocket = ClientSocket
        self.ClientAddress = ClientAddress
        self.Port = Port
        self.Host = Host
        self.UserPath = script_dir
        self.UserParentDir = ''
        print ('Connection request from address: ' + str(self.ClientAddress))
    
    def run(self):
        while 1:
            Input = self.ClientSocket.recv(4096).decode('UTF-8')
            Command,Argument = self.InputArgument(Input)
        
            if Command == 'STOR':
                self.Recieve_File(self.FileConnectionSocket,TypeList,Argument)
                continue
            
            elif Command == 'RETR':
                self.Transmit_File(self.FileConnectionSocket,TypeList,Argument)
                continue
            
            elif Command == 'PORT':
                print('502 Command not implemented.')
                continue
        
            elif Command == 'NOOP':
                self.NoAction(Command)
                continue
            
            elif Command == 'LIST':
                print(self.UserPath)
                self.CurrentFileDirectory(self.FileConnectionSocket,self.UserPath)
                continue
            
            elif Command == 'TYPE':
                self.DataType(Argument,TypeList)
                continue
                
            elif Command == 'PASV':
                self.FileConnectionSocket, address = self.PassiveMode(Host)
                continue
                
            elif Command == 'CWD':
                self.ChangeDirectory(Argument,self.UserPath)
                print(self.UserPath)
                continue
            
            elif Command == 'MKD':
                self.MakeDirectory(Argument)
                continue
            
            elif Command == 'RMD':
                self.RemoveDirectory(Argument)
                continue
            
            elif Command == 'CDUP':
                self.ParentDirectory(self.UserPath)
            
            elif Command == 'DELE':
                self.DeleteFile(Argument)
                continue
            
            elif Command == 'QUIT':
                self.ClientDisconnect(self.ClientAddress)
                break
            
            else:
                self.ClientSocket.send('Not Implemented')
                
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
    
    #Recive a File From Client
    def Recieve_File(self,FileConnectionSocket,TypeList,File_Name):
        #Determine Type of data transfer
        if(TypeList[0] == True):
            Encode_Type = 'UTF-8'
        elif(TypeList[1]==True):
            Encode_Type = 'cp500'
        
        #Store files in a folder stuff to see if files are being placed correctly
        File_Name = 'Stuff/' + File_Name
        if(TypeList[2] == True):
            RecievedData = FileConnectionSocket.recv(8192)
            File =  open(File_Name,'wb')
            
            while RecievedData:
                File.write(RecievedData)
                RecievedData = FileConnectionSocket.recv(8192)
        else:
            RecievedData = FileConnectionSocket.recv(8192).decode(Encode_Type)
            File =  open(File_Name,'wb')
            
            while RecievedData:
                File.write(RecievedData)
                RecievedData = FileConnectionSocket.recv(8192).decode(Encode_Type)
        File.close()
        Reply = '226 Successfully transferred \"' + File_Name + '\"'
        self.ClientSocket.send(Reply.encode('UTF-8'))
        FileConnectionSocket.close()
        
        return
    
    def Transmit_File(self,FileConnectionSocket,TypeList,File_Name):
        
        if(TypeList[0] == True):
            Encode_Type = 'UTF-8'
        elif(TypeList[1]==True):
            Encode_Type = 'cp500'
           
        TransmittedFile = open(File_Name,'rb')
        
        if(TypeList[2]==True):
            Reading = TransmittedFile.read(8192)
            while (Reading):
                FileConnectionSocket.send(Reading)
                Reading = TransmittedFile.read(8192)
        else:
            Reading = TransmittedFile.read(8192).encode(Encode_Type)
            while (Reading):
                FileConnectionSocket.send(Reading)
                Reading = TransmittedFile.read(8192).encode(Encode_Type)
                
        TransmittedFile.close()
        Reply = '226 Successfully transferred \"' + File_Name + '\"'
        print(Reply)
        self.ClientSocket.send(Reply.encode('UTF-8'))
        FileConnectionSocket.close()
    
        return
        
    #NOOP command returns 200 Ok
    def NoAction(self,Input):
        Input = '200 OK'
        self.ClientSocket.send(Input.encode('UTF-8'))
        return
    
    #Not Working With Multiple Users
    #List all files and folders in current directory
    def CurrentFileDirectory(self,FileConnectionSocket,UserPath):
        DirectoryName = os.path.basename(UserPath)
        Files = 'Files in Current Directory : \"' + DirectoryName + '\"\n'
        FileDirectory = os.listdir(UserPath)
        
        for i in FileDirectory:
            Files = Files + str(i) + '\n'
        FileConnectionSocket.send(Files.encode('UTF-8'))
        FileConnectionSocket.close()
        print(UserPath)
        return
        
    #Change the data type for file transfers
    def DataType(self,Type,TypeList):
        for i in xrange(0, len(TypeList)):
            TypeList[i] = False
        if(Type == 'A'):
            TypeList[0] = True
        elif(Type == 'E'):
            TypeList[1] = True
        elif(Type == 'I'):
            TypeList[2] = True
        else:
            Reply = '400 Type ' + Type + ' not supported'
            self.ClientSocket.send(Reply)
            return
        Reply = '200 Type set to ' + Type
        self.ClientSocket.send(Reply)
        print(Reply)
        return
    
    #Implement Passive Mode which initilises the socket to be used
    def PassiveMode(self,Host):
        FileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        FileTransferSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        FileTransferSocket.bind(('0.0.0.0', 0))
        FileTransferSocket.listen(5)
        DataPort = FileTransferSocket.getsockname()[1]
        
        #DataPort is a value of 256 get remainder    
        p2 = DataPort % 256
        #Subtract remainder to ensure its a multiple of 256
        p1 = (DataPort -p2)/256
        
        #Replace dots with commas to meet standards
        Host = Host.replace('.',',')
        
        Message = ( '227 Entering Passive Mode (' + Host +',' + str(p1) + ',' +str(p2) + ')\r\n' )
        self.ClientSocket.send(Message.encode("UTF-8"))
        
        ReplyCode = ('150 File status okay about to open data connection.\r\n')
        self.ClientSocket.send(ReplyCode.encode('UTF-8'))
        
        DataConnection, DataAddress = FileTransferSocket.accept()
        
        return DataConnection, DataAddress
    
    #Changes for all users needs to be fixed
    def ChangeDirectory(self,DirectoryName,UserPath):
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

    def ParentDirectory(self,UserPath):
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
    
    def ClientDisconnect(self,ClientAddress):
        print('Client at address: ' + str(ClientAddress) + ' Disconnected')
        Reply = '221 Service closing control connection. \nUserName Logged out' 
        self.ClientSocket.send(Reply.encode('UTF-8'))
        return

ControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#ControlSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
ControlSocket.bind((Host, Port))

while True:
    ControlSocket.listen(3)
    ControlConnection, ClientAddress = ControlSocket.accept()
    newthread = FTP_Threading(ControlConnection,ClientAddress)
    newthread.start()