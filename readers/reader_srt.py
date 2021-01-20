import re

SUPPORTED_EXTENSIONS = [
    ".srt"
]

def load_text_from(path):
    srt = parse_srt_file(path)
    lines = [item["text"] for item in srt]

    lines_clean = [re.sub(r" +-(\"?\w+)", r"\1", line) for line in lines]
    text = " ".join(lines_clean)

    return text

def parse_srt_file(path):
    with open(path) as fh:
        text = fh.read()
    
    return parse_srt(text)

def parse_srt(text):
    srt_rex = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.+)")
    out = []
    for match in srt_rex.finditer(text):
        sub_num = match.group(1)
        sub_timestamp = match.group(2)
        sub_text = match.group(3)

        out.append({
            "num": int(sub_num),
            "timestamp": sub_timestamp,
            "text": sub_text
        })
    return out

if __name__ == "__main__": 
    path = "/Users/max/Desktop/SKAM FRANCE EP.1 S3 _ Je crois que je suis amoureux (1080p_25fps_AV1-128kbit_AAC).Französisch.srt"
    
    print(get_clean_srt_text(path))