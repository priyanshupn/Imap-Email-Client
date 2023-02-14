import curses
# class to show bottom instructions
class Bottom_Line:
    # declaring variables
    _stdscr = curses.initscr()  # initializing curses library
    _options = []               # options avaiable at the bottom
    # Initialzing function
    def __init__(self, stdscr, options):
        self._stdscr = stdscr
        self._options = options
        self._bottom_bar()
    # Private Functions
    # setting the bottom bar
    def _bottom_bar(self):
        # getting height and width of the bottom bar
        h, w = self._stdscr.getmaxyx()
        # To show horizontal line
        self._stdscr.hline(h-4, 0, curses.ACS_HLINE, w)
        # to show all the options, loop
        x_start = 1
        for index, item in enumerate(self._options):
            start = h-3
            if index % 2 == 1: 
                start = h-2
            self._bottom_instruction(start, x_start, " " + item['key'] + ":", " " + item['msg'])
            if index % 2 == 1:
                x_start += 30
    # Utility function to show bottom instruction
    def _bottom_instruction(self, y_pos, x_pos, key, instruction):
        try:
            self._stdscr.attron(curses.A_STANDOUT)
            self._stdscr.addstr(y_pos, x_pos, key)
            self._stdscr.attroff(curses.A_STANDOUT)
            self._stdscr.attron(curses.A_BOLD)
            self._stdscr.addstr(y_pos, x_pos + len(key) , instruction)
            self._stdscr.attroff(curses.A_BOLD)
        except:
            return