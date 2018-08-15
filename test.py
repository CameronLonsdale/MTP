import urwid

class DecryptionsListBox(urwid.ListBox):
    def __init__(self, decryptions):
        body = urwid.SimpleFocusListWalker([
            urwid.Pile([
                urwid.Edit(d, edit_pos=0) for d in decryptions
            ])
        ])
        super(DecryptionsListBox, self).__init__(body)

   # def _move_up(self):
   #      if self.focus.focus_position - 1 < 0:
   #          self.focus_position = len(self.texts) - 1
   #      else:
   #          self.focus.focus_position -= 1

    def _move_down(self, step):
        if self.focus.focus_position + step > len(self.focus.contents) - 1:
            self.focus.focus_position = 0
        else:
            self.focus.focus_position += step

    def _move_up(self, step):
        if self.focus.focus_position - step < 0:
            self.focus.focus_position = len(self.focus.contents) - 1
        else:
            self.focus.focus_position -= step

    def _move_left(self):
        self.focus[self.focus_position].edit_pos -= 1
        print(self.focus[self.focus_position].edit_pos)
        # if self.index < 0:
        #     self.index = len(self.texts[self.level]) - 1

   #  def _move_right(self):
   #      self.index += 1
   #      if self.index >= len(self.texts[self.level]) - 1:
   #          self.index = 0

    def keypress(self, size, key):
        # Up, down, page up and page down automatically handled
        #key = super(DecryptionsListBox, self).keypress(size, key)
        #print(key)
        #print(len(self.focus))


        if key == 'down':
            self._move_down(1)
        elif key == 'up':
            self._move_up(1)
        elif key == 'left':
            self._move_left()

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


def create_decryptions_box():
    decryptions = ["decryption1", "decryption2"]

    #widget = urwid.Pile([SelectablePudding() for d in decryptions])
    widget = DecryptionsListBox(decryptions)
    #text = urwid.Text(decryptions)
    # Draw line and title around the text
    widget = urwid.LineBox(widget, title="Decryptions", title_align="right")
    #widget = urwid.Padding(widget, align='left')
    #widget = urwid.Filler(widget, 'top')
    return widget

def create_key_box():
    key = "KEY"

    text = urwid.Text(key)
    # Draw line and title around the text
    widget = urwid.LineBox(text, title="Key", title_align="right")
    #widget = urwid.Padding(widget, align='left')
    #widget = urwid.Filler(widget, 'bottom')
    return widget


def create_main_box():
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
