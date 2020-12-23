import spacy
from spacy_langdetect import LanguageDetector

with open("french_stopwords.txt", "r") as fh:
    stopwords = fh.readlines()
    stopwords = [word.strip() for word in stopwords]

model = spacy.load("fr_core_news_md")
model.Defaults.stop_words |= set(stopwords)
model.add_pipe(LanguageDetector(), name="language_detector", last=True)
