# ALSO REQUIRE POS etc (maybe directly spacy object?)

def filter(lemmas, all_sentences, lemma_raw_texts):
    print("Running low freq filter")
    
    out = []

    for counted_lemma in lemmas:
        lem, count, sentence_idxs = counted_lemma

        if count >= 3:
            out.append(counted_lemma)

    return out