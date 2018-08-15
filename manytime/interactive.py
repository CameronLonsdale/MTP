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
    """Manages an interactive decryption session"""

    def __init__(self, texts, indicator='^', default_index=0, on_change_hook=None):
        """Initialise an Interactive session for the user"""
        self.texts = texts
        self.indicator = indicator
        self.index = default_index
        self.level = 0
        self.stage = Stage.SELECTION
        self.on_change_hook = on_change_hook

    def start(self):
        """Start an interactive session"""
        return curses.wrapper(self._start)

    def _get_lines(self):
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

    def _draw(self):
        """Draw the curses UI on the screen"""
        self.screen.erase()

        x, y = 1, 1
        max_y, max_x = self.screen.getmaxyx()
        max_rows = max_y - y  # The max rows we can draw

        lines, current_line = self._get_lines()

        for line in lines:
            if type(line) is tuple:
                self.screen.addnstr(y, x, line[0], max_x - 2, line[1])
            else:
                self.screen.addnstr(y, x, line, max_x - 2)
            y += 1

        self.screen.refresh()


    def _move_up(self):
        self.level -= 1
        if self.level < 0:
            self.level = len(self.texts) - 1

    def _move_down(self):
        self.level += 1
        if self.level >= len(self.texts) - 1:
            self.level = 0

    def _move_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.texts[self.level]) - 1

    def _move_right(self):
        self.index += 1
        if self.index >= len(self.texts[self.level]) - 1:
            self.index = 0

    def _run_loop(self):
        while True:
            self._draw()
            c = self.screen.getch()

            if self.stage == Stage.SELECTION:
                if c in KEYS_RIGHT:
                    self._move_right()
                elif c in KEYS_LEFT:
                    self._move_left()
                elif c in KEYS_UP:
                    self._move_up()
                elif c in KEYS_DOWN:
                    self._move_down()
                elif c in KEYS_ENTER:
                    self.stage = Stage.REPLACEMENT
                elif c == KEYS_EXIT:
                    return

            elif self.stage == Stage.REPLACEMENT:
                self.texts = self.on_change_hook(self.level, self.index, c)
                self.stage = Stage.SELECTION

    def _config_curses(self):
        curses.use_default_colors()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)

    def _start(self, screen):
        self.screen = screen
        self._config_curses()
        return self._run_loop()
