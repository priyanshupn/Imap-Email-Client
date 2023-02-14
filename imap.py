# implementing an imap library
# importing all necessary modules
import os, socket
import ssl, base64, getpass
from bs4 import BeautifulSoup
import quopri
from dotenv import load_dotenv
# globals
CRLF = '\r\n'      # Carriage Return Line Feed, MAIL NEW LINE
IMAP_PORT = 143     # imap server default port
IMAP_SSL_PORT = 993     # imap server default ssl port
TIMEOUT = 20       # 20 seconds 
# IMAP Protocol
class IMAP:
    # Declaring some variables
    _socket = None    # this socket will do connection to imap server ()
    _email = "nandagawalipp19.comp@coep.ac.in"
    _password = "priya@1234"
    IMAP_PORT = 143
    CRLF = '\r\n'
    IMAP_SSL_PORT = 993
    # Assigning imap server address and port number for each domain
    _EMAIL_DOMAIN = [
        {
            'domain': 'gmail.com',
            'imap_server': 'imap.gmail.com',
            'port': IMAP_SSL_PORT
                    },
        {
            'domain': 'coep.ac.in',
            'imap_server': 'outlook.office365.com',
            'port': IMAP_SSL_PORT
        },
        {
            'domain': 'outlook.com',
            'imap_server': 'outlook.office365.com',
            'port': IMAP_SSL_PORT
        }
    ]
    _LOGIN_MSG = "A01 LOGIN"    # Authenticated login message
    _HOST = 'outlook.office365.com'    # default host address
    _debugging = False
    TIMEOUT = 20
# Initializing constructor to login into imap server
    def __init__(self, email, password, debugging = False):
        self._email = email
        self._password = password
        self._debugging = debugging
        if email is not None:
            email.split("@")[1].lower()
        # Determine host and imap port from email domain name 
        for email in self._EMAIL_DOMAIN:
            self._email = email['domain']
            self._HOST = email['imap_server']
            self.IMAP_SSL_PORT = email['port']
            break
        try:
            # Connect to imap server
            self._connect
        except Exception as e:
            raise Exception(e)

    # Connection to IMAP server

    def _connect(self):
        # create a socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setting timeout for above socket
        self._socket.settimeout(TIMEOUT)
        # connect to imap server
        self._socket.connect((self._HOST, self.IMAP_SSL_PORT))
        # Wrap the socket in ssl
        self._ssl_connect()
        # Receive message from server
        msg = self._socket.recv(1024).decode().strip(CRLF)
        if self._debugging:
            print("Server:", msg)
        if msg.split()[1] != "OK":
            raise Exception("Something Went Wrong! Failed to connect to imap server")
        # Login after connection
        self._login()

    # to wrap the socket
    def _ssl_connect(self):
        context = ssl.create_default_context()
        host = self._HOST
        self._socket = context.wrap_socket(self._socket, server_hostname = host)

    # Performing Authenticated Login
    def _login(self):
        # Tell imap server for authentication
        message = self._LOGIN_MSG + " " + self._email + " " + self._password + CRLF
        self._socket.send(message.encode('ascii'))
        recv_msg = self._socket.recv(100024).decode().strip(CRLF)
        if self._debugging:
            print(recv_msg)
        # Spliting the lines
        lines_arr = recv_msg.splitlines()
        # Get the last line 
        msg_tokens = lines_arr[-1].split(" ")
        # Check if second element of tokens is OK, if not raise exception
        if msg_tokens[1] != "OK":
            raise Exception("Invalid email or password")

