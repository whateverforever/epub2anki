import spacy
from spacy_langdetect import LanguageDetector

with open("french_stopwords.txt", "r") as fh:
    stopwords = fh.readlines()
    stopwords = [word.strip() for word in stopwords]

model = spacy.load("fr_core_news_lg")
model.Defaults.stop_words |= set(stopwords)
model.add_pipe(LanguageDetector(), name="language_detector", last=True)

def lemmatize_doc(partially_french_text):
    doc = model(partially_french_text)

    french_sents = [
        sent.text
        for sent in doc.sents
        if sent._.language["language"] == "fr" and sent._.language["score"] >= 0.75
    ]
    pure_french_text = " ".join(french_sents)

    return model(pure_french_text)


def get_lemmas_and_sentences(doc_in):
    # PROPN means a certain token represents a name of a person, company, whatever
    # see https://spacy.io/usage/linguistic-features
    doc = [token for token in doc_in if not token.is_stop and token.pos_ != "PROPN"]

    words_raw = [token.text.strip() for token in doc]
    words_lemmed = [token.lemma_.strip() for token in doc]
    sentences = [token.sent.text.strip() for token in doc]

    return words_raw, words_lemmed, sentences