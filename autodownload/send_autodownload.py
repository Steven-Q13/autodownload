#!/usr/bin/env python3

import autodownload, sys

#Send torrent
def send_autodownload(key, email, path):
    auto_obj = autodownload.autodownload(email)
    print(auto_obj.sendtorrent(key, path))

#Arguments, password, email, path to torrent
send_autodownload(sys.argv[1], sys.argv[2], sys.argv[3])
