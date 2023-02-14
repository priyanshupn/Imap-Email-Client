import curses, time
from threading import *
# class to load loading 
class Loading:
    # declaring variables    
    _stdscr = curses.initscr()
    text = "LOADING"
    thread = None
    _is_loading = False
    _count = 10
    # functions 
    def __init__(self, stdscr):
        self._stdscr = stdscr
    # function to show loading
    def load(self):
        curses.curs_set(0)
        self._stdscr.clear()
        temp_count = 1
        while self._is_loading:
            self._stdscr.clear()
            text = self.text
            for i in range(temp_count):
                text += "."
            h, w = self._stdscr.getmaxyx()
            x_pos = w // 2 - len(self.text) // 2
            y_pos = h // 2
            self._stdscr.attron(curses.A_BOLD)
            self._stdscr.addstr(y_pos, x_pos, str(text))
            self._stdscr.attroff(curses.A_BOLD)
            temp_count = temp_count % self._count + 1
            time.sleep(0.1)
            self._stdscr.refresh()
     # function to begin loading
    def start(self):        
        self._is_loading = True
        # create the thread to show loading
        self.thread = Thread(target=self.load)
        # start
        self.thread.start()
    # function to stop loading
    def stop(self):
        self._is_loading = False
# main function
def main(stdscr):
    loading = Loading(stdscr)
    loading.start()
    time.sleep(2)
    loading.stop()
if __name__ == "__main__":
    curses.wrapper(main)