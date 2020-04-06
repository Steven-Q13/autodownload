import os.path, sys, getpass, shutil

from cryptography.fernet import Fernet

class Setup:
	
	def __init__(password, json_path) {
		user = getpass.getuser()
	
		with open('/Users/%d/.auto_download/auto_download_info.txt' % user, 'w') as save:
			key = fernet.generate_key();
			with open('/Users/%d/.auto_download/auto_download_token.txt' % user, 'wb') as token:
				pickle.dump(key, token)
			f = fernet(key)
			password_encrypted.f.encrypt(password)
			save.write(password_encrypted)
			
		shutil.move(json_path, '/Users/%d/.auto_download/credentials.json' % user)	
		
		#Look for file storing the credential object
		if os.path.exists('/Users/%d/.auto_download/token.pickle' % user):
			with open('/Users/%d/.auto_download/token.pickle' % user) as token:
				creds = pickle.load(token)
	
		#If file didn't exist or credentials aren't valid reauthenticate
		# Opens pop-up window to authenticate
		# Uses json generated from getting API ID	
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file('/Users/%d/.auto_download/credentials.json' % user, SCOPES)
				creds = flow.run_local_server(port=0)
		
			#Saves newly gotten credentials
			with open('/Users/%d/.auto_download/token.pickle' % user, 'wb') as token:
				pickle.dump(creds, token)


		shutil.move('./com.auto_download.plist', '/Users/%d/Library/LaunchAgents/com.auto_download.plist' % user)
		shutil.move('./check_email', '/usr/local/bin')
	
	}

	def main():