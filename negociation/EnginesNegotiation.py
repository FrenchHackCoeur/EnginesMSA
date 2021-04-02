from typing import List, TYPE_CHECKING, Union
from negociation.Negotiation import Negotiation
import random

if TYPE_CHECKING:
    from preferences.Item import Item


class EnginesNegotiation(Negotiation):
    def __init__(self, engines: List['Item']):
        super().__init__("A negotiation about engines")
        self._engines = engines

    def get_engines(self) -> List['Item']:
        """
        Returns the list of engines that two agents may discuss
        """
        return self._engines

    def add_interlocutor(self, interlocutor_id: str):
        """
        Add an interlocutor to negotiate about engines
        """
        super().add_interlocutor(interlocutor_id)

        negotiations = dict()

        for engine in self._engines:
            negotiations[engine.get_name()] = []

        self._negotiations[interlocutor_id] = negotiations

    def add_argument_used_for_negotiations(self, interlocutor_id: str, engine: str, argument: str):
        """
        Append an argument used to negotiate about an engine
        """
        self._negotiations[interlocutor_id][engine].append(argument)

    def delete_negotiation_with_interlocutor(self, interlocutor_id: str, engine: str):
        """
        Delete a negotiation about an engine with a specific interlocutor
        """
        del self._negotiations[interlocutor_id][engine]

    def get_random_engine_for_negotiation(self, interlocutor_id: str) -> Union[str, None]:
        """
        Return a random negotiation to start with an agent
        """
        possible_neg = list(self._negotiations[interlocutor_id])

        if len(possible_neg) == 0:
            return None

        return random.choice(possible_neg)
