#!/usr/bin/env python3

import sys, autodownload

#Use this to check where the launchd file looks for modules
# >>> import sys
# >>> print('\n'.join(sys.path))
#To make launchd correctly import files you need to use pip with
# the "-t PATH" command to directly install to the site-packages 
# folder that launchd uses

#Called by ~/Library/LaunchAgents/com.autodownload.plist to check
# for and download torrent messages
def checkmail(email):
    #Autodownload object to initiate operations on
    auto_obj = autodownload.autodownload(email)
    #Function that checks for and downloads messages
    print(auto_obj.mailcheck())

#Argument: User email
checkmail(sys.argv[1])
