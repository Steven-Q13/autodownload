import os, getpass, subprocess, sys

def main():
    path = os.path.realpath(__file__)
    path = path.split('/')
    path.pop(-1)
    path.pop(-1)
    path = '/'.join(path)

    with open('%s/launchd/com.autodownload.plist' % path, 'r') as f:
        contents = f.read()
    
    contents = contents.replace('JJJ1', '%s/bin/checkmail.py' % path)
    contents = contents.replace('JJJ2', '%s/launchd/stoud.log' % path)
    contents = contents.replace('JJJ3', '%s/launchd/sterr.log' % path)
    contents = contents.replace('JJJ4', path)
    
    user = getpass.getuser()
    launchd_path = '/Users/%s/Library/LaunchAgents/com.autodownload.plist' % user
    
    with open(launchd_path, 'w') as fnew:
        fnew.write(contents)

    subprocess.call(['launchctl', 'load', launchd_path])



main()

