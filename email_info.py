import curses, textwrap
from imap import IMAP
from loading import Loading
from curses.textpad import rectangle
from Bottom_Line import Bottom_Line
import utils
# class to show details of an mail
class EMAIL_INFO:
        # declaring variables
    subject = ""
    _from = ""  
    _index = -1
    body = ""
    date = ""
    _is_error = False
    _attachment_present = False
    attachment_filenames = []
    _imap = IMAP
    _stdscr = curses.initscr()
    options = []
    # initializing functions
    def __init__(self, stdscr, email_details, imap):
        # initialize the variable
        self._stdscr = stdscr
        self._imap = imap
        self.options = [{'key': 'Q', 'msg': 'Go Back'}]
        # email details
        self._index, self.subject, self._from, self.date = email_details
        self.fetch_body(self._index)
        if not self._is_error:
            self.main()
    # wrap function
    def main(self):
        key = 0
        start = 0
        curses.curs_set(0)
        max_lines = self.main_layout(self.body.splitlines()[start:])
        Bottom_Line(self._stdscr, self.options)
        while key != ord('q'):
            key = self._stdscr.getch()
            flag = False
            if len(self.body.splitlines()) < max_lines:
                flag = True
            if not flag:
                if key == curses.KEY_DOWN and start <= len(self.body.splitlines()) - max_lines - 1:
                    start += 1
                elif key == curses.KEY_UP and start > 0:
                    start -= 1
            if self._attachment_present and key == ord('d'):
                self.download_attachment()
            max_lines = max(self.main_layout(self.body.splitlines()[start:]), max_lines)
            Bottom_Line(self._stdscr, self.options)
            self._stdscr.refresh()
    # function to fetch body
    def fetch_body(self, index):
        try:
            # start loading
            loading = Loading(self._stdscr)
            loading.start()
            response = self._imap.fetch_body(self._index)
            self.body = response['body']
            self._attachment_present = response['is_attachment']
            self.attachment_filenames = response['filename']
            if response['is_attachment']:
                self.options.insert(0, {'key': 'D', 'msg': 'Download Attachment'})
            loading.stop()
        except Exception as e:
            # Terror msg if any
            loading.stop()
            self._is_error = True
            msg = "Something went wrong! Press 'q' to go back"
            self.show_message(msg)
    # function to download attachments
    def download_attachment(self):
        try:
            utils.show_msg_status(stdscr=self._stdscr, msg="Downloading File.....", isLoading=True)
            msg = self._imap.download_attachment(self._index)
            utils.show_msg_status(self._stdscr, msg, time_to_show=3)
        except Exception as e:
            utils.show_msg_status(self._stdscr, str(e), time_to_show=2)
    # function for main page
    def main_layout(self, body):
        from_start = 3
        from_block_total = 4
        subject_lines = 4
        attachment_block = 0
        # height and width
        h, w = self._stdscr.getmaxyx()
        self._stdscr.clear()
        utils.title(self._stdscr, "Email Information")
        # from and to part
        self._stdscr.addstr(from_start, 1, "From: " + self._from)
        rectangle(self._stdscr, from_start - 1, 0, from_start + 1, w - 1)
        # date
        self._stdscr.addstr(from_start + 2, 1, "Date: " + self.date)
        rectangle(self._stdscr, from_start - 1, 0, from_start + 3, w - 1)
        # subject
        rectangle(self._stdscr, from_start + from_block_total, 0, from_start + from_block_total + subject_lines, w - 1)
        self._stdscr.addstr(from_start + from_block_total, 2, " SUBJECT ")
        if len(self.subject.strip()) == 0:
            self.subject = "(no subject)"
        # subject in various lines
        wrapper = textwrap.TextWrapper(width=w - 3)
        elipsize = "....."
        subject_arr = wrapper.wrap(self.subject)
        # wrap text
        for index, subject in enumerate(subject_arr):
            if index == 2:
                subject = subject[0:w - 10] + elipsize
                self._stdscr.addstr(from_start + from_block_total + 1 + index, 1, subject)
                break
            self._stdscr.addstr(from_start + from_block_total + 1 + index, 1, subject)
        # block for attachment
        if self._attachment_present == True:
            attachment_block = 2
            attachment_start = from_start + from_block_total + subject_lines
            # attachment conversion
            filename_string = "  ".join(name for name in self.attachment_filenames)
            attach_arr = wrapper.wrap(filename_string)
            # view attachments
            for item in attach_arr:
                self._stdscr.addstr(attachment_start + attachment_block, 2, item)
                attachment_block += 1
            rectangle(self._stdscr, attachment_start + 1, 0, attachment_start + attachment_block, w - 2)
            self._stdscr.addstr(attachment_start + 1, 2, " Attachments: ")
        # body 
        body_start = from_start + from_block_total + subject_lines + attachment_block
        rectangle(self._stdscr, body_start + 1, 0, h - 5, w - 1)
        self._stdscr.addstr(body_start + 1, 2, " BODY ")
        # break body into parts
        max_lines = (h - 5) - (body_start + 1) - 2
        body_start += 2
        body_end = body_start + max_lines
        for item in body:
            body_arr = wrapper.wrap(item)
            if body_start > body_end:
                break
            for body in body_arr:
                if body_start > body_end:
                    break
                self._stdscr.addstr(body_start, 1, body)
                body_start += 1
        # return max no. of lines
        return max_lines
    # function when mailbox is empty
    def show_message(self, msg):
        h, w = self._stdscr.getmaxyx()
        key = 0
        while key != ord('q'):
            # clear
            self._stdscr.clear()
            self._stdscr.attron(curses.A_BOLD)
            self._stdscr.addstr(h // 2, w // 2 - len(msg) // 2, msg)
            self._stdscr.attroff(curses.A_BOLD)
            # refresh
            self._stdscr.refresh()
            # user input
            key = self._stdscr.getch()