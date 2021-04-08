from typing import List, Union
from negociation.Negotiation import Negotiation
from preferences.Item import Item
from arguments.Argument import Argument
import random


class EnginesNegotiation(Negotiation):
    def __init__(self, engines: List['Item']):
        super().__init__("A negotiation about engines")
        self._engines = engines

    def get_engines(self) -> List['Item']:
        """
        Returns the list of engines that two agents may discuss

        return:
          A list of engines used for negotiation.
        """
        return self._engines

    def add_interlocutor(self, interlocutor_id: str):
        """
        Add an interlocutor to negotiate about engines

        params:
            - interlocutor_id: The id of our interlocutor

        """
        super().add_interlocutor(interlocutor_id)

    def add_negotiation_topic(self, interlocutor_id: str, topic: 'Item'):
        """
        Add an engine to be negotiated between the agent and interlocutor_id

        Params:
            - interlocutor_id the id of interlocutor to negotiate with
        """
        self._negotiations[interlocutor_id][topic] = []

    def add_argument(self, interlocutor_id: str, topic: 'Item', argument: 'Argument'):
        """
        Add an argument for a negotiation about a specific engine with interlocutor_id

        Params:
         - interlocutor_id: the id of the interlocutor with which the agent is currently negotiating about a specific
         engine.
         - topic: The engine currently being negotiating
         - argument: The argument used by the agent
        """
        self._negotiations[interlocutor_id][topic].append(argument)

    def get_random_negotiation_topic(self, interlocutor_id: str) -> Union[None, 'Item']:
        """
        Return an engine that has not been negotiated with interlocutor_id yet. It may possible that the function
        returns a None object if the agents have negotiated all the engines mentioned in engines_.

        Params:
            - interlocutor_id the id of interlocutor to negotiate with
        Return:
            An engine to negotiate if it's possible to do so
        """
        topics_negotiated = set(self._negotiations[interlocutor_id].keys())
        available_topics = set(self._engines).difference(topics_negotiated)

        if len(available_topics) == 0:
            return None

        selected_topic = random.choice(list(available_topics))

        # Adding the engine to the list of items that have been negotiated with interlocutor_id
        self.add_negotiation_topic(interlocutor_id, selected_topic)

        return selected_topic


if __name__ == '__main__':
    # Creating a list of engines
    engines = [
        Item("Electric Engine", "An engine that works with electricity"),
    ]

    # Creating Negotiation instance
    negotiations = EnginesNegotiation(engines)

    # Testing returning engines
    engines_ = negotiations.get_engines()

    assert len(engines_) == len(engines)
    print("[INFO] Getting engines... OK !")

    # Testing adding interlocutor
    agent_id = "Alice"
    negotiations.add_interlocutor(agent_id)
    negotiations_ = negotiations._negotiations

    assert len(negotiations_[agent_id]) == 0
    print("[INFO] Adding new interlocutor... OK !")

    # Testing adding a new negotiation topic
    topic = negotiations.get_random_negotiation_topic(agent_id)

    assert topic is not None
    assert type(topic) is Item
    print("[INFO] Getting random topic to negotiate with alice ... OK !")

    topic = negotiations.get_random_negotiation_topic(agent_id)

    assert topic is None
    print("[INFO] Getting none value as all the engines have been negotiated with alice... OK!")

    # Testing adding an argument
    negotiations.add_argument(agent_id, engines[0], Argument(True, engines[0]))
    negotiations_ = negotiations._negotiations[agent_id]

    assert len(negotiations_) == 1
    print("[INFO] Adding an argument concerning a specific negotiation... OK!")
