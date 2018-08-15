import curses
from enum import Enum

class Stage(Enum):
    SELECTION = 1
    REPLACEMENT = 2

KEYS_UP = (curses.KEY_UP,)
KEYS_DOWN = (curses.KEY_DOWN,)
KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_RIGHT = (curses.KEY_RIGHT,)
KEYS_LEFT = (curses.KEY_LEFT,)
KEYS_EXIT = (27,)


class Interactive:
    '''
    Manages an interactive decryption session
    '''

    def __init__(self, texts, indicator='^', default_index=0, on_change_hook=None):
        '''Initalise the session'''
        self.texts = texts
        self.indicator = indicator
        self.index = default_index
        self.level = 0
        self.stage = Stage.SELECTION
        self.on_change_hook = on_change_hook

    def get_lines(self):
        line = []
        for i in range(len(self.texts)):
            if i == self.level:
                line += [self.texts[i], ' ' * self.index + self.indicator]
            else:
                line += [self.texts[i]]

        if self.stage == Stage.SELECTION:
            return line, self.index
        elif self.stage == Stage.REPLACEMENT:
            line += ['Enter replacement letter: ']
            return line, self.index

    def draw(self):
        """Draw the curses UI on the screen"""
        self.screen.clear()

        x, y = 1, 1
        max_y, max_x = self.screen.getmaxyx()
        max_rows = max_y - y  # The max rows we can draw

        lines, current_line = self.get_lines()

        # Calculate how many lines we should scroll
        # scroll_top = getattr(self, 'scroll_top', 0)
        # if current_line <= scroll_top:
        #     scroll_top = 0
        # elif current_line - scroll_top > max_rows:
        #     scroll_top = current_line - max_rows
        # self.scroll_top = scroll_top

        # lines_to_draw = lines[scroll_top:scroll_top + max_rows]

        for line in lines:
            if type(line) is tuple:
                self.screen.addnstr(y, x, line[0], max_x - 2, line[1])
            else:
                self.screen.addnstr(y, x, line, max_x - 2)
            y += 1

        self.screen.refresh()


    def get_selected(self):
        return self.texts[self.level][self.index]

    def move_up(self):
        self.level -= 1
        if self.level < 0:
            self.level = len(self.texts) - 1

    def move_down(self):
        self.level += 1
        if self.level >= len(self.texts) - 1:
            self.level = 0

    def move_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.texts[self.level]) - 1

    def move_right(self):
        self.index += 1
        if self.index >= len(self.texts[self.level]) - 1:
            self.index = 0

    def run_loop(self):
        while True:
            self.draw()
            c = self.screen.getch()
            if self.stage == Stage.SELECTION:
                if c in KEYS_RIGHT:
                    self.move_right()
                elif c in KEYS_LEFT:
                    self.move_left()
                elif c in KEYS_UP:
                    self.move_up()
                elif c in KEYS_DOWN:
                    self.move_down()
                elif c in KEYS_ENTER:
                    self.stage = Stage.REPLACEMENT
                elif c == KEYS_EXIT:
                    return

            elif self.stage == Stage.REPLACEMENT:
                self.texts = self.on_change_hook(self.level, self.index, c)
                self.stage = Stage.SELECTION

    def config_curses(self):
        curses.use_default_colors()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)

    def _start(self, screen):
        self.screen = screen
        self.config_curses()
        return self.run_loop()

    def start(self):
        return curses.wrapper(self._start)
