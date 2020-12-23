import reader_anki
import reader_epub

def load_nlp_models():
    import nlp_french
    return {
        "french": nlp_french
    }