# *******Utility Methods*********
    # Function to send encoded message to imap server
    def _send_encoded_msg(self, message):
        if self._debugging:
            print("Client: ", message)
        message = message + CRLF
        if self._socket != None:
            self._socket.send(message.encode())
            received_msg = self._socket.recv(100024).decode().strip(CRLF)
            lines_arr = received_msg.splitlines()
            code = lines_arr[-1].split(" ")[1]
            if self._debugging:
                print("Server: ", received_msg)
            return code, received_msg
    
    # Function to get whole reply back from server
    def _get_whole_message(self):
        msg = ""
        email_results = ["OK", "NO", "BAD"]
        while True:
            try:
                # Receive message from server
                recv_bytes = self._socket.recv(1024)
                temp_msg = recv_bytes.decode(errors='ignore')
                # Split the lines from the received message
                lines_arr = temp_msg.splitlines()
                code1 = None
                code2 = None
                try:
                    code1 = lines_arr[-1].split(" ")[0]
                    code2 = lines_arr[-1].split(" ")[1]
                except Exception as e:
                    pass
                if code1 in email_results or code2 in email_results:
                    lines_arr.pop(-1)
                    # Add other lines
                    for item in lines_arr:
                        msg += item
                        msg += CRLF
                    # Remove first and last two line
                    msg = msg.splitlines()
                    reply = ""
                    # append other elements in array
                    for index in range(len(msg)):
                        reply += msg[index]
                        if index != len(msg) - 1:
                            reply += CRLF
                    return True, reply
                msg += temp_msg
            except Exception as e:
                return False, "Request Failed"

    # **********IMAP COMMANDS**********
    # 1. Listing all mailboxes
    def list_mailboxes(self):
        # LIST Command
        send = 'A02 LIST "" "*"'
        if self._socket != None:
            self._socket.settimeout(2)
            code, msg = self._send_encoded_msg(send)       
            self._socket.settimeout(TIMEOUT)
            if code != "OK":
                raise Exception("Not able to fetch mailboxes")
        # Separating different lines
            folders_imap = msg.splitlines()
            folders_imap.pop(-1)
            folders = []
            for item in folders_imap:
                tokens = item.split(" ")
                index = tokens.index('"/"')
                name = ""
                for i in range(index + 1, len(tokens)):
                    name += tokens[i]
                    name += " "
            if name[:-1] != '"[Gmail]"':
                folders.append(name[:-1])
        # Returning list of folders 
            return folders

    # 2. SELECT Mailbox
    def select_mailbox(self, name):
        # SELECT Command
        command = 'A02 SELECT {folder_name}{new_line}'.format(folder_name = name, new_line = CRLF)
        if self._socket is not None:
            self._socket.send(command.encode())
        msg = ""
        success = True
        # Receiving the response
        while True:
            if self._socket != None:
                temp_msg = self._socket.recv(1024).decode()
                msg += temp_msg
                flag = False
                for line in temp_msg.splitlines():
                    words = line.split()
                try:
                    if words[1] == "BAD" or words[1] == "NOT":
                        success = False
                        raise Exception("Failed to select mailbox")
                    elif words[1] == "OK" and (words[2] == "[READ-WRITE]" or words[2] == "[READ-ONLY]"):
                        flag = True
                        break
                except:
                    pass
                if flag:
                    break
            if not success:
                raise Exception('Invalid mailbox name')
            else:
                number_of_mails = 0
            # get the no. of mails in mailbox
            lines_arr = msg.splitlines()
            for item in lines_arr:
                try:
                    tokens = item.split(" ")
                    if tokens[2] == "EXISTS":
                        number_of_mails = int(tokens[1])
                except Exception as e:
                    continue
            return number_of_mails

    # 3. CLOSE Mailbox
    def close_mailbox(self):
        # CLOSE Command
        try:
            command = "A02 CLOSE"
            code, msg = self._send_encoded_msg(command)     
            if code == "OK":
                return True
            else:
                return False
        except:
            pass

    # 4. FETCH Mail
    def fetch_headers(self, start, count = 1):
        # FETCH email subject, from and date
        try:
            command = "A02 FETCH " + str(start - count) + ":" + str(start) +  " (FLAGS BODY[HEADER.FIELDS (DATE SUBJECT FROM)])" +  CRLF
            #if self._debugging:
                #print("Client: ", command)
            if self._socket != None:
                self._socket.send(command.encode())
            # Get output from server
                success, msg = self._get_whole_message()   
                emails = []
            # parse the header
                if success:
                    msg = self._separate_mail_headers(msg)  
                    for index, item in enumerate(msg):
                        decoded_email = self._decode_mail_headers(item) 
                        decoded_email['index'] = start - count + index
                        emails.insert(0, decoded_email)
                    return emails
            # return error
                else:
                    raise Exception("Failed to fetch email! Please try again!!")
        except:
            raise Exception("Failed to fetch email! Please try again!!")

    def get_boundary_id(self, index):
        # getting boundart id to separate different bodies of email
        try:
            command_boundary_id = "a02 FETCH " + str(index) +  " (BODY[HEADER.FIELDS (Content-Type)])" + CRLF
            self._socket.send(command_boundary_id.encode())
            success, msg = self._get_whole_message()    
            if success:
                main_header = '\n'.join(line for line in msg.splitlines()[1:-2])
                boundary_id = None
                boundary_key = "boundary="
                if main_header.find(boundary_key) == -1:
                    return None
                boundary_id = main_header[main_header.find(boundary_key) + len(boundary_key):]
                boundary_id = boundary_id[:main_header.find(';')]
                return boundary_id
        except:
            return None

    def fetch_body(self, index):
        # FETCHing text body of email
        try:
            filenames = self.get_body_structure(index)  
            is_attachment_present = False
            if len(filenames) != 0:
                is_attachment_present = True
            # Fetch the body
            command_body = "A02 FETCH " + str(index) +  " (BODY[1])" + CRLF
            if self._socket != None:
                self._socket.send(command_body.encode())
            # As attachment is not required
                success, msg = self._get_whole_message()    
                if success:
                    main = '\n'.join(line for line in msg.splitlines()[1:-1]).strip(CRLF)
                    try:
                        if main.splitlines()[1].lower().startswith("content-type:"):
                            multipart_boundary = main.splitlines()[0][2:]
                            body_list = self._get_email_body_list(multipart_boundary, main) 
                            main = ""
                            for item in body_list:
                                header, item = self._separate_body(item)    
                                headers = self._body_headers(header)    
                                item = self._get_cleaned_up_body(headers, item) 
                                main += item + "\n"
                    except:
                        pass

                 # string is base64 encoded
                    try:
                        main = base64.b64decode(main).decode()
                    except Exception as e:
                        pass
                    main = self._extract_text_from_html(main)   
                    temp_body = ""
                    main = main.replace("=20", "")
                    for line in main.splitlines():
                        try:
                            formatted_line = ' '.join(word for word in line.split() if not word.startswith("="))
                        except:
                            pass
                        temp_body += formatted_line + "\n"
                    main = temp_body.strip(CRLF)
                    main = main.replace("=\n", "")
                    return { 'body': main, 'is_attachment': is_attachment_present, 'filename': filenames }
                else:
                    raise Exception("Something went wrong! Body not fetched properly")
        except:
            raise Exception("Something went wrong! Body not fetched properly")
    # To fetch attachments
    def get_body_structure(self, index):
        # fetch the body
        command_body = "A02 FETCH " + str(index) + " (BODYSTRUCTURE)" + CRLF
        try:
            self._socket.send(command_body.encode())
            success, msg = self._get_whole_message()   
            msg = msg.lower()
            if not success:
                raise Exception("Something went wrong")
            filenames = []
            key = '"filename"'
            res = [i for i in range(len(msg)) if msg.startswith(key, i)]
            for i in res:
                temp = msg[i:]
                temp = temp[:temp.find(')')]
                filename = temp.split()[1]
                filename = filename.replace('"', '')
                filenames.append(filename)
            return filenames
        except Exception as e:
            return []
    # Download the file in mail
    def download_attachment(self, index):
        try:
            boundary_id = self.get_boundary_id(index)   
            # Fetch the body
            command_body = "A02 FETCH " + str(index) + " (BODY[text])" + CRLF
            self._socket.send(command_body.encode())
            success, msg = self._get_whole_message()    
            if boundary_id == None or not success:
                raise Exception("hi")
            body_list = self._get_email_body_list(boundary_id, msg)     
            username = getpass.getuser()
            dir_path = "/home/" + username + "/Downloads/"
            msg = "File downloaded in downloads folder"
            if not os.path.isdir(dir_path):
                dir_path = "/home/" + username + "/"
                msg = "File downloaded in home folder"
            for item in body_list:
                header, main = self._separate_body(item)    
                headers = self._body_headers(header)    
                try:
                    if headers[0].lower().startswith("video/") or headers[0].lower().startswith("image/") or headers[0].lower().startswith("application/"):
                        success, filename = self._get_attachment(header)  
                        filename = filename.replace('"', '')
                        if not success:
                            raise Exception("Hi")
                        file_path = dir_path + filename
                        attach = open(file_path, 'wb')
                        content = base64.b64decode(main)
                        attach.write(content)
                except:
                    pass
            return msg
        except Exception as e:
            raise Exception("Failed to download file! Please try again!!")

    # 5.DELETE Mail
    def delete_email(self, index):
        # DELETE Command
        command = "A02 STORE " +  str(index) + " +FLAGS (\\Deleted)" + CRLF
        self._socket.send(command.encode())
        success, msg = self._get_whole_message()    
        if success:
            command = "A02 EXPUNGE" + CRLF
            self._socket.send(command.encode())
            success, msg = self._get_whole_message()    
            if success:
                number_of_mails = 0
                # no. of mails
                lines_arr = msg.splitlines()
                for item in lines_arr:
                    try:
                        tokens = item.split(" ")
                        if tokens[2] == "EXISTS":
                            number_of_mails = int(tokens[1])
                    except:
                        continue
                return number_of_mails
            else:
                raise Exception("Something went wrong! Please try again")
        else:
            raise Exception("Something went wrong! Please try again")


