import os

import toga
from toga.constants import COLUMN
from toga.style.pack import Pack

import components as ui
from config import PADDING_UNIVERSAL
from screen_state import ScreenWithState


class ProcessingScreen(ScreenWithState):
    def construct_gui(self):
        lt_style = {"width": 50}

        epub_lt = ui.LabeledText("Epub:", "<placeholder>", label_style=lt_style)
        self.summary_epub_path = epub_lt.text_label

        anki_lt = ui.LabeledText("Anki:", "<placeholder>", label_style=lt_style)
        self.summary_anki_deck = anki_lt.text_label

        self.status_textarea = toga.MultilineTextInput(
            style=Pack(
                flex=1,
                font_family="monospace",
                padding_top=PADDING_UNIVERSAL,
                padding_bottom=PADDING_UNIVERSAL,
            )
        )

        self.done_btn = toga.Button("Done", on_press=self.mark_finished, enabled=False)

        main_box = toga.Box(
            children=[epub_lt, anki_lt, self.status_textarea, self.done_btn],
            style=Pack(direction=COLUMN, flex=1),
        )
        return main_box

    def update_gui_contents(self):
        self.summary_epub_path.text = os.path.basename(self._state["epub_path"])
        self.summary_anki_deck.text = self._state["anki_selected_deck"]

    def min_size(self):
        return (800, 600)

    def title(self):
        return "Running all the Algorithms"

    def update_progress(self, message):
        self.status_textarea.value += f"{message}\n"
    
    def enable_continue(self):
        self.done_btn.enabled = True
