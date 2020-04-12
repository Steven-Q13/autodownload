import os, getpass, subprocess, sys
    
#from cryptography.fernet import Fernet

#Spawns files used by autodownload
def setup_autodownload(token, email, cred_path):
    #Gets relative path of autodownload folder
    path = os.path.realpath(__file__)
    path = path.split('/')
    path.pop(-1)
    path.pop(-1)
    path = '/'.join(path)

    #Takes launch agent stored in package, inserts correct paths
    # and saves it to ~/Library/LaunchAgents and loads it
    with open('%s/launchd/com.autodownload.plist' % path, 'r') as f:
        contents = f.read()

        #Inserts correct relative path in the launch agent
        contents = contents.replace('JJJ1', '%s/bin/checkmail.sh' % path)
        contents = contents.replace('JJJ2', email)
        contents = contents.replace('JJJ3', '%s/launchd/stout.log' % path)
        contents = contents.replace('JJJ4', '%s/launchd/sterr.log' % path)
        contents = contents.replace('JJJ5', path)
        
        user = getpass.getuser()
        launchd_path = '/Library/LaunchDaemons/com.autodownload.plist' % user
        
        #Saves completed launch agent ~/Library/LaunchAgents and loads it
        with open(launchd_path, 'w') as fnew:
            fnew.write(contents)
        subprocess.call(['launchctl', 'load', launchd_path])

        #Can't implement encrypted key because it won't correctly install in
        # the folder that the launch agent looks for python modules in
        '''
        key = Fernet.generate_key()
        f = Fernet(key)
        token = token.encode('utf-8')
        token = f.encrypt(token)
        '''
        #Unsafe unecrypted saving password to local package area
        with open('%s/token.txt' % path, 'w') as ft:
            ft.write(token)
        '''
        with open('%s/key.txt' % path, 'wb') as fk:
            fk.write(key)
        '''

        #Puts the users API credentials in the package
        subprocess.call(['mv', cred_path, '%s/credentials.json' % path])

#Arguments are password, user email, and path to credentials.json from google API
setup_autodownload(sys.argv[1], sys.argv[2], sys.argv[3])
