def filter(lemmas, all_sentences, lemma_raw_texts):
    print("Running short filter")
    
    out = []

    for counted_lemma in lemmas:
        lem, count, sentence_idxs = counted_lemma

        if len(lem) > 3:
            out.append(counted_lemma)

    return out