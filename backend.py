import reader_anki
import reader_epub
import reader_srt

def load_nlp_models():
    import nlp_french
    return {
        "french": nlp_french
    }
