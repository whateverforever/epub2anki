import os

import toga
from toga.constants import COLUMN
from toga.style.pack import Pack

from .screen_state import ScreenWithState


class FileChoosingScreen(ScreenWithState):
    def construct_gui(self):
        epub_label = toga.Label("Please choose the epub file.", style=Pack(flex=1))
        self.epub_file_btn = toga.Button("Choose File", on_press=self.pressed_epub_btn)
        epub_box = toga.Box(
            children=[epub_label, self.epub_file_btn], style=Pack(padding_bottom=5)
        )

        anki_label = toga.Label(
            "Compare to which Anki deck?", style=Pack(flex=1)
        )
        self.anki_choice = toga.Selection(style=Pack(width=180))
        anki_box = toga.Box(
            children=[anki_label, self.anki_choice], style=Pack(padding_bottom=5)
        )

        finished_btn = toga.Button("Finished", on_press=self.pressed_finish_btn)

        main_box = toga.Box(
            children=[epub_box, anki_box, finished_btn],
            style=Pack(direction=COLUMN, width=400),
        )

        self.add(main_box)

    def title(self):
        return "Choose the Input Files"

    def update_gui_contents(self):
        self.anki_choice.items = self._state["anki_all_decks"]

    def pressed_finish_btn(self, sender):
        # if not self._state["epub_path"]:
        #     self._parent_wizard.app.main_window.error_dialog(
        #         "No Epub Selected",
        #         "You need to chose an epub. So far, nothing has been selected >:{",
        #     )
        #     return

        self._state["anki_selected_deck"] = self.anki_choice.value
        self.mark_finished(sender)

    def pressed_epub_btn(self, btn):
        app = self._parent_wizard.app
        epub_paths = [str(path) for path in app.main_window.open_file_dialog("Choose epub", multiselect=True)]

        # if not epub_paths.endswith(".epub"):
        #     app.main_window.error_dialog(
        #         "Invalid File Suffix",
        #         "The file doesn't end in .epub, and so I won't take it. Fight me >:{",
        #     )
        #     return

        self._state["epub_paths"] = epub_paths
        self.epub_file_btn.label = ", ".join([os.path.basename(path) for path in epub_paths])
