import re
from typing import List

RE_WORD = re.compile(r"\w+")


def count_words_forall_sentences(sentences: List[str]) -> List[int]:
    out = [-1] * len(sentences)
    for i, senti in enumerate(sentences):
        out[i] = count_words_in_sentence(senti)

    return out


def count_words_in_sentence(sent: str) -> int:
    return len(RE_WORD.findall(sent))


if __name__ == "__main__":
    print(
        count_words_in_sentence(
            "what's going on, this that; or maybe even thosidhsfoaisdhfo!!"
        )
    )

    print(count_words_forall_sentences([
        "I like this and that",
        "and you like other things., what, asdf,a sdf,a sdf"
    ]))

