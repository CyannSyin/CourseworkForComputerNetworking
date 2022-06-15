import tkinter as tk
from tkinter import *
from constant import *
from method import *
import re
import os
from tkinter import messagebox
from PIL import Image,ImageTk

class LoginPage:
    def __init__(self,window = None,sock = None):
        # username and password
        self.username = StringVar()
        self.password = StringVar()
        
        # initialize
        self.sock = sock
        self.window = window
        self.flag = None

        window.title('WcxChat')
        window.geometry('400x300')
        canvas = tk.Canvas(window,width=400,height=135,bg='white')
        img = Image.open('iniProfile.jpg')
        image_file = ImageTk.PhotoImage(img)
        image = canvas.create_image(200,10,anchor = 'n',image = image_file)

        canvas.pack(side = 'top')
        tk.Label(window,text = 'Welcome',font = ('Arial',16)).pack()

        tk.Label(window,text = 'User name:',font = ('Arial',14)).place(x=40,y=175)
        #tk.Label(window,text = 'Password:',font = ('Arial',14)).place(x=50,y=210)

        entry_usr_name = tk.Entry(window,textvariable = self.username,font=('Arial',14),show = None)
        entry_usr_name.place(x = 140, y = 175)

        #entry_usr_pwd = tk.Entry(window,textvariable = self.password,font = ('Arial',14),show = '*')
        #entry_usr_pwd.place(x=140,y=210)

        btn_login = tk.Button(window,text = 'Login',command = self.usr_login)
        btn_login.place(x=160,y=250)


        window.mainloop()


    def usr_login(self):
        user = self.username.get()
        #pwd  = self.password.get()

        if not user:
            messagebox.showerror('Error','Please check your username!')
            return

        print("Get username: (%s)"%(user))

        """
        Send LOGIN-INFORMATION 
             heaer + user
        """
        msg = str(LOGIN) + user
        send(self.sock, msg)

        try:
            data, _ = receive(self.sock)
        except:
            print("!! login error,")


        if data == str(LOGIN_SUCCESS):
            messagebox.showinfo('Info','Login success!')
            print("success")

            # !!! successful login ,set LOGIN.FLAG = USER
            self.flag = user
            self.window.destroy()
        elif data == str(LOGIN_DUPLICATE):
            messagebox.showerror('Error','Duplicated login!')
            self.username.set("")
            self.password.set("")

if __name__ == "__main__":
    page = LoginPage()
