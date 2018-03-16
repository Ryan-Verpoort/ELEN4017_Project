#coding: utf-8
import socket
import sys
from FTP_Client0 import *
PI_Port     = 12346  

def Connect(FTP_Client_Interface):
    FTP_Client_Interface.PI_Socket.connect(self.ServerAddressPI)
    
def FTP_Login(FTP_Client_Interface):
    command = "USER"
    FTP_Client_Interface.USER(command)
    command = "PASS"
    FTP_Client_Interface.PASS(command)
    if FTP_Client_Interface.loginFlag:
        return True
    else:
        return False
    
        
Client = FTP_Client_Interface()
while True:
    login = FTP_Login(Client)
    if not login:
        Connect(Client)
    else:
        break

Client.CommandProcessor()

 




