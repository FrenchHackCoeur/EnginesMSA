from typing import List
from preferences.Item import Item
from arguments.Argument import Argument


class Negotiation:
    def __init__(self, agents: List[str]):
        self._negotiations = self.initialize(agents)

    def initialize(self, agents: List[str]) -> dict:
        result = dict()
        agents_size = len(agents)
        for i in range(agents_size):
            for j in range(i + 1, agents_size):
                result[(agents[i], agents[j])] = {
                    "initiator": None,
                    "arguments": []
                }

        return result

    def get_tuple(self, initiator: str, interlocutor: str):
        return (initiator, interlocutor) if initiator < interlocutor else (interlocutor, initiator)

    def start_negotiation(self, initiator: str, interlocutor: str):
        tuple_ = self.get_tuple(initiator, interlocutor)
        self._negotiations[tuple_]["initiator"] = initiator

    def append_argument(self, initiator: str, interlocutor: str, argument: Argument):
        tuple_ = self.get_tuple(initiator, interlocutor)
        self._negotiations[tuple_]["arguments"].append(argument)

    def has_started_negotiation(self, initiator: str, interlocutor: str) -> bool:
        tuple_ = self.get_tuple(initiator, interlocutor)
        if self._negotiations[tuple_]["initiator"] is not None:
            return True

        return False

if __name__ == '__main__':
    agents = ["Alice", "Bob", "Hugo"]
    item = Item("Electric Engine", "An engine that works with electricity")
    negotiations = Negotiation(agents)

    # Testing structure of the dictionary
    dict_ = negotiations._negotiations
    assert len(list(dict_.keys())) == len(agents)
    try:
        obj_ = dict_[(agents[0], agents[1])]
    except Exception as err:
        print(err)
    print("[INFO] Structure of the dictionary is correct ... OK!")

    # Trying to start a negotiation
    negotiations.start_negotiation(agents[1], agents[0])

    assert dict_[(agents[0], agents[1])]["initiator"] == agents[1]
    print("[INFO] Starting a negotiation with Alice... OK!")

    # Trying to add an argument
    negotiations.append_argument(agents[0], agents[1], Argument(False, item))

    assert len(dict_[(agents[0], agents[1])]["arguments"])
    print("[INFO] Adding an argument to the list... OK!")

    # Testing function to determine if a negotiation has started with a specific interlocutor
    res = negotiations.has_started_negotiation(agents[0], agents[2])
    res_2 = negotiations.has_started_negotiation(agents[0], agents[1])
    assert res is False
    assert res_2 is True
    print("[INFO] Function has_started_negotiation works correctly... OK!")
