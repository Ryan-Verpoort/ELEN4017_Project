from FTP_Client0 import *
#PI_Port     = 21
#DTP_Port    = 12345

        
Client = FTP_Client_Interface()
while True:
    login = Client.FTP_Login()
    if not login:
        Client = FTP_Client_Interface()
    else:
        break
        
while True:
   
    Client.CommandProcessor()
    if not Client.connectFlag:
        Reconnect = raw_input("Reconnect: (Y/N)")
    
    if Reconnect == 'Y':
        Client.FTP_Connect()
    else:
        Client.FTP_Disconnect()
        break
