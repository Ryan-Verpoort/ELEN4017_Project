import sys
import socket
import os
from TCPClient3 import *  

# Class Containing all Client FTP commands 
''' TYPE - ASCII Non-print Image
         MODE - Stream
         STRUCTURE - File, Record
         COMMANDS - USER, QUIT, PORT,
                    TYPE, MODE, STRU,
                      for the default values
                    RETR, STOR,
                    NOOP.

      The default values for transfer parameters are:

         TYPE - ASCII Non-print
         MODE - Stream
         STRU - File'''
FTP_TYPE = {
    "ASCII Non-print": "A"
}
ENCODING = {
    "ASCII Non-print": "UTF-8"
}

FTP_MODE = { "STREAM": "S" }

FTP_STRU = { "FILE": "F" }

FTP_COMMAND = {  
    "USER": 1,            
    "PASS": 2,
    "QUIT": 3,
    "PORT": 4,
    "TYPE": 5,
    "MODE": 6,
    "STRU": 7,
    "RETR": 8,
    "STOR": 9,
    "LIST": 10,
    "HELP": 11,
    "NOOP": 12 
}

FTP_SM = {
"USER1":"331", # User name okay, need password.
"USER2":"332", # Need account for login.
"PASS1":"230", # User logged in, proceed.
"PASS2":"530", # Not logged in.
"QUIT":"221",  # Service closing control connection.
"OKAY":"200",  # Command okay.
"FAIL":"500",  # Syntax error, command unrecognized.
"DNE" :"502",  # Command not implemented.
"DATA":"225",  # Data connection open; no transfer in progress.
"DATAQ":"226"
}

DATA_FLOW = {
    "IN": 1,
    "OUT": 2,
    "NONE": 3
}

Dest_PI_Port = 12341
Source_PI_Port = 12350

class FTP_Client_Interface(object):

    def __init__ (self):
        self.PI_Socket = Socket(getNetworkIp(), Source_PI_Port)
        self.PI_Socket.setDestAddress(("localhost",Dest_PI_Port))
        self.PI_Socket.Connect()
        self.Port = 12345 # The Client will always have two ports, so that the two sockets can run in parallel
        
        self.connectFlag = False
        self.usernameFlag = False
        self.loginFlag = False
        self.quitFlag = False
        self.portFlag = False
        self.transferFlag = False
        
        self.dataFlow = DATA_FLOW["NONE"]
        self.type = FTP_TYPE["ASCII Non-print"]
        self.mode = FTP_MODE["STREAM"]
        self.stru = FTP_STRU["FILE"]
        
    def FTP_Connect(self):
        self.connectFlag = True
        self.PI_Socket.setDestAddress(("localhost",Dest_PI_Port))
        self.PI_Socket.Connect()
        
    def FTP_Disconnect(self):
        self.PI_Socket.Disconnect()
        print "Closing Socket..."
    def FTP_Login(self):
        command = "USER"
        self.USER(command)
        command = "PASS"
        self.PASS(command)
        if self.loginFlag:
            return True
        else:
            return False
            
    def FTP_Close(self):
        self.connectFlag = True
        self.PI_Socket.setDestAddress(("localhost",Dest_PI_Port))
        self.PI_Socket.Connect()
        
    def USER (self, command):
        username = raw_input('Username: ' )
        self.PI_Socket.sendCommand(command, username)
        msg = self.PI_Socket.serverResponse()
        if msg[0:3] == FTP_SM["USER1"]:
            print "Username right\n"
            self.usernameFlag = True
        else:
            self.usernameFlag = False
    
    def PASS (self, command):
        count = 3
        while count>0:
            password = raw_input('Password: ' )
            if self.usernameFlag == False:
                self.QUIT("QUIT")
                print "Invalid Credentials..."
                return
			
            self.PI_Socket.sendCommand(command, password)
            msg = self.PI_Socket.serverResponse()
            if msg[0:3] == FTP_SM["PASS1"]:
                self.loginFlag = True
                print "Logged In"
                break
            else:
                count = count-1
                print "Attempts Left: "+ str(count)
        if count == 0:
            self.QUIT("QUIT")
    
    def PORT(self, command):
        if self.portFlag:
            newPort = raw_input('NewPort: ' )
            self.Port = int (newPort)
        else:
            newPort = int(newPort)
            newPort = self.Port
            
        ipstring = getNetworkIp()
        Host = socket.inet_aton(ipstring)
        
        p1 = int(newPort)/256
        p2 = int(newPort)%256
        print p1
        print p2
        p1 = chr(p1)
        p2 = chr(p2)
        NewAddress = Host[0] + ',' +Host[1] +','+ Host[2] +','+ Host[3] + ',' + p1+ ',' +p2
        self.PI_Socket.sendCommand(command, NewAddress)
        msg = self.PI_Socket.serverResponse()
        if msg[0:3] == FTP_SM["OKAY"]:
            self.portFlag = False
            self.transferFlag = True
        else:
            self.transferFlag = False
            
    def STOR(self, command):
        #setup data socket
        '''LocalAddress = getNetworkIp()
        self.PORT(self, "PORT")
        DataSocket = Socket(LocalAddress, self.Port)
        
        if self.transferFlag: 
            self.transferFlag= False # only one transfer at a time
            DataSocket.socket.listen(1)
            self.dataFlow = DATA_FLOW["IN"]
            File_Name = raw_input('File Name: ')
            TransmittedFile = open(os.getcwd()+'\\'+File_Name,'rb')
            self.PI_Socket.sendCommand(command, File_Name)
            msg = self.PI_Socket.serverReponse()
            if msg[0:3] == FTP_SM["DATA"]:
                DataSocket.sendData(TransmittedFile, ENCODING["ASCII Non-print"])
        else:
            self.NOOP() 
            
        msg = self.PI_Socket.serverResponse() # should be closed
        if msg[0:3] == FTP_SM["DATAQ"]:
            DataSocket.close()
        self.PI_Socket.dataFlow = DATA_FLOW["NONE"]'''
        return
        
    def RETR(self, command):
        '''LocalAddress = getNetworkIp()
        DataSocket = Socket(LocalAddress, self.Port)
        self.ServerMsg = self.PORT(self, "PORT")
        self.transferFlag = DATA_FLOW["IN"]
        
        FileTransferSocket = self.socket.accept()
        File_Name = raw_input('Enter File Name: ')
        Reply = FTPCommand('RETR',File_Name)
        print('Control connection reply: \n' + str(Reply))
        if Reply[0] != '5':
            return'''
            
        return
    def NOOP(self,command):
        self.PI_Socket.sendcommand(command)
        msg = serverReponse()
        return
        
    def QUIT (self, command):
        self.PI_Socket.sendCommand(command)
        msg = self.PI_Socket.serverResponse()
        print msg
        if msg[0:3] == FTP_SM["QUIT"]:
            print "Disconnected"
            self.loginFlag = False
            self.usernameFlag = False
            self.quitFlag = True
            self.connectFlag = False
            
    def CommandProcessor(self):
        # This function takes in 
        while not self.quitFlag:
            cmd = Input()
            print "CMD: "+cmd
            if FTP_COMMAND[cmd] == FTP_COMMAND["USER"]:
                self.ServerMsg = self.USER(cmd)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["PASS"]:
                self.ServerMsg = self.PASS(cmd)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["PORT"]:
                self.portFlag = True
                self.ServerMsg = self.PORT(cmd)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["STOR"]:
                self.ServerMsg = self.STOR(cmd)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["RETR"]:
                self.ServerMsg = self.RETR(cmd)
                continue
            elif FTP_COMMAND[cmd] == FTP_COMMAND["NOOP"]:
                self.ServerMsg = self.NOOP(cmd)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["QUIT"]:
                self.ServerMsg = self.QUIT(cmd)
                break
            
            else:
                print "command not implemented"
                
                self.ServerMsg == FTP_SM["DNE"]
                continue 
                
    def sendCommand(self, command, argument=''):
        Command = create_FTP_str(command,argument)
        print command
        self.PI_Socket.sendCommand(Command)
    
    def serverResponse(self):
        msg = self.PI_Socket.serverResponse()
        print msg
        return msg
 
