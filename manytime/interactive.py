"""
Interactive module
"""

import math
import urwid

from manytime.models import Key

from typing import Iterable, Optional


# Directional keys
NO_KEY = ''
LEFT = 'left'
RIGHT = 'right'

# Management keys
ESCAPE_KEY = 'esc'

# Removal keys
BACKSPACE = 'backspace'
DELETE = 'delete'

# Keys which are used to remove a letter from a decryption
REMOVE_KEYS = (BACKSPACE, DELETE)

# Keys which are in urwid.command_map but we wish to use as input
EXCLUDE_KEYS = (' ',)

# Colour palette to use
palette = [
    ('unknown', 'dark red,bold', 'black'),
    ('line_num', 'light gray,bold', 'black'),
    ('reversed', 'standout', 'black'),
]


def partial_decrypt(key: Key, ciphertext: bytearray, unknown_character: str = ('unknown', '_')) -> Iterable[str]:
    """
    Decrypt ciphertext using key
    Decrypting a letter using an unknown key element will result in unknown_character
    """
    return [chr(k ^ c) if k is not None else unknown_character for k, c in zip(key, ciphertext)]


class CustomEdit(urwid.Edit):
    """
    Custom Edit Widget
    Because the original is not good enough
    """
    def set_edit_pos(self, pos):
        """
        Overload the set_edit_pos function to restrict
        the edit position to the end of the string, not 1 past the end
        """
        if pos >= len(self._edit_text):
            pos = len(self._edit_text) - 1

        super().set_edit_pos(pos)

    def move_cursor_to_coords(self, size, x, y):
        """
        Overload the move_cursor_to_coords function because urwid does
        not reuse set_edit_pos for this functionality
        """
        ret_val = super().move_cursor_to_coords(size, x, y)
        self.set_edit_pos(self.edit_pos)
        return ret_val

    def set_edit_text(self, text):
        """
        Overload the set_edit_text function because the original does not support markup.
        Warning, there is a bug here that doesnt make it work with captions.
        This should be fixed
        """
        self._edit_text, self._attrib = urwid.util.decompose_tagmarkup(text)
        self._invalidate()


def numbered_row(line_num, text, max_number):
    right_side_spaces = 3
    left_side_spaces = 2
    line_num_col_width = left_side_spaces + len(str(max_number)) + right_side_spaces

    line_num_widget = urwid.Text(('line_num', str(line_num) + ' ' * right_side_spaces), align='right')
    decryption_edit_widget = CustomEdit(edit_text=text)

    return urwid.Columns([
        (line_num_col_width, line_num_widget),
        # I can't use pack here, it breaks the formatting
        ('weight', 1, decryption_edit_widget)
    ], focus_column=1)


class DecryptionsListBox(urwid.ListBox):
    """List of decryptions to be interacted with"""
    def __init__(self, parent, ciphertexts: Iterable[bytearray], key: Key):
        self.ciphertexts = ciphertexts
        self.key = key
        self.parent = parent

        partial_decryptions = [partial_decrypt(key, c) for c in ciphertexts]

        max_number = len(ciphertexts) + 1
        body = urwid.SimpleFocusListWalker([
            numbered_row(i + 1, d, max_number) for i, d in enumerate(partial_decryptions)
        ])
        super(DecryptionsListBox, self).__init__(body)


    def _edit_decryption(self, letter: str) -> None:
        """Edit a decryption by modifying the key"""
        ciphertext = self.ciphertexts[self.focus_position]

        # TODO: The edit position can go beyond the end of the string, this needs to be fixed
        index = self.focus[self.focus.focus_position].edit_pos

        # Backspace should delete the letter previous to the one selected
        if letter == BACKSPACE:
            index = min(index - 1, len(ciphertext) - 1)
            # We're trying to backspace from the start of the string, this is invalid
            if index < 0:
                return

        # Update the key
        self.key[index] = None if letter in REMOVE_KEYS else ord(letter) ^ ciphertext[index]

        # Update all decryptions
        new_decryptions = [partial_decrypt(self.key, c) for c in self.ciphertexts]
        for row, decryption in zip(self.body, new_decryptions):
            decryption_widget = row[1]
            decryption_widget.set_edit_text(decryption)

        # Update displayed key value
        self.parent.key_widget.set_text(self.key.to_text())


    def keypress(self, size, key: str):
        """
        Custom handling of keyboard presses
        Key in this context refers to keyboard key, not cryptographic key
        """
        if urwid.command_map[key] is None or key in EXCLUDE_KEYS:
            self._edit_decryption(key)
            
            # We want to move the cursor left when a letter was removed
            # If it is the delete key we do not want to move the cursor
            # All other keys we count as a letter placement and move the cursor to the right
            if key == BACKSPACE:
                key = LEFT
            elif key == DELETE:
                key = NO_KEY
            else:
                key = RIGHT
        elif key == ESCAPE_KEY:
            self.parent.open_menu()
            return

        super(DecryptionsListBox, self).keypress(size, key)


class CustomButton(urwid.Button):
    button_left = urwid.Text("")
    button_right = urwid.Text("")

    def __init__(self, label, on_press=None, user_data=None):
        """
        Need to rewrite the init class for a button
        in order to set the cursor_position to an unreachable value.
        This stops the cursor from being rendered
        """
        self._label = urwid.SelectableIcon(text="", cursor_position=math.inf)
        cols = urwid.Columns([
            ('fixed', 1, self.button_left),
            self._label,
            ('fixed', 1, self.button_right)],
            dividechars=1)

        urwid.WidgetWrap.__init__(self, cols)

        # The old way of listening for a change was to pass the callback
        # in to the constructor.  Just convert it to the new way:
        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)


def create_menu(parent):
    """
    Create the menu view
    """
    body = urwid.ListBox([
        urwid.AttrMap(CustomButton("Export"), None, focus_map='reversed'),
        urwid.AttrMap(CustomButton("Quit"), None, focus_map='reversed'),
        urwid.AttrMap(CustomButton("Close", parent.reset_layout), None, focus_map='reversed')
    ])
 
    layout = urwid.LineBox(body, title="Menu", title_align="center")
    return layout


class Application():
    def __init__(self, ciphertexts: Iterable[bytearray], key: Key):

        self.key_widget = urwid.Text(key.to_text())
        self.decryption_widget = DecryptionsListBox(self, ciphertexts, key)

        self.main_screen = urwid.Pile([
            ('weight', 1, urwid.LineBox(self.decryption_widget, title="Decryptions", title_align="left")),
            ('pack',  urwid.LineBox(self.key_widget, title="Key", title_align="left"),)
        ])

        self.menu = create_menu(self)

        # Create the body such that the menu is hidden on startup
        self._body = self.main_screen

        self._loop = urwid.MainLoop(
            self._body,
            palette=palette,
            pop_ups=True
        )

    def run(self):
        self._loop.run()

    def open_menu(self):
        w = urwid.Overlay(
            self.menu,
            self._body,
            align='center',
            width=22,
            valign='middle',
            height=7
        )

        self._loop.widget = w

    def reset_layout(self, *args):
        '''
        Resets the console UI to the default layout
        '''
        self._loop.widget = self._body
        self._loop.draw_screen()


def interactive(ciphertexts: Iterable[bytearray], key: Iterable) -> None:
    Application(ciphertexts, Key(key)).run()
