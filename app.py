import asyncio
import os
import re
import sys
import time

import dill
import numpy as np
import toga
from toga.constants import COLUMN
from toga.style.pack import Pack
from togawizard import WizardBox

import backend
import screens
from cardgenerators import gen_first_sent
from config import (DEBUG_STATE_DUMP, FILTER_PIPELINE, MAX_WORDS_PER_SENT,
                    PADDING_UNIVERSAL)
from utils import highlight_word
from utils.filter_count_words import count_words_forall_sentences

RE_MULTI_NEWLINES = re.compile(r"\n+")
KILLED_SENTENCE = "<killed>"


class Epub2Anki(toga.App):
    def startup(self):
        state = {
            "app": self,
            "epub_paths": None,
            "anki_all_decks": None,
            "anki_selected_deck": None,
            "vocab_current": 0,
            "vocab_words": [],
            "vocab_sentences": [],
            "vocab_ignored": [],
            "vocab_taken": [],
            "vocab_taken_current": 0,
            "card_models": [],
        }

        welcome_screen = screens.FileChoosingScreen(state=state)
        welcome_screen.on_gui_constructed(self.load_anki_decks)

        process_screen = screens.ProcessingScreen(state=state)
        process_screen.on_gui_constructed(self.on_process_screen_ready)

        vocab_screen = screens.VocabScreen(state=state)

        self.sentence_screen = screens.SentenceScreen(state=state)
        commands = [
            toga.Command(
                self.clipboard_paste_cmd,
                label=f"Paste",
                shortcut=toga.Key.MOD_1 + toga.Key.V,
            ),
            toga.Command(
                self.interesting_key_pressed,
                label="CMD Enter",
                shortcut=toga.Key.MOD_1 + toga.Key.ENTER,
            ),
            toga.Command(self.interesting_key_pressed, label="1", shortcut=toga.Key._1),
            toga.Command(self.interesting_key_pressed, label="2", shortcut=toga.Key._2),
            toga.Command(self.interesting_key_pressed, label="3", shortcut=toga.Key._3),
        ]
        self.commands.add(*commands)

        card_screen = screens.CardScreen(state=state)
        card_screen.on_gui_constructed(self.on_card_screen_constructed)

        self.progress_label = toga.Label("Step X/X: XXXXX")
        self.progress_bar = toga.ProgressBar(
            style=Pack(flex=1, padding_left=PADDING_UNIVERSAL)
        )
        progress_box = toga.Box()
        progress_box.add(self.progress_label)
        progress_box.add(self.progress_bar)

        self.wizard_box = WizardBox(
            [
                welcome_screen,
                process_screen,
                vocab_screen,
                self.sentence_screen,
                card_screen,
            ]
        )
        self.wizard_box.style.update(flex=1)
        self.wizard_box.on_screen_change(self.update_progress_bar)

        main_content = toga.Box(
            children=[
                progress_box,
                toga.Divider(style=Pack(padding=(PADDING_UNIVERSAL / 2, 0))),
                self.wizard_box,
            ],
            style=Pack(direction=COLUMN),
        )

        self.main_window = toga.MainWindow(title=self.formal_name, size=(30, 30))
        self.main_window.content = main_content
        self.main_window.content.style.update(padding=PADDING_UNIVERSAL)
        self.main_window.show()

    # HACK, since clipboard doesn't work on macOS by default for this toga version
    # Doesn't respect cursor position
    def clipboard_paste_cmd(self, cmd):
        import pyperclip

        contents = pyperclip.paste()

        self.sentence_screen.definition_field.value += contents

    def interesting_key_pressed(self, cmd: toga.Command):
        self.wizard_box.current_screen.pressed_key(cmd.shortcut)

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

            # DEBUG
            if os.path.isfile(DEBUG_STATE_DUMP):
                with open(DEBUG_STATE_DUMP, "rb") as fh:
                    disk_state = dill.load(fh)
                    screen._state.update(disk_state)

                screen.update_progress(
                    "DEBUG: Loaded from {} instead of computing".format(
                        DEBUG_STATE_DUMP
                    )
                )
                screen.enable_continue()
                await asyncio.sleep(3)
                screen.mark_finished(None)
                return

            def step_load_nlp(state):
                text_epub = ""
                for path in state["epub_paths"]:
                    _, ext = os.path.splitext(path)

                    if ext not in backend.reader_for_extension:
                        self.main_window.error_dialog(
                            f"No plugin for .{ext} files",
                            f"The file you're trying to open ({path}) is not supported, because there is no plugin available for it.",
                        )
                        continue

                    file_reader = backend.reader_for_extension[ext]
                    text_epub += file_reader.load_text_from(path)

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
                (
                    words_raw_epub,
                    words_lem_epub,
                    sents_epub,
                ) = nlp.get_lemmas_and_sentences(state["doc_epub"])
                (
                    words_raw_anki,
                    words_lem_anki,
                    sents_anki,
                ) = nlp.get_lemmas_and_sentences(state["doc_anki"])

                sent_lens = count_words_forall_sentences(sents_epub)
                for idx, _ in enumerate(sents_epub):
                    if sent_lens[idx] > MAX_WORDS_PER_SENT:
                        words_lem_epub[idx] = KILLED_SENTENCE
                        sents_epub[idx] = KILLED_SENTENCE

                # Needs to be imported in the thread it's used in, don't move to top
                import nimporter

                from utils.counter import countWithIndex, removeDuplicates

                lemmas_with_counts = [
                    (lem, count, idxs)
                    for lem, count, idxs in countWithIndex(words_lem_epub)
                    if lem not in words_lem_anki and lem != KILLED_SENTENCE
                ]

                sents_epub = [RE_MULTI_NEWLINES.sub(" ", senti) for senti in sents_epub]

                out = {
                    "vocab_words": [],
                    "vocab_sentences": [],
                    "vocab_frequencies": [],
                }

                for filter_module in FILTER_PIPELINE:
                    try:
                        filtered_lemmas = filter_module.filter(
                            lemmas_with_counts, sents_epub, words_raw_epub
                        )
                    except Exception as e:
                        print(
                            "Filter {} failed with exception {}. Failing gracefully by ignoring filter".format(
                                filter_module.__name__, e
                            )
                        )
                        continue

                    lemmas_with_counts = filtered_lemmas

                for counted_lemma in lemmas_with_counts:
                    lem, count, sentence_idxs = counted_lemma

                    if len(lem) < 3:
                        continue

                    lem_sentences = [sents_epub[i] for i in sentence_idxs]
                    lem_verbatum_texts = [words_raw_epub[i] for i in sentence_idxs]

                    highlighted_sentences = [
                        highlight_word(
                            lem_verbatum_texts[isent], sent, highlight="<u>WORD</u>"
                        )
                        for isent, sent in enumerate(lem_sentences)
                    ]
                    out["vocab_words"].append(lem)
                    out["vocab_frequencies"].append(count)
                    out["vocab_sentences"].append(highlighted_sentences)

                # TEMP
                out["vocab_words"] = list(reversed(out["vocab_words"]))
                out["vocab_frequencies"] = list(reversed(out["vocab_frequencies"]))
                out["vocab_sentences"] = list(reversed(out["vocab_sentences"]))

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

            with open(DEBUG_STATE_DUMP, "wb+") as fh:
                # DEBUG: To keep things picklable
                del screen._state["doc_epub"]
                del screen._state["doc_anki"]
                del screen._state["nlp_module"]
                del screen._state["nlp_model"]
                del screen._state["app"]

                disk_state = dill.dump(screen._state, fh)

            screen.update_progress("DEBUG: Wrote state to {}".format(DEBUG_STATE_DUMP))
            screen.enable_continue()

            await asyncio.sleep(5)
            screen.mark_finished(None)

        self.add_background_task(do_background_nlp_stuff)

    def on_card_screen_constructed(self, screen):
        screen._state["card_generators"] = [gen_first_sent]


if __name__ == "__main__":
    app = Epub2Anki("epub2anki", "de.thousandyardstare.epub2anki")
    app.main_loop()
