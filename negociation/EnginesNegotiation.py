from typing import List, Union
from negociation.Negotiation import Negotiation
from preferences.Item import Item
from preferences.CriterionName import CriterionName
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

        negotiations = dict()

        for engine in self._engines:
            negotiations[engine] = []

        self._negotiations[interlocutor_id] = negotiations

    def add_criterion_used_for_negotiation(self, interlocutor_id: str, engine: 'Item', criterion: str):
        """
        Append an argument used to negotiate about an engine

        params:
            - interlocutor_id: The id of our interlocutor
            - engine: A reference to the engine that is currently being negotiated with a specific interlocutor

        """
        self._negotiations[interlocutor_id][engine].append(criterion)

    def get_criterion_used_for_negatiation(self, interlocutor_id: str, engine: 'Item') -> List[str]:
        """
        Return all the criterion used for a negotiation concerning a specific engine

        params:
            - interlocutor_id: The id of our interlocutor
            - engine: A reference to the engine that is currently being negotiated with a specific interlocutor

        return:
            A list of criterion that have been used for negotiation
        """
        return self._negotiations[interlocutor_id][engine]

    def delete_negotiation_with_interlocutor(self, interlocutor_id: str, engine: 'Item'):
        """
        Delete a negotiation about an engine with a specific interlocutor

        params:
        - interlocutor_id: The id of our interlocutor
        - engine: A reference to the engine that is currently being negotiated with a specific interlocutor
        """
        del self._negotiations[interlocutor_id][engine]

    def get_random_engine_for_negotiation(self, interlocutor_id: str) -> Union['Item', None]:
        """
        Return a random negotiation to start with an agent

        params:
            - interlocutor_id: The id of our interlocutor

        return:
            An engine with which an agent can start a negotiation with another agent if they have still engines to
            talk about.
        """
        possible_neg = list(self._negotiations[interlocutor_id])

        if len(possible_neg) == 0:
            return None

        return random.choice(possible_neg)


if __name__ == '__main__':
    # Creating a list of engines
    engines = [
        Item("Electric Engine", "An engine that works with electricity"),
        Item("Diesel Engine", "An engine that works with fuel"),
        Item("Hydrogen Engine", "An engine that works with hydrogen")
    ]

    # Creating Negotiation instance
    negotiations = EnginesNegotiation(engines)

    # Verifying that the _engines property is set
    engines_ = negotiations.get_engines()
    assert engines_ is not None
    assert len(engines_) == 3
    print("[INFO] engines_ property set correctly... ok")

    # Creating an interlocutor named Alice
    alice_id = "alice"

    negotiations.add_interlocutor(alice_id)

    # Checking that negotiations is not empty
    neg_keys = list(negotiations._negotiations.keys())
    assert len(neg_keys) == 1
    assert neg_keys[0] == alice_id
    print("[INFO] adding new interlocutor... ok")

    # Checking that we can discuss with alice about three different engines
    engines_with_alice = list(negotiations._negotiations[alice_id].keys())
    assert len(engines_with_alice) == len(engines)
    print("[INFO] Engines has been added successfully in dict... ok")

    # Checking to pick a random engine
    random_engine = negotiations.get_random_engine_for_negotiation(alice_id)

    assert random_engine is not None
    print("[INFO] getting a random engine to negotiate with alice... ok")

    # Check adding a criteria used for negotiation
    negotiations.add_criterion_used_for_negotiation(alice_id, random_engine, CriterionName.CONSUMPTION.value)

    assert len(negotiations._negotiations[alice_id][random_engine]) == 1
    print("[INFO] Adding a criteria used for a negotiation with Alice... ok")

    # Check retrieving the criteria used for negotiation with Alice
    criterion = negotiations.get_criterion_used_for_negatiation(alice_id, random_engine)
    assert len(criterion) == 1
    assert criterion[0] == CriterionName.CONSUMPTION.value
    print("[INFO] Retrieving criteria used for a negotiation with Alice... ok")

    # Checking deletion of an engine that has been negotiated with Alice
    engine_ = engines[0]
    negotiations.delete_negotiation_with_interlocutor(alice_id, engine_)
    neg_engines_alice = list(negotiations._negotiations[alice_id].keys())
    assert len(neg_engines_alice) == len(engines) - 1
    assert engine_ is not None
    print("[INFO] Deletion of an engine that has been discussed... ok")
    print(engine_)

