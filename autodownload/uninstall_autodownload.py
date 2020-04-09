import os, getpass, subprocess, sys

from cryptography.fernet import Fernet


def uninstall_autodownload(pword):
    path = os.path.realpath(__file__)
    path = path.split('/')
    path.pop(-1)
    path.pop(-1)
    path = '/'.join(path)
    
    with open('%s/key.txt' % path, 'r') as fk:
        key = fk.read()
    f = Fernet(key)
    with open('%s/token.txt' % path, 'rb') as ft:
        token = ft.read()
    token = f.decrypt(token)
    token = token.decode('utf-8')

    if token==pword:
        os.remove('%s/key.txt' % path)
        os.remove('%s/token.txt' % path)
        os.remove('/Users/%s/Library/LaunchAgents/com.autodownload.plist' % getpass.getuser())
        return 'Uninstalled'
    return 'Inva;id Password'


uninstall_autodownload(sys.argv[1])
