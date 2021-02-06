import os

import genanki
import toga

from .screen_state import ScreenWithState


class CardScreen(ScreenWithState):
    def construct_gui(self):
        return toga.Box(children=[toga.Label("Creating cards or so")])

    def update_gui_contents(self):
        fields = [
            {"name": "sentence-0"},
            {"name": "sentence-1"},
            {"name": "sentence-2"},
            {"name": "sentence-3"},
            {"name": "sentence-4"},
            {"name": "definition"},
        ]

        multisentence_model = genanki.Model(
            1667392319,
            "Some Model from epub2anki",
            fields=fields,
            templates=[
                {
                    "name": f"One-To-Many Cards, Sentence {isent}",
                    "qfmt": "{{FIELDNAME}} {{tts fr_FR speed=1.25 :FIELDNAME}}".replace(
                        "FIELDNAME", sentence_field["name"]
                    ),
                    "afmt": '{{FrontSide}}<hr id="answer">{{definition}} {{tts fr_FR speed=1.25 :definition}}',
                }
                for isent, sentence_field in enumerate(fields)
            ],
        )

        epub_path = self._state["epub_paths"][0]
        deck_name = os.path.basename(epub_path)
        book_deck = genanki.Deck(2059400110, deck_name)

        for card in self._state["card_models"]:
            field_definition = card["definition"]

            note_basic = genanki.Note(
                model=multisentence_model, fields=[*card["sentences"], field_definition]
            )
            book_deck.add_note(note_basic)

        genanki.Package(book_deck).write_to_file("output.apkg")

