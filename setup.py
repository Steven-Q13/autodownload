from setuptools import setup

setup(version='0.1',
      description='Automatic Downloader via gmail for Macs',
      long_description=readme(),
      url='https://github.com/Steven-Q13/auto_download',
      author='Steven Queen',
      author_email='sequeen0@gmail.com'
      license='GNU',
      packages=['auto_download'],
      zip_safe=False,
      install_requires=['base64', 'pickle', 'os', 'getpass', 'time',
                        'datetime', 'sys', 'mimetypes', 'bencode', 'json'
                        'subprocess', 'googleapiclient.discovery',
                        'google_auth_oauthlib.flow', 
                        'google.auth.transport.requests',
                        'apiclient', 'cryptography.fernet', 'collections',
                        'email.mime.audio', 'email.mime.audio'
                        'email.mime.image', 'email.mime.multipart',
                        'wmail.mime.text']
      scripts=['']
      )


def readme():
    with open('README.md') as file:
        return file.read()
      
