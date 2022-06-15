import socket
import sys
import os
import select

from constant import *
import method
from server import broadcast

def login(conn,msg):
    try:
        user = msg
        assert user.find("\t") == -1
    except Exception as e:
        print("!! wrong login",e)
        return str(LOGIN_ERROR)

    return str(LOGIN_SUCCESS),user



