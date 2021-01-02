import toga
from screen_state import ScreenWithState

class CardScreen(ScreenWithState):
    def construct_gui(self):
        return toga.Box(toga.Label("Creating cards or so"))