from io import StringIO
import sys
import os
import threading
import time

import toga
from toga.constants import COLUMN
from toga.style.pack import Pack
from togawizard import WizardBox, WizardScreen
from travertino.constants import BOLD, RIGHT, VISIBLE

import backend
import components as ui


class Logger:
    def set_textarea(self, textarea):
        self._textarea = textarea

    def debug(self, message):
        self._textarea.value += f"{message}\n"


class Step:
    """
    Context manager to frame output while executing something. Use custom_print_fun
    to log to UI elements.
    """

    def __init__(self, step_name, custom_print_fun=None, capture_stdouterr=True):
        self.t_start = time.time()
        self.step_name = step_name
        self.custom_print_fun = custom_print_fun or print

        self.stdout_buffer = None
        if capture_stdouterr:
            self.stdout_buffer = StringIO()

    def __enter__(self):
        self.custom_print_fun(f"Starting '{self.step_name}' [...")

        if self.stdout_buffer:
            sys.stdout = self.stdout_buffer
            sys.stderr = self.stdout_buffer

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.stdout_buffer:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.custom_print_fun(self.stdout_buffer.getvalue())

        self.custom_print_fun(
            f"...] Finished '{self.step_name}', took {time.time() - self.t_start:.1f}s\n"
        )


LOG = Logger()


class Epub2Anki(toga.App):
    def startup(self):
        log_textarea = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        self.log_window = toga.Window(title="Under the Hood")
        self.log_window.content = toga.Box(children=[log_textarea])
        self.log_window.show()

        LOG.set_textarea(log_textarea)
        LOG.debug("Logging window is up and running...")

        state = {
            "app": self,
            "epub_path": None,
            "anki_all_decks": None,
            "anki_selected_deck": None,
        }

        welcome_screen = FileChoosingScreen(state=state)
        welcome_screen.on_gui_constructed(self.load_anki_decks)
        info_screen = InfoScreen(state=state)
        info_screen.on_gui_constructed(self.process_text_sources)
        vocab_screen = VocabScreen(state=state)

        wizard = WizardBox([vocab_screen])
        wizard.style.update(flex=1)

        self.main_window = toga.MainWindow(title=self.formal_name, size=(30, 30))
        self.main_window.content = wizard
        self.main_window.content.style.update(padding=10)
        self.main_window.show()

    def load_anki_decks(self, screen):
        LOG.debug("Loading Anki decks...")

        anki_decks = backend.reader_anki.get_all_decks()
        screen._state["anki_all_decks"] = anki_decks

        for deck in anki_decks:
            LOG.debug("- Found {}".format(deck))

    def process_text_sources(self, screen):
        def do_slow_stuff():
            state = screen._state
            with screen.step("Loading epub contents"):
                text_epub = backend.reader_epub.read_and_clean_epub(state["epub_path"])
                state["epub_contents"] = text_epub

            with screen.step("Loading anki card contents"):
                text_anki = backend.reader_anki.get_deck_string(
                    state["anki_selected_deck"]
                )
                state["anki_deck_contents"] = text_anki
                print(text_anki[:100])

            with screen.step("Loading NLP model..."):
                nlp_module = backend.load_nlp_models()
                nlp_model = nlp_module["french"].model
                state["nlp_model"] = nlp_model
                state["nlp_module"] = nlp_module["french"]

            with screen.step("NLP'ing the epub"):
                doc_epub = state["nlp_module"].lemmatize_doc(text_epub)

            with screen.step("NLP'ing the anki cards"):
                doc_anki = state["nlp_module"].lemmatize_doc(text_anki)

            with screen.step("Extracting lemmatized words and sentences"):
                texts_epub, lemmas_epub, sents_epub = state[
                    "nlp_module"
                ].get_lemmas_and_sentences(doc_epub)
                print("lemmas", lemmas_epub[0:50])

            with screen.step("Extracting lemmatized words and sentences from Anki"):
                texts_anki, lemmas_anki, sents_anki = state[
                    "nlp_module"
                ].get_lemmas_and_sentences(doc_anki)
                print("lemmas anki", lemmas_anki[0:50])

        th = threading.Thread(target=do_slow_stuff)
        th.start()


