#!/usr/bin/env python3

import bencode
import base64, pickle, os, getpass, time, datetime, sys, mimetypes 
import json, subprocess

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

from cryptography.fernet import Fernet
from collections import OrderedDict

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class autodownload:

    SCOPES = ['https://mail.google.com/']
    UID = 'me'

    def __init__(self, email):
        self.service = self.getAPI()
        self.email = email


    def mailcheck(self):
        key = autodownload.getkey()
        queryT = '''filename:txt subject:DON'T newer_than:2d "This message is used for autodownload" +%s''' % (key)
        queryJ = '''filename:json subject:DON'T newer_than:2d "This message is used for autodownload" +%s''' % (key)
        
        
        msg_idT = self.searchmail(queryT)
        msg_idJ = self.searchmail(queryJ)
        
        if(msg_idT==[] or msg_idJ==[]):
            return 1
        locT = self.downloadtorrent(msg_idT[0]['id'], binary=True)
        locJ = self.downloadtorrent(msg_idJ[0]['id'])

        js = json.load(open(locJ, 'r'), object_pairs_hook=OrderedDict)
        with open(locT, 'rb') as f:
            bb = f.read()
        bb = base64.urlsafe_b64decode(bb)
        #Fix sending so that you only have to decode once
        # Or mabye because you have to encode file and then
        # encode whole message you have to do it twice
        bb = base64.urlsafe_b64decode(bb)
        js['info']['pieces'] = bb
        name = locT.split('/')
        name = name[-1]
        name = name.split('.')
        name = name[0]
        path = '/Users/%s/Downloads/%s.torrent' % (getpass.getuser(), name)

        bencode.bwrite(js, path)
        #OS opens file with torrent client to start download
        # Torrent closes when download is done
        #process = subprocess.Popen('open', '/Users/%s/Downloads/%s' % (getpass.getuser(), part['filename']))

        process = subprocess.Popen(['open', path])

        self.deletemsg(msg_idT[0]['id'])
        self.deletemsg(msg_idJ[0]['id'])

        os.remove(locT)
        os.remove(locJ)

        message = self.msgnormal(self.email, 
                                 'Download Confirmation: autodownload', 
                                 self.normaltext())

        self.sendmsg(message)
        return 'Download Started'



    def getkey():
        path = os.path.realpath(__file__)
        path = path.split('/')
        path.pop(-1)
        path.pop(-1)
        path = '/'.join(path)

        with open('%s/key.txt' % path, 'rb') as fk:
            key = fk.read()
        fer = Fernet(key)
        with open('%s/token.txt' % path, 'rb') as ft:
            token = ft.read()
        token = fer.decrypt(token)
        token = token.decode('utf-8')

        return token



    def attachmenttext(key):
        #Checks if password is correct
        if key!=autodownload.getkey():
            raise AssertionException('Invalid Password')

        date = datetime.datetime.fromtimestamp(time.time())
        #Message in email
        text ='''Don't delete this message, it will auto delete after downloading
                 This message is used for autodownload
                 Sent at: %s
                 Procces Spawned from: %s
                 Torrent autodownload for gmail
                 Password: %s''' % (date.strftime('%Y - %B, %d - %H:%M:%S'), 
                                    os.path.abspath(os.path.dirname(sys.argv[0])), 
                                    key)
        return text



    def normaltext(self):
        date = datetime.datetime.fromtimestamp(time.time())
        text ='''This message is from for autodownloader
            Your download of %s has started

            Sent at: %s
            Procces Spawned from: %s
            Torrent autodownload for gmail
            ''' % (self.file_name,
                   date.strftime('%Y - %B, %d - %H:%M:%S'), 
                   os.path.abspath(os.path.dirname(sys.argv[0])))
        return text


        
    #Service arg is authorized obj to use API on
    # User_id should be 'me'
    # Query should contain password
    def searchmail(self, query, id=UID):
        #Return valid message id
        try:
            #Looks for results with valid query
            response = self.service.users().messages().list(
                    userId=id, q=query).execute()

            #List of returned messages
            messages = []

            #If key 'messages' is in response then query succesfully found a result
            if 'messages' in response:
                messages.extend(response['messages'])

            #A search only checks one page at a time and returns a nextPageToken
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']

                #Using nextPageToken you can search the next token
                response = self.service.users().messages().list(
                        userId=user_id, q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])
            return messages
        except errors.HttpError as e:
            print ('Error occurred in searching mail: %s' % error)



    #Program returns message in valid format for sending through gmail api
    def msgnormal(self, to, subject, text, sendFrom=UID):
        message = MIMEText(text)
        message['to'] = to
        message['from'] = sendFrom
        message['subject'] = subject
	
	#Return object with raw key to be passed to body object
	# Raw value needs to be in base 64 which needs a byte object
	# so it is encoded, however raw needs to be decoded
        return {'raw': base64.urlsafe_b64encode(
            message.as_string().encode('utf-8')).decode('utf-8')}



    #Permissions for the program, granted through OAuth process
    # Returns object to operate API on
    def getAPI(self):
        creds = None
	
	#Look for file storing the credential object
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
	
	#If file didn't exist or credentials aren't valid reauthenticate
	# Opens pop-up window to authenticate
	# Uses json generated from getting API ID
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
		
	    #Saves newly gotten credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
	
	#Object to use API on
        return build('gmail', 'v1', credentials=creds)



    #Program to get torrent attchment 
    def downloadtorrent(self, msg, binary=False):
        try:
            #Gets the message with its id
            message = self.service.users().messages().get(userId='me', id=msg).execute()

            #Looks in the payload and parts of the message for a file
            for part in message['payload']['parts']:
                if part['filename']:
                    self.file_name = part['filename']

                    #part['body'] doesn't actually end up containing data, but it
                    # does contain we an id we can use for an API call to get
                    # where the attachment id actually is
                    attachmentId = part['body']['attachmentId']
                    file_data = self.service.users().messages().attachments().get(
                        userId='me', messageId=msg, id=attachmentId).execute()

                    path = ('/Users/%s/Downloads/%s' % 
                        (getpass.getuser(), part['filename']))

                    #Gets the data from the correct location and needs to encode 
                    # it so that it can correctly decode it
                    if binary:
                        #file_data = base64.urlsafe_b64decode(file_data['data'])
                        with open(path,'w') as f:
                            f.write(file_data['data'])

                    else:
                        file_data = base64.urlsafe_b64decode(
                            file_data['data'].encode('UTF-8'))
                        with open(path,'wb') as f:
                            f.write(file_data)

            return path

        except errors.HttpError as e:
            print ('Error in getting attachment: %s' % e)



    #Program to delete message with a given id
    def deletemsg(self, msg_id, id=UID):
        try:
            self.service.users().messages().delete(userId=id, id=msg_id).execute()
        
        except errors.HttpError as e:
            print ('Error in deleting message: %s' % e)



    #Program sends outs an email to my own gmail account sequeen0@gmail.com
    def sendmsg(self, message, sendFrom=UID):
        try:
    	    message_info = self.service.users().messages().send(
                userId=sendFrom, body=message).execute()
        except errors.HttpError as e:
            print ('Error sending confirmation email: %s' % e)



    def msgattachment(self, to, subject, text, path, sendFrom=UID, binary=False):

        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sendFrom
        message['subject'] = subject

        msg = MIMEText(text)

        message.attach(msg)
        try:
            content_type, encoding = mimetypes.guess_type(path)
        except Error as e:
            print('Error in msg attachment: %s' % e)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)

        if binary:
            fp = open(path, 'rb')
            file_input = fp.read()
            #safe_file = base64.urlsafe_b64encode(file_input)
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(file_input)
            fp.close()
        else:
            fp = open(path, 'r')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        name = path.split('/')
        name = name[-1]
        msg.add_header('Content-Disposition', 'attachment', filename=name)
        message.attach(msg)

        return {'raw' : base64.urlsafe_b64encode(
            message.as_string().encode('utf-8')).decode('utf-8')}



    def splittorrent(self, path):
        bt = bencode.bread(path)
        bb = bt['info']['pieces']
        bt['info']['pieces'] = 'PLACEHOLDER'

        secs = path.split('/')
        ending = secs.pop()
        name = ending.split('.')
        name = name[0]
        pathBeginning = '/'
        pathBeginning = pathBeginning.join(secs)

        jsPath = '/Users/%s/Downloads/%s.json' % (getpass.getuser(), name)
        jsPath = jsPath
        js = json.dump(bt, open(jsPath, 'w'))

        bbPath = '/Users/%s/Downloads/%s.txt' % (getpass.getuser(), name)
        bb = base64.urlsafe_b64encode(bb)
        with open(bbPath, 'wb') as f:
            f.write(bb)

        return [jsPath, bbPath]



    def sendtorrent(self, key, path):
        try:
            text = autodownload.attachmenttext(key)
        except Exception as e:
            print ('Error sending torrent: %s' % e)
        paths = self.splittorrent(path)
        msg = self.msgattachment(
            self.email, "DON'T DELETE: autodownload", text, paths[0]) 
        self.sendmsg(msg)
        msg2 = self.msgattachment(
            self.email, "DON'T DELETE: autodownload", text, paths[1], binary=True) 
        self.sendmsg(msg2)

        os.remove(paths[0])
        os.remove(paths[1])
        return 'Message Sent'

