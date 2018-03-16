import socket
import sys
# Class Containing all Client FTP commands 
''' TYPE - ASCII Non-print
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

FTP_COMMAND = {  
"USER": 1,            
"PASS": 2,
"QUIT": 3,        
}
FTP_SM = {
"USER1":"331", # User name okay, need password.
"USER2":"332", # Need account for login.
"PASS1":"230", # User logged in, proceed.
"PASS2":"530", # Not logged in.
"QUIT":"221",  # Service closing control connection.
}
#ControlSocket.send(Command.encode('UTF-8'))
#ServerReply = ControlSocket.recv(8192).decode('UTF-8')
PI_Port     = 12346 

class FTP_Client_Interface(object):

    def __init__ (self):
        self.PI_Socket         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerAddressPI   = ('localhost', PI_Port)
        self.PI_Socket.connect(self.ServerAddressPI)
        self.usernameFlag = False
        self.loginFlag = False
        self.quitFlag = False
        self.command = ''
        self.argument = ''
        
    def USER (self, command):
        username = raw_input('Username: ' )
        self.sendCommand(command, username)
        msg = self.serverResponse()
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
                print "Invalid Credentials..."
                return
			
            self.sendCommand(command, password)
            msg = self.serverResponse()
            if msg[0:3] == FTP_SM["PASS1"]:
                self.loginFlag = True
                print "Logged In"
                break
            else:
                count = count-1
                print "Attempts Left: "+ str(count)
        if count == 0:
            self.QUIT("QUIT")
            
    
    def QUIT (self, command):
        self.sendCommand(command)
        msg = self.serverResponse()
        print msg
        if msg[0:3] == FTP_SM["QUIT"]:
            print "Closing..."
            self.loginFlag = False
            self.usernameFlag = False
            self.quitFlag = True
            self.PI_Socket.close()
        
    def CommandProcessor(self):
        # This function takes in 
        while not self.quitFlag:
            #in = Input()
            cmd = Input()
            print "CMD: "+cmd
            if FTP_COMMAND[cmd] == FTP_COMMAND["USER"]:
                self.ServerMsg = self.USER(cmd)
                continue
                
            elif FTP_COMMAND[cmd] == FTP_COMMAND["PASS"]:
                self.ServerMsg = self.PASS(cmd)
                continue
            elif FTP_COMMAND[cmd] == FTP_COMMAND["QUIT"]:
                self.ServerMsg = self.QUIT(cmd)
                break
            
            else:
                print "command not implemented"
                continue 
                
    def sendCommand(self, command, argument=''):
        command = create_FTP_str(command,argument)
        #print command
        self.PI_Socket.sendall(command.encode('UTF-8'))
    
    def serverResponse(self):
        msg = self.PI_Socket.recv(8192).decode('UTF-8')
        print msg
        return msg
 
def create_FTP_str(Command, Argument=''):
    if Argument == '':
        Command = str(Command) + '\r\n'
    else:
        Command = str(Command) + ' ' + str(Argument) + '\r\n'
    #print Command
    return Command
    #ControlSocket.send(Command.encode('UTF-8'))
    #ServerReply = ControlSocket.recv(8192).decode('UTF-8')
    
#-------------------------------------
#            Input(self)
#-------------------------------------
# out: list of strings (command, arg)
# -> Takes in the clients commandline
# -> Upper cases the command
#-------------------------------------
def Input(): 
    command = raw_input('CMD: ' )
    command = command.upper()
    return (command) 

       
    ''''     TRANSFER MODE (MODE)

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