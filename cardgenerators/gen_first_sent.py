import genanki

_NAME = "Single Sentence Generator"
_DESCRIPTION = """This generator only uses the first chosen sentence for a simple two-way cards. The others get ignored."""

def generate_notes(card_models):
    """Takes a bunch of card models (see XXX) and returns a list of genanki notes"""
    for card in card_models:
        field_definition = card["definition"]

        note_basic = genanki.Note(
            model=multisentence_model, fields=[*card["sentences"], field_definition]
        )