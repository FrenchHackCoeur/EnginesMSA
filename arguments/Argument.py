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
