import socket
import select
import sys

import tkinter as tk
#from tkinter import *
import tkinter.messagebox
#from PIL import Image,ImageTk
import PIL.Image
import PIL.ImageTk
from tkinter import filedialog

from LoginPage import *
from PrivateChatPage import *
import _thread
import time
import os
import method

HOST = "127.0.0.1"
PORT = 65435
User = None
user2room = {}
#user2room_history = {}
groups = []

def get_users(sock,user):
    header = str(GET_ALL_USERS)

    method.send(sock,header)

    try:
        data, rest = method.receive(sock)
    except Exception as e:
        messagebox.showerror('Error','Get users error!')
        return None

    state = data
    if state == str(GET_SUCCESS):
        #rest = rest.decode("utf-8")
        users = rest.split("\r\n")
        print("find users: ")
        for user in users:
            print(user)
        return users
def show_msg(sender,msg,color,is_file = False,msg_time = None):
    if msg_time == None:
        msg_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

    text_recv.config(state = NORMAL)
    text_recv.see(END)

    text_recv.insert('end',"{0} {1} \n".format(sender,msg_time),color)

    if is_file == False :
        text_recv.insert('end','{0} \n'.format(msg))

    text_recv.see('end')
    text_recv.config(state = DISABLED)


def send_message():
    text = input_text.get('0.0','end')
    header = str(SEND_MESSAGE) + "\r\n" + str(len(text))

    if text is None:
        return
    try:
        send_text = text.encode("utf-8")
        method.send(sock,header,send_text)
        show_msg('<Me>',text,'blue',is_file = False)
    except Exception as e:
        messagebox.showerror('Error','Sending message error!')
        print('send msg error,',e)

    input_text.delete('0.0','end')

def room_exists(room):
    if room is None:
        return False
    if int(room.master.winfo_exists())==0:
        return False
    return True


def private_chat(event):
    choice = friend_list.get(friend_list.curselection())
    if choice == User:
        return
    if room_exists(user2room.get(choice))==False:
        # init - get chat history

        user2room[choice] = PrivateChatPage(window,User,choice,sock,user2room_history)

#def create_group():
#    win_ = Toplevel()
#    win_.title("Create NewGroup")
#    win_.geometry("300x200")

#    tk.Label(win_, text='Group name:', font=('Arial', 14)).place(x=10, y=40)
#    #entry_group_name = tk.Entry(win_, textvariable=, font=('Arial', 12))
#    #entry_group_name.place(x=90, y=40)

#    create_button = tk.Button(win_, text='Create', font=('Arial', 12), width=10, height=2, command=send_add_friend_request)
#    create_button.place(x=80, y=80)


def listener(sock,root):
    print("?? then ??")
    listen_this = [sock]

    while True:
        reads, writes, errors = select.select(listen_this,[],[])

        for master in reads:
            if master == sock:
                try:
                    data, rest = method.receive(master)
                    print(data,rest)
                    print("--- check which step is in ---")
                    print(data[:3])

                except Exception as e:
                    print("receiver error :",e)
                    #messagebox.showerror('Error','Receive Error!{0}'.format(e))
                    continue

                if len(data)==0:
                    print("receive wrong data: len==0")
                    continue
                try:
                    msg_type = data[:3]
                    print("check msg_tpye",msg_type)
                    if msg_type == str(LOGIN_USERNAME):
                        ## new user login in
                        new_user = rest
                        #new_user = rest.decode("utf-8")
                        hinter = new_user + " login!"
                        show_msg('<System>', hinter, 'red', is_file=False)
                        friend_list.insert('end',new_user)
                        users.append(new_user)
                        #SEND_MESSAGE_ALL
                    elif msg_type == str(SEND_MESSAGE_ALL):
                        print("get this step")
                        try:
                            data_ = data[3:]
                            sender, length = data_.split("\r\n")
                        except Exception as e:
                            messagebox.showerror('Error','Receive message error!')
                        show_msg(sender,rest,'green')

                    elif msg_type == str(LOGOUT_INFO):
                        logout_user = rest
                        hinter = logout_user + " log out!"
                        show_msg('<System>', hinter, 'red')
                        friend_list.delete(users.index(logout_user))
                        users.remove(logout_user)

                    elif msg_type == str(SEND_MESSAGE_PER_STORE):
                        messagebox.showinfo('Info',rest+" is offline, message is cached!")

                    elif msg_type == str(SEND_MESSAGE_PER):
                        try :
                            sender, text = rest.split("\r\n")

                        except Exception as e:
                            print("split SEND_MESSAGE_PER error: ",e)


                        if room_exists(user2room.get(sender)):
                            user2room[sender].show_msg(sender,text,'green')
                        else:
                            user2room[sender] = PrivateChatPage(window,User,sender,sock,user2room_history)
                            user2room[sender].show_msg(sender,text,'green')

                except Exception as e:
                    print("encounter error: ",e)
                    messagebox.showerror('Error','Detect information type error!')




if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        sock.connect((HOST,PORT))
        print(sock)
    except:
        print("Fail to connect (%s,%s)"%(HOST,PORT))

    print("Client Begin...")

    root = tk.Tk()


    login = LoginPage(window = root,sock = sock)

    if login.flag is None:
        print("----LOGIN FAILUSER END -----")
        exit()
    
    User = login.flag # get the user
    print("----CHATTING BEGIN -----")

    user2room_history = {}
    users = get_users(sock,User)

    window = tk.Tk()
    # initialize
    window.title('WcxChat  '+User)
    window.geometry('800x600')
    # canvas - listing user's img, chat button, friends button
    cv = tk.Canvas(window, background='orange', width=90, height=600)
    cv.place(x=0, y=0)
    # user_imgs
    ## when database is completed, introduce user's img and load user's img when initialized
    img = PIL.Image.open('iniProfile2.jpg')

    image_file = PIL.ImageTk.PhotoImage(img)
    image = cv.create_image(45, 30, anchor='n', image=image_file)

    chat_button = tk.Button(cv, text='Chat', font=('Arial', 12), width=10, height=1, )
    chat_button.place(x=10, y=150)
    top = None
    win_ = None

    l = tk.Label(window, text='Online Users', font=('Arial', 13), width=15, height=2)
    l.place(x=100, y=10)

    # list all online users
    sb = Scrollbar(window)
    sb.pack(side=RIGHT,fill=Y)
    friend_list = tk.Listbox(window,yscrollcommand=sb.set)
    friend_list.place(x=95,y=45,height=80,width=140)
    sb.config(command=friend_list.yview)
    for u in users:
        friend_list.insert('end',u)
    


    s_bar = Scrollbar(window,orient = "vertical")
    s_bar.place(x=500,y=10,height=60)
    text_recv = tk.Text(window, width=460, height=60)
    text_recv.place(x=260, y=10,height=400)
    text_recv.config(yscrollcommand = s_bar.set)
    text_recv.tag_config('green', foreground='#008b00')
    text_recv.tag_config('red', foreground='#FF0000')
    text_recv.tag_config('blue', foreground='#0000FF')
    s_bar.config(command=text_recv.yview)

    cv2 = tk.Canvas(window, background='white', width=540, height=160, bd=1, highlightbackground='orange')
    cv2.place(x=250, y=425)

    send_button = tk.Button(cv2, text='Send', command=send_message)
    send_button.place(x=90, y=10)

    # textvariable
    input_text = tk.Text(cv2, width=460, height=90)
    input_text.place(x=5, y=30)

    _thread.start_new_thread(listener,(sock,window))
    window.mainloop()
