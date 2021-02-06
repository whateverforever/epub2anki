import os

import genanki
import toga
from toga.style import Pack
from toga.constants import COLUMN

from .screen_state import ScreenWithState


class CardScreen(ScreenWithState):
    def construct_gui(self):
        label = toga.Label("Which generator should make your cards?")
        self.generator_selection = toga.Selection(on_select=self.gen_selected)
        self.generator_description = toga.MultilineTextInput(readonly=True)
        generate_btn = toga.Button("Generate Deck!", on_press=self.gen_btn_pressed)

        return toga.Box(
            children=[
                label,
                self.generator_selection,
                self.generator_description,
                generate_btn,
            ],
            style=Pack(direction=COLUMN),
        )

    def update_gui_contents(self):
        generators = self._state["card_generators"]

        self.gen_by_name = {}
        for gen in generators:
            self.gen_by_name[gen._NAME] = gen
        
        self.generator_selection.items = self.gen_by_name.keys()
        self.gen_selected(self.generator_selection)

    def gen_selected(self, selector):
        self.generator = self.gen_by_name[selector.value]
        self.generator_description.value = self.generator._DESCRIPTION

    def gen_btn_pressed(self, button):
        epub_path = self._state["epub_paths"][0]
        deck_name = os.path.basename(epub_path)
        book_deck = genanki.Deck(2059400110, deck_name)

        notes = self.generator.generate_notes(self._state["card_models"])
        for note in notes:
            book_deck.add_note(note)

        genanki.Package(book_deck).write_to_file("output.apkg")
