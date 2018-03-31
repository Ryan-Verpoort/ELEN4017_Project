from Tkinter import *
from Client import *
import math
import time
import os
import shutil
import tkSimpleDialog
import tkMessageBox
from PIL import Image, ImageTk

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# class App
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# This class is responsible for the presentation of the FTP client and also processing of some data
# that it may receive from the client to display to the user
#
# It uses the methods and flags in the Client class to create functionality
# and displays the correlating state to the user
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

class App:
    
    def __init__(self, master):

        self.frame=Frame(master)
        self.frame.pack()
        self.master=master

        self.master.resizable(width=False, height=False)
        self.master.geometry("500x500")
        self.master.title("FTP GUI")
        self.createCanvas()
        self.createAllVisuals()
        self.bindButtons()
        self.client = Client()
        self.cwd = ""
    
    # Setup visuals
    def createCanvas(self):
        #background
        image2 = Image.open('background.jpg')
        image1 = ImageTk.PhotoImage(image2)
        self.panel1 = Label(root, image=image1)
        self.panel1.pack(side='top', fill='both', expand='yes')
        self.panel1.image = image1
        
        #can1 = login screen
        self.can1 = Canvas(self.panel1, width=350, height=150, bg="black",borderwidth=0, highlightthickness=0)

        #can2 = server status
        self.can2 = Canvas(self.panel1, width=125, height=110, bg="black",borderwidth=0, highlightthickness=0)
        self.connectIndicator   = self.can2.create_oval(10, 10, 30, 30, fill="red", width=0)
        self.loginIndicator     = self.can2.create_oval(10, 50, 30, 70, fill="red", width=0)
        self.dataIndicator     = self.can2.create_oval(10, 90, 30, 110, fill="red", width=0)
        self.ShowServerStatus1()

        #can3 = connect screen
        self.can3 = Canvas(self.panel1, width=120, height=50, bg="black", borderwidth=0, highlightthickness=0)
        self.ShowConnectUI()

        #can4 = disconnect screen
        self.can4 = Canvas(self.panel1, width=120, height=50, bg="black",borderwidth=0, highlightthickness=0)

        #can5 = client upload list from upload folder
        self.can5 = Canvas(self.panel1, width=220, height=200, bg="black",borderwidth=0, highlightthickness=5)
        self.can5.config(highlightbackground='OrangeRed2')

        #can6 = server download list
        self.can6 = Canvas(self.panel1, width=165, height=200, bg="black",borderwidth=0, highlightthickness=5)
        self.can6.config(highlightbackground='purple1')
        
        #can7 = client commands
        self.can7 = Canvas(self.panel1, width=500, height=50, bg="OrangeRed2")
        self.ShowClientCommandsUI()

        #can8 = server replies
        self.can8 = Canvas(self.panel1, width=500, height=50, bg="purple1")
        self.ShowServerRepliesUI()
        #self.can7.place(x=0,y=450)
        
    # Control for visuals
    def HideBackground(self):
        self.bground.place_forget()
        
    def ShowBackground(self):
        self.bground.pack(expand=True, fill=BOTH)
        
    # can 1: Login
    def ShowLoginUI(self):
        self.can1.place(x=5, y=175)

    def HideLoginUI(self):
        self.can1.place_forget()

    # can 2: Server Status
    def ShowServerStatus1(self):
        self.can2.place(x=350, y=50)
        
    def HideServerStatus1(self):
        self.can2.place_forget()

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
        self.can5.place(x=15, y=175)
        self.UpdateUploadListUI()

    def HideUploadListUI(self):
        self.can5.place_forget()

    def UpdateUploadListUI(self):
        Text = "Client Files"
        self.uploadlist=[]
        self.uploadFiles= []
        UL  = Label(self.can5, text=Text, font=("Times", 15), bg='OrangeRed2',justify=LEFT).grid(row=0,column=1, columnspan=3)
        scrollbar = Scrollbar(self.can5)
        scrollbar.grid(row=5,column=3, rowspan=5, sticky=N+S)
        self.uploadlist= Listbox(self.can5, height=5, yscrollcommand=scrollbar.set, width=20)
        self.uploadlist.config(bg='black', fg='white')
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
        DL  = Label(self.can6, text=Text, font=("Times", 15),bg='purple1', justify=LEFT).grid(row=0,column=1, columnspan=3)
        #CWD = Label(self.can6, text=self.cwd, font=("Times", 15),bg='purple1', justify=RIGHT).grid(row=0,column=1, columnspan=3)
        scrollbar = Scrollbar(self.can6)
        scrollbar.grid(row=1,column=3, rowspan=5, sticky=N+S)
        self.downloadlist= []
        self.downloadlist= Listbox(self.can6, height=5,yscrollcommand=scrollbar.set, width=20)
        self.downloadlist.config(bg='black', fg='white')
        self.downloadlist.grid(row=1,column=2,rowspan=5)
        scrollbar.config(command=self.downloadlist.yview)
        
        # setup connection
        self.client.passiveMode()
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        serverList = self.client.FileDirectory()
       
        #print "List"
        for filename in serverList:
            #need to look for : and then go three spaces forward
            x = str(filename)
            #print x
            pos = x.find(':')
            x = x.replace("\\","")
            if pos > -1:
                x=x[pos+4:len(filename)-1]
            else:
                x=x[0:len(filename)]
            print x
            
            self.downloadlist.insert(END,x)
            
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
    #can 7 
    def ShowClientCommandsUI(self):
        self.can7.place(x=15,y=370)
        self.can7.config(highlightbackground="OrangeRed2")
        Text = "Client -> Server Commands"
        CC  = Label(self.can7, text=Text, font="Times 15 bold",bg='OrangeRed2', justify=LEFT).grid(row=0,column=0, columnspan=3)
        scrollbar = Scrollbar(self.can7)
        scrollbar.grid(row=1,column=3, rowspan=2, sticky=N+S)
        self.clientCommandsList= []
        self.clientCommandsList= Listbox(self.can7, height=2, yscrollcommand=scrollbar.set, width=50)
        self.clientCommandsList.config(bg='black', fg='white')
        self.clientCommandsList.grid(row=1,column=2,rowspan=2)
        scrollbar.config(command=self.clientCommandsList.yview)
        self.clientCommandsList.see(END)

    #can8
    def ShowServerRepliesUI(self):
        self.can8.place(x=15,y=430)
        self.can8.config(highlightbackground="purple1")
        Text = "Server -> Client Replies"
        CC  = Label(self.can8, text=Text, font="Times 15 bold", justify=LEFT,bg='purple1').grid(row=0,column=0, columnspan=3,)
        scrollbar = Scrollbar(self.can8)
        scrollbar.grid(row=1,column=3, rowspan=2, sticky=N+S)
        self.serverRepliesList= []
        self.serverRepliesList= Listbox(self.can8, height=2, yscrollcommand=scrollbar.set, width=50)
        self.serverRepliesList.config(bg='black', fg='white')
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
        T15 = "Transfer"

    #create and place labels
        T1L  = Label(self.panel1, text=T1 , font=("Times", 30), justify=LEFT,fg='white',bg='black')
        T2L  = Label(self.can1, text=T2 , font=("Times", 20), justify=LEFT,fg='white',bg='black')
        T3L  = Label(self.can1, text=T3 , font=("Times", 20), justify=LEFT,fg='white',bg='black')
        T5L  = Label(self.can2, text=T5 , font=("Times", 15), justify=LEFT,fg='white',bg='black')
        T6L  = Label(self.can2, text=T6 , font=("Times", 15), justify=LEFT,fg='white',bg='black')
        T7L  = Label(self.panel1, text=T7 , font=("Times", 20), justify=LEFT, fg='white',bg='black')
        T15L = Label(self.can2, text=T15 , font=("Times", 15), justify=LEFT,fg='white',bg='black')
        #T10L  = Label(self.can2, text=T10, font=("Times", 15), justify=LEFT)

        T1L.place(  x=200 , y=10)
        T2L.place(  x=10 , y=10)
        T3L.place(  x=10 , y=60)
        T5L.place(  x=40 , y=10)
        T6L.place(  x=40 , y=50)
        T7L.place(  x=350, y=20)
        #T10L.place( x=40 , y=90)
        T15L.place( x=40 , y=90)
   
        # create entry fields for username and password
        self.username=Entry(self.can1, width=20, font=("Times", 20))
        self.username.insert(5,'')
        self.username.place(x=110,y=10)
       
        self.passphrase=Entry(self.can1,width=20, font=("Times", 20))
        self.passphrase.insert(5,'')
        self.passphrase.place(x=110,y=60)
         
        # create buttons
        self.LoginButton=Button(self.can1,text=T4, width=15, font=("Times", 20))
        self.LoginButton.config(highlightbackground='black')
        self.LoginButton.place(x=110,y=110)

        self.ConnectButton=Button(self.can3, width=10,font=("Times", 20))
        self.ConnectButton.config(text=T8, highlightbackground='black')

        self.ConnectButton.place(x=0,y=0)
        

        self.DisconnectButton=Button(self.can4, text=T9, width=10, font=("Times", 20))
        self.DisconnectButton.config(highlightbackground='black')
        self.DisconnectButton.place(x=0,y=0)

        self.UploadButton=Button(self.can5, text=T11, width=10, font=("Times", 15))
        self.UploadButton.config(highlightbackground='OrangeRed2')
        self.UploadButton.grid(row=10,column=1,columnspan=3)

        self.UpdateUploadButton=Button(self.can5, text=T12, width=10, font=("Times", 15))
        self.UpdateUploadButton.config(highlightbackground='OrangeRed2')
        self.UpdateUploadButton.grid(row=11,column=1,columnspan=3)

        self.DeleteUploadButton=Button(self.can5, text=T14, width=10, font=("Times", 15))
        self.DeleteUploadButton.config(highlightbackground='OrangeRed2')
        self.DeleteUploadButton.grid(row=12,column=1,columnspan=3)

        # DELETE, DOWNLOAD, UPDATE server stuff
        self.DownloadButton=Button(self.can6, text=T13, width=13, font=("Times", 15))
        self.DownloadButton.config(highlightbackground='purple1')
        self.DownloadButton.grid(row=10,column=1,columnspan=3)

        self.DeleteDownloadButton=Button(self.can6, text=T14, width=13, font=("Times", 15))
        self.DeleteDownloadButton.config(highlightbackground='purple1')
        self.DeleteDownloadButton.grid(row=11,column=1,columnspan=3)

        self.UpdateDownloadButton=Button(self.can6, text=T12, width=13, font=("Times", 15))
        self.UpdateDownloadButton.config(highlightbackground='purple1')
        self.UpdateDownloadButton.grid(row=12,column=1,columnspan=3)
        
        self.FolderChangeButtonServer=Button(self.can6, text=">", width=1, font=("Times", 15))
        self.FolderChangeButtonServer.config(highlightbackground='purple1')
        self.FolderChangeButtonServer.grid(row=10,column=4)
        
        self.HomeButtonServer=Button(self.can6, text="H", width=1, font=("Times", 15))
        self.HomeButtonServer.config(highlightbackground='purple1')
        self.HomeButtonServer.grid(row=11,column=4)
        
        self.AddFolderButton=Button(self.can6, text="+", width=1, font=("Times", 15))
        self.AddFolderButton.config(highlightbackground='purple1')
        self.AddFolderButton.grid(row=12,column=4)
        
        self.HelpButton = Button(self.panel1, text="?", width=1, font= ("Time", 15))
        self.HelpButton.config(highlightbackground='black')
        self.HelpButton.place(x=10,y=20)

    # functions from client are assigned to appropriate methods using procedures
    def ConnectCommands(self):
        #send command to server, receive server response, change color according to status
        self.client.Connect()
        self.addServerReplyText(self.client.server_reply)
        self.ConnectedScreen()

    def DisconnectCommands(self):
        if self.client.ControlConnectionFlag:
            self.client.Disconnect()
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            self.DisconnectedScreen()
    
    def LoginCommands(self):
        # must check to see if logged in successfully
        if self.client.ControlConnectionFlag:
            self.Login()
            #self.cwd = self.client.getCWD()
            self.LoggedScreen()
        
    def Login(self):    
        u=self.username.get()
        p=self.passphrase.get()
          
        self.client.USER(u)
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
        self.client.PASS(p)
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
        self.client.Authenticate()
        self.username.delete(0,END)
        self.passphrase.delete(0,END)

        
    def UploadCommands(self, event):
        file = str(self.uploadlist.get(self.uploadlist.curselection()))
        # Set Type
        self.client.DataType(getType(file))
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        # Set Data Conn
        self.client.passiveMode()
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        # Upload File
        self.client.Transmit_File(file)
        print "Uploading: " + str(file)
        # send + receive msg
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        
        print "Turn it RED"
        self.mode3()
        self.UpdateDownloadListUI()
        
    def DownloadCommands(self,event):
        name = str(self.downloadlist.get(self.downloadlist.curselection()))
        isfile = isFile(name)
        if isfile:
            print "Downloading " + name
            # Set Type
            self.client.DataType(getType(name))
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # Set Data Conn
            self.client.passiveMode()
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            # Download File
            self.client.Receive_File(name)
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            
        self.mode3()
        self.UpdateUploadListUI()
            

    def ServerDeleteCommands(self):
        
        ## try to delete file ##
        name = str(self.downloadlist.get(self.downloadlist.curselection()))
        Removed = False
        print name
        
        isfile = isFile(name)
        name = "\\"+name+"\\"
        if isfile:
            self.client.DeleteFile(name)
            Removed = True
            print "Deleted file: " +str(name)
        else:
            self.client.RemoveDirectory(name)
            Removed = True
            print "Deleted folder:" +str(name) 
             
        if Removed == True:
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            self.UpdateDownloadListUI()
    
    def ServerAddDirCommands(self):
        folder=tkSimpleDialog.askstring("Add Directory", "Name of new folder?")
        self.client.MakeDirectory(folder)
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        self.UpdateDownloadListUI()
        
    #If client wants to delete their own folders for convience
    def UploadDeleteCommands(self):
        try:
            File_Name = str(self.uploadlist.get(self.uploadlist.curselection()))
            name = os.path.abspath(os.path.join(os.path.sep,self.client.UserPath,File_Name))
            print name
            os.remove(name)
            self.UpdateUploadListUI()  
            print "Deleted file from: " +str(name)
        except:
            print "No selected item."
    
    def CHDirCommands(self):
        #cwd, list
        name = str(self.downloadlist.get(self.downloadlist.curselection()))
        name = "\\"+name+"\\"
        if not isFile(name):
            self.client.ChangeDirectory(name)
            self.addClientCommandText(self.client.command)
            self.addServerReplyText(self.client.server_reply)
            #self.cwd = self.client.getCWD()
            self.UpdateDownloadListUI()
        
        
    def HomeDirCommands(self):
        self.client.ParentDirectory()
        self.addClientCommandText(self.client.command)
        self.addServerReplyText(self.client.server_reply)
        #self.cwd = self.client.getCWD()
        self.UpdateDownloadListUI()
    
    def Help(self):
        if self.client.ControlConnectionFlag:
            self.client.GetHelp()
            tkMessageBox.showinfo("Server Commands", self.client.server_reply)
    
    def bindButtons(self):
        self.LoginButton.config(command=self.LoginCommands)
        self.ConnectButton.config(command=self.ConnectCommands)
        self.DisconnectButton.config(command=self.DisconnectCommands)
        self.UploadButton.bind('<ButtonPress-1>',self.mode4)
        self.UploadButton.bind('<ButtonRelease-1>',self.UploadCommands)
        self.DownloadButton.bind('<ButtonPress-1>',self.mode4)
        self.DownloadButton.bind('<ButtonRelease-1>',self.DownloadCommands)
        self.DeleteDownloadButton.config(command=self.ServerDeleteCommands)
        self.UpdateDownloadButton.config(command=self.UpdateDownloadListUI)
        self.DeleteUploadButton.config(command=self.UploadDeleteCommands)
        self.AddFolderButton.config(command=self.ServerAddDirCommands)
        self.FolderChangeButtonServer.config(command=self.CHDirCommands)
        self.HomeButtonServer.config(command=self.HomeDirCommands)
        self.HelpButton.config(command=self.Help)
    
    def addClientCommandText(self, text):
        self.clientCommandsList.insert(END, text)
        self.clientCommandsList.see(END)

    def addServerReplyText(self,text):
        self.serverRepliesList.insert(END, text)
        self.serverRepliesList.see(END)
    
    #disconnected mode
    def mode1(self):
        self.can2.itemconfigure(self.connectIndicator ,fill="red")
        self.can2.itemconfig(self.loginIndicator ,fill="red")
        self.can2.itemconfig(self.dataIndicator ,fill="red")
    #connected mode
    def mode2(self):
        self.can2.itemconfig(self.connectIndicator ,fill="green")
        self.can2.itemconfig(self.loginIndicator ,fill="red")
        self.can2.itemconfig(self.dataIndicator ,fill="red")
    #logged in mode
    def mode3(self):
        print "Mode 3"
        self.can2.itemconfigure(self.connectIndicator ,fill="green")
        self.can2.itemconfigure(self.loginIndicator ,fill="green")
        self.can2.itemconfigure(self.dataIndicator ,fill="red")
        self.panel1.update_idletasks()
    #transfering data
    def mode4(self,event):
        print "Mode 4"
        # can 2: Server Status
        self.can2.itemconfig(self.connectIndicator ,fill="green")
        self.can2.itemconfig(self.loginIndicator ,fill="green")
        self.can2.itemconfig(self.dataIndicator ,fill="green")
        self.panel1.update_idletasks()
    
    # methods that control what can be seen by the user
    # for different states
    def DisconnectedScreen(self):
        if not self.client.ControlConnectionFlag:
            print "DC..."
            self.mode1()
            self.HideDisconnectUI()
            self.HideLoginUI()
            self.HideUploadListUI()
            self.HideDownloadListUI()
            self.ShowConnectUI()
            
    def ConnectedScreen(self):
        if self.client.ControlConnectionFlag:
            print "C..."
            self.mode2()
            self.ShowDisconnectUI()
            self.HideConnectUI()
            self.ShowLoginUI()
    
    def LoggedScreen(self):
        if self.client.LoginFlag:
            print "L..."
            self.mode3()
            self.HideLoginUI()
            self.ShowUploadListUI()
            self.ShowDownloadListUI()
            

def isFile(name):
    for char in name:
        if char == ".":
            return True
    return False
    
folder = ""
root = Tk()
app= App(root)
root.mainloop()