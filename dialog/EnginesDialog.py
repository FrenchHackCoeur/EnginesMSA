from dialog.Dialog import Dialog
from dialog.DialogTopics import DialogTopics


class EnginesDialog(Dialog):
    def __init__(self, engines):
        super().__init__("A dialog about engines")
        self._engines = engines

    def get_engines(self):
        """
        Returns the list of engines that two agents may discuss
        """
        return self._engines

    def add_interlocutor(self, interlocutor_id):
        """
        Add an interlocutor to talk about engines
        """
        super().add_interlocutor(interlocutor_id)
        self._dialogs[interlocutor_id] = DialogTopics(self._engines)

