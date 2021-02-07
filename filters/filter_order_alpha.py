# USELESS FILTER FOR DEMONSTRATION PURPS

def filter(lemmas, all_sentences, lemma_raw_texts):
    print("Running alphabetic ordering filter")

    out = sorted(lemmas, key=lambda x: x[0])

    return out