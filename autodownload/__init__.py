from .autodownload import autodownload
from .setup_autodownload import setup_autodownload
from .send_autodownload import send_autodownload
from .checkmail import checkmail

import subprocess, os, getpass

def main():
    path = os.path.realpath(__file__)
    path = path.split('/')
    path.pop(-1)
    path.pop(-1)
    path = '/'.join(path)


    with open('%s/bin/setup_autodownload' % path, 'w') as fset:
        command = '#!/bin/bash\npython3 %s/autodownload/setup_autodownload.py $1 $2 $3' % path
        fset.write(command)

    with open('%s/bin/send_autodownload' % path, 'w') as fsend:
        command2 = '#!/bin/bash\npython3 %s/autodownload/send_autodownload.py $1 $2 $3' % path
        fsend.write(command2)

    with open('%s/bin/uninstall_autodownload' % path, 'w') as fun:
        command3 = '#!/bin/bash\npython3 %s/autodownload/uninstall_autodownload.py $1' % path
        fsend.write(command3)

    with open('/Users/%s/.bash_profile' % getpass.getuser() , 'a') as f:
        command4 = 'export PATH=$PATH:%s/bin' % path
        f.append(command4)

main()
