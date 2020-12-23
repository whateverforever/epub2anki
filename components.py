import toga
from toga.constants import BOLD, RIGHT
from toga.style.pack import Pack


class LabeledText(toga.Box):
    def __init__(self, label, text, label_style=None, text_style=None, **kwargs):
        super().__init__(**kwargs)

        self.label_label = toga.Label(label, style=Pack(font_weight=BOLD, text_align=RIGHT))
        self.text_label = toga.Label(text)

        if isinstance(label_style, dict):
            self.label_label.style.update(**label_style)
        if isinstance(text_style, dict):
            self.text_label.style.update(**text_style)

        self.add(self.label_label)
        self.add(self.text_label)
