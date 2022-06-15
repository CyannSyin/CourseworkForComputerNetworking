import socket
import sys
import os
import select

from constant import *
from method import *
from events import *

"""
Global Variables 
 - conn : all connections
 - (HOST,PORT)
 - conn2user : dictionary(store users corresponding to their connections)
 - user2conn : dictionary(store conns corresponding to users)
"""


HOST = "127.0.0.1"
PORT = 65435

# BROADCAST
def broadcast(conn,msg,rest = b""):
    print("--->> broadcast <<----",msg,rest)
    for receiver in connections:
        # conditions
        if receiver!=conn and receiver!=sock and conn2user.get(conn) is not None:
            try:
                send(receiver,msg,rest)
            except Exception as e:
                print("!! broadcast error,",e)

# RELEASE CONNECTION
def release(conn):
    # print release information
    print("## release connection: ",conn,"    ##")

    # del this from CONNECTIONS
    connections.remove(conn)

    if user2conn.get(conn2user[conn])==conn:
        user = conn2user[conn]
        rest = user.encode("utf-8")
        broadcast(conn,str(LOGOUT_INFO),rest)
        del user2conn[user]


    # close this
    conn.close()
    del conn2user[conn]


# HANDLE MESSAGE
def handle(conn, msg, rest):
    state = ""
    try:
        type = int(msg[0])
    except Exception as e:
        print("!! wrong request",e)
        send(conn,str(WRONG_MESSAGE))
        return

    #print(msg[:2])

    if type == LOGIN:
        # msg = heaer + user + \r\n + pwd
        msg = msg[1:]
        state,user = login(conn,msg)
        if user !="":
            if user2conn.get(user) is not None:
                state = str(LOGIN_DUPLICATE)
        if state == str(LOGIN_SUCCESS):
            conn2user[conn] = user
            user2conn[user] = conn
            print("---Existing users with conns:")
            for key in conn2user.keys():
                print(key,conn2user[key])

            print("---Existing conns with users:")
            for key in user2conn.keys():
                print(key,user2conn[key])

            header = str(LOGIN_USERNAME)
            msg = user.encode("utf-8")
            broadcast(conn,header,msg)
        send(conn,state)
        return

    elif type == GET_ALL_USERS:
        user_list = user2conn.keys()
        if user_list is None:
            state = str(GET_USERS_ERROR)
            send(conn,state)
            return
        else:
            users = "\r\n".join(user_list)
            users = users.encode("utf-8")
            header = str(GET_SUCCESS)
            msg = users
            print("send users:",msg)
            send(conn,header,msg)
            return

    elif type == SEND_MESSAGE:
        try:
            sender = conn2user[conn]
            text = msg[1:]
            receiver, length = text.split("\r\n")
            print("in SEND_MESSAGE_STEP, receiver = {0}, sender = {1}, message content = {2}".format(receiver,sender,rest))
            #length = int(length)
            if len(receiver)==0 :
                print("in bigGroup")
                header = str(SEND_MESSAGE_ALL) + sender + "\r\n" + length
                print("header: ",header)
                text = rest.encode("utf-8")
                print("in this steo")
                print("succ insert into big group chat history")
                try:
                    broadcast(conn, header, text)
                    return
                except Exception as e:
                    print("send message error(during broadcast,", e)
                    header = str(SEND_ERROR)
                    method.send(conn, header)
                return

            else :
                send_sock = user2conn.get(receiver)

                if send_sock is None: #用户不在线，把聊天信息缓存给该用户
                    #add_privateChat_history(sender,receiver,rest)
                    # 提示消息已经缓存
                    print("message is stored")
                    msg = receiver.encode("utf-8")
                    method.send(conn,str(SEND_MESSAGE_PER_STORE),msg)
                    return
                else :
                    #add_privateChat_history(sender,receiver,rest)
                    try:
                        msg = sender + "\r\n" +rest
                        msg = msg.encode("utf-8")
                        method.send(send_sock,str(SEND_MESSAGE_PER),msg)
                    except Exception as e:
                        print("send private chat error {0}, receiver: {1}".format(e,receiver))
                    return

        except Exception as e:
            print("Wrong message， ",e)
            state = str(WRONG_MESSAGE)
            send(conn,state)
            return



if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind((HOST,PORT))
    sock.listen()

    print("******* Server Starting (",HOST,",",PORT,") *******")

    connections = [sock]

    conn2user = {}
    user2conn = {}

    # keep Listening

    while True:
        reads, writes, errors = select.select(connections,[],[])
        for cur in reads:
            if cur == sock: #new connection
                conn, addr = sock.accept()
                print("## new connection",addr,"   ##")
                connections.append(conn)
                conn2user[conn] = None
            else : # old connection
                print("## now: ",cur,"  ##")

                try :
                    data, rest = receive(cur)

                except Exception as e:
                    print(e)
                    release(cur) # release this connection
                    continue

                if data:
                    print(" request: ",data.encode("utf-8"))
                    if len(data)==0:
                        print("!!Error: wrong message")
                    else :
                        handle(cur,data,rest)
                else :
                    print("!!Error: receive data error")
                    release(cur)


    sock.close()