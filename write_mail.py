import curses, textwrap
from curses.textpad import Textbox, rectangle
from Bottom_Line import Bottom_Line
from smtp import SMTP
import utils
import email.mime.multipart, email.mime.text, email.mime.application
from get_credentials import Credentials
_stdscr = curses.initscr()
# writing class to create interface to write mail
class Write_Mail:
    # declaring variables
    _stdscr = curses.initscr()
    # sender
    _email_from = ""
    # receiver
    _email_to = ""
    _key = 0
    _title = "Send a new mail"
    # subject of mail
    _subject = ""
    # body of mail
    _body = ""
    _pass = ""
    _attachments = ""
    # flag when mail isn't send yet
    _is_mail_sent = False           # True when sends
    #  email variables 
    _confirm_index = 0
    _confirm_menu = ["YES", "NO"]
    # default messages Ctrl+G to save
    _input_subject_msg = "Enter Subject of Mail "
    _input_msg_body = "Enter body of Mail "
    _attachment_msg = "Enter attachments absolute path"
    # Key variables
    # TODO: Change this key which are placed less
    _BODY_EDIT = ord('b')
    _SUBJECT_EDIT = ord('s')
    _QUIT = ord('q')
    _MAIL_CONFIRM = ord('m')
    _MAIL_TO_KEY_EDIT = ord('t')
    _ATTACHMENT_EDIT = ord('a')
    # initializing functions
    def __init__(self, stdscr):
        curses.curs_set(0)
        self._stdscr = stdscr
        _stdscr.border(0)
        cred = Credentials()
        _, self._email_from, self._pass = cred.get_credentials()
        self._color_pairs()
        self.draw()
    # other functions
    # function showing all elements on screen
    def draw(self):
        start = 0
        max_lines = self._main_layout(self._body.splitlines()[start:])
        while (self._key != self._QUIT) and not self._is_mail_sent:
            self._stdscr.clear()
            h, w = self._stdscr.getmaxyx()
            self._default_screen(self._title, isMain=True)
            max_lines = max(self._main_layout(self._body.splitlines()[start:]), max_lines)
            flag = False
            if len(self._body.splitlines()) < max_lines:
                flag = True
            self._key = self._stdscr.getch()
            if self._key == self._SUBJECT_EDIT:
                self._subject = self._edit_box(self._input_subject_msg, self._input_subject_msg, self._subject)
            elif self._key == self._BODY_EDIT:
                self._body = self._edit_box(self._input_msg_body, self._input_msg_body, self._body, size=h - 4)
            elif self._key == self._ATTACHMENT_EDIT:
                self._attachments = self._edit_box(self._attachment_msg, self._attachment_msg, self._attachments, is_attachment=True)
            elif self._key == self._MAIL_TO_KEY_EDIT:
                self._email_to = self._mail_to(self._email_to).strip()
            elif self._key == self._MAIL_CONFIRM:
                self._default_screen(self._title, isConfirm=True)
            if not flag:
                if self._key == curses.KEY_DOWN and start <= len(self._body.splitlines()) - max_lines - 1:
                    start += 1
                elif self._key == curses.KEY_UP and start > 0:
                    start -= 1
    #******Main Functions*******#
    # function for whole layout of main page
    def _main_layout(self, body):
        from_start = 3
        from_block_total = 4
        subject_lines = 4
        attachment_block = 0
        h, w = self._stdscr.getmaxyx()
        # from, to part
        rectangle(self._stdscr, from_start - 1, 0, from_start + 1, w - 1)
        self._stdscr.addstr(from_start - 1, 2, " To: ")
        self._stdscr.addstr(from_start, 2, self._email_to)
        # Subject part 
        rectangle(self._stdscr, from_start + from_block_total - 1, 0, from_start + from_block_total + subject_lines, w - 1)
        self._stdscr.addstr(from_start + from_block_total - 1, 2, " SUBJECT ")
        # divide subject
        wrapper = textwrap.TextWrapper(width=w - 3)
        elipsize = "....."
        subject_arr = wrapper.wrap(self._subject)
        for index, subject in enumerate(subject_arr):
            if index == 2:
                subject = subject[0:w - 10] + elipsize
                self._stdscr.addstr(from_start + from_block_total + index, 1, subject)
                break
            self._stdscr.addstr(from_start + from_block_total + index, 1, subject)
        # to show the block for attachment
        if len(self._attachments.strip()) != 0:
            attachment_block = 2
            attachment_start = from_start + from_block_total + subject_lines
            # attachment array to string
            filename_string = "  ".join(str(index + 1) + "." + name for index, name in enumerate(self._attachments.split(';')))
            # wrap attachment
            attach_arr = wrapper.wrap(filename_string)
            # Show the attachments
            for item in attach_arr:
                self._stdscr.addstr(attachment_start + attachment_block, 2, item)
                attachment_block += 1
            rectangle(self._stdscr, attachment_start + 1, 0,
                      attachment_start + attachment_block, w - 2)
            self._stdscr.addstr(attachment_start + 1, 2, " Attachments: ")
        # Body part
        body_start = from_start + from_block_total + subject_lines + attachment_block
        rectangle(self._stdscr, body_start + 1, 0, h - 5, w - 1)
        self._stdscr.addstr(body_start + 1, 2, " BODY ")
        # dividing body 
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
        return max_lines
    # to show edit box
    def _edit_box(self, title, input_msg, placeholder="", size=5, is_attachment=False):
        curses.curs_set(1)
        self._default_screen(title)
        _, w = self._stdscr.getmaxyx()
        number_of_lines = size
        number_of_columns = w - 3
        # create a new window
        editwin = curses.newwin(number_of_lines, number_of_columns, 2, 1)
        rectangle(self._stdscr, 1, 0, 2 + number_of_lines, 2 + number_of_columns)
        if is_attachment:
            self._stdscr.addstr(number_of_lines + 3, 1,"* Use ; to separate multiple filepaths")
        self._stdscr.refresh()
        editwin.insstr(placeholder)
        # make it to edit
        box = Textbox(editwin)
        box.edit()
        self._default_screen(self._title, isMain=True)
        curses.curs_set(0)
        return box.gather()
    # edit mail
    def _mail_to(self, to):
        curses.curs_set(1)
        h, w = self._stdscr.getmaxyx()
        to_msg = " To: "
        editwin = curses.newwin(1, w - 5, 3, 2)
        editwin.insstr(to)
        self._stdscr.attron(curses.A_BOLD)
        self._stdscr.addstr(2, 2, to_msg)
        self._stdscr.attroff(curses.A_BOLD)
        self._stdscr.refresh()
        box = Textbox(editwin)
        box.stripspaces = True
        box.edit()
        self._main_layout(self._body.splitlines())
        curses.curs_set(0)
        return box.gather()
    # default screen 
    def _default_screen(self, title, isMain=False, isConfirm=False):
        self._stdscr.clear()
        utils.title(self._stdscr, title)
        if isMain:
            self._bottom_bar()
        # calling main layout function
        if isConfirm:
            self._main_layout(self._body.splitlines())
            self._email_bar()
        self._stdscr.refresh()
    # function for bottom bar
    def _bottom_bar(self):
        options = [
            {'key': 'S', 'msg': 'edit subject of Mail'},
            {'key': 'B', 'msg': 'edit body of mail'},
            {'key': 'M', 'msg': 'send mail'},
            {'key': 'Q', 'msg': 'go back'},
            {'key': 'T', 'msg': 'edit mail To'},
            {'key': 'A', 'msg': 'add attachment'}
        ]
        # show the bottom bar
        Bottom_Line(self._stdscr, options)
    # to show bottom bar
    def _bottom_line_menu(self):
        h, _ = self._stdscr.getmaxyx()
        start_h = h - 3
        for index, item in enumerate(self._confirm_menu):
            y_pos = start_h + index
            # background white
            if self._confirm_index == index:
                self._stdscr.attron(curses.color_pair(1))
            # string
            self._stdscr.addstr(y_pos, 2, item)
            if self._confirm_index == index:
                self._stdscr.attroff(curses.color_pair(1))
        self._stdscr.refresh()
    # function for setting up email bar
    def _email_bar(self):
        h, w = self._stdscr.getmaxyx()
        rectangle(self._stdscr, h - 4, 0, h - 1, w - 2)
        title = " confirm sending email ".upper()
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
                    utils.show_msg_status(self._stdscr, "Sending email....", isLoading=True)
                    try:
                        self._check_validation()
                        # Authenticate
                        smtp = SMTP(self._email_from, self._pass)
                        receiver_emails = self._email_to.split(';')
                        data = smtp.add_attachment(self._subject, self._body, self._attachments.split(';'))
                        smtp.send_email(receiver_emails, data=data)
                        # mail sent successfully message
                        utils.show_msg_status(self._stdscr, "Mail sent Successfully", time_to_show=1.5)
                        self._is_mail_sent = True
                        # quitting smtp
                        smtp.quit()
                    except Exception as e:
                        utils.show_msg_status(self._stdscr, str(e), 2)
                self._default_screen(self._title, isMain=True)
                break
            self._bottom_line_menu()

    # Utility functions
    # function to add attachment in body
    def _setup_body(self):
        msg = email.mime.multipart.MIMEMultipart()
        body = email.mime.text.MIMEText(self._body.strip())
        msg.attach(body)
        paths = self._attachments.split(';')
        for filepath in paths:
            pdf_file = open(filepath.strip(), 'rb')
            attach = email.mime.application.MIMEApplication(pdf_file.read(), _subtype="pdf")
            pdf_file.close()
            attach.add_header("Content-Disposition", "attachment", filename="test.pdf")
            msg.attach(attach)
        return msg.as_string()
    # data filled is valid or not
    def _check_validation(self):
        # check if receiver email is empty
        if self._email_to == "":
            raise Exception("Please Enter Receiver Email")
        # check if subject is empty
        if self._subject == "":
            raise Exception("Please Enter Subject Of Email")
        # check if body is empty
        if self._body == "":
            raise Exception("Please Enter Body Of Email")
    # color pairs required
    def _color_pairs(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
def main(stdscr):
    Write_Mail(stdscr)
if __name__ == "__main__":
    curses.wrapper(main)