import urwid

class DecryptionsListBox(urwid.ListBox):
    # TODO: turn into ciphertext
    # TOOD: need key
    def __init__(self, ciphertexts, key):
        self.ciphertexts = ciphertexts
        self.key = key

        body = urwid.SimpleFocusListWalker([
            urwid.Pile([
                urwid.Edit(caption=f'#{i} ', edit_text=d) for i, d in enumerate(decryptions)
            ])
        ])
        super(DecryptionsListBox, self).__init__(body)

        self.focus.focus_position = self.selected_decryption
        self.focus[self.selected_decryption].edit_pos = self.letter_position

    def _get_current_decryption(self) -> str:
        return self.decryptions[self.selected_decryption]

    def _move_down(self, step: int = 1) -> None:
        self.selected_decryption += step
        if self.selected_decryption >= len(self.decryptions):
            self.selected_decryption = 0

        self.focus.focus_position = self.selected_decryption

    def _move_up(self, step: int = 1) -> None:
        self.selected_decryption -= step
        if self.selected_decryption < 0:
            self.selected_decryption = len(self.decryptions) - 1

        self.focus.focus_position = self.selected_decryption

    def _move_left(self, step=1):
        self.letter_position -= step
        if self.letter_position < 0:
            self.letter_position = len(self._get_current_decryption()) - 1

        self.focus[self.selected_decryption].edit_pos = self.letter_position

    def _move_right(self, step=1):
        self.letter_position += step
        if self.letter_position >= len(self._get_current_decryption()):
            self.letter_position = len(self._get_current_decryption()) - 1

        self.focus[self.selected_decryption].edit_pos = self.letter_position

    def _edit_decryption(self, key: str) -> None:
        """Edit a decryption by modifying the key"""

    def keypress(self, size, key):
        # Up, down, page up and page down automatically handled
        #key = super(DecryptionsListBox, self).keypress(size, key)
        #print(key)
        #print(len(self.focus))

        # print("HELLO")
        # print('down' in urwid.command_map)

       # print(key)

        #print(str('q' in urwid.command_map))


        if urwid.command_map[key] is None:
            print('UNHANDLED')


        super(DecryptionsListBox, self).keypress(size, key)

        # print(vars(urwid.command_map))

        # if key == 'down':
        #     self._move_down()
        # elif key == 'up':
        #     self._move_up()
        # elif key == 'left':
        #     self._move_left()
        # elif key == 'right':
        #     self._move_right()

        #print('lol ' + str(decryption.text))
        #self.focus_position += 1
        # if key == 'down':
        #     self.focus_position += 1

        # if key != 'enter':
        #     return key
        # name = self.focus[0].edit_text
        # if not name:
        #     raise urwid.ExitMainLoop()
        # # replace or add response
        # self.focus.contents[1:] = [(answer(name), self.focus.options())]
        # pos = self.focus_position
        # # add a new question
        # self.body.insert(pos + 1, question())
        # self.focus_position = pos + 1


def create_decryptions_box(ciphertexts, key):
    decryptions = ["decryption1", "decryption2"]

    #widget = urwid.Pile([SelectablePudding() for d in decryptions])
    widget = DecryptionsListBox(decryptions, )
    #text = urwid.Text(decryptions)
    # Draw line and title around the text
    widget = urwid.LineBox(widget, title="Decryptions", title_align="right")
    #widget = urwid.Padding(widget, align='left')
    #widget = urwid.Filler(widget, 'top')
    return widget

def create_key_box(key, ):
    text = urwid.Text(key)
    # Draw line and title around the text
    widget = urwid.LineBox(text, title="Key", title_align="right")
    #widget = urwid.Padding(widget, align='left')
    #widget = urwid.Filler(widget, 'bottom')
    return widget


def create_main_box(ciphertexts, key):
    boxes = [
        ('weight', 1, create_decryptions_box(),),
        ('pack', create_key_box(),)
    ]
    return urwid.Pile(boxes)

# decryptions_box = None
# key_box = None
# pile = urwid.Pile([decryptions_box, key_box])


#top_level = urwid.Filler(create_decryptions_box())





urwid.MainLoop(create_main_box()).run()
