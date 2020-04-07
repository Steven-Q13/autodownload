import os, getpass, subprocess, sys

from cryptography.fernet import Fernet


def uninstall_autodownload(pword):
    path = os.path.realpath(__file__)
    path = path.split('/')
    path.pop(-1)
    path.pop(-1)
    path = '/'.join(path)
    
    token = f.encrypt(token)
    with open('%s/key.txt' % path, 'r') as fk:
        key = fk.read()
    f = Fernet(key)
    with open('%s/token.txt' % path, 'rb') as ft:
        token = ft.read()
    token = f.decrypt(token)

    if token==pword:
        #Uninstall


uninstall_autodownload(sys.argv[1])
