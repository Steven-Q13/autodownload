import os, getpass, subprocess, sys

from cryptography.fernet import Fernet

def setup_autodownload(token, email, cred_path):
    path = os.path.realpath(__file__)
    path = path.split('/')
    path.pop(-1)
    path.pop(-1)
    path = '/'.join(path)

    with open('%s/launchd/com.autodownload.plist' % path, 'r') as f:
        contents = f.read()
    
        contents = contents.replace('JJJ1', '%s/bin/checkmail' % path)
        contents = contents.replace('JJJ2', email)
        contents = contents.replace('JJJ3', '%s/launchd/stoud.log' % path)
        contents = contents.replace('JJJ4', '%s/launchd/sterr.log' % path)
        contents = contents.replace('JJJ5', path)
        
        user = getpass.getuser()
        launchd_path = '/Users/%s/Library/LaunchAgents/com.autodownload.plist' % user
        
        with open(launchd_path, 'w') as fnew:
            fnew.write(contents)
        subprocess.call(['launchctl', 'load', launchd_path])

        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(token)
        with open('%s/token.txt' % path, 'w') as ft:
            f.write(token)
        with open('%s/key.txt' % path, 'wb') as fk:
            f.write(key)

        subprocess.call(['mv', cred_path, '%s/credentials.json' % path])

    #Arguments are password, user email, and path to credentials.json from google API
setup_autodownload(sys.argv[1], sys.argv[2], sys.argv[3])
