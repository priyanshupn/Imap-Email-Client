from imap import IMAP
from loading import Loading
from menu import Menu
import curses
from email_list import EMAIL_LIST
import utils
from get_credentials import Credentials
# class to show mailboxes
class Show_Folders:
    # declaring variables
    _stdscr = curses.initscr()
    # functions
    def __init__(self, stdscr):
        self._stdscr = stdscr
        loading = Loading(stdscr)
        loading.start()
        try:
            cred = Credentials()
            flag, email, password = cred.get_credentials()
            if not flag:
                raise Exception("Invalid credentials")
            imap = IMAP(email, password)
            folders = imap.list_mailboxes()
            options = []
            for item in folders:
                options.append({'title': item.replace('"', ''), 'Function': EMAIL_LIST, 'args': (item, imap)})
            options.append({'title': "Back", 'Function': None, 'args': None})
            loading.stop()
            Menu(self._stdscr, options, "Folders")
        except:
            loading.stop()
            utils.show_message(self._stdscr, "Something went wrong! Press 'q' to go back")