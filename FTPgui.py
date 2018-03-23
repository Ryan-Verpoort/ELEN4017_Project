from Tkinter import *
from Client import *
import math
import os
import shutil

class App:
    
    def __init__(self, master):

        self.frame=Frame(master)
        self.frame.pack()
        self.master=master
        self.master.geometry("500x500")
        self.master.title("FTP GUI")
        self.createCanvas()
        self.createAllVisuals()
        self.bindButtons()
        self.client = Client()
        # self.connectCFlag = False
        # self.loginFlag = False
        
        
    def createCanvas(self):

        #can1 = login screen
        self.can1 = Canvas(self.master, width=350, height=150, bg="grey")

        #can2 = server status
        self.can2 = Canvas(self.master, width=125, height=100, bg="grey")
        self.connectIndicator   = self.can2.create_oval(10, 10, 30, 30, fill="red", width=0)
        self.loginIndicator     = self.can2.create_oval(10, 50, 30, 70, fill="red", width=0)
        self.ShowServerStatus1()

        #can3 = connect screen
        self.can3 = Canvas(self.master, width=200, height=100, bg="grey")
        self.ShowConnectUI()

        #can4 = disconnect screen
        self.can4 = Canvas(self.master, width=200, height=100, bg="grey")

        #can5 = client upload list from upload folder
        self.can5 = Canvas(self.master, width=150, height=200, bg="red")

        #can6 = server download list
        self.can6 = Canvas(self.master, width=150, height=200, bg="blue")

        #can7 = client commands
        self.can7 = Canvas(self.master, width=500, height=50, bg="red")
        self.ShowClientCommandsUI()

        #can8 = server replies
        self.can8 = Canvas(self.master, width=500, height=50, bg="blue")
        self.ShowServerRepliesUI()
        #self.can7.place(x=0,y=450)

    # can 1: Login
    def ShowLoginUI(self):
        self.can1.place(x=5, y=175)

    def HideLoginUI(self):
        self.can1.place_forget()

    # can 2: Server Status
    def ShowServerStatus1(self):
        self.can2.place(x=350, y=50)

    # can 3: Connect 
    def ShowConnectUI(self):
        self.can3.place(x=10, y=50)

    def HideConnectUI(self):
        self.can3.place_forget()

    # can 4: Disconnect
    def ShowDisconnectUI(self):
        self.can4.place(x=10, y=50)

    def HideDisconnectUI(self):
        self.can4.place_forget()

    # can 5: Upload UI
    def ShowUploadListUI(self):
        self.can5.place(x=10, y=175)
        self.UpdateUploadListUI()

    def HideUploadListUI(self):
        self.can5.place_forget()

    def UpdateUploadListUI(self):
        Text = "Client Files"
        self.uploadlist=[]
        self.uploadFiles= []
        UL  = Label(self.can5, text=Text, font=("Times", 15), justify=LEFT).grid(row=0,column=1, columnspan=3)
        scrollbar = Scrollbar(self.can5)
        scrollbar.grid(row=5,column=3, rowspan=5, sticky=N+S)
        self.uploadlist= Listbox(self.can5, height=5, yscrollcommand=scrollbar.set, width=20)
        self.uploadlist.grid(row=5,column=2,rowspan=5)
        scrollbar.config(command=self.uploadlist.yview)

        for filename in os.listdir(self.client.UserPath):
            if filename[0] == ".":
                continue
            x= str(filename)
            self.uploadlist.insert(END,x)
            self.uploadFiles.insert(-1,filename)

    def ShowDownloadListUI(self):
        self.can6.place(x=250,y=175)
        self.UpdateDownloadListUI()

    def HideDownloadListUI(self):
        self.can6.place_forget()

    def UpdateDownloadListUI(self):
        Text = "Server Files"
        DL  = Label(self.can6, text=Text, font=("Times", 15), justify=LEFT).grid(row=0,column=1, columnspan=3)
        scrollbar = Scrollbar(self.can6)
        scrollbar.grid(row=1,column=3, rowspan=5, sticky=N+S)
        self.downloadlist= []
        self.downloadlist= Listbox(self.can6, height=5,yscrollcommand=scrollbar.set, width=20)
        self.downloadlist.grid(row=1,column=2,rowspan=5)
        scrollbar.config(command=self.downloadlist.yview)
        
        self.client.passiveMode()
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
        serverList = self.client.FileDirectory()
       
        for filename in serverList:
            if str(filename)[0:1] == "." or str(filename)=="":
                continue
            x = str(filename)
            self.downloadlist.insert(END,x)
            
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
    #can 7 
    def ShowClientCommandsUI(self):
        self.can7.place(x=0,y=375)
        Text = "Client -> Server Commands"
        CC  = Label(self.can7, text=Text, font=("Times", 15), justify=LEFT).grid(row=0,column=0, columnspan=3)
        scrollbar = Scrollbar(self.can7)
        scrollbar.grid(row=1,column=3, rowspan=2, sticky=N+S)
        self.clientCommandsList= []
        self.clientCommandsList= Listbox(self.can7, height=2, yscrollcommand=scrollbar.set, width=50)
        self.clientCommandsList.grid(row=1,column=2,rowspan=2)
        scrollbar.config(command=self.clientCommandsList.yview)
        self.clientCommandsList.see(END)

    #can8
    def ShowServerRepliesUI(self):
        self.can8.place(x=0,y=430)
        Text = "Server -> Client Replies"
        CC  = Label(self.can8, text=Text, font=("Times", 15), justify=LEFT).grid(row=0,column=0, columnspan=3)
        scrollbar = Scrollbar(self.can8)
        scrollbar.grid(row=1,column=3, rowspan=2, sticky=N+S)
        self.serverRepliesList= []
        self.serverRepliesList= Listbox(self.can8, height=2, yscrollcommand=scrollbar.set, width=50)
        self.serverRepliesList.grid(row=1,column=2,rowspan=2)
        scrollbar.config(command=self.serverRepliesList.yview)
        self.serverRepliesList.see(END)

    def createAllVisuals(self):

    #create text
        T1 = "FTP"
        T2 = "Username"
        T3 = "Password"
        T4 = "Login"
        T5 = "Connection"
        T6 = "Login"
        T7 = "Server Status"
        T8 = "Connect"
        T9 = "Disconnect"
        #T10 = "Connection D"
        T11 = "Upload item"
        T12 = "Update"
        T13 = "Download item"
        T14 = "Delete item"

    #create and place labels
        T1L  = Label(self.master, text=T1 , font=("Times", 30), justify=LEFT)
        T2L  = Label(self.can1, text=T2 , font=("Times", 20), justify=LEFT)
        T3L  = Label(self.can1, text=T3 , font=("Times", 20), justify=LEFT)
        T5L  = Label(self.can2, text=T5 , font=("Times", 15), justify=LEFT)
        T6L  = Label(self.can2, text=T6 , font=("Times", 15), justify=LEFT)
        T7L  = Label(self.master, text=T7 , font=("Times", 20), justify=LEFT)
        #T10L  = Label(self.can2, text=T10, font=("Times", 15), justify=LEFT)

        T1L.place(  x=10 , y=10)
        T2L.place(  x=10 , y=10)
        T3L.place(  x=10 , y=60)
        T5L.place(  x=40 , y=10)
        T6L.place(  x=40 , y=50)
        T7L.place(  x=350, y=20)
        #T10L.place( x=40 , y=90)
   
    #create entry fields for username and password
        self.username=Entry(self.can1, width=20, font=("Times", 20))
        self.username.insert(5,'')
        self.username.place(x=110,y=10)
       
        self.passphrase=Entry(self.can1,width=20, font=("Times", 20))
        self.passphrase.insert(5,'')
        self.passphrase.place(x=110,y=60)
      
        self.LoginButton=Button(self.can1, text=T4, width=15, font=("Times", 20))
        self.LoginButton.place(x=110,y=110)

        self.ConnectButton=Button(self.can3, text=T8, width=10, font=("Times", 20))
        self.ConnectButton.place(x=0,y=0)

        self.DisconnectButton=Button(self.can4, text=T9, width=10, font=("Times", 20))
        self.DisconnectButton.place(x=0,y=0)

        self.UploadButton=Button(self.can5, text=T11, width=10, font=("Times", 15))
        self.UploadButton.grid(row=10,column=1,columnspan=3)

        self.UpdateUploadButton=Button(self.can5, text=T12, width=10, font=("Times", 15))
        self.UpdateUploadButton.grid(row=11,column=1,columnspan=3)

        self.DeleteUploadButton=Button(self.can5, text=T14, width=10, font=("Times", 15))
        self.DeleteUploadButton.grid(row=12,column=1,columnspan=3)

        # DELETE, DOWNLOAD, UPDATE server stuff
        self.DownloadButton=Button(self.can6, text=T13, width=13, font=("Times", 15))
        self.DownloadButton.grid(row=10,column=1,columnspan=3)

        self.DeleteDownloadButton=Button(self.can6, text=T14, width=13, font=("Times", 15))
        self.DeleteDownloadButton.grid(row=11,column=1,columnspan=3)

        self.UpdateDownloadButton=Button(self.can6, text=T12, width=10, font=("Times", 15))
        self.UpdateDownloadButton.grid(row=12,column=1,columnspan=3)


    def ConnectCommands(self):
        #send command to server, receive server response, change color according to status
        if not self.client.ControlConnectionFlag:
            self.can2.itemconfig(self.connectIndicator,fill="green")
            self.ShowLoginUI()
            self.ShowDisconnectUI()
            self.HideConnectUI()
            self.client.Connect()
            #self.addServerReplyText(self.Client.ServerMsg)
        #self.addServerReplyText("Connecting you to the server ... ")

    def DisconnectCommands(self):
        if self.client.ControlConnectionFlag:
            self.can2.itemconfig(self.connectIndicator,fill="red")
            self.can2.itemconfig(self.loginIndicator,fill="red")
            self.HideDisconnectUI()
            self.HideLoginUI()
            self.HideUploadListUI()
            self.HideDownloadListUI()
            self.ShowConnectUI()
            self.client.Disconnect()
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
    
    def LoginCommands(self):
        # must check to see if logged in successfully
        
        if self.client.ControlConnectionFlag:
            self.Login()
            if self.client.LoginFlag:
                self.can2.itemconfig(self.loginIndicator,fill="green")
                self.HideLoginUI()
                self.ShowUploadListUI()
                self.ShowDownloadListUI()
        
    def Login(self):    
        u=self.username.get()
        p=self.passphrase.get()
          
        self.client.USER(u)
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
        self.client.PASS(p)
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
        self.username.delete(0,END)
        self.passphrase.delete(0,END)
        
    def UploadCommands(self):
        try:
            file = str(self.uploadlist.get(self.uploadlist.curselection()))
            print "Uploading " +name
            # Set Type
            self.client.DataType(findType(getEncoding(file)))
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # Set Data Conn
            self.client.passiveMode()
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # Upload File
            self.client.TransmitFile(file)
            print "Uploading: " + str(file)
            # send + receive msg
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
        except:
            print "No item selected."

    def DownloadCommands(self):
        
        try:
            name =str(self.downloadlist.get(self.downloadlist.curselection()))
            print "Downloading " +name
            # Set Type
            self.client.DataType(findType(name))
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # Set Data Conn
            self.client.passiveMode()
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # Download File
            self.client.ReceiveFile(name)
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # os.system("cp DownloadFolder/"+str(name)+" UploadFolder") #hacks
        except:
            print "No item selected."

    #send command to server, then getNewList
    #mimic = delete, then update
    def ServerDeleteCommands(self):
        
        try:
            name = str(self.downloadlist.get(self.downloadlist.curselection()))
            client.RemoveDirectory(name)
            print "Deleted file from: " +str(name)
            self.UpdateDownloadListUI()
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
        except:
            print "No selected item." 

    def ServerAddDirCommands(self):
        try:
            name = "DownloadFolder/"+str(self.downloadlist.get(self.downloadlist.curselection()))
            os.remove(name)
            print "Deleted file from: " +str(name)
            self.UpdateDownloadListUI()
            self.addClientCommandText("Delete the selected file yo")

            self.addServerReplyText("Deleted the selected file :D")
        except:
            print "No selected item." 
        
    #If client wants to delete their own folders for convience
    def UploadDeleteCommands(self):
        try:
            name = self.client.UserPath+str(self.uploadlist.get(self.uploadlist.curselection()))
            os.remove(name)
            print "Deleted file from: " +str(name)
        except:
            print "No selected item."
        self.UpdateUploadListUI() 

    def bindButtons(self):
        self.LoginButton.config(command=self.LoginCommands)
        self.ConnectButton.config(command=self.ConnectCommands)
        self.DisconnectButton.config(command=self.DisconnectCommands)
        self.UpdateUploadButton.config(command=self.UpdateUploadListUI)
        self.UploadButton.config(command=self.UploadCommands)
        self.DownloadButton.config(command=self.DownloadCommands)
        self.DeleteDownloadButton.config(command=self.ServerDeleteCommands)
        self.UpdateDownloadButton.config(command=self.UpdateDownloadListUI)
        self.DeleteUploadButton.config(command=self.UploadDeleteCommands)

    def addClientCommandText(self, text):
        self.clientCommandsList.insert(END, text)
        self.clientCommandsList.see(END)

    def addServerReplyText(self,text):
        self.serverRepliesList.insert(END, text)
        self.serverRepliesList.see(END)


root = Tk()
app= App(root)
root.mainloop()