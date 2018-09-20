"""
Interactive module
"""

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

# Global key widget to allow for text updates after creation
global_key_widget = None
# Global program widget to allow for menu popup
global_program = None


# Colour palette to use
palette = [
    ('unknown', 'dark red,bold', 'black')
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


class DecryptionsListBox(urwid.ListBox):
    """List of decryptions to be interacted with"""
    def __init__(self, ciphertexts: Iterable[bytearray], key: Key):
        self.ciphertexts = ciphertexts
        self.key = key

        partial_decryptions = [partial_decrypt(key, c) for c in ciphertexts]

        body = urwid.SimpleFocusListWalker([
            urwid.Pile([
                CustomEdit(edit_text=d, edit_pos=0) for i, d in enumerate(partial_decryptions)
            ])
        ])
        super(DecryptionsListBox, self).__init__(body)


    def _edit_decryption(self, letter: str) -> None:
        """Edit a decryption by modifying the key"""
        ciphertext = self.ciphertexts[self.focus.focus_position]

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
        for widget, decryption in zip(self.focus.widget_list, new_decryptions):
            widget.set_edit_text(decryption)

        # Update displayed key value
        global_key_widget.set_text(self.key.to_text())


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
            global_program.open_pop_up()
            return

        super(DecryptionsListBox, self).keypress(size, key)


class Menu(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']

    def __init__(self):
        export_button = urwid.Button("Export")
        quit_button = urwid.Button("Quit")
        close_button = urwid.Button("Close")
        urwid.connect_signal(close_button, 'click', lambda button:self._emit("close"))
        pile = urwid.LineBox(urwid.Pile([
            export_button,
            quit_button,
            close_button
        ]), title="Menu",title_align="center")

        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))


class Program(urwid.PopUpLauncher):
    def __init__(self, widget):
        self.__super.__init__(widget)
        #urwid.connect_signal(self.original_widget, 'click', lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = Menu()
        urwid.connect_signal(pop_up, 'close', lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':50, 'top':25, 'overlay_width':32, 'overlay_height':7}


def create_decryptions_view(ciphertexts: Iterable[bytearray], key: Key) -> urwid.LineBox:
    """Create a decryptions list box with a border"""
    widget = DecryptionsListBox(ciphertexts, key)

    # Draw line and title around the text
    widget = urwid.LineBox(widget, title="Decryptions", title_align="right")
    return widget


def create_key_view(key: Key) -> urwid.LineBox:
    """Create a global key text box with a border"""
    global global_key_widget
    global_key_widget = urwid.Text(key.to_text())

    # Draw line and title around the text
    widget = urwid.LineBox(global_key_widget, title="Key", title_align="right")
    return widget


def create_main_view(ciphertexts: Iterable[bytearray], key: Key) -> urwid.Pile:
    global global_program

    boxes = [
        ('weight', 1, create_decryptions_view(ciphertexts, key),),
        ('pack', create_key_view(key),)
    ]
    pile = urwid.Pile(boxes)
    global_program = Program(pile)

    return global_program


def interactive(ciphertexts: Iterable[bytearray], key: Iterable) -> None:
    urwid.MainLoop(create_main_view(ciphertexts, Key(key)), palette=palette, pop_ups=True).run()
