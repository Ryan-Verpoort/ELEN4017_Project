import socket

Port = 22
Host = '127.0.0.1'#'66.220.9.50'#'ftp.dlptest.com' #'ftp.mirror.ac.za'
TypeList = [True,False,False]

ControlSocket = socket.socket()
ControlSocket.connect((Host,Port))



def FTPCommand(Command,Argument):
    if Argument == '':
        FTP_CMD = str(Command) + '\r\n'
    else:
        FTP_CMD = str(Command) + ' ' + str(Argument) + '\r\n'
    ControlSocket.send(FTP_CMD.encode('UTF-8'))
    ServerReply = ControlSocket.recv(8192).decode('UTF-8')
    return ServerReply


#def Recieve_ASCII_File(Host, Encode_Type): For EBCDIC
def Recieve_File(Host,TypeList):
    
    if(TypeList[0] == True):
        Encode_Type = 'UTF-8'
    elif(TypeList[1]==True):
        Encode_Type = 'cp500'
    
    Host,File_Port = passiveMode()

    FileTransferSocket = socket.socket()
    FileTransferSocket.connect((Host,File_Port))
    
    
    File_Name = raw_input('Enter File Name: ')
    Reply = FTPCommand('RETR',File_Name)
    print('Control connection reply: \n' + str(Reply))
    if Reply[0] != '5':
        File_Name = 'Docs/'+File_Name
        
        if(TypeList[2] == True):
            RecievedData = FileTransferSocket.recv(8192)
            File =  open(File_Name,'wb')
            
            while RecievedData:
                File.write(RecievedData)
                RecievedData = FileTransferSocket.recv(8192)
        else:
            RecievedData = FileTransferSocket.recv(8192).decode(Encode_Type)
            File =  open(File_Name,'wb')
            
            while RecievedData:
                File.write(RecievedData)
                RecievedData = FileTransferSocket.recv(8192).decode(Encode_Type)
        File.close()
        Reply = ControlSocket.recv(8192).decode('UTF-8')
        print(Reply)
    FileTransferSocket.close()
    
    return

def Transmit_File(Host,TypeList):
    
    if(TypeList[0] == True):
        Encode_Type = 'UTF-8'
    elif(TypeList[1]==True):
        Encode_Type = 'cp500'
    print(TypeList)
    Host,File_Port = passiveMode()
    
    File_Name = raw_input('Enter File Name: ')
    
    FileTransferSocket = socket.socket()
    FileTransferSocket.connect((Host,File_Port))   
    
    Reply = FTPCommand('STOR',File_Name)
    print('Control connection reply: \n' + str(Reply))
    
   
    TransmittedFile = open(File_Name,'rb')
    
    if(TypeList[2]==True):
        Reading = TransmittedFile.read(8192)
        while (Reading):
            FileTransferSocket.send(Reading)
            Reading = TransmittedFile.read(8192)
    else:
        Reading = TransmittedFile.read(8192).encode(Encode_Type)
        while (Reading):
            FileTransferSocket.send(Reading)
            Reading = TransmittedFile.read(8192).encode(Encode_Type)
    TransmittedFile.close()
    FileTransferSocket.close()
    Reply = ControlSocket.recv(8192).decode('UTF-8')
    print(Reply)

    return

#Change The port of the File connection
def NewPort(Host, NewPort):
    
    Host,Port = passiveMode()
    #Replace the . with , to conform to the FTP PORT configuration h1,h2,h3,h4
    Host = str(Host).replace('.',',')
    #Convert the Port into Hex pairing them into 2 sets of 2 => p1,p2
    NewPort = hex(NewPort)[2:]
    #Create the new address to connect to convert the hex into dec and send h1,h2,h3,h4,p1,p2
    NewAddress = str(Host) + ',' + str(int(NewPort[0:2],16)) +str(int(NewPort[2:],16))
    #Create Request String
    Request = 'PORT ' + NewAddress + '\r\n'
    
    ControlSocket.send(Request.encode('UTF-8'))
    #Port = NewPort
    Reply = ControlSocket.recv(8196).decode('UTF-8')
    
    print(Reply)
    return NewAddress

