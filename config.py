NUM_SENTENCES = 5  # Number of sentences we want on our cards
MAX_WORDS_PER_SENT = 15
PADDING_UNIVERSAL = 15

DEBUG_STATE_DUMP = "state.pickle"

from filters import filter_low_freq

FILTER_PIPELINE = [
    filter_low_freq
]

# Preview:
# BOOK_PLUGIN = "reader_epub"
# NLP_PLUGIN = "nlp_france"