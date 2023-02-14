import curses, sys, textwrap
from utils import title
from write_mail import Write_Mail
from curses.textpad import rectangle
from get_credentials import Credentials
import login
_stdscr = curses.initscr()
def temp(stdscr):
    # height and width of screen
    h, w = _stdscr.getmaxyx()
    # at centre
    _stdscr.clear()
    msg = "entered into temporary mode!"
    x_pos = w // 2 - len(msg) // 2
    y_pos = h // 2
    _stdscr.addstr(y_pos, x_pos, msg)
    _stdscr.refresh()
    # If backspace is pressed
    key = _stdscr.getch()
    # input from user
    while key != curses.KEY_BACKSPACE:
        key = _stdscr.getch()
# class which will show menu on screen
class Menu:
    # declaring variables 
    # current index of menu
    _curr_pos = 0  
    # initializing standard screen curses librart
    _stdscr = curses.initscr()
    # menu options available
    _menu = [] 
    _is_main = False
    # TODO: Change this message later
    _screen_size_msg = "Screen size is too small! Please increase screen size"
    _title = ""
    # Confirm Email Variables
    _confirm_index = 0
    _confirm_menu = ["YES", "NO"]

    # initializinf functions
    def __init__(self, stdscr, menu_options, title, isMain=False):
        curses.curs_set(0)
        self._stdscr = stdscr
        self._menu = menu_options
        self._title = " " + title.upper() + " "
        self._is_main = isMain
        self._color_pairs()
        self._menu_display()

        while True:
            key = _stdscr.getch()
            # after pressing key, the action is 
            if key == curses.KEY_UP and self._curr_pos != 0:
                # decrease _curr_pos if up key is there
                self._curr_pos-= 1
            elif key == curses.KEY_DOWN and self._curr_pos != len(self._menu) - 1:
                # increase _curr_pos if down key is pressed
                self._curr_pos += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # the exit signal
                if self._curr_pos == len(self._menu) - 1:
                    # if main menu exit out of app
                    if self._is_main:
                        sys.exit()
                    else:
                        break
                elif self._curr_pos == len(self._menu)-2 and self._is_main:
                    self._email_bar()
                    break
                else:
                    self._press_enter()
                    continue
            self._menu_display()

    # Main function which displays menu
    def _menu_display(self):
        # obtaining height and width of menu
        h, w = self._stdscr.getmaxyx()
        # to store max len
        max_len = 0
        # clear screen
        self._stdscr.clear()
        y_start = h // 2 - len(self._menu) // 2
        # tracking each option
        for index, item in enumerate(self._menu):
            # middle pos of menu
            x_pos = w // 2 - len(item['title']) // 2
            y_pos = y_start + index
            # make background white of selected item
            if self._curr_pos == index:
                self._stdscr.attron(curses.color_pair(1))
            title = "  " + item['title'] + "  "
            # max len of title
            if max_len < len(title):
                max_len = len(title)
            # string on screen
            self._stdscr.addstr(y_pos, x_pos, title)
            # turn off the attribute
            if self._curr_pos == index:
                self._stdscr.attroff(curses.color_pair(1))
        # start position of menu
        y_end = h // 2 + len(self._menu) // 2
        x_start = w // 2 - max_len // 2
        x_end = w // 2 + max_len // 2
        # padding
        if x_start - 4 > 1:
            x_start -= 4
        else:
            x_start -= 2
        if x_start + 8 < w - 1:
            x_end += 8
        else:
            x_start += 2
        if y_start - 4 > 1:
            y_start -= 4
        else:
            y_start -= 2
        if y_end + 4 < h - 1:
            y_end += 4
        else:
            y_end += 1
        try:
            # title of menu and rectangle
            rectangle(self._stdscr, y_start, x_start, y_end, x_end)
            self._stdscr.attron(curses.A_BOLD)
            self._stdscr.addstr(y_start, w // 2 - len(self._title) // 2 + 2, self._title)
            self._stdscr.attroff(curses.A_BOLD)
            # Refresh
            self._stdscr.refresh()
        except:
            # menu not show exception
            self._stdscr.clear()
            wrapper = textwrap.TextWrapper(width=w-2)
            error_msgs = wrapper.wrap(self._screen_size_msg)
            for index, msg in enumerate(error_msgs):
                x_pos = w // 2 - len(msg) // 2
                y_pos = h // 2 + index
                self._stdscr.addstr(y_pos, x_pos, msg)
            self._stdscr.refresh()

    # function defininig what actions to be taken after pressing enter
    def _press_enter(self):
        if self._menu[self._curr_pos] == "STDSCR_NR":
            self._menu[self._curr_pos]['Function']()
        elif self._menu[self._curr_pos] != None:
            arguements = self._menu[self._curr_pos]
            arg1, arg2 = arguements
            self._menu[self._curr_pos]['Function'](arguements)
        else:
            # call desired function
            self._menu[self._curr_pos]['Function'](self._stdscr)
        # Display menu 
        self._menu_display()

    # Utility Function
    # to setup color pairs
    def _color_pairs(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # function to display logout button
    def _bottom_line_menu(self):
        h, _ = self._stdscr.getmaxyx()
        start_h = h - 3
        for index, item in enumerate(self._confirm_menu):
            y_pos = start_h + index
            # highlight the background 
            if self._confirm_index == index:
                self._stdscr.attron(curses.color_pair(1))
            # printing string
            self._stdscr.addstr(y_pos, 2, item)
            if self._confirm_index == index:
                self._stdscr.attroff(curses.color_pair(1))
        self._stdscr.refresh()
    # cnfrm email for logout
    def _email_bar(self):
        h, w = self._stdscr.getmaxyx()
        title = " Do you want to logout ".upper()
        rectangle(self._stdscr, h - 4, 0, h - 1, w - 2)
        self._stdscr.attron(curses.A_BOLD)
        self._stdscr.addstr(h - 4, 1, title)
        self._stdscr.attroff(curses.A_BOLD)
        self._bottom_line_menu()
        while True:
            key = self._stdscr.getch()
            if key == curses.KEY_UP and self._confirm_index != 0:
                self._confirm_index -= 1
            elif key == curses.KEY_DOWN and self._confirm_index != len(self._confirm_menu) - 1:
                self._confirm_index += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self._confirm_index == 0:
                    cred = Credentials()
                    cred.remote_credentials()
                    login.LOGIN_UI(self._stdscr)
                break
            self._bottom_line_menu()
menu_strings = ["View email", "Logout", "Exit"]
def main(stdscr):
    menu = [{'title': "Compose mail", 'Function': Write_Mail}]
    for item in menu_strings:
        menu.append({'title': item, 'Function': temp})
    Menu(_stdscr, menu, "Sample Menu", isMain=True)
if __name__ == "__main__":
    curses.wrapper(main)