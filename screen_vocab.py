import toga
import components as ui
from screen_state import ScreenWithState
from toga.constants import COLUMN
from toga.style.pack import Pack
from config import PADDING_UNIVERSAL


class VocabScreen(ScreenWithState):
    def construct_gui(self):
        vocab_lt = ui.LabeledText("Vocab:", "<vocab_lt placeholder>",)
        self.vocab_label = vocab_lt.text_label

        self.examples_list = toga.Table(["Example Sentences"])
        self.examples_list.style.update(flex=1, padding=(PADDING_UNIVERSAL, 0))

        self.ignore_btn = toga.Button(
            "Ignore Word",
            style=Pack(flex=1, padding_right=PADDING_UNIVERSAL),
            on_press=self.ignore_btn_clicked,
        )
        self.skip_btn = toga.Button(
            "Skip Word",
            style=Pack(flex=1, padding_right=PADDING_UNIVERSAL),
            on_press=self.skip_btn_clicked,
        )
        self.take_btn = toga.Button(
            "Take Word", style=Pack(flex=2), on_press=self.take_btn_clicked
        )

        button_box = toga.Box()
        button_box.add(self.ignore_btn)
        button_box.add(self.skip_btn)
        button_box.add(self.take_btn)

        self.finish_btn = toga.Button(
            "Finish Word Selection",
            style=Pack(flex=1, padding_top=PADDING_UNIVERSAL),
            on_press=self.mark_finished,
        )

        return toga.Box(
            children=[vocab_lt, self.examples_list, button_box, self.finish_btn],
            style=Pack(direction=COLUMN, flex=1),
        )

    def title(self):
        return "Pick Interesting Vocabs"

    def update_gui_contents(self):
        state = self._state

        vocab_idx = state["vocab_current"]

        if vocab_idx < len(state["vocab_words"]):
            new_word = state["vocab_words"][vocab_idx]
            sentences = state["vocab_sentences"][vocab_idx]
        else:
            new_word = "[No more words]"
            sentences = []

        frequency = 999

        self.vocab_label.text = (
            f"{new_word} (x{frequency}) ({vocab_idx+1} of {len(state['vocab_words'])})"
        )
        self.examples_list.data = sentences

        self.ensure_refresh()

    def pressed_key(self, shortcut):
        if shortcut == (toga.Key._1):
            self.ignore_btn.focus()
            self.ignore_btn_clicked(None)
        elif shortcut == toga.Key._2:
            self.skip_btn.focus()
            self.skip_btn_clicked(None)
        elif shortcut == toga.Key._3:
            self.take_btn.focus()
            self.take_btn_clicked(None)
        elif shortcut == toga.Key.MOD_1 + toga.Key.ENTER:
            self.mark_finished(None)

    def ignore_btn_clicked(self, sender):
        vocab_idx = self._state["vocab_current"]
        word = self._state["vocab_words"][vocab_idx]
        self._state["vocab_ignored"].append(word)

        self._state["vocab_current"] += 1
        self.update_gui_contents()

    def skip_btn_clicked(self, sender):
        self._state["vocab_current"] += 1
        self.update_gui_contents()

    def take_btn_clicked(self, sender):
        vocab_idx = self._state["vocab_current"]
        self._state["vocab_taken"].append(vocab_idx)

        self._state["vocab_current"] += 1
        self.update_gui_contents()
