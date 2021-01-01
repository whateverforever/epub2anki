import asyncio
import random
import re
import sys
import time

sys.path.append("/Users/max/Coding/python/ellana-vocab")

import numpy as np
import toga
from toga.constants import COLUMN
from toga.style.pack import Pack
from togawizard import WizardBox

import backend
from config import MAX_SENTENCES, PADDING_UNIVERSAL
from html_cleaner import highlight_word
from screen_filechoosing import FileChoosingScreen
from screen_processing import ProcessingScreen
from screen_sentence import SentenceScreen
from screen_vocab import VocabScreen

RE_MULTI_NEWLINES = re.compile(r"\n+")
class Epub2Anki(toga.App):
    def startup(self):
        state = {
            "app": self,
            "epub_path": None,
            "anki_all_decks": None,
            "anki_selected_deck": None,
            "vocab_current": 0,
            "vocab_words": [],
            "vocab_sentences": [],
            "vocab_ignored": [],
            "vocab_taken": [],
            "vocab_taken_current": 0,
            "card_models": []
        }

        welcome_screen = FileChoosingScreen(state=state)
        welcome_screen.on_gui_constructed(self.load_anki_decks)

        process_screen = ProcessingScreen(state=state)
        process_screen.on_gui_constructed(self.on_process_screen_ready)

        vocab_screen = VocabScreen(state=state)

        sentence_screen = SentenceScreen(state=state)

        self.progress_label = toga.Label("Step X/X: XXXXX")
        self.progress_bar = toga.ProgressBar(
            style=Pack(flex=1, padding_left=PADDING_UNIVERSAL)
        )
        progress_box = toga.Box()
        progress_box.add(self.progress_label)
        progress_box.add(self.progress_bar)

        wizard_box = WizardBox(
            [welcome_screen, process_screen, vocab_screen, sentence_screen]
        )
        wizard_box.style.update(flex=1)
        wizard_box.on_screen_change(self.update_progress_bar)

        main_content = toga.Box(
            children=[
                progress_box,
                toga.Divider(style=Pack(padding=(PADDING_UNIVERSAL / 2, 0))),
                wizard_box,
            ],
            style=Pack(direction=COLUMN),
        )

        self.main_window = toga.MainWindow(title=self.formal_name, size=(30, 30))
        self.main_window.content = main_content
        self.main_window.content.style.update(padding=PADDING_UNIVERSAL)
        self.main_window.show()

    def update_progress_bar(self, wizard, screen):
        title = screen.title()
        nscreens = len(wizard._screens)
        idx_screen = wizard._current_screen

        if title:
            self.progress_label.text = f"Step {idx_screen+1}/{nscreens}: {title}"

        self.progress_bar.value = (idx_screen) / nscreens

    def load_anki_decks(self, screen):
        anki_decks = backend.reader_anki.get_all_decks()
        screen._state["anki_all_decks"] = anki_decks

    def on_process_screen_ready(self, screen):
        async def do_background_nlp_stuff(asdf):
            loop = asyncio.get_event_loop()

            def step_load_nlp(state):
                text_epub = backend.reader_epub.read_and_clean_epub(state["epub_path"])
                text_anki = backend.reader_anki.get_deck_string(
                    state["anki_selected_deck"]
                )
                nlp_module = backend.load_nlp_models()
                nlp_model = nlp_module["french"].model

                state["epub_contents"] = text_epub
                state["anki_deck_contents"] = text_anki
                state["nlp_model"] = nlp_model
                state["nlp_module"] = nlp_module["french"]

            def step_nlp_epub(state):
                doc_epub = state["nlp_module"].lemmatize_doc(state["epub_contents"])
                state["doc_epub"] = doc_epub

            def step_nlp_anki(state):
                doc_anki = state["nlp_module"].lemmatize_doc(
                    state["anki_deck_contents"]
                )
                state["doc_anki"] = doc_anki

            def step_counting(state):
                nlp = state["nlp_module"]
                texts_epub, lemmas_epub, sents_epub = nlp.get_lemmas_and_sentences(
                    state["doc_epub"]
                )
                texts_anki, lemmas_anki, sents_anki = nlp.get_lemmas_and_sentences(
                    state["doc_anki"]
                )

                import nimporter
                from counter import countWithIndex, removeDuplicates

                lemmas_with_counts = [
                    (lem, count, idxs)
                    for lem, count, idxs in countWithIndex(lemmas_epub)
                    if lem not in lemmas_anki
                ]

                counts = [count for lem, count, idxs in lemmas_with_counts]

                lemmas_with_counts = [
                    (lem, count, idxs)
                    for lem, count, idxs in countWithIndex(lemmas_epub)
                    if count >= np.quantile(counts, 0.95)
                    and count <= np.quantile(counts, 0.99)
                ]

                sents_epub = [RE_MULTI_NEWLINES.sub(" ", senti) for senti in sents_epub]

                out = {"vocab_words": [], "vocab_sentences": []}
                for counted_lemma in lemmas_with_counts:
                    lem, count, idxs = counted_lemma
                    counts.append(count)

                    if lem in lemmas_anki:
                        continue

                    random.seed(1234)
                    try:
                        lem_sentences = random.sample(
                            ([sents_epub[i] for i in idxs]), MAX_SENTENCES
                        )
                    except ValueError:
                        pass

                    random.seed(1234)
                    try:
                        lem_verbatum_texts = random.sample(
                            ([texts_epub[i] for i in idxs]), MAX_SENTENCES
                        )
                    except ValueError:
                        pass

                    highlighted_sentences = [
                        highlight_word(
                            lem_verbatum_texts[isent], sent, highlight="**WORD**"
                        )
                        for isent, sent in enumerate(lem_sentences)
                    ]
                    out["vocab_words"].append(lem)
                    out["vocab_sentences"].append(highlighted_sentences)
                return out

            # todo maybe echo the size of the models etc
            steps = [
                (step_load_nlp, "Loading the NLP Model etc."),
                (step_nlp_epub, "NLP'ing the epub"),
                (step_nlp_anki, "NLP'ing the anki deck"),
                (step_counting, "Counting, filtering and highlighting"),
            ]

            for i, (step_fun, step_end_description) in enumerate(steps):
                t_start = time.time()
                screen.update_progress(
                    "Step {:02d}: Starting '{}'".format(i, step_end_description)
                )

                out = await loop.run_in_executor(None, step_fun, screen._state)
                duration = time.time() - t_start

                if out:
                    screen._state.update(out)

                screen.update_progress(
                    "Step {:02d}: Finished '{}'. Took {:.2f}s\n".format(
                        i, step_end_description, duration
                    )
                )
            
            screen.enable_continue()

        self.add_background_task(do_background_nlp_stuff)


if __name__ == "__main__":
    app = Epub2Anki("epub2anki", "de.thousandyardstare.epub2anki")
    app.main_loop()
