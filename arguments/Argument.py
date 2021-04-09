#!/usr/bin/env python3
from typing import List, Union
from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue
from preferences.CriterionName import CriterionName
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

    @staticmethod
    def argument_parsing(argument: 'Argument') -> List:
        return [
            (argument.__decision, argument.__item),
            [*argument.__couple_values_list, *argument.__comparison_list]
        ]

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

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
