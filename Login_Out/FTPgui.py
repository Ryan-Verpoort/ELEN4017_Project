from Tkinter import *
import math


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
        self.connectFlag = False
        self.loginFlag = False

    def createCanvas(self):

        #can1 = login screen
        self.can1 = Canvas(self.master, width=350, height=150, bg="grey")

        #can2 = server status
        self.can2 = Canvas(self.master, width=125, height=125, bg="grey")
        self.connectIndicator = self.can2.create_oval(10, 10, 30, 30, fill="red", width=0)
        self.loginIndicator   = self.can2.create_oval(10, 50, 30, 70, fill="red", width=0)
        self.ShowServerStatus1()

        #can3 = connect screen
        self.can3 = Canvas(self.master, width=200, height=100, bg="grey")
        self.ShowConnectUI()

        #can4 = disconnect screen
        self.can4 = Canvas(self.master, width=200, height=100, bg="grey")

    def ShowLoginUI(self):
        self.can1.place(x=5, y=190)

    def HideLoginUI(self):
        self.can1.place_forget()

    def ShowServerStatus1(self):
        self.can2.place(x=350, y=50)

    def ShowConnectUI(self):
        self.can3.place(x=10, y=50)

    def HideConnectUI(self):
        self.can3.place_forget()

    def ShowDisconnectUI(self):
        self.can4.place(x=10, y=50)

    def HideDisconnectUI(self):
        self.can4.place_forget()

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

    #create and place labels

        T1L  = Label(self.master, text=T1 , font=("Times", 30), justify=LEFT)
        T2L  = Label(self.can1, text=T2 , font=("Times", 20), justify=LEFT)
        T3L  = Label(self.can1, text=T3 , font=("Times", 20), justify=LEFT)
        T5L  = Label(self.can2, text=T5 , font=("Times", 15), justify=LEFT)
        T6L  = Label(self.can2, text=T6 , font=("Times", 15), justify=LEFT)
        T7L  = Label(self.master, text=T7 , font=("Times", 20), justify=LEFT)

        T1L.place(  x=10 , y=10)
        T2L.place(  x=10 , y=10)
        T3L.place(  x=10 , y=60)
        T5L.place(  x=40 , y=10)
        T6L.place(  x=40 , y=50)
        T7L.place(  x=350 , y=20)
   
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

    def LoginCommands(self):
        #must check to see if logged in successfully
        self.can2.itemconfig(self.loginIndicator,fill="green")
        if self.connectFlag == True:
            self.LoginFlag = True
            self.HideLoginUI()

    def ConnectCommands(self):
        #send command to server, receive server response, change color according to status
        self.can2.itemconfig(self.connectIndicator,fill="green")
        self.connectFlag = True
        self.ShowLoginUI()
        self.ShowDisconnectUI()
        self.HideConnectUI()

    def DisconnectCommands(self):
        self.can2.itemconfig(self.connectIndicator,fill="red")
        self.can2.itemconfig(self.loginIndicator,fill="red")
        self.HideDisconnectUI()
        self.HideLoginUI()
        self.ShowConnectUI()

    def bindButtons(self):
        self.LoginButton.config(command=self.LoginCommands)
        self.ConnectButton.config(command=self.ConnectCommands)
        self.DisconnectButton.config(command=self.DisconnectCommands)


root = Tk()
app= App(root)
root.mainloop()