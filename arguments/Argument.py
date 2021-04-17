#!/usr/bin/env python3
from typing import List, Union, Tuple

from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue

from preferences.Preferences import Preferences
from preferences.CriterionName import CriterionName
from preferences.Item import Item
from preferences.Value import Value


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:
        item:
        comparison_list:
        couple_values_list:
    """

    def __init__(self, boolean_decision, item):
        """Creates a new Argument.
        """
        self.__decision = boolean_decision
        self.__item = item
        self.__comparison_list: List['Comparison'] = []
        self.__couple_values_list: List['CoupleValue'] = []

    def add_premiss_comparison(self, val_1: Union[CriterionName, Value], val_2: Union[CriterionName, Value]):
        """Adds a premiss comparison in the comparison list.
        """
        if type(val_1) != type(val_2):
            raise Exception("Types mismatch")

        self.__comparison_list.append(Comparison(val_1, val_2))

    def get_criterion_used_name(self) -> CriterionName:
        """
        Returns the name of the criterion used to create our argument
        """
        return self.__couple_values_list[0].get_criterion_name()

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    @staticmethod
    def argument_parsing(argument: 'Argument') -> List:
        return [
            (argument.__decision, argument.__item),
            [*argument.__couple_values_list, *argument.__comparison_list]
        ]

    @staticmethod
    def support_proposal(item: Item, preferences: Preferences) -> Tuple:
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: str - name of the item which was proposed
        :param preferences: Preferences - the preferences of an agent.
        :return: string - the strongest supportive argument
        """
        return Argument.list_supporting_proposal(item, preferences)[0]

    @staticmethod
    def list_supporting_proposal(item: Item, preferences: Preferences) -> List[Tuple]:
        """
        Generate a list of premisses which can be used to support an item
        :param
            item: Item - name of the item
            preference: Preferences - preferences of an agent
        :return: list of all premisses PRO an item (sorted by order of importance based on agent's preferences)
        """
        result = []
        feelings_about_engine = preferences.get_criterion_value_for_item(item)
        criterion_preferences = preferences.get_criterion_name_list()

        for preference in criterion_preferences:
            criterion_value = feelings_about_engine[preference]

            if criterion_value == Value.VERY_GOOD or criterion_value == Value.GOOD:
                result.append((preference, criterion_value))

        return result

    @staticmethod
    def list_attacking_proposal(item: Item, preferences: Preferences) -> List[Tuple]:
        """
        Generate a list of premisses which can be used to attack an item
        :param item: Item - name of the item
        :param preferences: Preferences - the preferences of an agent
        :return: list of all premisses CON an item (sorted by order of importance based on preferences)
        """
        result = []
        feelings_about_engine = preferences.get_criterion_value_for_item(item)
        criterion_preferences = preferences.get_criterion_name_list()

        for preference in criterion_preferences:
            criterion_value = feelings_about_engine[preference]

            if criterion_value == Value.VERY_BAD or criterion_value == Value.BAD:
                result.append((preference, criterion_value))

        return result

    def __eq__(self, other) -> bool:
        """Overrides the default implementation"""
        if self is other:
            return True

        if isinstance(other, Argument):
            # Then we check if the the two objects talk about the same engine
            if self.__item != other.__item:
                return False

            # We also need to verify the decision (ie the argument is in favor of the engine or not)
            if self.__decision != other.__decision:
                return False

            # Then we check if the two objects have the same number of premisses of type comparison
            if len(self.__comparison_list) == len(other.__comparison_list):
                if len(self.__comparison_list) != 0:
                    comparison_1 = self.__comparison_list[0]
                    comparison_2 = other.__comparison_list[0]

                    if type(comparison_1.get_best_criterion_name()) != type(comparison_2.get_best_criterion_name()):
                        return False

                    if comparison_1.get_best_criterion_name() != comparison_2.get_best_criterion_name():
                        return False

                    if comparison_1.get_worst_criterion_name() != comparison_2.get_worst_criterion_name():
                        return False
            else:
                return False

            # Finally we check if the two objects have the same number of premisses of type couple value
            if len(self.__couple_values_list) == len(other.__couple_values_list):
                if len(self.__couple_values_list) != 0:
                    cp_1 = self.__couple_values_list[0]
                    cp_2 = other.__couple_values_list[0]

                    if cp_1.get_criterion_name() != cp_2.get_criterion_name():
                        return False

                    if cp_1.get_value() != cp_2.get_value():
                        return False
            else:
                return False
            return True
        return NotImplemented

    def __str__(self):
        not_in_favor = 'not' if not self.__decision else ''

        string = f"ARGUE({not_in_favor} {self.__item} <= "

        for item in self.__couple_values_list:
            string += f"{item.__str__()}, "

        for item in self.__comparison_list:
            string += f"{item.__str__()}"

        string = string.rstrip(', ')
        string += ")"

        return string


if __name__ == "__main__":
    engine = Item("Porsche", "An engine from Stuttgart")

    argument_1 = Argument(True, engine)
    argument_2 = Argument(False, engine)

    assert argument_1 != argument_2
    argument_2 = Argument(True, engine)
    assert argument_1 == argument_2
    print("[INFO] Simple equality check ... OK!")

    argument_1.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD)
    argument_2.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.GOOD)

    assert argument_1 != argument_2
    argument_2 = Argument(True, engine)
    argument_2.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD)
    assert argument_1 == argument_2

    print("[INFO] Equality with couple value... OK!")

    argument_1.add_premiss_comparison(CriterionName.CONSUMPTION, CriterionName.ENVIRONMENT_IMPACT)
    argument_2.add_premiss_comparison(CriterionName.DURABILITY, CriterionName.NOISE)

    assert argument_1 != argument_2
    argument_2 = Argument(True, engine)
    argument_2.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD)
    argument_2.add_premiss_comparison(CriterionName.CONSUMPTION, CriterionName.ENVIRONMENT_IMPACT)
    assert argument_1 == argument_2
    print("[INFO] Equality with comparison... OK!")

    argument_2 = Argument(True, engine)
    argument_2.add_premiss_couple_values(CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD)
    argument_2.add_premiss_comparison(Value.VERY_GOOD, Value.GOOD)

    assert argument_1 != argument_2
    print("[INFO] Testing type difference ... OK!")