#************MAIL HEADERS**********#

    # getting separate individual mails
    def _separate_mail_headers(self, msg):
        lines_arr = msg.splitlines()
        ans = []
        email = ""
        prev_start = 0
        index = 0
        while index < len(lines_arr):
            # indicates end of particular mail
            if lines_arr[index] == "":
                email = ""
                for item in lines_arr[prev_start + 1:index]:
                    email += item + "\n"
                prev_start = index + 2
                ans.append(email)
            index += 1
        return ans

    # Decoding text if it is in encoded word syntax
    def _extract_text(self, encoded_words):
        try:
            temp = encoded_words[2:]
            # Get the charset from encoded subject
            i1 = temp.find("?")
            charset = temp[:i1].lower()
            temp = temp[i1:]
            # Get the encoding type
            encoding = temp[1].upper()
            # Get the main text
            main_text = temp[3:]
            # This will be encoded string
            ending_index = main_text.find("?=")
            main_text = main_text[:ending_index]
            if encoding == "B":
                main_text = base64.b64decode(main_text)
            elif encoding == "Q":
                main_text = quopri.decodestring(main_text)
            return main_text.decode(charset), encoded_words.find("?=") + 3
        except Exception as e:
            return encoded_words

    # Decoding mail headers
    def _decode_mail_headers(self, msg):
        # function to separate subject, from and date from mail header
        lines_arr = msg.splitlines()
        index = 0
        subject = ""
        date = ""
        mail_from = ""
        subject_key = "subject:"
        date_key = "date:"
        from_key = "from:"
        # Separate subject
        sub_index = 0
        for index, line in enumerate(lines_arr):
            if line.lower().startswith(subject_key):
                sub_index = index
                break
        subject = lines_arr[sub_index][len(subject_key):]
        for line in lines_arr[sub_index + 1:]:
            if line.lower().startswith(date_key) or line.lower().startswith(from_key):
                break
            subject += line
        subject = subject.strip()
        # Separate date
        date_index = 0
        for index, line in enumerate(lines_arr):
            if line.lower().startswith(date_key):
                date_index = index
                break
        date = lines_arr[date_index][len(date_key):]
        for line in lines_arr[date_index + 1:]:
            if line.lower().startswith(subject_key) or line.lower().startswith(from_key):
                break
            date += line
        date = date.strip()
        # Separate mail_from 
        from_index = 0
        for index, line in enumerate(lines_arr):
            if line.lower().startswith(from_key):
                from_index = index
                break
        mail_from = lines_arr[from_index][len(date_key):]
        for line in lines_arr[from_index + 1:]:
            if line.lower().startswith(subject_key) or line.lower().startswith(date_key):
                break
            mail_from += line
        mail_from = mail_from.strip()
        # Decoding subject
        main_subject = ""
        # Check if the subject is in encoded word syntax
        if subject.startswith("=?"):        
            # Normalize the data to ascii
            while subject.startswith("=?"):
                output, ending_index = self._extract_text(subject)
                main_subject += output
                subject = subject[ending_index:]
        else:
            main_subject = subject
        # Decoding main_mail_from
        main_mail_from = ""
        # Check if the date is in encoded words syntax
        if mail_from.startswith("=?"):
            while mail_from.startswith("=?"):
                output, ending_index = self._extract_text(mail_from)
                main_mail_from += output
                mail_from = mail_from[ending_index:]
        main_mail_from += mail_from
        return {'Subject': main_subject, 'Date': date, 'From': main_mail_from}


