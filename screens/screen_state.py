from togawizard import WizardScreen

class ScreenWithState(WizardScreen):
    def __init__(self, state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = state