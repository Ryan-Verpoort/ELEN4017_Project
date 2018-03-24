import socket

def WriteToSocket(socket,File_Name,Encode_Type):
    File = open(File_Name,'rb')
    
    Reading = File.read(8192)
    if(Encode_Type == "None"):
        
        while (Reading):
            self.DataSocket.send(Reading)
            Reading = File.read(8192)
            
    else:
        Reading = File.read(8192).encode(Encode_Type)
        while (Reading):
            self.DataSocket.send(Reading)
            Reading = File.read(8192).encode(Encode_Type)

    File.close()



def ReadFromSocket(socket,File_Name,Encode_Type):
    File = open(File_Name,'wb')
    ReceivedData = socket.recv(8192)
    
    if(Encode_Type == "None"):
    
        while ReceivedData:
            File.write(ReceivedData)
            ReceivedData = socket.recv(8192)
            
    else:
        ReceivedData = socket.recv(8192).decode(Encode_Type)
        while ReceivedData:
            File.write(ReceivedData)
            ReceivedData = socket.recv(8192).decode(Encode_Type)
            
    File.close()