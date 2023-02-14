from cryptography.fernet import Fernet
import getpass, os
from dotenv import load_dotenv
# class which stores email and pass 
class Credentials:
    _dir_path = ""
    _env_path = ""
    # initialing function
    def __init__(self):
        user = getpass.getuser()
        self._dir_path = os.path.join("/home", user, "cn.mail")
        self._env_path = os.path.join(self._dir_path, "cred.env")
    # function to create encryption
    def _create_key(self):
        key_name = '.mail.key'
        key_path = os.path.join(self._dir_path, key_name)
        try:
            open(key_path)
        except Exception as e:
            key = Fernet.generate_key()
            key_file = open(key_path, 'wb')
            key_file.write(key)
            key_file.close()
    # to get key
    def __get_key(self):
        key_file_name = '.mail.key'
        key_path = os.path.join(self._dir_path, key_file_name)
        key = open(key_path, 'rb').read()
        return key
    # to get email and pass
    def get_credentials(self):
        try:
            self._decrypt_file()
            load_dotenv(self._env_path)
            password = os.getenv("PASSWORD")
            email = os.getenv("EMAIL")
            os.remove(self._env_path)
            return True, email, password
        except:
            return False, " ", " "
    # function for decrypt file to write email and pass
    def _decrypt_file(self):
        f = Fernet(self.__get_key())
        encrypted_file_path = os.path.join(self._dir_path, ".env.encrypted")
        with open(encrypted_file_path, 'rb') as test:
            data = test.read()
        credentials = f.decrypt(data).decode()
        with open(self._env_path, 'w') as env_file:
            env_file.write(credentials)
    # function to store 
    def store_credentials(self, email, password):
        fi = open(self._env_path, "w")
        fi.write("EMAIL=" + email + "\n")
        fi.write("PASSWORD=" + password + "\n")
        fi.close()
        self._encrypt_file()
        os.remove(self._env_path)
    # function to encrypt file
    def _encrypt_file(self):
        self._create_key()
        f = Fernet(self.__get_key())
        with open(self._env_path, 'rb') as test:
            data = test.read()
        encrypted = f.encrypt(data)
        encrypted_file_path = os.path.join(self._dir_path, ".env.encrypted")
        with open(encrypted_file_path, 'wb') as enc:
            enc.write(encrypted)
    # function to remove email and pass on logout
    def remote_credentials(self):
        try:
            encrypted_file_path = os.path.join(self._dir_path, ".env.encrypted")
            os.remove(encrypted_file_path)
        except:
            pass
# main function
if __name__ == "__main__":
    cred = Credentials()
    cred.store_credentials("nandagawalipp19.comp@coep.ac.in", "priya@1234")
    print(cred.get_credentials())