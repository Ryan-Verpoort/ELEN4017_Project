import socket
#import time
import os

'''
            Code     Meaning

             128     End of data block is EOR
              64     End of data block is EOF
              32     Suspected errors in data block
'''

Port = 22
Host = '127.0.0.1'
#TypeList to determine what typeof data encoding to be used
TypeList = [True,False,False]

#Create and Connect to Control Socket for commands
ControlSocket =socket.socket()
ControlSocket.bind((Host, Port))
ControlSocket.listen(3)
connectionSocket, address = ControlSocket.accept()

#Path for listing files
#need to modify to take in user input for reading and writing 
#path = os.getcwd()

#Formatting of Input arguments for server to decide what must be done
def InputArgument(Input):
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
def Recieve_File(FileConnectionSocket,TypeList,File_Name):
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
    connectionSocket.send(Reply.encode('UTF-8'))
    FileConnectionSocket.close()
    
    return

def Transmit_File(FileConnectionSocket,TypeList,File_Name):
    
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
    connectionSocket.send(Reply.encode('UTF-8'))
    FileConnectionSocket.close()

    return
    
#NOOP command returns 200 Ok
def NoAction(Input):
    Input = '200 OK'
    connectionSocket.send(Input.encode('UTF-8'))
    return
    
#List all files and folders in current directory
def CurrentFileDirectory(FileConnectionSocket):
    DirectoryName = os.path.basename(os.getcwd())
    Files = 'Files in Current Directory : \"' + DirectoryName + '\"\n'
    FileDirectory = os.listdir(os.getcwd())
    
    for i in FileDirectory:
        Files = Files + str(i) + '\n'
    FileConnectionSocket.send(Files.encode('UTF-8'))
    FileConnectionSocket.close()
    return
    
#Change the data type for file transfers
def DataType(type,TypeList):
    for i in xrange(0, len(TypeList)):
        TypeList[i] = False
    if(type == 'A'):
        TypeList[0] = True
    elif(type == 'E'):
        TypeList[1] = True
    elif(type == 'I'):
        TypeList[2] = True
    else:
        Reply = '400 Type ' + type + ' not supported'
        connectionSocket.send(Reply)
        return
    Reply = '200 Type set to ' + type
    print(Reply)
    return

#Implement Passive Mode which initilises the socket to be used
def PassiveMode(Host):
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
    connectionSocket.send(Message.encode("UTF-8"))
    
    ReplyCode = ('150 File status okay about to open data connection.\r\n')
    connectionSocket.send(ReplyCode.encode('UTF-8'))
    
    DataConnection, DataAddress = FileTransferSocket.accept()
    
    return DataConnection, DataAddress

def ChangeDirectory(DirectoryName):
    os.chdir(DirectoryName)
    Reply = '250 CWD successful. \"' + DirectoryName + '\" is current directory.'
    connectionSocket.send(Reply.encode('UTF-8'))
    return

def MakeDirectory(DirectoryName):
    os.mkdir(DirectoryName)
    Reply = '257 \"' + DirectoryName + '\" created successfully'
    connectionSocket.send(Reply.encode('UTF-8'))
    return

def RemoveDirectory(DirectoryName):
    os.rmdir(DirectoryName)
    Reply = '250 \"' + DirectoryName + '\" deleted successfully.'
    connectionSocket.send(Reply.encode('UTF-8'))
    return

def DeleteFile(File_Name):
    os.remove(File_Name)
    Reply = '250 \"' + File_Name + '\" deleted successfully.'
    connectionSocket.send(Reply.encode('UTF-8'))
    return

print ('Connection request from address: ' + str(address))
true = 1
while 1:
    Input = connectionSocket.recv(4096).decode('UTF-8')
    Command,Argument = InputArgument(Input)
    Input = Command
    print(Input)

    if Input == 'STOR':
        #connectionSocket.send('Hello Darkness')
        Recieve_File(FileConnectionSocket,TypeList,Argument)
        continue
    
    elif Input == 'RETR':
        #connectionSocket.send('Hello Darkness')
        Transmit_File(FileConnectionSocket,TypeList,Argument)
        continue
    
    elif Input == 'PORT':
        print('502 Command not implemented.')
        continue

    elif Input == 'NOOP':
        #connectionSocket.send('Hello Darkness')
        NoAction(Input)
        continue
    
    elif Input == 'LIST':
        #connectionSocket.send('Hello Darkness')
        CurrentFileDirectory(FileConnectionSocket)
        continue
    
    elif Input == 'QUIT':
        connectionSocket.close()
        break
    
    elif Input == 'TYPE':
        DataType(Argument,TypeList)
        continue
        
    elif Input == 'PASV':
        FileConnectionSocket, address = PassiveMode(Host)
        continue
        
    elif Input == 'CWD':
        ChangeDirectory(Argument)
        continue
    
    elif Input == 'MKD':
        MakeDirectory(Argument)
        continue
    
    elif Input == 'RMD':
        RemoveDirectory(Argument)
        continue
    
    elif Input == 'DELE':
        DeleteFile(Argument)
        continue
    
    else:
        connectionSocket.send('Not Implemented')