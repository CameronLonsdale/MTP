"""
Interactive module
"""

import json
import urwid
from enum import Enum

from manytime import keys

from manytime.models import Key, DecryptEdit, MenuButton

from typing import Iterable, Optional, Tuple, NoReturn, Union, Any, List


def partial_decrypt(key: Key, ciphertext: bytearray, unknown_character: Union[Tuple[str, str], str] = ('unknown', '_')) -> Iterable:
    """
    Decrypt ciphertext using key
    Decrypting a letter using an unknown key element will result in unknown_character
    """
    return [chr(k ^ c) if k is not None else unknown_character for k, c in zip(key, ciphertext)]


class DecryptionsListBox(urwid.ListBox):
    """List of partial decryptions to be edited"""

    # Keys which are used to remove a letter from a decryption
    REMOVE_KEYS = (keys.BACKSPACE, keys.DELETE)

    # Keys which are in urwid.command_map but we wish to use as input
    EXCLUDE_KEYS = (keys.SPACE,)

    def __init__(self, application) -> None:
        """Initialise the decryptions list box inside an application"""
        self.application = application
        self.x_pos: int = 0

        partial_decryptions = [partial_decrypt(self.application.key, c) for c in self.application.ciphertexts]

        body = urwid.SimpleFocusListWalker([
            self._create_decryption_with_line_number(index + 1, decryption)
            for index, decryption in enumerate(partial_decryptions)
        ])
        super().__init__(body)

    def _edit_decryption(self, letter: str) -> None:
        """Edit a decryption by modifying the key"""
        ciphertext = self.application.ciphertexts[self.focus_position]

        index = self.focus[self.focus.focus_position].edit_pos

        # Backspace should delete the letter previous to the one selected
        if letter == keys.BACKSPACE:
            index = min(index - 1, len(ciphertext) - 1)
            # We're trying to backspace from the start of the string, this is invalid
            if index < 0:
                return

        # Update the key
        if len(letter) == 1 or letter in self.REMOVE_KEYS:
            # Letters which are longer, for example "shift left" are not key presses we want to deal with.
            # All special characters are handled elsewhere, this code handles letters and delete keys
            # therefore we ignore all others.
            self.application.key[index] = None if letter in self.REMOVE_KEYS or len(letter) > 1 else ord(letter) ^ ciphertext[index]

        # Update all decryptions
        new_decryptions = [partial_decrypt(self.application.key, c) for c in self.application.ciphertexts]
        for row, decryption in zip(self.body, new_decryptions):
            decryption_widget = row[1]
            decryption_widget.set_edit_text(decryption)

        # Update displayed key value
        self.application.key_widget.set_text(self.application.key.to_formatted_text())

    def keypress(self, size: Tuple, key: str) -> None:
        """
        Custom handling of keyboard presses
        Key in this context refers to keyboard key, not cryptographic key
        """
        if urwid.command_map[key] is None or key in self.EXCLUDE_KEYS:
            self._edit_decryption(key)

            # We want to move the cursor left when a letter was removed
            # If it is the delete key we do not want to move the cursor
            # All other keys we count as a letter placement and move the cursor to the right
            if key == keys.BACKSPACE:
                key = keys.LEFT
            elif key == keys.DELETE:
                key = keys.RIGHT
            else:
                key = keys.RIGHT
        elif key == keys.ESCAPE_KEY:
            self.application.open_menu()
            return

        super().keypress(size, key)

    def _create_decryption_with_line_number(self, line_number: int, text: Iterable[Any]) -> urwid.Columns:
        """Create the decryption edit text with a prefixed line number"""
        right_side_spaces = 3
        left_side_spaces = 2
        max_line_number = len(self.application.ciphertexts) + 1
        line_num_col_width = left_side_spaces + len(str(max_line_number)) + right_side_spaces

        line_num_widget = urwid.Text(('line_number', str(line_number) + ' ' * right_side_spaces), align='right')
        decryption_edit_widget = DecryptEdit(self, edit_text=text)

        return urwid.Columns([
            (line_num_col_width, line_num_widget),
            # Can't use pack here, it breaks the formatting
            ('weight', 1, decryption_edit_widget)
        ], focus_column=1)


class Application:
    """An application to decipher ciphertexts using key, interactively"""
    palette = [
        ('unknown', 'dark red,bold', 'black'),
        ('line_number', 'light gray,bold', 'black'),
        ('reversed', 'standout', 'black'),
    ]

    def __init__(self, ciphertexts: Iterable[bytearray], key: Key, results_filename: str) -> None:
        # Store the values in the application for ease of exporting
        self.ciphertexts = ciphertexts
        self.key = key
        self.results_filename = results_filename

        self.key_widget = urwid.Text(key.to_formatted_text())
        self.decryption_widget = DecryptionsListBox(self)

        # The body is the visible element on the screen
        self._body = urwid.Pile([
            ('weight', 1, urwid.LineBox(self.decryption_widget, title="Decryptions", title_align="left")),
            ('pack',  urwid.LineBox(self.key_widget, title="Key", title_align="left"))
        ])  # We 'pack' the key widget to place it at the bottom of the screen

        self.menu_widget = self._create_menu_widget()

        self._loop = urwid.MainLoop(
            self._body,
            palette=self.palette,
            pop_ups=True
        )

    def run(self) -> None:
        """Run the main loop of the interface"""
        self._loop.run()

    def open_menu(self) -> None:
        """Overlays the menu ontop of the main screen"""
        self._loop.widget = urwid.Overlay(
            self.menu_widget, self._body,
            align='center', valign='middle',
            width=22, height=7
        )

    def reset_layout(self, *args) -> None:
        """Resets the console UI to the default layout (hides the menu)"""
        self._loop.widget = self._body
        self._loop.draw_screen()

    def quit(self, *args) -> NoReturn:
        """Exit the application"""
        raise urwid.ExitMainLoop()

    def export(self, *args) -> None:
        """Export the state to a file"""
        state = {
            "decryptions": [
                ''.join(partial_decrypt(self.key, ciphertext, unknown_character='_')) for ciphertext in self.ciphertexts
            ],
            "key": ''.join([item for sublist in self.key.to_plain_text() for item in sublist])
        }

        with open(self.results_filename, 'w') as f:
            json.dump(state, f)

        # Hide the menu
        self.reset_layout()

    def _create_menu_widget(self) -> urwid.LineBox:
        """Create the menu widget"""
        body = urwid.ListBox([
            urwid.AttrMap(MenuButton("Export", self.export), None, focus_map='reversed'),
            urwid.AttrMap(MenuButton("Quit", self.quit), None, focus_map='reversed'),
            urwid.AttrMap(MenuButton("Close", self.reset_layout), None, focus_map='reversed')
        ])

        return urwid.LineBox(body, title="Menu", title_align="center")


def interactive(ciphertexts: Iterable[bytearray], key: List[Optional[int]], results_filename: str) -> None:
    """Start an interactive session to decrypt ciphertexts using key"""
    Application(ciphertexts, Key(key), results_filename).run()