def create_FTP_str(Command, Argument=''):
    if Argument == '':
        Command = str(Command) + '\r\n'
    else:
        Command = str(Command) + ' ' + str(Argument) + '\r\n'
    #print Command
    return Command
    
#-------------------------------------
#            Input(self)
#-------------------------------------
# out: list of strings (command, arg)
# -> Takes in the clients commandline
# -> Splits the commandLine
# -> Upper cases the command
#-------------------------------------
def Input(): 
    command = raw_input('CMD: ' )
    command = command.upper()
    return (command) 

#This function gets the local machines IP
def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
    
#print getNetworkIp()
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.connect(("localhost", 12345))
#p = PORT(12346)

#PORT1(p)    
# Port number = p1*256 + p2
# p1,p2
#  Reply with 200 to indicate success. Reply with 500 to indicate failure
#  Port numbers: 0 to 65535
'''
def PORT(self, newPort): #Port number must be > 1024
    
    start = Reply.find('')
    end = Reply.find('')
    Reply = Reply[start+1:end]
    Reply = Reply.split(',')
    Host = str(Reply[0]) + '.'+ str(Reply[1]) +'.'+ str(Reply[2]) +'.'+ str(Reply[3])
    Port = (int(Reply[4])*256) + int(Reply[5])
    print('New host Data Connection: \n' + str(Host))
    print('New port Data Connection:\n ' + str(Port))
    
    return Host,Port

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
'''

'''     TRANSFER MODE (MODE)

                       The argument is a single Telnet character code specifying
                       the data transfer modes described in the Section on
                       Transmission Modes.

                       The following codes are assigned for transfer modes:

                          S - Stream
                          B - Block
                          C - Compressed
            
            FILE STRUCTURE (STRU)

                      The argument is a single Telnet character code specifying
                      file structure described in the Section on Data
                      Representation and Storage.

                      The following codes are assigned for structure:

                         F - File (no record structure)
                         R - Record structure
                         P - Page structure
            
            REPRESENTATION TYPE (TYPE)

                        The argument specifies the representation type as described
                        in the Section on Data Representation and Storage.  Several
                        types take a second parameter.  The first parameter is
                        denoted by a single Telnet character, as is the second
                        Format parameter for ASCII and EBCDIC; the second parameter
                        for local byte is a decimal integer to indicate Bytesize.
                        The parameters are separated by a <SP> (Space, ASCII code
                        32).

                        The following codes are assigned for type:

                                     \    /
                           A - ASCII |    | N - Non-print
                                     |-><-| T - Telnet format effectors
                           E - EBCDIC|    | C - Carriage Control (ASA)
                                     /    \
                           I - Image

                           L <byte size> - Local byte Byte size
            
            '''