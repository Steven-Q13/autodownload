from setuptools import setup

setup(version='0.1',
      description='Automatic Downloader via gmail for Macs',
      long_description=readme(),
      url='',
      author='Steven Queen',
      author_email='sequeen0@gmail.com'
      license='GNU',
      packages=['auto_download'],
      zip_safe=False,
      install_requires=['os','google-api-python-client', 
                        'google-auth-httplib2', 'google-auth-oauthlib',
                        'picke', 'datetime', 'time', 'email.mime.text',
                        'base64', 'getpass', 'sys', 'cryptography.fernet']
      scripts=['']
      )


def readme():
    with open('README.md') as file:
        return file.read()
      

