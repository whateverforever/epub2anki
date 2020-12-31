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
        self.examples_list.style.update(
            flex=1, padding_top=PADDING_UNIVERSAL, padding_bottom=PADDING_UNIVERSAL
        )

        button_box = toga.Box()
        button_box.add(
            toga.Button(
                "Ignore Word",
                style=Pack(flex=1, padding_right=PADDING_UNIVERSAL),
                on_press=self.ignore_btn_clicked,
            )
        )
        button_box.add(
            toga.Button(
                "Skip Word",
                style=Pack(flex=1, padding_right=PADDING_UNIVERSAL),
                on_press=self.skip_btn_clicked,
            )
        )
        button_box.add(
            toga.Button("Take Word", style=Pack(flex=2), on_press=self.take_btn_clicked)
        )

        finish_btn = toga.Button(
            "Finish",
            style=Pack(flex=1, padding_top=PADDING_UNIVERSAL),
            on_press=self.mark_finished,
        )

        return toga.Box(
            children=[vocab_lt, self.examples_list, button_box, finish_btn],
            style=Pack(direction=COLUMN, flex=1),
        )

    def title(self):
        return "Pick Interesting Vocabs"

    def update_gui_contents(self):
        state = self._state

        vocab_idx = state["vocab_current"]

        try:
            new_word = state["vocab_words"][vocab_idx]
            sentences = state["vocab_sentences"][vocab_idx]
        except IndexError:
            new_word = "[No more words]"
            sentences = []

        self.vocab_label.text = new_word
        self.examples_list.data = sentences

        self.ensure_refresh()

    def ignore_btn_clicked(self, sender):
        # add word to ignore list
        vocab_idx = self._state["vocab_current"]
        word = self._state["vocab_words"][vocab_idx]
        self._state["vocab_ignored"].append(word)

        self._state["vocab_current"] += 1
        self.update_gui_contents()

    def skip_btn_clicked(self, sender):
        self._state["vocab_current"] += 1
        self.update_gui_contents()

    def take_btn_clicked(self, sender):
        # save somewhere
        self._state["vocab_taken"].append(self._state["vocab_current"])
        self._state["vocab_current"] += 1

        self.update_gui_contents()