from curses.textpad import rectangle
import textwrap, curses, utils
from Bottom_Line import Bottom_Line
# class to show instructions on login screen
class Instructions:
    # declaring variables
    # standard screen of curses
    _stdscr = curses.initscr()
    _less_secure = ["1. Go to your Google Account",
                     "2. Select Security. ",
                     "3. Click Turn on access link under Less secure app access section in right.",
                     "4. Now turn on Allow less secure apps:ON toggle button in the new page.",
                     "5. Now login to app using your email and password"
                     ]
    options = [{'key': 'Q', 'msg': 'Go Back'}]
    _screen_size_msg = "Screen size is too small! Please increase screen size"
    # defining functions
    def __init__(self, stdscr):
        self._stdscr = stdscr
        self._main_layout()
    # function for layout
    def _main_layout(self):
        key = 0
        while key != ord('q'):
            h, w = self._stdscr.getmaxyx()
            try:
                wrapper = textwrap.TextWrapper(width = w - 3)
                self._stdscr.clear()
                utils.title(self._stdscr, "LOGIN INSTRUCTIONS")
                start = self._array_text(wrapper, w, start + 2, self._less_secure, " Enable less Secure apps :  ")
                # show the bottom bar
                Bottom_Line(self._stdscr, self.options)
                self._stdscr.refresh()
                key = self._stdscr.getch()
            except:
                self._stdscr.clear()
                wrapper = textwrap.TextWrapper(width=w-2)
                error_msgs = wrapper.wrap(self._screen_size_msg)
                for index, msg in enumerate(error_msgs):
                    x_pos = w // 2 - len(msg) // 2
                    y_pos = h // 2 + index
                    self._stdscr.addstr(y_pos, x_pos, msg)
                self._stdscr.refresh()
    # function for text
    def _array_text(self, wrapper, width, st, text, title):
        old_start = st  # st = start of the text
        start = old_start + 1
        start += 1
        for item in text:
            item_arr = wrapper.wrap(item)
            for subitem in item_arr:
                self._stdscr.addstr(start, 2, subitem)
                start += 1
        rectangle(self._stdscr, old_start, 0, start, width - 2)
        self._stdscr.attron(curses.A_BOLD)
        self._stdscr.addstr(old_start, 1, title)
        self._stdscr.attroff(curses.A_BOLD)
        return start