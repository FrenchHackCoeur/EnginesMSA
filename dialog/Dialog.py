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

    def add_interlocutor(self, interlocutor_id: str):
        """
        Add an interlocutor
        """
        self._dialogs[interlocutor_id] = None  # Specialised classes will take care of it

    def remove_interlocutor(self, interlocutor_id: str):
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


if __name__ == '__main__':
    description = "A dialog about life"
    dialog = Dialog(description)

    assert dialog.get_dialog_description() == description
    print("[INFO] Method to return the description of the dialog... OK")

    # Test adding an interlocutor
    interlocutor = "AgentSmith"

    dialog.add_interlocutor(interlocutor)

    interlocutors = dialog.get_interlocutors()
    assert len(interlocutors) == 1
    assert interlocutors[0] == interlocutor
    print("[INFO] Method to add an interlocutor and to return interlocutors... OK")

    # Test to remove an interlocutor
    dialog.remove_interlocutor(interlocutor)
    interlocutors = dialog.get_interlocutors()

    assert len(interlocutors) == 0
    print("[INFO] Method to delete an interlocutor... OK")

    # Testing the function that indicates if we are already discussing with a specific agent
    dialog.add_interlocutor(interlocutor)
    answer_1 = dialog.is_not_an_interlocutor(interlocutor)
    answer_2 = dialog.is_not_an_interlocutor("AgentPamela")

    assert answer_1 is False
    assert answer_2 is True

    print("[INFO] Testing the method that indicates whether or not we are already discussing with an agent... OK")
