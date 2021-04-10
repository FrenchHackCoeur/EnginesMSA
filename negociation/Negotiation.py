from typing import List
from preferences.Item import Item
from arguments.Argument import Argument

from arguments.CoupleValue import CoupleValue
from arguments.Comparison import Comparison

from preferences.CriterionName import CriterionName
from preferences.Value import Value


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
                    "arguments": [],
                    "accepted_engine": None,
                    "close_agreements": [],
                    "engines_mentioned": {}
                }

        return result

    def get_tuple(self, agent_1: str, agent_2: str):
        return (agent_1, agent_2) if agent_1 < agent_2 else (agent_2, agent_1)

    def start_negotiation(self, initiator: str, interlocutor: str):
        tuple_ = self.get_tuple(initiator, interlocutor)
        self._negotiations[tuple_]["initiator"] = initiator

    def add_argument(self, agent_1: str, agent_2: str, argument: Argument):
        tuple_ = self.get_tuple(agent_1, agent_2)
        conclusion, _ = Argument.argument_parsing(argument)

        # Saving the engine mentioned in the argument
        self._add_engine(agent_1, agent_2, conclusion[1])

        self._negotiations[tuple_]["arguments"].append(argument)

    def has_started_negotiation(self, initiator: str, interlocutor: str) -> bool:
        tuple_ = self.get_tuple(initiator, interlocutor)
        if self._negotiations[tuple_]["initiator"] is not None:
            return True

        return False

    def set_accepted_engine(self, agent_1: str, agent_2, engine: Item):
        tuple_ = self.get_tuple(agent_1, agent_2)
        self._negotiations[tuple_]["accepted_engine"] = engine

    def accept_ending_negotiation(self, agent_1: str, agent_2: str):
        tuple_ = self.get_tuple(agent_1, agent_2)
        self._negotiations[tuple_]["close_agreements"].append(agent_1)

    def is_negotiation_ended(self, agent_1: str, agent_2: str):
        tuple_ = self.get_tuple(agent_1, agent_2)
        return len(self._negotiations[tuple_]["close_agreements"]) == 2

    def is_argument_already_used(self, agent_1: str, agent_2: str, argument: Argument) -> bool:
        tuple_ = self.get_tuple(agent_1, agent_2)
        conclusion, premisses = Argument.argument_parsing(argument)
        arguments = self._negotiations[tuple_]["arguments"]

        for index in range(len(arguments)):
            argument: Argument = arguments[index]
            conclusion_bis, premisses_bis = Argument.argument_parsing(argument)

            if len(premisses) != len(premisses_bis):
                continue

            if conclusion[0] != conclusion_bis[0]:
                # boolean decision are different
                continue

            if conclusion[1] != conclusion_bis[1]:
                # mismatch concerning the engine
                continue

            if len(premisses) == 1:
                couple_value: CoupleValue = premisses[0]
                couple_value_bis: CoupleValue = premisses_bis[0]

                if couple_value.get_criterion_name() == couple_value_bis.get_criterion_name():
                    return True
            else:
                couple_value: CoupleValue = premisses[0]
                couple_value_bis: CoupleValue = premisses_bis[0]

                comparison: Comparison = premisses[1]
                comparison_bis: Comparison = premisses_bis[1]

                if couple_value.get_criterion_name() != couple_value_bis.get_criterion_name():
                    continue

                if comparison.get_best_criterion_name() != comparison_bis.get_best_criterion_name():
                    continue

                if comparison.get_worst_criterion_name() != comparison_bis.get_worst_criterion_name():
                    continue

                return True

        return False

    def _add_engine(self, agent_1: str, agent_2: str, engine: Item):
        tuple_ = self.get_tuple(agent_1, agent_2)
        self._negotiations[tuple_]["engines_mentioned"][engine] = 1

    def has_engine_been_proposed(self, agent_1: str, agent_2: str, engine: Item) -> bool:
        tuple_ = self.get_tuple(agent_1, agent_2)
        engines_mentioned = self._negotiations[tuple_]["engines_mentioned"]
        return engine in engines_mentioned


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
    argument_1 = Argument(False, item)
    argument_1.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD)

    argument_2 = Argument(False, item)
    argument_2.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD)
    argument_2.add_premiss_comparison(CriterionName.ENVIRONMENT_IMPACT, CriterionName.CONSUMPTION)

    negotiations.add_argument(agents[0], agents[1], argument_1)
    negotiations.add_argument(agents[0], agents[1], argument_2)

    assert len(dict_[(agents[0], agents[1])]["arguments"])
    print("[INFO] Adding an argument to the list... OK!")

    # Testing function to determine if a negotiation has started with a specific interlocutor
    res = negotiations.has_started_negotiation(agents[0], agents[2])
    res_2 = negotiations.has_started_negotiation(agents[0], agents[1])
    assert res is False
    assert res_2 is True
    print("[INFO] Function has_started_negotiation works correctly... OK!")

    # Testing ending a negotiation
    negotiations.accept_ending_negotiation(agents[0], agents[1])
    negotiations.accept_ending_negotiation(agents[1], agents[0])

    assert negotiations.is_negotiation_ended(agents[0], agents[1]) is True
    print("[INFO] Negotion has ended successfully... OK!")

    # Testing non redundancy of arguments
    resp = negotiations.is_argument_already_used(agents[0], agents[1], argument_1)
    assert resp is True
    resp = negotiations.is_argument_already_used(agents[0], agents[1], argument_2)
    assert resp is True
    print("[INFO] Detecting redundancy in arguments... OK!")

    # Checking the function to determiner if an engine has already been discussed
    resp = negotiations.has_engine_been_proposed(agents[0], agents[1], item)
    assert resp is True
    resp = negotiations.has_engine_been_proposed(agents[0], agents[2], item)
    assert resp is False
    print("[INFO] An agent can check if an engine has already been mentioned... OK!")