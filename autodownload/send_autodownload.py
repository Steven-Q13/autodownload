#!/usr/bin/env python3

import autodownload, sys

#Sends torrents as two messages one is json with torrent 
# info and one is bbinary information held in torrent
def send_autodownload(key, email, path):
    auto_obj = autodownload.autodownload(email)
    print(auto_obj.sendtorrent(key, path))

#Arguments: password, email, path to torrent
send_autodownload(sys.argv[1], sys.argv[2], sys.argv[3])
