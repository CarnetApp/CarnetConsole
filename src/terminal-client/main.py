import curses
import curses.textpad
from os import path
import shutil
import time;

from .note_manager import NoteManager
from .settings_manager import *
from .path_lister import *
from .latest_lister import *
from .recent_db_manager import RecentDBManager

import logging
class Screen(object):
    UP = -1
    DOWN = 1

    def __init__(self):
        self.logger = logging.getLogger(__file__)
        hdlr = logging.FileHandler("/home/phie/carnetty" + ".log")
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.DEBUG)

        self.logger.info("begin")
        """ Initialize the screen window
        Attributes
            window: A full curses screen window
            width: The width of `window`
            height: The height of `window`
            max_lines: Maximum visible line count for `result_window`
            top: Available top line position for current page (used on scrolling)
            bottom: Available bottom line position for whole pages (as length of items)
            current: Current highlighted line number (as window cursor)
            page: Total page count which being changed corresponding to result of a query (starts from 0)
            ┌--------------------------------------┐
            |1. Item                               |
            |--------------------------------------| <- top = 1
            |2. Item                               | 
            |3. Item                               |
            |4./Item///////////////////////////////| <- current = 3
            |5. Item                               |
            |6. Item                               |
            |7. Item                               |
            |8. Item                               | <- max_lines = 7
            |--------------------------------------|
            |9. Item                               |
            |10. Item                              | <- bottom = 10
            |                                      |
            |                                      | <- page = 1 (0 and 1)
            └--------------------------------------┘
        Returns
            None
        """
        self.window = None

        self.width = 0
        self.height = 0

        self.init_curses()

        self.current_view = "Latest"
        self.refreshItemsList()
        self.line_per_items=4
        self.top_margin = 4
        self.bottom_margin = 1

        self.max_lines = curses.LINES - self.top_margin - self.bottom_margin
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

        self.notesMetadata = {}
        self.current_directory = "/"

        
        import _thread
        _thread.start_new_thread( self.merge, ("Thread-1", 2, ))

    def merge(self, threadName, delay):
        recentDBManager = RecentDBManager()
        if(recentDBManager.merge()):
            self.switchToCurrentView(True)

    def init_curses(self):
        """Setup the curses"""
        self.window = curses.initscr()
        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_MAGENTA)

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

    def run(self):
        """Continue running the TUI until get interrupted"""
        try:
            self.display()
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()

    def input_stream(self):
        """Waiting an input and run a proper method according to type of input"""
        while True:
            

            ch = self.window.getch()
            if ch == curses.KEY_UP:
                self.scroll(self.UP)
                self.display()
            elif ch == curses.KEY_DOWN:
                self.scroll(self.DOWN)
                self.display()
            elif ch == curses.KEY_LEFT:
                self.paging(self.UP)
                self.display()
            elif ch == curses.KEY_RIGHT:
                self.paging(self.DOWN)
                self.display()
            elif ch == ord('\t'):
                if(self.current_view == "Latest"):
                    self.current_view = "Browser"
                else:
                    self.current_view = "Latest"
                self.switchToCurrentView()
                self.display()
            elif ch == ord('n'):
                try:
                    shutil.rmtree("/tmp/carnettty")
                except FileNotFoundError:
                    None
                noteManager = NoteManager()
                notePath = noteManager.createNewNote(self.current_directory, "/tmp/carnettty")
                self.openNote(notePath,False, True)
                self.switchToCurrentView(True)
                    

            elif ch == ord('p'):
                noteManager = NoteManager(settingsManager.getNotePath()+"/"+self.items[self.top +self.current]['path'])
                noteManager.extractNote("/tmp/carnettty")
                import subprocess
                
                curses.savetty()
                curses.endwin()
                subprocess.run(['lynx','/tmp/carnettty/index.html'])
                curses.resetty()
                curses.curs_set(0)
                self.window.refresh()
                self.display()
            elif ch == 10:
                self.openNote(self.items[self.top +self.current]['path'])       

            elif ch == curses.ascii.ESC:
                break

    def saveNoteIfChanged(self, noteManager, notePath, addToRecent, mod_date):
        new_mod_date = os.stat('/tmp/carnettty/index.html').st_mtime
        if(mod_date != new_mod_date):
            #we need to save
            noteManager.saveCurrentNote("/tmp/carnettty")
            if(addToRecent):
                notePath = notePath
                while(notePath.startswith("/")):
                    notePath = notePath[1:]
                actions = []
                action = {}
                action['action'] = "add"
                action['time'] = int(time.time() * 1000)
                action['path'] = notePath
                actions.append(action)
                recentDBManager = RecentDBManager()
                recentDBManager.addActionsToMyDB(actions)
                
        return new_mod_date

    def saveNoteThread(self, noteManager, notePath, addToRecent, mod_date):
        while self.shouldSave:
            
            new_mod_date = self.saveNoteIfChanged(noteManager, notePath, addToRecent, mod_date)
            mod_date = new_mod_date
            for i in range(0,20):
               if(self.shouldSave):
                  time.sleep(0.2)


    # returns true if modified, false otherwise
    def openNote(self, path, extract=True, addToRecent=False):
       
        noteManager = NoteManager(settingsManager.getNotePath()+"/"+path)
        if(extract):
            noteManager.extractNote("/tmp/carnettty")
        import subprocess
        
        f = open("/tmp/carnettty/index_tidy.html", "w")

        proc = subprocess.Popen(['tidy','--hide-comments', 'yes','--show_warnings', 'no',  '--show-body-only', 'yes', '-indent', '--indent-spaces', '2',   '--quiet', 'yes',   '--tidy-mark', 'no', '/tmp/carnettty/index.html'], stdout=subprocess.PIPE,
                        universal_newlines=True)
        data = proc.stdout.read()
        
        f.write(data)
        f.close()
        #subprocess.run(['tidy', "/tmp/carnettty/index.html", "--show-body-only", "yes"], stdout=f)
        subprocess.run(['sed', '-i', '/floating/d', '/tmp/carnettty/index_tidy.html']) 
        try:
            os.remove("/tmp/carnettty/index.html")
        except FileNotFoundError:
            None
        os.rename("/tmp/carnettty/index_tidy.html", "/tmp/carnettty/index.html")    
        curses.savetty()
        curses.endwin()
        mod_date = os.stat('/tmp/carnettty/index.html').st_mtime
        import _thread
        #pb ici: le shoudSave passe à false après, puis à nouveau à true pendannt le sleep du coup l'ancien thread continue
        self.shouldSave = True
        from threading import Thread
        th = Thread(target=self.saveNoteThread, args=(noteManager, path, addToRecent, mod_date,))
        th.start()