def NoAction(Input):
    
    ServerReply = FTPCommand('NOOP','')
    print(ServerReply) 
    return

def FileDirectory(Input):

    Host,File_Port = passiveMode()
    FileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    FileTransferSocket.connect((Host,File_Port))
    
    Reply = FTPCommand('LIST','')
    
    print('Control connection: \n' + str(Reply))
    
    Reply = FileTransferSocket.recv(4096).decode('UTF-8')
    print('Data port reply:\n ' + str(Reply))
    
    #Reply = ControlSocket.recv(4096).decode('UTF-8')
    #print('Control connection:\n ' + str(Reply))
    
    FileTransferSocket.close()
    
    return


def Login(port,Host):    
    
    ServerReply = ControlSocket.recv(4096).decode('UTF-8')
    print('Reply from server:\n' + str(ServerReply))

    ServerReplyCode = ''
    while 1:
        
        Username = raw_input('USER ')
        ServerReplyCode = FTPCommand('USER',Username)
        print( 'Reply from server: \n' + str(ServerReplyCode))
        
        if ServerReplyCode[0:3] == '331' or ServerReplyCode[0:3] =='230':
            break
        
    ServerReplyCode =''
    while 1:
        
        Password = raw_input('PASS ')#'eiTqR7EMZD5zy7M' 
        ServerReplyCode = FTPCommand('PASS',Password)
        print('Reply from server: \n' + str(ServerReplyCode))
        
        if ServerReplyCode[0:3] == '230':
            break

    return

def passiveMode():
    
    Reply = FTPCommand('PASV','')
    print(Reply)
    start = Reply.find('(')
    end = Reply.find(')')
    Reply = Reply[start+1:end]
    Reply = Reply.split(',')
    Host = str(Reply[0]) + '.'+ str(Reply[1]) +'.'+ str(Reply[2]) +'.'+ str(Reply[3])
    Port = (int(Reply[4])*256) + int(Reply[5])
    print('New host Data Connection: \n' + str(Host))
    print('New port Data Connection:\n ' + str(Port))
    
    return Host,Port

def GetHelp(Input):
    Input = raw_input('Enter Command: ')
    Input = Input.upper()
    print(FTPCommand('HELP',Input))
    print(ControlSocket.recv(8192).decode('UTF-8'))
    return

#Login(Port,Host)

def DataType(type,TypeList):
    type = raw_input('Type: ')
    for i in xrange(0, len(TypeList)):
        TypeList[i] = False
    if(type == 'E'):
        TypeList[1] = True
    elif(type == 'I'):
        TypeList[2] = True
    else:
        TypeList[0] = True
    print(FTPCommand('TYPE',type))
    return

UserInput = raw_input('Input: ' )
UserRequest = UserInput.upper()

while UserRequest != 'QUIT':

    if UserRequest == 'STOR':
        Transmit_File(Host,TypeList)
    
    elif UserRequest == 'RETR':
        Recieve_File(Host,TypeList)
        
    elif UserRequest == 'PORT':
        NewPort(Host,1250)

    elif UserRequest == 'NOOP':
        NoAction(UserRequest)
        
    elif UserRequest == 'LIST':
        FileDirectory(UserRequest)
        
    elif UserRequest == 'TYPE':
        DataType(UserRequest,TypeList)
        
    elif UserRequest == 'HELP':
        GetHelp(UserRequest)
        
    elif UserRequest == 'PASV':
        passiveMode()
        
    else:
        print(FTPCommand(UserInput,''))
    
    UserInput = raw_input('Input: ' )
    UserRequest = UserInput.upper()

ControlSocket.send(UserInput.encode('UTF-8'))
ControlSocket.close()