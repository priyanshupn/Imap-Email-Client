import curses, time
# show status message while authenticating
def show_msg_status(stdscr, msg, time_to_show = -1, isLoading=False):
    stdscr = curses.initscr()
    h, w = stdscr.getmaxyx()
    if isLoading:
        stdscr.attron(curses.A_BLINK)
    stdscr.attron(curses.A_STANDOUT)
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(h - 5, w // 2 - len(msg) // 2, " " + str(msg) +  " ")
    stdscr.refresh()
    if time_to_show != -1:
        time.sleep(time_to_show)
    # disable attributes
    stdscr.attroff(curses.A_STANDOUT)
    stdscr.attroff(curses.A_BOLD)
    if isLoading:
        stdscr.attroff(curses.A_BLINK)
# show msg when mailbox is empty
def show_message(stdscr, msg):
    stdscr = curses.initscr()
    h, w = stdscr.getmaxyx()
    key = 0
    while key != ord('q'):
        # Clear the screen
        stdscr.clear()
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(h // 2, w // 2 - len(msg) // 2, msg)
        stdscr.attroff(curses.A_BOLD)
        # Refresh the screen
        stdscr.refresh()
        key = stdscr.getch()
# to show title        
def title(stdscr, title):
    stdscr = curses.initscr()
    x, w = stdscr.getmaxyx()
    # set title at centre and background white
    count = w // 2 - len(title) // 2
    temp_title = ""
    for x in range(count):
        temp_title += " "
    temp_title += title.upper()
    for x in range(count - 1):
        temp_title += " "
    # title print
    stdscr.attron(curses.A_STANDOUT)
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(0, 0, temp_title)
    stdscr.attroff(curses.A_BOLD)
    stdscr.attroff(curses.A_STANDOUT)
    stdscr.refresh()