#        th = _thread.start_new_thread( self.saveNoteThread, (noteManager, path,  addToRecent, mod_date))
        subprocess.run(['nano', '-$cwS', "/tmp/carnettty/index.html"])
        self.shouldSave = False
        th.join()
        self.saveNoteIfChanged(noteManager, path, addToRecent, mod_date)
      

            
        #subprocess.run(['lynx','-dump', '/tmp/carnettty/index_tidy.html'])
        curses.resetty()
        curses.curs_set(0)
        self.window.refresh() 
        self.display(True)

    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.current + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            return
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        if (direction == self.DOWN) and (next_line == int(self.max_lines/self.line_per_items)) and (self.top + int(self.max_lines/self.line_per_items) < self.bottom):
            self.top += direction
            return
        # Scroll up
        # current cursor position or top position is greater than 0
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            return
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        if (direction == self.DOWN) and (next_line < int(self.max_lines/self.line_per_items)) and (self.top + next_line < self.bottom):
            self.current = next_line
            return

    def paging(self, direction):
        """Paging the window when pressing left/right arrow keys"""
        current_page = (self.top + self.current) // self.max_lines
        next_page = current_page + direction
        # The last page may have fewer items than max lines,
        # so we should adjust the current cursor position as maximum item count on last page
        if next_page == self.page:
            self.current = min(self.current, self.bottom % self.max_lines - 1)

        # Page up
        # if current page is not a first page, page up is possible
        # top position can not be negative, so if top position is going to be negative, we should set it as 0
        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return
        # Page down
        # if current page is not a last page, page down is possible
        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return
    
    def refreshItemsList(self):
        if(self.current_view == "Browser"):
            lister = PathLister(self.current_directory)
        else:
            lister = LatestLister()
        self.items = lister.getList()
        
    def switchToCurrentView(self, display=True):
        self.refreshItemsList()
        self.top = 0
        self.current = 0
        self.current_page = 0
        self.bottom = len(self.items)
        self.page = self.bottom // self.max_lines
        if(display):
            self.display()

    def displayCommands(self):
        print ("pet")

    def display(self, refreshMetadata=False):
        """Display the items on window"""
        self.window.erase()
        num_rows, num_cols = self.window.getmaxyx()
        middle_row = int(num_rows / 2)

        # Calculate center column, and then adjust starting position based
        # on the length of the message
        title = "📓 Carnet - TTY Edition"
        half_length_of_title = int(len(title) / 2)
        middle_column = int(num_cols / 2)
        x_position_title = middle_column - half_length_of_title
        subtitle = str(self.top+self.current+1)+" / "+str(len(self.items))
        half_length_of_subtitle = int(len(subtitle) / 2)
        x_position_subtitle = middle_column - half_length_of_subtitle
        self.window.addstr(1, x_position_title, title, curses.color_pair(1))
        self.window.addstr(2, x_position_subtitle, subtitle, curses.color_pair(1))
        self.window.addstr(2, self.width - 9, "Syncing", curses.color_pair(1) | curses.A_BLINK)
        view_txt = "Views:"
        latest_txt = "Latest"
        self.window.addstr(2, 3, view_txt, curses.color_pair(1))
        if(self.current_view == "Latest"):
            form = curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE
        else:
            form = curses.color_pair(1)
        self.window.addstr(2, 3+1+len(view_txt), latest_txt, form)
        if(self.current_view == "Browser"):
            form = curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE
        else:
            form = curses.color_pair(1)
        self.window.addstr(2, 3+len(view_txt)+1+len(latest_txt)+1, "Browser", form)
        
        for idx, item in enumerate(self.items[self.top:self.top + int(self.max_lines/self.line_per_items)]):
            # Highlight the current cursor line
            
            long_space="                                                                                                                            "
            title = " "+path.basename(item['name'])[0:self.width-5]+" "
            title = title+long_space[0:self.width-3-len(title)]
            if(item['isFile']):
                try:
                    note = self.notesMetadata[item['path']]
                except KeyError:
                    note = -1 #-1 because none can mean that notesMetadata hasn't found it, no need to reload, then
                if(note == -1 or refreshMetadata):
                    noteManager = NoteManager(settingsManager.getNotePath()+item['path'])
                    note = noteManager.getCachedMetadata()
                    self.notesMetadata[item['path']] = note
                if(note != None):
                    text = note["shorttext"].strip().replace("\n", " ").replace("  ", " ").replace("  ", " ")[0:self.width-5]
                else:
                    text = ""
            else:
                text=""
            text = " "+text+" "
            text = text+long_space[0:self.width-3-len(text)]
            if idx == self.current:
                self.window.addstr(idx*self.line_per_items+self.top_margin, 2, title, curses.color_pair(2)| curses.A_BOLD )
            else:
                self.window.addstr(idx*self.line_per_items+self.top_margin, 2, title, curses.color_pair(1)| curses.A_BOLD )
            if idx == self.current:
                self.window.addstr(idx*self.line_per_items+1+self.top_margin, 2, text, curses.color_pair(2))
            else:
                self.window.addstr(idx*self.line_per_items+1+self.top_margin, 2, text, curses.color_pair(1))
            self.window.addstr(idx*self.line_per_items+2+self.top_margin, 2, "", curses.color_pair(1)| curses.A_BOLD | curses.A_UNDERLINE)
        bottom_txt = "<enter> Edit note <d> Display all commands <n> New Note <p> Preview html note <tab> Switch view <s> Settings"
        bottom_txt = bottom_txt[0:self.width-5]
        self.window.addstr(self.max_lines + self.top_margin, 1, bottom_txt, curses.color_pair(1))
        self.window.refresh()







def main(version):
    screen = Screen()
    screen.run()
if __name__ == '__main__':
    main(1)