# autodownload
Automated remote torrent downloader through email transfer

Guide:

Setup:
- Go to https://developers.google.com/gmail/api/quickstart/js and click "Enable the Gmail API" and "Create API Key"
- Note where the downloaded file "credentials.json" was saved
- In terminal put: 
"sudo pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib -t /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.7/lib/python3.7/site-packages
"
and
"sudo pip install bencode.py -t /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.7/lib/python3.7/site-packages"
and
"pip install autodownload"
- Close the terminal window and reopen a new one
- Then "bash setup_autodownload PASSWORD EMAIL_ADDRESS FULL_PATH_OF_CREDENTIALS.JSON"
	- PASSWORD will be your password you need for using the service
	- Email address will be the gmail you are using for the service and enacted the API on

- Both the receiving and sending computer will need to have the system downloaded on it
- To send a torrent first type "launchctl unload ~/Library/LaunchAgents/com.autodownload.plist" into terminal
- Then send the torrent with "bash send_autodownload PASSWORD EMAIL FULL_PATH_OF_TORRENT"
	- PASSWORD is your password that you entered upon installing
	- EMAIL is the gmail you are using gor the service and enacted the API on
- When you recieve you confirmation email type "launchctl load ~/Library/LaunchAgents/com.autodownload.plist" into the computer you sent the torrent from
