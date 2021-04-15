from typing import List, Tuple
from preferences.Item import Item
from arguments.Argument import Argument

from arguments.CoupleValue import CoupleValue
from arguments.Comparison import Comparison

from preferences.CriterionName import CriterionName
from preferences.Value import Value


class Negotiation:
    def __init__(self, agents: List[str]):
        self._negotiations = Negotiation.initialize(agents)

    @staticmethod
    def initialize(agents_id: List[str]) -> dict:
        """
        This function aims to initialize the dictionary that will contain all the negotiation objects. Each negotiation
        object is identified by the identifier of the two agents negotiating one or several engines.

        Params:
            - agents_id (List): A list containing the identifiers of all the agents to construct the negotiations object.
        Returns:
            A dictionary containing several negotiation objects..

        """
        result = dict()
        agents_size = len(agents_id)
        for i in range(agents_size):
            for j in range(i + 1, agents_size):
                result[(agents_id[i], agents_id[j])] = {
                    "initiator": None,
                    "arguments": [],
                    "accepted_engine": None,
                    "close_agreements": [],
                    "engines_mentioned": {}
                }

        return result

    @staticmethod
    def _get_tuple(agent_1: str, agent_2: str) -> Tuple:
        """
        This function aims to create a key to access a negotiation object

        Params:
            - agent_1 (int): The identifier of one of the agents that is part of a specific negotiation T.
            - agent_2 (int): The identifier of the other agent involved in the negotiation T.

        Returns:
             A tuple to access a negotiation object.
        """
        return (agent_1, agent_2) if agent_1 < agent_2 else (agent_2, agent_1)

    def start_negotiation(self, initiator: str, interlocutor: str):
        """
        The purpose of this function is to start a negotiation between two agents to discuss engines. The negotiation
        will end when both agents agree on a motor M.

        Params:
            - initiator (int): The identifier of the agent that starts the negotiation process
            - interlocutor (int): The identifier of the other agent involved in the newly created negotiation process.

        """
        tuple_ = Negotiation._get_tuple(initiator, interlocutor)
        self._negotiations[tuple_]["initiator"] = initiator

    def add_argument(self, agent_1: str, agent_2: str, argument: Argument):
        """
        This function aims to add an argument that has been mentioned by agent_1 during the negotiation process.

        Params:
             - agent_1 (int): The identifier of the agent who proposed the argument
             - agent_2 (int): The identifier of the agent involved in the negotiation process for which the argument was
             proposed.
             - argument (Argument): The argument that has been advanced by agent_1

        """
        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        conclusion, _ = Argument.argument_parsing(argument)

        # Saving the engine mentioned in the argument
        self._add_engine(agent_1, agent_2, conclusion[1])

        self._negotiations[tuple_]["arguments"].append((agent_1, argument))

    def has_started_negotiation(self, agent_1: str, agent_2: str) -> bool:
        """
        This function aims to check whether or not a negotiation process has started between two agents.

        Params:
            - agent_1 (int): The identifier of one of the two agents that should be involved in a specific negotiation T.
            _agent_2 (int): The identifier of the second agent that should be involved in the T negotiation.

        Returns:
             A boolean indicating whether or not the two agents have started arguing about which engine they will
             retain in the end.
        """
        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        if self._negotiations[tuple_]["initiator"] is not None:
            return True

        return False

    def set_accepted_engine(self, agent_1: str, agent_2: str, engine: Item):
        """
        This function aims to store the engine that has been retained by the two agents.

        Params:
            - agent_1 (int): The identifier of one of two agents involved in the negotiation T.
            - agent_2 (int): The identifier of the second agent involved in the negotiation T.
            - engine (Item): The engine that has been retained by the two agents.

        """
        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        self._negotiations[tuple_]["accepted_engine"] = engine

    def accept_ending_negotiation(self, agent_1: str, agent_2: str):
        """
        This function aims to indicate that agent_1 is in favor of stopping the negotiation. This way of thinking is
        highly inspired by the three hand shakes protocol used in TCP.

        Params:
            - agent_1 (int): The identifier of one of two agents involved in the negotiation T.
            - agent_2 (int): The identifier of the second agent involved in the negotiation T.
        """
        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        self._negotiations[tuple_]["close_agreements"].append(agent_1)

    def is_negotiation_ended(self, agent_1: str, agent_2: str) -> bool:
        """
        This function aims to check whether or not the two agents have already agreed on a specific engine.

        Params:
            - agent_1 (int): The identifier of one of two agents involved in the negotiation T.
            - agent_2 (int): The identifier of the second agent involved in the negotiation T.

        Returns:
            A boolean indicating whether or not the two agents have already agreed on a specific engine.
        """

        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        return len(self._negotiations[tuple_]["close_agreements"]) == 2

    def is_argument_already_used(self, agent_1: str, agent_2: str, argument: Argument) -> bool:
        """
        This function aims to check whether or not the argument object has already been used in the negotiation process
        between agent_1 and agent_2.

        Params:
            - agent_1 (int): The identifier of one of two agents involved in the negotiation T.
            - agent_2 (int): The identifier of the second agent involved in the negotiation T.
            - argument (Argument): The argument that agent_1 would try to advance to agent_2 in their negotiation.

        Returns:
            A boolean indicating whether or not the argument advanced by agent_1 has already been used in the
            negotiation.
        """
        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        conclusion, premisses = Argument.argument_parsing(argument)
        arguments = self._negotiations[tuple_]["arguments"]

        for index in range(len(arguments)):
            argument: Argument = arguments[index][1]
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
        """
        This function aims to store in memory an engine that has been discussed between two agents.

        Params:
           - agent_1 (int): The identifier of one the two agents involved in a specific negotiation T.
            - agent_2 (int): The identifier of the second agent involved in the negotiation T.
            - engine (Item): An engine that has just been discussed between the two agents.

        """
        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        self._negotiations[tuple_]["engines_mentioned"][engine] = 1

    def has_engine_been_proposed(self, agent_1: str, agent_2: str, engine: Item) -> bool:
        """
        This function aims to check whether or not an engine has been mentioned during a negotiation process.

        Parameters:
            - agent_1 (int): The identifier of one the two agents involved in a specific negotiation T.
            - agent_2 (int): The identifier of the second agent involved in the negotiation T.
            - engine (Item): The engine for which we would like to know if the latter has already been mentioned in the
            negotiation T.

        Returns:
            A boolean indicating whether or not a specific engine has already been discussed between the two agents.

        """

        tuple_ = Negotiation._get_tuple(agent_1, agent_2)
        engines_mentioned = self._negotiations[tuple_]["engines_mentioned"]
        return engine in engines_mentioned


if __name__ == '__main__':
    agents = ["Alice", "Bob", "Hugo"]
    item = Item("Electric Engine", "An engine that works with electricity")
    negotiations = Negotiation(agents)

    # Testing structure of the dictionary
    dict_ = negotiations._negotiations
    assert len(list(dict_.keys())) == len(agents)

    print("[INFO] Structure of the dictionary is correct ... OK!")
    # Trying to start a negotiation
    negotiations.start_negotiation(agents[0], agents[1])

    assert dict_[(agents[0], agents[1])]["initiator"] == agents[0]
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
    print("[INFO] Negotiation has ended successfully... OK!")

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