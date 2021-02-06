# epub2anki

## Installing Requirements

- `python -m spacy download fr_core_news_md`

## Wanted features

### Must Have

- [ ] Ignoring simple words that you don't even want to create a card for
  - How to identify?
    - If frequency --> Might miss important words
- [x] In sentence picking: show how far progress is
- [x] When using hierarchical decks, make sure to anki subdecks as well
- [ ] Error dialog if anki is running
- [x] Ignore sentences that are too long
- [x] Vocab picking needs shortcuts
- [ ] ~~Add skip button also to sentence~~
- [x] Make it so Anki TTS can be used
- [x] Make card generation module replaceable
- [ ] Make it so User can modify how generated cards look like
- [x] Copy Paste for definition field

### Should Have

- [ ] If a sentence of a frequent word contains another unknown word, add that one too
- [ ] Sort Words in Vocab Selection by frequency (arent't they already?)
- [ ] Extra field for question side (e.g. for infinitive: haissent - "hair")

### Nice to Have

- [ ] Add image to definition field
- [x] From [here](https://www.reddit.com/r/Anki/comments/kfhiyp/ideas_about_a_sentence_addon_that_would_repeat/): Instead of only taking one sentence for a given word, take all and randomly display different sentences when querying.
- [ ] Somehow highlight just replaced sentence in table
- [ ] Give score to book, analogous to https://towardsdatascience.com/the-best-netflix-movies-series-to-learn-english-according-to-data-science-dec7b047b164
  - i.e. how much of the 1000 most common words does the book cover?

## Known Bugs

- [ ] Words that are for sure in Anki are still in the "not in Anki" list. Like éclater, poids, faillir
  - Is that because of subdecks?