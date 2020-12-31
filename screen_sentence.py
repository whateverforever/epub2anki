import re

import toga
from toga.constants import COLUMN
from toga.style.pack import Pack

import components as ui
from config import NUM_SENTENCES, PADDING_UNIVERSAL
from screen_state import ScreenWithState


class SentenceScreen(ScreenWithState):
    def construct_gui(self):
        vocab_lt = ui.LabeledText("Vocab:", "<vocab_lt placeholder>",)
        self.vocab_label = vocab_lt.text_label

        self.examples_list = toga.Table(["Sentences"])
        self.examples_list.style.update(
            flex=1, padding_top=PADDING_UNIVERSAL, padding_bottom=PADDING_UNIVERSAL
        )

        commands = [
            toga.Command(
                self.replace_sent_cmd,
                label=f"Replace Sentence {idx+1}",
                shortcut=toga.Key.MOD_1 + f"{idx+1}",
                order=idx,
            )
            for idx in range(NUM_SENTENCES)
        ]
        self._state["app"].commands.add(*commands)

        numbered_replace_btns = [
            toga.Button(f"{idx+1}", on_press=self.replace_sent_btn)
            for idx in range(NUM_SENTENCES)
        ]
        button_box = toga.Box()
        button_box.add(
            toga.Label("Replace Sentence", style=Pack(padding_right=PADDING_UNIVERSAL)),
            *numbered_replace_btns,
        )

        self.definition_field = toga.MultilineTextInput(
            placeholder="Please paste your definition here"
        )
        self.definition_field.style.update(flex=2, padding_top=PADDING_UNIVERSAL)

        return toga.Box(
            children=[vocab_lt, self.examples_list, button_box, self.definition_field],
            style=Pack(direction=COLUMN, flex=1),
        )

    def title(self):
        return "Pick Some Sentences"

    def update_gui_contents(self):
        vocab_idx = self._state["vocab_current"]
        self.examples_list.data = self._state["vocab_sentences"][vocab_idx]
        self.vocab_label.text = self._state["vocab_words"][vocab_idx]

    def replace_sent_cmd(self, sender: toga.Command):
        sentence_number = re.sub(r"<.+?>", "", sender.shortcut)
        sentence_idx = int(sentence_number) - 1

        self.replace_sentence(sentence_idx)

    def replace_sent_btn(self, sender: toga.Button):
        sentence_number = int(sender.label)
        sentence_idx = sentence_number - 1

        self.replace_sentence(sentence_idx)

    def replace_sentence(self, sentence_idx):
        print(f"Someone wants to replace sentence {sentence_idx}")
