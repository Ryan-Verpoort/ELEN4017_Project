from FTP_Client0 import *
#PI_Port     = 21
#DTP_Port    = 12345

        
Client = FTP_Client_Interface()

def Login(Client):
    while True:
        login = Client.FTP_Login()
        if not login:
            Client = FTP_Client_Interface()
        else:
            break

def Reconnect(Client):
    Reconnect = raw_input("Reconnect: (Y/N)")
    if Reconnect == 'Y':
        return True
    else: 
        return False
        
while True:
    Login(Client)
    Client.CommandProcessor()
    Client.FTP_Disconnect()
    if Client.quitFlag and Reconnect(Client):
        NewClient = FTP_Client_Interface()
        Client = NewClient
    else:
        break
        
