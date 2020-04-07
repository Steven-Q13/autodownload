import sys, autodownload

#Called by checkmail exectuable in bin to check for download messages
def checkmail(email):
    auto_obj = autodownload.autodownload(email)
    print(obj.mailcheck())

checkmail(sys.argv[1])
