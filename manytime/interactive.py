import urwid


EXCLUDE_KEYS = {
    'esc': 27,
    ' ': 32
}

def partial_decrypt(key, ciphertext, unknown_character='*'):
    """
    Decrypt ciphertext using key
    Decrypting a letter using an unknown key element will result in unknown_character
    """
    return [chr(k ^ c) if k is not None else unknown_character for k, c in zip(key, ciphertext)]


class DecryptionsListBox(urwid.ListBox):
    def __init__(self, ciphertexts, key):
        self.ciphertexts = ciphertexts
        self.key = key

        partial_decryptions = [partial_decrypt(key, c) for c in ciphertexts]

        body = urwid.SimpleFocusListWalker([
            urwid.Pile([
                urwid.Edit(caption=f'{i}| ', edit_text=''.join(d)) for i, d in enumerate(partial_decryptions)
            ])
        ])
        super(DecryptionsListBox, self).__init__(body)

        # self.focus.focus_position = self.selected_decryption
        # self.focus[self.selected_decryption].edit_pos = self.letter_position

    # def _get_current_decryption(self) -> str:
    #     return self.decryptions[self.selected_decryption]

    # def _move_down(self, step: int = 1) -> None:
    #     self.selected_decryption += step
    #     if self.selected_decryption >= len(self.decryptions):
    #         self.selected_decryption = 0

    #     self.focus.focus_position = self.selected_decryption

    # def _move_up(self, step: int = 1) -> None:
    #     self.selected_decryption -= step
    #     if self.selected_decryption < 0:
    #         self.selected_decryption = len(self.decryptions) - 1

    #     self.focus.focus_position = self.selected_decryption

    # def _move_left(self, step=1):
    #     self.letter_position -= step
    #     if self.letter_position < 0:
    #         self.letter_position = len(self._get_current_decryption()) - 1

    #     self.focus[self.selected_decryption].edit_pos = self.letter_position

    # def _move_right(self, step=1):
    #     self.letter_position += step
    #     if self.letter_position >= len(self._get_current_decryption()):
    #         self.letter_position = len(self._get_current_decryption()) - 1

    #     self.focus[self.selected_decryption].edit_pos = self.letter_position

    def _edit_decryption(self, letter: str) -> None:
        """Edit a decryption by modifying the key"""
        ciphertext = self.ciphertexts[self.focus.focus_position]
        index = self.focus[self.focus.focus_position].edit_pos

        # Update the key
        self.key[index] = None if letter == 'esc' else ord(letter) ^ ciphertext[index]

        # Update all decryptions
        new_decryptions = [partial_decrypt(self.key, c) for c in self.ciphertexts]
        for widget, decryption in zip(self.focus.widget_list, new_decryptions):
            widget.edit_text = ''.join(decryption)

        # TODO: Change key value in the key box



    def keypress(self, size, key):
        """
        Not to be confusing, but key in this context refers to keyboard key, not cryptographic key
        """
        if urwid.command_map[key] is None or key in EXCLUDE_KEYS:
            self._edit_decryption(key)
        else:
            super(DecryptionsListBox, self).keypress(size, key)


def create_decryptions_box(ciphertexts, key):
    #decryptions = ["decryption1", "decryption2"]

    #widget = urwid.Pile([SelectablePudding() for d in decryptions])
    widget = DecryptionsListBox(ciphertexts, key)
    #text = urwid.Text(decryptions)
    # Draw line and title around the text
    widget = urwid.LineBox(widget, title="Decryptions", title_align="right")
    #widget = urwid.Padding(widget, align='left')
    #widget = urwid.Filler(widget, 'top')
    return widget

def create_key_box(key):
    key = ''.join(format(x, '02x') if x else '_' for x in key )

    text = urwid.Text(key)
    # Draw line and title around the text
    widget = urwid.LineBox(text, title="Key", title_align="right")
    #widget = urwid.Padding(widget, align='left')
    #widget = urwid.Filler(widget, 'bottom')
    return widget

# TODO, global var for keybox to change value?

def create_main_box(ciphertexts, key):
    boxes = [
        ('weight', 1, create_decryptions_box(ciphertexts, key),),
        ('pack', create_key_box(key),)
    ]
    return urwid.Pile(boxes)

# decryptions_box = None
# key_box = None
# pile = urwid.Pile([decryptions_box, key_box])


#top_level = urwid.Filler(create_decryptions_box())


def interactive(ciphertexts, key) -> None:
    urwid.MainLoop(create_main_box(ciphertexts, key)).run()
