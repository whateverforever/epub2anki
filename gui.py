
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


class Logger:
    def set_textarea(self, textarea):
        self._textarea = textarea

    def debug(self, message):
        self._textarea.value += f"{message}\n"


LOG = Logger()


class Epub2Anki(toga.App):
    def startup(self):
        log_textarea = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        self.log_window = toga.Window(title="Under the Hood")
        self.log_window.content = toga.Box(children=[log_textarea])
        self.log_window.show()

        LOG.set_textarea(log_textarea)
        LOG.debug("Logging window is up and running...")

        LOG.debug("Loading Anki decks...")
        anki_decks = backend.reader_anki.get_all_decks()
        for deck in anki_decks:
            LOG.debug("- Found {}".format(deck))

        self._state = {
            "epub_path": None,
            "anki_all_decks": anki_decks,
            "anki_selected_deck": None,
        }

        welcome_screen = FileChoosingScreen(state=self._state)
        info_screen = InfoScreen(state=self._state)
        info_screen.on_gui_ready(self.process_text_sources)

        wizard = WizardBox([welcome_screen, info_screen])
        wizard.style.update(flex=1)

        self.main_window = toga.MainWindow(title=self.formal_name, size=(30, 30))
        self.main_window.content = wizard
        self.main_window.content.style.update(padding=10)
        self.main_window.show()

    def process_text_sources(self, screen):
        def do_slow_stuff():
            with screen.step("Loading epub contents"):
                text = backend.reader_epub.read_and_clean_epub(self._state["epub_path"])
                self._state["epub_contents"] = text

            with screen.step("Loading anki card contents"):
                text = backend.reader_anki.get_deck_string(
                    self._state["anki_selected_deck"]
                )
                self._state["anki_deck_contents"] = text
                print(text[:100])

            with screen.step("Loading NLP model..."):
                nlp_models = backend.load_nlp_models()
                nlp_model = nlp_models["french"]
                self._state["nlp_model"] = nlp_model

            with screen.step("NLP'ing the epub"):
                time.sleep(1.34)

            with screen.step("NLP'ing the anki cards"):
                time.sleep(5.67)

        th = threading.Thread(target=do_slow_stuff)
        th.start()


class ScreenWithState(WizardScreen):
    def __init__(self, state):
        super().__init__()
        self._state = state


class InfoScreen(ScreenWithState):
    def construct_gui(self):
        epub_label = toga.Label(
            "Epub:", style=Pack(width=50, font_weight=BOLD, text_align=RIGHT)
        )
        self.summary_epub_path = toga.Label("<epub path placeholder>")
        summary_epub_box = toga.Box(children=[epub_label, self.summary_epub_path])

        summary_anki = toga.Label(
            "Anki:", style=Pack(width=50, font_weight=BOLD, font_family="monospace", text_align=RIGHT)
        )
        self.summary_anki_deck = toga.Label("<anki deck placeholder>")
        summary_anki_box = toga.Box(
            children=[summary_anki, self.summary_anki_deck],
            style=Pack(padding_bottom=10),
        )

        self.status_textarea = toga.MultilineTextInput(style=Pack(flex=1))

        main_box = toga.Box(
            children=[summary_epub_box, summary_anki_box, self.status_textarea],
            style=Pack(direction=COLUMN, flex=1),
        )
        return main_box

    def populate(self):
        self.summary_epub_path.text = os.path.basename(self._state["epub_path"])
        self.summary_anki_deck.text = self._state["anki_selected_deck"]

    def step(self, step_name):
        return self.Step(self, step_name)

    class Step:
        def __init__(self, outer_class, step_name, capture_stdouterr=True):
            self.t_start = time.time()
            self.outer_class = outer_class
            self.step_name = step_name

            self.stdout_buffer = None
            if capture_stdouterr:
                self.stdout_buffer = StringIO()

        def __enter__(self):
            self.outer_class.update_progress(f"Starting '{self.step_name}' [...")
            
            if self.stdout_buffer:
                sys.stdout = self.stdout_buffer
                sys.stderr = self.stdout_buffer


        def __exit__(self, exc_type, exc_value, exc_traceback):
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            self.outer_class.update_progress(self.stdout_buffer.getvalue())
            self.outer_class.update_progress(
                f"...] Finished '{self.step_name}', took {time.time() - self.t_start:.1f}s\n"
            )

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
