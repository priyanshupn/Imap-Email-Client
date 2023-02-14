import curses, time, os, getpass, sys
from login import LOGIN_UI
from dotenv import load_dotenv
from imap import IMAP
from main_menu import Main_Menu
from get_credentials import Credentials
# function to create directory
def createDirectory(dir_path):
    try:
        os.mkdir(dir_path)
    except FileExistsError as e:
        pass
    except Exception as e:
        sys.exit()
# user logging in 
def authenticate():
    cred = Credentials()
    flag, email, password = cred.get_credentials()
    if not flag:
        return flag
    # check if email and password present in file
    if email != None and password != None:
        try:
            IMAP(email, password)
        except:
            # Credentials are invalid
            flag = False
    return flag
# show intro screen
def show_main_intro(stdscr):
    title1 = "**************************************************"
    title2 = "***************** EMAIL_CLIENT *******************"
    title3 = "**************************************************"
    stdscr = curses.initscr()
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.A_BOLD)
    x_pos = w // 2 - (len(title1) // 2)
    y_pos = h // 2 - 1
    stdscr.addstr(y_pos, x_pos, title1)
    stdscr.refresh()
    time.sleep(0.15)
    x_pos = w // 2 - (len(title2) // 2)
    y_pos = h // 2
    stdscr.addstr(y_pos, x_pos, title2)
    stdscr.refresh()
    time.sleep(0.15)
    x_pos = w // 2 - (len(title3) // 2)
    y_pos = h // 2 + 1
    stdscr.addstr(y_pos, x_pos, title3)
    stdscr.refresh()
    flag = authenticate()
    if flag == False:
        time.sleep(0.5)
    while y_pos < h - 3:
        stdscr.clear()
        y_pos += 2
        stdscr.addstr(y_pos - 1, x_pos, title1)
        stdscr.addstr(y_pos, x_pos, title2)
        stdscr.addstr(y_pos + 1, x_pos, title3)
        stdscr.refresh()
        if y_pos < h - 6:
            stdscr.attron(curses.A_DIM)
        time.sleep(0.035)
    stdscr.clear()
    stdscr.refresh()
    stdscr.attroff(curses.A_DIM)
    stdscr.attroff(curses.A_BOLD)
    return flag
# main function
def main(stdscr):
    curses.curs_set(0)
    # get username
    user = getpass.getuser()
    # mail directory path
    dir_path = '/home/'+user+'/.mail'
    createDirectory(dir_path)
    # environment file
    env_path = dir_path + "/.env"
    load_dotenv(env_path)
    is_authenticated = show_main_intro(stdscr)
    # if user authenticated go to main menu
    if is_authenticated == True:
        Main_Menu(stdscr).show()
    # else show the login page
    else:
        LOGIN_UI(stdscr)
if __name__ == "__main__":
    curses.wrapper(main)