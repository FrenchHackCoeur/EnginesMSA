from typing import List
from dialog.DialogTopics import DialogTopics

class Dialog:
    def __init__(self, description):
        # Permits to understand what the agents will be talking about
        self._description = description
        self._dialogs = dict()

    def get_dialog_description(self):
        """
        Return a description of the discussion
        """
        return self._description

    def add_interlocutor(self, interlocutor_id):
        """
        Add an interlocutor
        """
        self._dialogs[interlocutor_id] = None  # Specialised classes will take care of it

    def remove_interlocutor(self, interlocutor_id):
        """
        Delete an interlocutor we would be able to talk with.
        """
        del self._dialogs[interlocutor_id]

    def get_interlocutors(self) -> List:
        """
        Return a list of interlocutors
        """
        return list(self._dialogs.keys())

    def get_dialog_with_agent(self, agent_id) -> DialogTopics:
        """
        Return a dialog with a specific agent.
        """
        return self._dialogs[agent_id]

    def is_not_an_interlocutor(self, agent_id) -> bool:
        """
        Return a boolean to indicate whether or not the agent is already communicating with another agent
        """
        try:
            discussion = self._dialogs[agent_id]
            return False
        except KeyError:
            return True


