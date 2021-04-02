#!/usr/bin/env python3
from typing import TYPE_CHECKING, List, Dict
from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue
from preferences.Item import Item
from pw_argumentation import ArgumentModel, ArgumentAgent

if TYPE_CHECKING:
    from preferences.Item import Item


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
        self.__item = item.get_name()
        self.__comparison_list: List['Comparison'] = []
        self.__couple_values_list: List['CoupleValue'] = []

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    @staticmethod
    def argument_parsing(argument: 'Argument') -> Dict:
        return dict(
            criterion_used_name=argument.__couple_values_list[0].get_criterion_name(),
            criterion_used_value=argument.__couple_values_list[0].get_value(),
        )

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def __str__(self):
        not_in_favor = 'not' if not self.__decision else ''

        string = f"ARGUE({not_in_favor} {self.__item} <= "

        for item in self.__couple_values_list:
            string += f"{item.__str__()},"

        for item in self.__comparison_list:
            string += f"{item.__str__()}"

        string = string.rstrip(',')
        string += ")"

        return string
