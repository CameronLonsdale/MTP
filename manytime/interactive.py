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

# Removal keys
BACKSPACE = 'backspace'
DELETE = 'delete'

# Keys which are used to remove a letter from a decryption
REMOVE_KEYS = (BACKSPACE, DELETE)

# Keys which are in urwid.command_map but we wish to use as input
EXCLUDE_KEYS = (' ',)

# Global key widget to allow for text updates after creation
global_key_widget = None


def clamp(a: int, x: int, b: int) -> int:
    """Clamp value x between a and b"""
    return max(a, min(x, b))


def partial_decrypt(key: Key, ciphertext: bytearray, unknown_character: str = '_') -> Iterable[str]:
    """
    Decrypt ciphertext using key
    Decrypting a letter using an unknown key element will result in unknown_character
    """
    return [chr(k ^ c) if k is not None else unknown_character for k, c in zip(key, ciphertext)]


class DecryptionsListBox(urwid.ListBox):
    """List of decryptions to be interacted with"""
    def __init__(self, ciphertexts: Iterable[bytearray], key: Key):
        self.ciphertexts = ciphertexts
        self.key = key

        partial_decryptions = [partial_decrypt(key, c) for c in ciphertexts]

        body = urwid.SimpleFocusListWalker([
            urwid.Pile([
                urwid.Edit(caption=f'{i}| ', edit_text=''.join(d), edit_pos=0) for i, d in enumerate(partial_decryptions)
            ])
        ])
        super(DecryptionsListBox, self).__init__(body)


    def _edit_decryption(self, letter: str) -> None:
        """Edit a decryption by modifying the key"""
        ciphertext = self.ciphertexts[self.focus.focus_position]
        index = self.focus[self.focus.focus_position].edit_pos

        # Backspace should delete the letter previous to the one selected
        if letter == BACKSPACE:
            index = clamp(0, index - 1, len(ciphertext) - 1)

        # Update the key
        self.key[index] = None if letter in REMOVE_KEYS else ord(letter) ^ ciphertext[index]

        # Update all decryptions
        new_decryptions = [partial_decrypt(self.key, c) for c in self.ciphertexts]
        for widget, decryption in zip(self.focus.widget_list, new_decryptions):
            widget.edit_text = ''.join(decryption)

        # Update displayed key value
        global_key_widget.set_text(str(self.key))


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

        super(DecryptionsListBox, self).keypress(size, key)


def create_decryptions_view(ciphertexts: Iterable[bytearray], key: Key) -> urwid.LineBox:
    """Create a decryptions list box with a border"""
    widget = DecryptionsListBox(ciphertexts, key)

    # Draw line and title around the text
    widget = urwid.LineBox(widget, title="Decryptions", title_align="right")
    return widget


def create_key_view(key: Key) -> urwid.LineBox:
    """Create a global key text box with a border"""
    global global_key_widget
    global_key_widget = urwid.Text(str(key))

    # Draw line and title around the text
    widget = urwid.LineBox(global_key_widget, title="Key", title_align="right")
    return widget


def create_main_view(ciphertexts: Iterable[bytearray], key: Key) -> urwid.Pile:
    boxes = [
        ('weight', 1, create_decryptions_view(ciphertexts, key),),
        ('pack', create_key_view(key),)
    ]
    return urwid.Pile(boxes)


def interactive(ciphertexts: Iterable[bytearray], key: Iterable) -> None:
    urwid.MainLoop(create_main_view(ciphertexts, Key(key))).run()
