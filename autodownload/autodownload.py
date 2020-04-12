#!/usr/bin/env python3

import base64, pickle, os, getpass, time, datetime, sys, mimetypes 
import json, subprocess
import importlib.util

import bencode
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

#Launchd wont support this module in the folder that it looks in for imports
# so the password is not encrypted
#from cryptography.fernet import Fernet
from collections import OrderedDict

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Autodownload class provides functionality for sending, recieving, encoding, and
# downloading torrent files via transfer over gmail using its API and OAuth process
class autodownload:
    
    #Used by gmail API when getting credentials for API interaction
    # =This scope gives acess to the users entire inbox
    SCOPES = ['https://mail.google.com/']

    #Special key used by gmail to denote the ID of the user
    UID = 'me'
    
    #Initliazes with users gmail address
    def __init__(self, email):
        self.service = self.getAPI()
        self.email = email

    #Checks if there is a message sent from autodownload with the valid password
    # if there is it downloads the json and binary data puts them together and remakes the torrent
    # and opens the torrent to begin the downloading process and sends a confirmation email
    def mailcheck(self):
        #Gets searches for valid emails, there are two, the json and binary file
        key = autodownload.getkey()
        queryT = '''filename:txt subject:DON'T newer_than:2d "This message is used for autodownload" +%s''' % (key)
        queryJ = '''filename:json subject:DON'T newer_than:2d "This message is used for autodownload" +%s''' % (key)
        
        msg_idT = self.searchmail(queryT)
        msg_idJ = self.searchmail(queryJ)
        
        if(msg_idT==[] or msg_idJ==[]):
            return 1

        #Saves the attachments to the computer
        locT = self.downloadtorrent(msg_idT[0]['id'], binary=True)
        locJ = self.downloadtorrent(msg_idJ[0]['id'])

        #Opens the json as an ordered dict and inserts the safely encoded binary data into the correct
        # pair so that it can then be saved as a torrent
        js = json.load(open(locJ, 'r'), object_pairs_hook=OrderedDict)
        with open(locT, 'rb') as f:
            bb = f.read()
        bb = base64.urlsafe_b64decode(bb)
        #Needs to be decoded twice so because the binary data is encoded for safe transmission and
        # then the entire message is encoded again
        bb = base64.urlsafe_b64decode(bb)
        js['info']['pieces'] = bb
        name = locT.split('/')
        name = name[-1]
        name = name.split('.')
        name = name[0]
        path = '/Users/%s/Downloads/%s.torrent' % (getpass.getuser(), name)

        #Writes the new torrent file
        bencode.bwrite(js, path)
        #Opens the torrent file with a client to begin download
        process = subprocess.Popen(['open', path])

        #Deletes gmail messages that the json and binary data are from
        self.deletemsg(msg_idT[0]['id'])
        self.deletemsg(msg_idJ[0]['id'])
    
        #Removes files from computer that were used for rebuilding torrent
        os.remove(locT)
        os.remove(locJ)
        
        #Sends a confimation email
        message = self.msgnormal(self.email, 
                                 'Download Confirmation: autodownload', 
                                 self.normaltext())
        self.sendmsg(message)
        return 'Download Started'


    #Returns password, unencrypted
    def getkey():
        #Gets relative path of autodownload folder
        path = os.path.realpath(__file__)
        path = path.split('/')
        path.pop(-1)
        path.pop(-1)
        path = '/'.join(path)

        #Cant use encryption module, not supported
        '''
        with open('%s/key.txt' % path, 'rb') as fk:
            key = fk.read()
        fer = Fernet(key)
        with open('%s/token.txt' % path, 'rb') as ft:
            token = ft.read()
        token = fer.decrypt(token)
        token = token.decode('utf-8')

        return token
        '''
        #Opens and gets password from file its saved in
        with open('%s/token.txt' % path, 'r') as ft:
            token = ft.read()
        return token


    #Returns formatted text that is used in emails that are sending the torrent
    def attachmenttext(key):
        #Checks if password is correct
        if key!=autodownload.getkey():
            raise AssertionException('Invalid Password')

        date = datetime.datetime.fromtimestamp(time.time())
        #Message includes password, time sent, and what sent the email
        text ='''Don't delete this message, it will auto delete after downloading
                 This message is used for autodownload
                 Sent at: %s
                 Procces Spawned from: %s
                 Torrent autodownload for gmail
                 Password: %s''' % (date.strftime('%Y - %B, %d - %H:%M:%S'), 
                                    os.path.abspath(os.path.dirname(sys.argv[0])), 
                                    key)
        return text


    #Returns formatted text used in confirmation email
    def normaltext(self):
        date = datetime.datetime.fromtimestamp(time.time())
        #Message includes time sent, what it downloaded, and what sent the email
        text ='''This message is from autodownloader
            Your download of %s has started

            Sent at: %s
            Procces Spawned from: %s
            Torrent autodownload for gmail
            ''' % (self.file_name,
                   date.strftime('%Y - %B, %d - %H:%M:%S'), 
                   os.path.abspath(os.path.dirname(sys.argv[0])))
        return text


        
    #Returns message ids that of messages that contain the match the query
    # User_id should be 'me' or account that your is being searched
    # Query should contain password,terms used to look for emails with the torrent
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



    #Program to download an attahment from a given message
    # msg is id of message to get attachment from
    # If binary is true it saves it as binary data
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

                    if binary:
                        #Writes binary data to file, it is not a binary file
                        # becuase it is still safely encoded for normal transmission
                        with open(path,'w') as f:
                            f.write(file_data['data'])

                    else:
                        #Needs to be decoded but its in string format so it
                        # first needs to be encoded and then decoded
                        file_data = base64.urlsafe_b64decode(
                            file_data['data'].encode('UTF-8'))
                        with open(path,'wb') as f:
                            f.write(file_data)

            return path

        except errors.HttpError as e:
            print ('Error in getting attachment: %s' % e)



    #Is given an id for a message and deletes
    # id should be 'me' or the email address for the account
    def deletemsg(self, msg_id, id=UID):
        try:
            self.service.users().messages().delete(userId=id, id=msg_id).execute()
        
        except errors.HttpError as e:
            print ('Error in deleting message: %s' % e)



    #Program sends email
    # Message should be a mime formatted object to send
    # Send from is 'me' or email address for account
    # Sends the message from the given API credentials account
    def sendmsg(self, message, sendFrom=UID):
        try:
    	    message_info = self.service.users().messages().send(
                userId=sendFrom, body=message).execute()
        except errors.HttpError as e:
            print ('Error sending confirmation email: %s' % e)


    #Returns correctly formatted message thats ready to be sent, includes an attachment
    # to: email address to send message to
    # subject: email subject
    # text: text in email body
    # path: path of a file on the computer to use for attachment
    # sendFrom: 'me' should be API enabled account
    # binary: Is true if the file type is binary
    def msgattachment(self, to, subject, text, path, sendFrom=UID, binary=False):
        #Makes the mime message and sets each part of the message
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sendFrom
        message['subject'] = subject

        #Makes mime text part to attach to the message
        msg = MIMEText(text)
        message.attach(msg)

        #MIME guesses file type
        try:
            content_type, encoding = mimetypes.guess_type(path)
        except Error as e:
            print('Error in msg attachment: %s' % e)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)

        #If the file type is binary it uses base64 encoding
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

        #Gets name for attachment
        name = path.split('/')
        name = name[-1]
        msg.add_header('Content-Disposition', 'attachment', filename=name)
        message.attach(msg)

        #Returns mime message as raw, component that is ready to be sent in gmail API
        return {'raw' : base64.urlsafe_b64encode(
            message.as_string().encode('utf-8')).decode('utf-8')}


    #Takes torrent file breaking it into a json file and a binary file
    # Returns path to the two new files
    def splittorrent(self, path):
        #Uses bencode library to get the torrent as an Ordered Dict
        bt = bencode.bread(path)
        #['info']['peices'] value of the dict contains the binary data
        bb = bt['info']['pieces']
        bt['info']['pieces'] = 'PLACEHOLDER'

        #Gets filename of original torrent
        secs = path.split('/')
        ending = secs.pop()
        name = ending.split('.')
        name = name[0]
        pathBeginning = '/'
        pathBeginning = pathBeginning.join(secs)

        #Saves to donwloads
        jsPath = '/Users/%s/Downloads/%s.json' % (getpass.getuser(), name)
        jsPath = jsPath
        js = json.dump(bt, open(jsPath, 'w'))
        bbPath = '/Users/%s/Downloads/%s.txt' % (getpass.getuser(), name)

        #Encodes binary data as base64 for safe transmission
        bb = base64.urlsafe_b64encode(bb)
        with open(bbPath, 'wb') as f:
            f.write(bb)

        return [jsPath, bbPath]


    #Sends message two messages with torrent components for autodownload to collect
    # key: users password
    # path: path to torrent file saved on computer
    def sendtorrent(self, key, path):
        #Text in email body
        text = autodownload.attachmenttext(key)
        #Splits torrent into json and binary file
        paths = self.splittorrent(path)
        #Sends json file as an attachment
        msg = self.msgattachment(
            self.email, "DON'T DELETE: autodownload", text, paths[0]) 
        self.sendmsg(msg)
        #Sends binary file as attachment
        msg2 = self.msgattachment(
            self.email, "DON'T DELETE: autodownload", text, paths[1], binary=True) 
        self.sendmsg(msg2)

        #Deletes two files used for split the torrent
        os.remove(paths[0])
        os.remove(paths[1])
        return 'Message Sent'

