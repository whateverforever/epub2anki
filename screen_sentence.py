import re

import toga
from toga.constants import COLUMN
from toga.style.pack import Pack
from toga_cocoa.libs import SEL

import components as ui
from config import NUM_SENTENCES, PADDING_UNIVERSAL
from screen_state import ScreenWithState


class SentenceScreen(ScreenWithState):
    def construct_gui(self):
        vocab_lt = ui.LabeledText("Vocab:", "<vocab_lt placeholder>",)
        vocab_lt.style.update(
            padding=(PADDING_UNIVERSAL * 5, 0),
            background_color="#afa",
            font_size=80,
            flex=1,
            text_align="center",
        )
        self.vocab_label = vocab_lt.text_label

        self.examples_list = toga.Table(["No.", "Sentences"])
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

        save_button = toga.Button(
            "Save Word with Sentences", on_press=self.save_btn_pressed
        )
        finish_button = toga.Button(
            "Enough, Generate Anki Deck", on_press=self.finish_btn
        )

        return toga.Box(
            children=[
                vocab_lt,
                self.examples_list,
                button_box,
                self.definition_field,
                save_button,
                finish_button,
            ],
            style=Pack(direction=COLUMN, flex=1),
        )

    def title(self):
        return "Pick Some Sentences"

    def update_gui_contents(self):
        try:
            vocab_idx_taken = self._state["vocab_taken_current"]
            vocab_idx_global = self._state["vocab_taken"][vocab_idx_taken]
            original_sentences = self._state["vocab_sentences"][vocab_idx_global]

            self.vocab_word = self._state["vocab_words"][vocab_idx_global]

            if not hasattr(self, "sentence_idxs") or not self.sentence_idxs:
                self.sentence_idxs = list(range(NUM_SENTENCES))
                print("self.sentence_idxs", self.sentence_idxs)

            self.chosen_sentences = [original_sentences[i] for i in self.sentence_idxs]
        except IndexError:
            # This catches too much. This also catches if no more
            # sentences are there for the current word
            self.vocab_word = "[No more words]"
            original_sentences = []

        self.vocab_label.text = self.vocab_word
        self.examples_list.data = [
            (f"[{i+1}]", sent) for i, sent in enumerate(self.chosen_sentences)
        ]
        self.ensure_refresh()

    def finish_btn(self, sender):
        self.mark_finished(sender)
    
    def pressed_key(self, shortcut):
        if shortcut == (toga.Key.MOD_1 + toga.Key.ENTER):
            self.save_btn_pressed(None)

    def save_btn_pressed(self, sender):
        self._state["card_models"].append(
            {
                "word": self.vocab_word,
                "sentences": self.chosen_sentences,
                "definition": str(self.definition_field.value),
            }
        )

        self._state["vocab_taken_current"] += 1
        self.sentence_idxs = None
        self.definition_field.clear()

        self.update_gui_contents()

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

        max_sent_index = max(self.sentence_idxs)
        self.sentence_idxs[sentence_idx] = max_sent_index + 1

        print("self.sentence_idxs", self.sentence_idxs)
        self.update_gui_contents()
