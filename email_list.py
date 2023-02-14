import curses, textwrap
from Bottom_Line import Bottom_Line
from loading import Loading
from imap import IMAP
from email_info import EMAIL_INFO
from curses.textpad import rectangle
import utils
# class to show email list
class EMAIL_LIST:
    # declaring variables
    _stdscr = curses.initscr()
    # mailbox name
    _directory_name = "/home/piryanshu/Desktop/CN_PROJECT"  
    # to check error
    _is_error = False  
    # storing imap variable
    _imap = IMAP  
    _curr_position = 0
    _arr_position = 0
    _num = 0
    _fetched_emails = 0
    _max_len = 20
    is_end = False
    # key options
    options = [
        {'key': 'd', 'msg': 'Delete Mail'},
        {'key': 'q', 'msg': 'Go Back'},
        {'key': '⇵', 'msg': 'Navigate through emails'},
        {'key': '⏎', 'msg': 'To See Details'},
        {'key': 'f', 'msg': "fetch more emails"}
    ]
    _main_list = []
    _display_list = []
    emails = []
    # email variables
    _confirm_index = 0
    confirm_menu = ["YES", "NO"]
    # check if fetching email is true
    _is_fetching_emails = True
    # initializing functions
    def __init__(self, stdscr, directory_name, imap):
        # To disable cursor
        curses.curs_set(0)
        # the variables
        self._stdscr = stdscr
        self._directory_name = directory_name
        self._imap = imap
        self._main_list = []
        self.main()
    # logical functions
    def main(self):
        # fetching mails
        self.fetch_emails()
        if not self._is_error:
            # to show instructions
            self._bottom_bar()
            # emails list
            self.main_layout()
            # refresh
            self._stdscr.refresh()
    # function to fetch mail from imap
    def fetch_emails(self):
        try:
            # load until mails being fetched
            loading = Loading(self._stdscr)
            loading.start()
            # Select  mailbox
            num = self._imap.select_mailbox(self._directory_name)
            if num == 0:
                loading.stop()
                self._is_error = True
                msg = "Nothing in " + \
                    self._directory_name.replace('"', '') + "!! Press 'q' to go back"
                utils.show_message(self._stdscr, msg)
                return
            self._num = num
            # first fetch 30 mails
            count = min(self._num - 1, 30)
            if (self._num - self._fetched_emails) > 0:
                emails = self._imap.fetch_headers(self._num - self._fetched_emails, count)
                self._fetched_emails += count + 1
                self._main_list.extend(emails)
                self.emails = emails
            else:
                self.is_end = True
            loading.stop()
        except Exception as e:
            # error message
            loading.stop()
            self._is_error = True
            msg = "Something went wrong! Press 'q' to go back"
            utils.show_message(self._stdscr, msg)
    # to bring main layout setup
    def main_layout(self):
        try:
            key = 0
            arr_start = 0
            # mails which can be shown on a single page
            self._display_list = self._main_list
            self._max_len = self.email_list()
            while key != ord('q'):
                key = self._stdscr.getch()
                # up key
                if key == curses.KEY_UP and self._arr_position != 0:
                    self._curr_position -= 1
                    self._arr_position -= 1
                    # to show previous page
                    if self._curr_position == -1:
                        arr_start = arr_start - self._max_len
                        self._curr_position = self._max_len - 1
                # down key
                elif key == curses.KEY_DOWN:
                    if self._arr_position != len(self._main_list) - 1:
                        self._curr_position += 1
                        self._arr_position += 1
                        # to show next page
                        if self._curr_position >= self._max_len:
                            arr_start = self._arr_position
                            # reset current position
                            self._curr_position = 0
                # key d
                elif key == ord('d'):
                    self.email_bar()
                # another set of mails
                elif key == ord('f'):
                    self.fetch_emails()
                # enter key
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    # show details of email
                    EMAIL_INFO(self._stdscr,
                               (self._num - self._arr_position, self._main_list[self._arr_position]['Subject'],
                                self._main_list[self._arr_position]['From'], self._main_list[self._arr_position]['Date']),
                               self._imap)
                # end of display
                arr_end = min(arr_start + self._max_len,len(self._main_list))
                # the email list
                self._display_list = self._main_list[arr_start:arr_end]
                self._max_len = max(self.email_list(), self._max_len)
                # if mails are end 
                if self.is_end:
                    utils.show_msg_status(self._stdscr, "No more emails available to fetch!!", time_to_show=2)
                    self.is_end = False
        except Exception as e:
            msg = "Something went wrong! Press 'q' to go back"
            utils.show_message(self._stdscr, msg)
    # function to show list of email
    def email_list(self, isConfirm=False):
        try:
            # height and width 
            h, w = self._stdscr.getmaxyx()
            self._stdscr.clear()
            # title
            title = "Emails in " + self._directory_name
            utils.title(self._stdscr, title)
            # Start
            start = 2
            i = 0
            while start < h - 5 and i < len(self._display_list):
                is_focused = i == self._curr_position
                # show email
                start = self.mail_item(start, self._display_list[i]['Subject'],
                                             self._display_list[i]['From'],
                                             self._display_list[i]['Date'], h, w, is_focused=is_focused)
                i += 1
            # email menu
            if isConfirm:
                rectangle(self._stdscr, h - 4, 0, h - 1, w - 2)
                title = " Do you want to delete email? ".upper()
                self._stdscr.attron(curses.A_BOLD)
                self._stdscr.addstr(h - 4, 1, title)
                self._stdscr.attroff(curses.A_BOLD)
                self._bottom_menu()
            else:
                self._bottom_bar()
            # refresh
            self._stdscr.refresh()
            # total no. of shown emails
            return i
        except:
            utils.show_message(self._stdscr, "Something went wrong! Press 'q' to go back")
    # to show a particular mail
    def mail_item(self, start, subject, mail_from, date, height, width, is_focused=False, is_seen=False):
        curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        if is_focused:
            self._stdscr.attron(curses.color_pair(10))
            self._stdscr.attron(curses.A_BOLD)
        # date and mail from
        mail_from = "From: " + mail_from
        formatted_date = "Date: " + date
        old_start = start - 1
        date_start = width - len(formatted_date) - 2
        if len(subject.strip()) == 0:
            subject = "(no subject)"
        #self._stdscr.attron(curses.A_BOLD)
        wrapper = textwrap.TextWrapper(width=width - 2)
        formatted_subject = wrapper.wrap(subject)
        for index, subject in enumerate(formatted_subject):
            flag = False
            if index == 1:
                ellipsize = "...."
                sub_end = min(width - 15, len(subject))
                # add ellipses
                if sub_end != len(subject):
                    subject = subject[0:sub_end] + ellipsize
                    # make flag true
                    flag = True
            self._stdscr.addstr(start, 1, subject)
            start += 1
            if flag:
                break
        # mail from
        self._stdscr.addstr(start, 1, mail_from)
        # date
        self._stdscr.addstr(start, date_start, formatted_date)
        start += 1
        # h line at end 
        self._stdscr.hline(start, 0, curses.ACS_HLINE, width)
        start += 1
        if is_focused:
            self._stdscr.attroff(curses.color_pair(10))
            rectangle(self._stdscr, old_start, 0, start - 1, width - 1)
            self._stdscr.attroff(curses.A_BOLD)
        # Return
        return start
    # function for email bar 
    def email_bar(self):
        try:
            h, w = self._stdscr.getmaxyx()
            self._stdscr.clear()
            self.email_list(isConfirm=True)
            while True:
                key = self._stdscr.getch()
                if key == curses.KEY_UP and self._confirm_index != 0:
                    self._confirm_index -= 1
                elif key == curses.KEY_DOWN and self._confirm_index != len(self.confirm_menu) - 1:
                    self._confirm_index += 1
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if self._confirm_index == 0:
                        utils.show_msg_status(self._stdscr, "Deleting email....", isLoading=True)
                        try:
                            num = self._imap.delete_email(self._num - self._arr_position)
                            # new mail count
                            self._num = num
                            main_list_length = len(self._main_list)
                            # update array
                            self._main_list.pop(self._arr_position)
                            if main_list_length - 1 == self._arr_position:
                                self._curr_position -= 1
                                self._arr_position -= 1
                            # success of mail
                            utils.show_msg_status(self._stdscr, "Mail deleted Successfully", time_to_show=1)
                        except Exception as e:
                            utils.show_msg_status(self._stdscr, str(e), 2)
                    self.email_list()
                    break
                self.email_list(isConfirm=True)
        except:
            utils.show_message(self._stdscr, "Something went wrong! Press 'q' to go back")
    # function to show email bottom
    def _bottom_menu(self):
        h, l = self._stdscr.getmaxyx()
        start_h = h - 3
        for index, item in enumerate(self.confirm_menu):
            y_pos = start_h + index
            # make background white 
            if self._confirm_index == index:
                self._stdscr.attron(curses.color_pair(1))
            # string 
            self._stdscr.addstr(y_pos, 2, item)
            if self._confirm_index == index:
                self._stdscr.attroff(curses.color_pair(1))
        self._stdscr.refresh()

    # utility function
    # function for bottom bar
    def _bottom_bar(self):
        Bottom_Line(self._stdscr, self.options)
# main function
def main(stdscr):
    EMAIL_LIST(stdscr, "INBOX", None)
if __name__ == "__main__":
    curses.wrapper(main)