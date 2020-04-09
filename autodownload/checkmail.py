import sys, autodownload

#Called by checkmail exectuable in bin to check for download messages
def checkmail(email):
    auto_obj = autodownload.autodownload(email)
    print('Started Mail Check')
    print(auto_obj.mailcheck())

checkmail(sys.argv[1])