#*********MAIL Body Utility**************#
    def _get_boundary_indices(self, boundary_id, msg):
        # Replace quotes
        boundary_id = boundary_id.replace('"', '')
        # Add --
        boundary_id = "--" + boundary_id
        res = [i for i in range(len(msg)) if msg.startswith(boundary_id, i)]
        # Return the array
        return res

    # Separting email bodies
    def _get_email_body_list(self, boundary_id, msg):
        boundary_indices = self._get_boundary_indices(boundary_id, msg)
        body_list = []
        i = 0
        while i < len(boundary_indices) - 1:
            # Select body
            temp_msg = msg[boundary_indices[i]:boundary_indices[i + 1]].strip()
            body_list.append('\n'.join(line for line in temp_msg.splitlines()[1:]))
            i += 1
        # Return all the bodies
        return body_list

    # Separating header and body
    def _separate_body(self, body):
        i = 0
        # Loop over lines to find CRLF
        for line in body.splitlines():
            if line == '':
                break
            i += 1
        # Lines before CRLF is header
        header = '\n'.join(line for line in body.splitlines()[:i])
        # Lines after CRLF is body
        body = '\n'.join(line for line in body.splitlines()[i:])
        # Return header and body
        return header, body

    # Getting headers of the body
    def _body_headers(self, header):
        content_type = ""
        content_encoding = ""
        content_type_key = "content-type:"
        content_encoding_key = "content-transfer-encoding:"
        boundary_key = "boundary="
        boundary = None
        for line in header.splitlines():
            line = line.lower()
            if line.find(boundary_key) != -1:
                boundary = line[line.find(boundary_key) + len(boundary_key):]
                boundary = boundary[:boundary.find(';')]
            # To find the content type
            if line.find(content_type_key) != -1:
                start = line.find(content_type_key) + len(content_type_key)
                content_type = line[start:]
                content_type = content_type[:content_type.find(';')].strip()
            # To find the content transfer encoding
            elif line.find(content_encoding_key) != -1:
                content_encoding = line[line.find(content_encoding_key) + len(content_encoding_key):].strip()
        return content_type, content_encoding, boundary

    # Function to get filename
    def _get_attachment(self, header):
        key = "filename="
        for line in header.splitlines():
            index = line.find(key)
            if index != -1:
                start = index + len(key) + 1
                name = line[start:]
                end_index = name.find(";")
                if end_index == -1:
                    name = name[:-1]
                else:
                    name = name[:end_index]
                return True, name
        return False, "File does not exits"

    # Funtion to get text from body according to content-type
    def _get_cleaned_up_body(self, header, body):
        text = body
        if header[1].lower().strip() == "base64":
            text = base64.b64decode(text).decode('utf-8')
        text = self._extract_text_from_html(text)   # defining later
        try:
            text = quopri.decodestring(text).decode()
        except Exception as e:
            pass
        ans = '\n'.join(line for line in text.splitlines() if line).strip(CRLF)
        return ans

    # To get text from html
    def _extract_text_from_html(self, body):
        text = ""
        try:
            soup = BeautifulSoup(body, "html.parser")
            for extras in soup(['script', 'style']):
                extras.extract()
            text = soup.get_text()
        except Exception as e:
            text = body
        ans = ""
        for line in text.splitlines():
            if line.strip() == '':
                continue
            new_line = ""
            for word in line.split(" "):
                new_line += word.strip() + " "
            ans += new_line.strip() + "\n"
        return ans
if __name__ == "__main__":
    load_dotenv('./.env')
    old_mail = os.getenv('EMAIL')
    old_pass = os.getenv('PASSWORD')
    imap = IMAP (email=old_mail, password=old_pass, debugging=True)
    folders = imap.list_mailboxes()
    num = imap.select_mailbox(folders)
    headers = imap.fetch_headers(num , count=2)
    result = imap.fetch_body(num - 6)
    print("IMAP Server ready")
