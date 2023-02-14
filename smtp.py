# Implementing smtp library for sending email over 'new.toad.com' server
# importing required modules
import socket, ssl, os
from dotenv import load_dotenv
import mimetypes
from email.base64mime import body_encode as encode_64
import email.mime.multipart, email.mime.image, email.mime.application, email.mime.text
from imap import CRLF
# We are going to login to smtp server using email and password => and send an email thorugh smtp server
# Below is the class which is going to work as SMTP Protocol
class SMTP:
    # defining some variables 
    # socket which connects to smtp server
    _socket = None
    # Protocol messages to connect to the smtp server
    _DEFAULT_INTRO_MSG =  "HELO"
    # Authenticated login
    _AUTH_MSG = "AUTH LOGIN"
    # mailid of sender
    _MAIL_FROM = "MAIL FROM: "
    # maildid of receiver
    _RCPT_TO = "RCPT TO:"
    # data present in mail
    _DATA = "DATA"
    # security connection to the server
    _STARTTLS = "STARTTLS"
    # new line of the mail
    _NEW_LINE = "\r\n"
    # to quit from mail
    _QUIT = "QUIT"
    # to end the message
    _END_MSG = "\r\n.\r\n"
    # timeout for the socket
    _TIMEOUT = 20       # 20 seconds
    # host and port to connect to smtp server
    _HOST = ''
    _SMTP_PORT = 25             # smtp plain text default port 
    _SMTP_TLS_PORT = 587        # smtp tls default port 
    _SMTP_SSL_PORT = 465        # smtp ssl default port 

    # storing the smtp mail address and port for each domain below
    _SMTP_EMAILS = [
        {
            'domain': 'gmail.com',
            'smtp_server': 'smtp.gmail.com',
            'port': _SMTP_SSL_PORT or _SMTP_TLS_PORT,
            'is_tls': True
        },
        {
            'domain': 'coep.ac.in',
            'smtp_server': 'outlook.office365.com',
            'port': _SMTP_TLS_PORT,
            'is_tls': True
        },
        {
            'domain': 'outlook.com',
            'smtp_server': 'outlook.office365.com',
            'port': _SMTP_TLS_PORT,
            'is_tls': True
        }
    ]
    # if for outlook smtp requires starttls encryption then
    _is_tls = False
    # Utility variable 
    _debugging = False
    # email and password
    _email = ""
    _password = ""

    # Intializing functions for smtp server
    def __init__(self, email, password, debug = False):
        self._email = email
        self._password = password
        self._debugging = debug
        if email is not None:
            email_domain = email.split("@")[1].lower()
        for email in self._SMTP_EMAILS:
            self._email = email['domain']
            self._HOST = email['smtp_server']
            self._SMTP_PORT = email['port']
            self._is_tls = email['is_tls']
            break
        # Connect to smtp server
        self._connect
        # INTRO to the smtp server
        self._say_hello
        # Login using email and password
        self._login

#***************Private Functions**********#
# Function to connect to smtp server
    def _connect(self):
        # Make TCP connection with smtp server
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._TIMEOUT)
        self._socket.connect((self._HOST, self._SMTP_SSL_PORT))
        msg = ""
        # starttls encryption (for outlook)
        if self._is_tls:
            msg = self._socket.recv(1024).decode().strip(CRLF)
            self._say_hello()
            self._start_tls()
            self._ssl_connect()
        else:
            self._ssl_connect()
            msg = self._socket.recv(1024).decode().strip(CRLF)
        code = int(msg[:3])
        if self._debugging:
            print(msg)
        if code != 220:
            raise Exception("Connection Failed")

    # establishing connection between client and server
    def _say_hello(self):
        self._send_encoded_msg(self._DEFAULT_INTRO_MSG)
    # TLS secure encryption
    def _start_tls(self):
        self._send_encoded_msg(self._STARTTLS)
    # Connection with ssl to smtp server
    def _ssl_connect(self):
        context = ssl.create_default_context()
        host = self._HOST
        self._socket = context.wrap_socket(self._socket, server_hostname = host)
    # Diconnecting with smtp server
    def _close_connection(self):
        self._socket.close()

