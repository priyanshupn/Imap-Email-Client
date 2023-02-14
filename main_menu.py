from menu import Menu
import curses
from write_mail import Write_Mail
from show_folders import Show_Folders
# creating class to show main menu
class Main_Menu:
    # declaring variables
    _menu_strings = ["Logout", "Exit"]
    _menu = []
    _stdscr = curses.initscr()
    # Confirm Email Variables
    _curr_confirm_index = 0
    _confirm_menu = ["YES", "NO"]

    # initializing functions
    def __init__(self, stdscr):
        self._stdscr = stdscr
        menu = [{'title': "Compose mail", 'Function': Write_Mail, 'args': None}]
        menu.append({'title': "Show mails", 'Function': Show_Folders, 'args': None})
        for item in self._menu_strings:
            menu.append({'title': item, 'Function': None, 'args': None})
        self._menu = menu
    # function to show the menu
    def show(self):
        Menu(self._stdscr, self._menu, "Main menu", isMain=True)