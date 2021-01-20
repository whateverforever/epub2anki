from readers import reader_anki, reader_epub, reader_srt

input_readers = [reader_anki, reader_epub, reader_srt]
reader_for_extension = {}

class DefectPluginError(Exception):
    pass

for reader in input_readers:
    if not hasattr(reader, "load_text_from"):
        raise DefectPluginError("{} lacks a load_text_from() function.".format(reader))

    for ext in reader.SUPPORTED_EXTENSIONS:
        if ext not in reader_for_extension:
            reader_for_extension[ext] = reader
        else:
            raise Exception(
                "{} supports extension .{}, but that one is already claimed by {}. \
                Please remove one of the conflicting plugins.".format(
                    reader, ext, reader_for_extension
                )
            )


def load_nlp_models():
    import nlp.french.nlp_french
    return {"french": nlp.french.nlp_french}

