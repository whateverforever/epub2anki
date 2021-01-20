def highlight_word(word, sentence, highlight="<u>WORD</u>"):
    patch = highlight.replace("WORD", word)
    highlighted_sentence = sentence.replace(word, patch)
    return highlighted_sentence