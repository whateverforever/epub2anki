import sqlite3

from ankipandas import Collection

from html_cleaner import strip_tags

def get_all_decks():
    col = Collection()

    try:
        col.notes
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(
            "Seems like Anki is running. Can't access database while that is the case. Please quit Anki"
        )
        return None

    res = sorted(col.cards.cdeck.unique())
    del col

    return res 

def get_deck_string(deck_name):
    """
    Returns all cards in one deck concatenated together as a single string.
    """

    col = Collection()

    try:
        col.notes
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(
            "Seems like Anki is running. Can't access database while that is the case. Please quit Anki"
        )
        return None

    french_cards = col.cards[col.cards.cdeck.str.contains(deck_name)]
    french_notes = col.notes[col.notes.nid.isin(french_cards.nid)]

    partially_french_fields = french_notes["nflds"]
    partially_french_fields = [
        strip_tags(field)
        for all_fields in partially_french_fields
        for field in all_fields
    ]

    anki_text = " ; ".join(partially_french_fields)

    del col
    return anki_text

if __name__ == "__main__":
    get_all_decks()