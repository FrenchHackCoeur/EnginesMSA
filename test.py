


def list_attacking_proposal(self, item) -> List[Tuple]:
    """
    Generate a list of premisses which can be used to attack an item
    :param item: Item - name of the item
    :return: list of all premisses CON an item (sorted by order of importance based on preferences)
    """
    result = []
    feelings_about_engine = self.preference.get_criterion_value_for_item(item)
    preferences = self.preference.get_criterion_name_list()

    for preference in preferences:
        criterion_value = feelings_about_engine[preference]

        if criterion_value == Value.VERY_BAD or criterion_value == Value.BAD:
            result.append((preference, criterion_value))

    return result


def try_get_counter_argument(self, argument: Argument) -> Union[Argument, None]:
    conclusion, premisses = Argument.argument_parsing(argument)
    arguments = []
    if conclusion[0]:
        if len(premisses) == 1:
            # Checking if the premiss is a CoupleValue
            if type(premisses[0]) == CoupleValue:
                premiss: CoupleValue = premisses[0]
                criterion = premiss.get_criterion_name()

                # Trying to find a better criterion
                better_criterion = self.preference.get_better_criterion(criterion)
                if not better_criterion:
                    argument = Argument(False, conclusion[1])
                    argument.add_premiss_comparison(better_criterion, criterion)
                    arguments.append(argument)

                # Trying to find a better product

        # Selecting a random coutner argument
        return random.choice(arguments)
    else:
        pass

    if len(arguments) == 0:
        return None

    return random.choice(arguments)


elif performative == MessagePerformative.ARGUE:
# Getting the argument used by the other agent.
argument: Argument = message.get_content()

# Getting engine
engine: Item = Argument.argument_parsing(argument)[0][1]

# Keeping the argument in memory for later use
self._negotiations.add_argument(expeditor, engine, argument)

# Trying to get a counter argument
counter_argument = self.try_get_counter_argument(argument)

# Keeping argument for later use
self._negotiations.add_argument(expeditor, engine, counter_argument)

# Sending counter argument
self.send_message(Message(
    self.get_name(),
    expeditor,
    MessagePerformative.ARGUE,
    counter_argument
))

