import socket
import os
from FileRW import *
script_dir = os.path.dirname(__file__)

        
FTP_TYPE = {
    "A": "UTF-8",
    "E": "cp500",
    "I": "None"
}

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
        string = EXTENSION[extension]
        print string
        return string
    print "Only Processing .jpeg .png .mp4 .txt"
    return "" 
    
class Client(object):
    def __init__(self):
        # information needed for the gui
        self.ControlConnectionFlag = False
        self.DataConnectionFlag = False
        self.LoginFlag = False
        self.username = ""
        self.server_reply = ""
        self.command = ""
        #self.fsHandler = FileSocketHandler()
        # FTP information
        self.Port = 2500
        self.Host = '127.0.0.1' #'66.220.9.50'#'ftp.dlptest.com' #'ftp.mirror.ac.za'
        self.type = FTP_TYPE["A"]
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
            self.command=str(Command) + '\r\n'
        else:
            self.command = str(Command) + ' ' + str(Argument) + '\r\n'
        self.ControlSocket.send(self.command.encode('UTF-8'))
        self.server_reply = self.ControlSocket.recv(8192).decode('UTF-8')
        print "C----------->S "+self.command 
        print "C<-----------S "+self.server_reply 
        

    def USER (self, user, command="USER", ):
        self.FTPCommand(command, user)
    
    def PASS (self,  password, command="PASS"):
        print self.username+ " Logged in successfully"
        self.FTPCommand(command, password)
        if self.server_reply[0] == "2":
            self.LoginFlag = True
        else:
            self.LoginFlag = False
        
    # [A,E,I]
    def Receive_File(self, File_Name):
       
        self.FTPCommand('RETR', File_Name)
        
        if not self.server_reply[0] == '5':
            File_Name = str(self.UserPath)+ '/' + File_Name
            ReadFromSocket(self.DataSocket, File_Name, self.type)
            
        self.server_reply = self.ControlSocket.recv(8192).decode('UTF-8')
        self.DataSocket.close()
        self.type = FTP_TYPE["A"]
        self.DataConnectionFlag = False
        return

    def Transmit_File(self, File_Name):
        
        self.FTPCommand('STOR',File_Name)
        if not self.server_reply[0] == '5':
            File_Name = str(self.UserPath)+ '/' + str(File_Name)
            print File_Name
            WriteToSocket(self.DataSocket, File_Name, self.type)
        
        self.DataSocket.shutdown(socket.SHUT_WR)
        self.server_reply = self.ControlSocket.recv(8192).decode('UTF-8')
        self.DataSocket.close()
        self.type = FTP_TYPE["A"]
        self.DataConnectionFlag = False
        return
        
    def NoAction(self):
    
        ServerReply = FTPCommand('NOOP','')
        return

    def FileDirectory(self):
        
        self.FTPCommand('LIST') 
        
        if self.server_reply[0] == "1" or self.server_reply[0] == "2":
            DataReply = self.DataSocket.recv(4096).decode('UTF-8')
            DataReply = DataReply
            DataReply = DataReply.split('\n')
    
        self.DataSocket.close()
        self.DataConnectionFlag = False
        return DataReply

    def passiveMode(self):
    
        self.FTPCommand('PASV')
        Reply = self.server_reply 
        Reply = Reply.replace(".",",")
        start = Reply.find('(')
        end   = Reply.find(')')
        Reply = Reply[start+1:end]
        Reply = Reply.split(',')

        Host = str(Reply[0]) + '.'+ str(Reply[1]) +'.'+ str(Reply[2]) +'.'+ str(Reply[3])
        Port = (int(Reply[4])*256) + int(Reply[5])
        
        self.DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.DataSocket.connect((Host,Port))
        self.DataConnectionFlag = True

    def GetHelp(self):
        self.FTPCommand('HELP',Input)
        commandInfo = self.ControlSocket.recv(8192).decode('UTF-8')
        return commandInfo

    def ChangeDirectory(self,DirectoryName ):
        self.FTPCommand('CWD',DirectoryName)
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


    def DataType(self, Type):
        if Type in FTP_TYPE:
            self.type = FTP_TYPE[Type]
            
        else:
            self.type = FTP_TYPE["A"]
            print "type argument not implemented-- Setting to default type"
        self.FTPCommand("TYPE",Type)
        return

    def Disconnect(self):
        self.FTPCommand('QUIT')
        self.ControlConnectionFlag = False
        return
        
    def Connect(self):
        self.ControlSocket = socket.socket()
        self.ControlSocket.connect((self.Host,self.Port))
        self.ControlConnectionFlag = True
        return

