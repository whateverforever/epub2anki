from readers import reader_anki, reader_epub, reader_srt

def load_nlp_models():
    import nlp.french.nlp_french
    return {
        "french": nlp.french.nlp_french
    }
