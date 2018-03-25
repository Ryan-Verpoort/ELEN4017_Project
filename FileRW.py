import socket



def ReadFromSocket(socket,File_Name,Encode_Type):
    
    File = open(File_Name,'wb')
    
    if(Encode_Type == "None"):
        ReceivedData = socket.recv(8192)
        while ReceivedData:
            #print "Receiving..."
            File.write(ReceivedData)
            ReceivedData = socket.recv(8192)
            
    else:
        ReceivedData = socket.recv(8192).decode(Encode_Type)
        while ReceivedData:
            File.write(ReceivedData)
            ReceivedData = socket.recv(8192).decode(Encode_Type)
            
    File.close()

def WriteToSocket(socket,File_Name,Encode_Type):
   
    File = open(str(File_Name),'rb')
  
    if(Encode_Type == "None"):
        Reading = File.read(8192)
        while (Reading):
            #print "Sending..."
            socket.send(Reading)
            Reading = File.read(8192)
            
    else:
        Reading = File.read(8192).encode(Encode_Type)
        while (Reading):
            socket.send(Reading)
            Reading = File.read(8192).encode(Encode_Type)
            
    File.close()