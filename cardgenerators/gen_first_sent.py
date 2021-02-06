import genanki

_NAME = "Single Sentence Generator"
_DESCRIPTION = """This generator only uses the first chosen sentence for a simple two-way cards. The others get ignored."""


def generate_notes(card_models):
    """Takes a bunch of card models (see XXX) and returns a list of genanki notes"""

    multisentence_model = genanki.Model(
        1108891939,
        "Simpel Sentence Card",
        fields=[{"name": "sentence"}, {"name": "definition"}],
        templates=[
            {
                "name": "One-to-One Card",
                "qfmt": "{{sentence}} {{tts fr_FR speed=1.25 :sentence}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{definition}} {{tts fr_FR speed=1.25 :definition}}',
            }
        ],
    )

    notes = []
    for card in card_models:
        first_sent = card["sentences"][0]
        vocab_definition = card["definition"]

        note_basic = genanki.Note(
            model=multisentence_model, fields=[first_sent, vocab_definition]
        )

        notes.append(note_basic)

    return notes