class ScreenWithState(WizardScreen):
    def __init__(self, state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = state


class VocabScreen(ScreenWithState):
    def construct_gui(self):
        vocab_lt = ui.LabeledText("Vocab:", "<vocab_lt placeholder>",)
        self.vocab_label = vocab_lt.text_label

        self.examples_list = toga.Table(["Example Sentences"])
        self.examples_list.style.update(flex=1, padding_top=10, padding_bottom=10)

        button_box = toga.Box()
        button_box.add(
            toga.Button(
                "Ignore Word",
                style=Pack(flex=1, padding_right=10),
                on_press=self.ignore_btn_clicked,
            )
        )
        button_box.add(
            toga.Button(
                "Skip Word",
                style=Pack(flex=1, padding_right=10),
                on_press=self.skip_btn_clicked,
            )
        )
        button_box.add(
            toga.Button("Take Word", style=Pack(flex=2), on_press=self.take_btn_clicked)
        )

        return toga.Box(
            children=[vocab_lt, self.examples_list, button_box],
            style=Pack(direction=COLUMN, flex=1),
        )

    def populate(self):
        self.vocab_label.text = "asdfasdfasdfasdf"
        self.examples_list.data = ["asdf", "asd adf ad f f kasjdflkj asdfjlkjf"]

    def ignore_btn_clicked(self, sender):
        pass

    def skip_btn_clicked(self, sender):
        pass

    def take_btn_clicked(self, sender):
        pass


class InfoScreen(ScreenWithState):
    def construct_gui(self):
        epub_label = toga.Label(
            "Epub:", style=Pack(width=50, font_weight=BOLD, text_align=RIGHT)
        )
        self.summary_epub_path = toga.Label("<epub path placeholder>")
        summary_epub_box = toga.Box(children=[epub_label, self.summary_epub_path])

        summary_anki = toga.Label(
            "Anki:", style=Pack(width=50, font_weight=BOLD, text_align=RIGHT)
        )
        self.summary_anki_deck = toga.Label("<anki deck placeholder>")
        summary_anki_box = toga.Box(
            children=[summary_anki, self.summary_anki_deck],
            style=Pack(padding_bottom=10),
        )

        self.status_textarea = toga.MultilineTextInput(
            style=Pack(flex=1, font_family="monospace")
        )

        done_btn = toga.Button("Done", on_press=self.mark_finished)

        main_box = toga.Box(
            children=[
                summary_epub_box,
                summary_anki_box,
                self.status_textarea,
                done_btn,
            ],
            style=Pack(direction=COLUMN, flex=1),
        )
        return main_box

    def populate(self):
        self.summary_epub_path.text = os.path.basename(self._state["epub_path"])
        self.summary_anki_deck.text = self._state["anki_selected_deck"]

    def step(self, step_name):
        return Step(step_name, self.update_progress)

    def update_progress(self, message):
        self.status_textarea.value += f"{message}\n"


class FileChoosingScreen(ScreenWithState):
    def construct_gui(self):
        epub_label = toga.Label("Please choose the epub file", style=Pack(flex=1))
        self.epub_file_btn = toga.Button("Choose File", on_press=self.pressed_epub_btn)
        epub_box = toga.Box(
            children=[epub_label, self.epub_file_btn], style=Pack(padding_bottom=5)
        )

        anki_label = toga.Label("Which is your existing anki deck?", style=Pack(flex=1))
        self.anki_choice = toga.Selection(style=Pack(width=180))
        anki_box = toga.Box(
            children=[anki_label, self.anki_choice], style=Pack(padding_bottom=5)
        )

        finished_btn = toga.Button("Finished", on_press=self.pressed_finish_btn)

        main_box = toga.Box(
            children=[epub_box, anki_box, finished_btn],
            style=Pack(direction=COLUMN, width=400),
        )

        self.add(main_box)

    def populate(self):
        self.anki_choice.items = self._state["anki_all_decks"]

    def pressed_finish_btn(self, sender):
        if not self._state["epub_path"]:
            self._parent_wizard.app.main_window.error_dialog(
                "No Epub Selected",
                "You need to chose an epub. So far, nothing has been selected >:{",
            )
            return

        self._state["anki_selected_deck"] = self.anki_choice.value
        self.mark_finished(sender)

    def pressed_epub_btn(self, btn):
        app = self._parent_wizard.app
        epub_path = str(app.main_window.open_file_dialog("Choose epub"))

        if not epub_path.endswith(".epub"):
            app.main_window.error_dialog(
                "Invalid File Suffix",
                "The file doesn't end in .epub, and so I won't take it. Fight me >:{",
            )
            return

        self._state["epub_path"] = epub_path
        self.epub_file_btn.label = os.path.basename(epub_path)


if __name__ == "__main__":
    app = Epub2Anki("epub2anki", "de.thousandyardstare.epub2anki")
    app.main_loop()
