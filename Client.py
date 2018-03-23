import socket
import os

script_dir = os.path.dirname(__file__)

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
        self.Port = 2500
        self.Host = '127.0.0.1' #'66.220.9.50'#'ftp.dlptest.com' #'ftp.mirror.ac.za'
        self.TypeList = [True,False,False]
        self.ControlSocket = socket.socket()
        self.DataSocket = socket.socket()
        self.DataAddress = ("",0)
        # Client directory paths for upload/download
        self.UserPath = os.path.abspath(os.path.join(os.path.sep,script_dir,"Local_Client_Files"))
        print str(self.UserPath)

    def __del__(self):
        self.ControlSocket.close()
    
    '''
    list is done from the function list which lists whats in directory 
    gui will have to manage whats on the clients machine server has no access to clieents machine or directories
    '''

    def FTPCommand(self,Command,Argument=""):
        if Argument == '':
            FTP_CMD = str(Command) + '\r\n'
        else:
            FTP_CMD = str(Command) + ' ' + str(Argument) + '\r\n'
        self.ControlSocket.send(FTP_CMD.encode('UTF-8'))
        ServerReply = self.ControlSocket.recv(8192).decode('UTF-8')
        self.command = FTP_CMD
        self.server_reply = ServerReply 
        print "C----------->S "+self.command 
        print "C<-----------S "+self.server_reply 
        return ServerReply

    def USER (self, user, command="USER", ):
        print "hello "+user
        here = self.FTPCommand(command, user)
    
    def PASS (self,  password, command="PASS"):
        print self.username+ " Logged in successfully"
        msg = self.FTPCommand(command, password)
        if msg[0] == "2":
            self.LoginFlag = True
        else:
            self.LoginFlag = False
        
    # [A,E,I]
    def Receive_File(self, File_Name):
        print "err1"
        if(self.TypeList[0] == True):
            Encode_Type = 'UTF-8'
        elif(self.TypeList[1]==True):
            Encode_Type = 'cp500'
        
        Reply = FTPCommand('RETR', File_Name)
        print('Control connection reply: \n' + str(Reply))
        
        if Reply[0] != '5':
            File_Name = self.UserPath+"/"+File_Name
            if(TypeList[2] == True):
                ReceivedData = self.DataSocket.recv(8192)
                File =  open(File_Name,'wb')
            
                while ReceivedData:
                    File.write(ReceivedData)
                    ReceivedData = self.DataSocket.recv(8192)
            else:
                ReceivedData = self.DataSocket.recv(8192).decode(Encode_Type)
                File =  open(File_Name,'wb')
                while ReceivedData:
                    File.write(ReceivedData)
                    ReceivedData = self.DataSocket.recv(8192).decode(Encode_Type)
                    
            File.close()
            Reply = self.ControlSocket.recv(8192).decode('UTF-8')
            print(Reply)
            
        self.DataSocket.close()
        return

    def Transmit_File(self, File_Name):
    
        if(self.TypeList[0] == True):
            Encode_Type = 'UTF-8'
        elif(self.TypeList[1]==True):
            Encode_Type = 'cp500'
        print(self.TypeList)
        
        Reply= FTPCommand('STOR',File_Name)
        print('Control connection reply: \n' + str(Reply))
        self.servermsg = Reply
        TransmittedFile = open(self.UserPath+'/'+File_Name,'rb')
        if Reply[0] != '5':
            if(TypeList[2]==True):
                Reading = TransmittedFile.read(8192)
                while (Reading):
                    self.DataSocket.send(Reading)
                    Reading = TransmittedFile.read(8192)
            else:
                Reading = self.DataSocket.read(8192).encode(Encode_Type)
                while (Reading):
                    self.DataSocket.send(Reading)
                    Reading = self.DataSocket.read(8192).encode(Encode_Type)
            TransmittedFile.close()
        
        Reply = ControlSocket.recv(8192).decode('UTF-8')
        
        self.servermsg = Reply
        self.DataSocket.close()
        
        return
        
    def NoAction(self):
    
        ServerReply = FTPCommand('NOOP','')
        print(ServerReply) 
        return

    def FileDirectory(self):
        
        ControlReply = self.FTPCommand('LIST') 
        
        if ControlReply[0] == "1" or ControlReply[0] == "2":
            DataReply = self.DataSocket.recv(4096).decode('UTF-8')
            DataReply = DataReply
            DataReply = DataReply.split('\n')
    
        self.DataSocket.close()
        return DataReply

    def passiveMode(self):
    
        Reply = self.FTPCommand('PASV')
        print(Reply)
        Reply = Reply.replace(".",",")
        start = Reply.find('(')
        end = Reply.find(')')
        Reply = Reply[start+1:end]
        Reply = Reply.split(',')
        print(Reply)
        Host = str(Reply[0]) + '.'+ str(Reply[1]) +'.'+ str(Reply[2]) +'.'+ str(Reply[3])
        Port = (int(Reply[4])*256) + int(Reply[5])
        print('New host Data Connection: \n' + str(Host))
        print('New port Data Connection:\n ' + str(Port))
        self.DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.DataSocket.connect((Host,Port))
        

    def GetHelp(self):
        Input = raw_input('Enter Command: ')
        Input = Input.upper()
        print(self.FTPCommand('HELP',Input))
        print(self.ControlSocket.recv(8192).decode('UTF-8'))
        return

    def ChangeDirectory(self,DirectoryName ):
        print(self.FTPCommand('CWD',DirectoryName))
        return

    def MakeDirectory(self, DirectoryName ):
        self.FTPCommand('MKD',DirectoryName)
        return

    def RemoveDirectory(self, DirectoryName ):
        self.FTPCommand('RMD',DirectoryName)
        return

    def ParentDirectory(self):
        self.FTPCommand('CDUP','')
        return

    def DeleteFile(self, File_Name):
        self.FTPCommand('DELE',File_Name)
        return

    #Login(Port,Host)
    #[A,E,I]
    def DataType(self):
        Type = raw_input('Type: ')
        for i in xrange(0, len(TypeList)):
            TypeList[i] = False
        if(Type == 'E'):
            TypeList[1] = True
        elif(Type == 'I'):
            TypeList[2] = True
        else:
            TypeList[0] = True
        print(FTPCommand('TYPE',Type))
        return

    def Disconnect(self):
        self.FTPCommand('QUIT')
        self.ControlConnectionFlag = False
        return
        
    def Connect(self):
        self.ControlSocket = socket.socket()
        self.ControlSocket.connect((self.Host,self.Port))
        self.ControlConnectionFlag = True
        print "Connecting" 

'''        
FTP_TYPE = {
    "A": "UTF-8",
    "E": "cp500"
    "I": "None"
}'''

EXTENSION = {
    ".jpeg": "I",
    ".png" : "I",
    ".mp4" : "I",
    ".txt" : "A"
}
def getType(File_Name):
    end=len(File_Name)
    extensionIndex = File_Name.find(".")
    extension = File_Name [extensionIndex:end]
    if extension in EXTENSION:
        return EXTENSION[extension]
    print "Only Processing .jpeg .png .mp4 .txt"
    return "" 