#*********Utility Functions************#
    # Function to send encoded msg to smtp
    def _send_encoded_msg(self, message):
        if self._debugging:
            print("Client: ", message)
        message = message + self._NEW_LINE
        self._socket.send(message.encode('ascii'))
        received_msg = self._socket.recv(1024).decode().strip(CRLF)
        if self._debugging:
            print(received_msg)
        return int(received_msg[:3]), received_msg[4:]

    #********LOGIN******#
    def _login(self):
        code, reply = self._send_encoded_msg(self._AUTH_MSG)
        # Send email
        encoded_mail = encode_64(self._email.encode('ascii'), eol='')
        code, reply = self._send_encoded_msg(encoded_mail)
        # Send password 
        encoded_pass = encode_64(self._password.encode('ascii'), eol='')
        pass_msg = encoded_pass
        code, reply = self._send_encoded_msg(pass_msg)
        if code == 235:
            pass
        else:
            raise Exception('Invalid username or password')

    #***********SMTP FUNTIONS**********(Public Functions)#
    # 1. SEND: Function used to send mail to smtp server
    def send_email(self, mail_to, data):
        self._send_mail_from()
        for item in mail_to:
            self._send_RCPT_TO(item.strip())
        self._send_DATA(data)

    # Function to make body and add attachments 
    def add_attachemnt(self, subject, text, filepaths):
        try:
            msg = email.mime.multipart.MIMEMultipart()
            msg['Subject'] = subject
            body = email.mime.text.MIMEText(text)
            msg.attach(body)
            for filepath in filepaths:
                filepath = filepath.strip()
                if filepath != None and len(filepath) != 0:
                    attach = None
                    file_type = mimetypes.MimeTypes().guess_type(filepath)[0]
                    # if starts from application
                    if file_type.startswith('application/'):
                        application_file = open(filepath, 'rb')
                        attach = email.mime.application.MIMEApplication(application_file.read(), _subtype = file_type.split('/')[1])
                        application_file.close()
                    # Check if attachment is image
                    elif file_type.startswith('image/'):
                        image_file = open(filepath, 'rb')
                        attach = email.mime.image.MIMEImage(image_file.read(), _subtype = file_type.split('/')[1])
                        image_file.close()
                    attach.add_header("Content-Disposition", "attachment", filename = os.path.basename(filepath))
                    msg.attach(attach)
            return msg.as_string()
        except:
            raise Exception("Invalid filename")

    # 2. QUIT: Function to quit connection with the smtp server
    def quit(self):
        self._send_encoded_msg(self._QUIT)

#************SEND email***********#
    # Functions to send email
    def _send_mail_from(self):
        msg = self._MAIL_FROM + "<" + self._email + "> "
        code, reply = self._send_encoded_msg(msg)
        # code should be 250
        if code != 250:
            raise Exception('Invalid sender mail')

    # Function to send mail to recipient
    def _send_RCPT_TO(self, mail_to):
        msg = self._RCPT_TO + "<" + mail_to + ">"
        code, reply = self._send_encoded_msg(msg)
        # response code should be 250
        if code != 250:
            raise Exception('Invalid receiver mail')

    # Function to send subject and body to smtp
    def _send_DATA(self, data):
        # Send data to smtp server
        code, reply = self._send_encoded_msg(self._DATA)
        # response code should be 354
        if code != 354:
            raise Exception('Something went wrong')
        self._socket.send(data.encode())
        # Send end message
        code, reply = self._send_encoded_msg(self._END_MSG)
        # response code should be 250
        if code != 250:
            raise Exception('Mail not sent successfully! Please try again')

if __name__ == "__main__":
    load_dotenv(dotenv_path='./.env')
    old_mail = os.getenv('EMAIL')
    old_pass = os.getenv('PASSWORD')
    SMTP(email = old_mail, password=old_pass, debug=True)
    print("SMTP Server Ready")
