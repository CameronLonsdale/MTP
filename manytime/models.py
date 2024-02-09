"""
Models module
"""

import urwid
import math

from manytime import keys

from typing import Optional, List, Tuple, Union, Iterator, Any


class Key:
    """
    A key used for decrypting OTP
    supports partial decryption
    """
    def __init__(self, key: List[Optional[int]], unknown_character: str = '_') -> None:
        self.key = key
        self.unknown_character = unknown_character

    def to_formatted_text(self) -> List:
        """
        Turn key into formatted text representation,
        for being printed by urwid
        """
        unknown_char_formatted = ('unknown', self.unknown_character)
        return self._to_text(unknown_char_formatted)

    def to_plain_text(self) -> List:
        """Turn key into a plain text representation"""
        return self._to_text(self.unknown_character)

    def _to_text(self, unknown: Union[str, Tuple[str, str]]) -> List:
        """Private function to turn key into text representation"""
        # Using two unknown characters in this way in order to not merge two tuples
        return [format(k, '02x') if k is not None else [unknown, unknown] for k in self.key]

    def __iter__(self) -> Iterator:
        """Iterator wrapper over key"""
        return iter(self.key)

    def __getitem__(self, index: int) -> Optional[int]:
        """Getter wrapper"""
        return self.key[index]

    def __setitem__(self, index: int, value: Optional[int]) -> None:
        """Setter wrapper"""
        self.key[index] = value


class DecryptEdit(urwid.Edit):
    """Edit Widget to use for a decryption"""

    def __init__(self, parent, edit_text):
        self.parent = parent
        self.previous_event: Tuple[Optional[str], Any] = (None, None)
        super().__init__(edit_pos=0, edit_text=edit_text)

    def set_edit_pos(self, pos: int) -> None:
        """
        Overload the set_edit_pos function to restrict
        the edit position to the end of the string, not 1 past the end
        """
        if pos >= len(self._edit_text):
            pos = len(self._edit_text) - 1

        super().set_edit_pos(pos)

        # Set the x pos (this handles left and right keys)
        if self.previous_event[0] in (keys.LEFT, keys.RIGHT):
            self.parent.x_pos = self.get_cursor_coords(self.previous_event[1])[0]

    def move_cursor_to_coords(self, size: Tuple, x: int, y: int) -> bool:
        """
        Overload the move_cursor_to_coords function because urwid does
        not reuse set_edit_pos for this functionality
        """
        if self.previous_event[0] in (keys.HOME, keys.END, keys.MOUSE_EVENT):
            # Allow the cursor to move freely
            ret_val = super().move_cursor_to_coords(size, x, y)
            self.set_edit_pos(self.edit_pos)

            # And update parent value
            self.parent.x_pos = self.get_cursor_coords(size)[0]

            return ret_val

        # Otherwise, we move cursor to the max parent value
        ret_val = super().move_cursor_to_coords(size, self.parent.x_pos, y)
        # We set edit pos so that we don't go 1 past the end of the string
        self.set_edit_pos(self.edit_pos)
        return ret_val

    def mouse_event(self, size, event, button, x, y, focus) -> bool:
        """
        We overide mouse event in order to record the event
        for use in move_cursor_to_coords
        """
        self.previous_event = (keys.MOUSE_EVENT, size)
        return super().mouse_event(size, event, button, x, y, focus)

    def set_edit_text(self, text) -> None:
        """
        Overload the set_edit_text function because the original does not support markup.
        Warning, there is a bug here that doesnt make it work with captions.
        """
        self._edit_text, self._attrib = urwid.util.decompose_tagmarkup(text)
        self._invalidate()

    def keypress(self, size, key) -> Optional[str]:
        """
        We overide keypress in order to record the event
        for use in move_cursor_to_coords
        """
        self.previous_event = (key, size)
        return super().keypress(size, key)


class MenuButton(urwid.Button):
    """A custom button to use in the menu"""
    button_left = urwid.Text("")
    button_right = urwid.Text("")

    def __init__(self, label: str, on_press=None, user_data=None) -> None:
        """
        Need to rewrite the init class for a button
        in order to set the cursor_position to an unreachable value.
        This stops the cursor from being rendered.
        """
        # Set the cursor position to inifite in order to stop it rendering
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
