def list_supporting_proposal(self, item) -> List[Tuple]:
    """
    Generate a list of premisses which can be used to support an item
    :param item: Item - name of the item
    :return: list of all premisses PRO an item (sorted by order of importance based on agent's preferences)
    """
    result = []
    feelings_about_engine = self.preference.get_criterion_value_for_item(item)
    preferences = self.preference.get_criterion_name_list()

    for preference in preferences:
        criterion_value = feelings_about_engine[preference]

        if criterion_value == Value.VERY_GOOD or criterion_value == Value.GOOD:
            result.append((preference, criterion_value))

    return result


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


def support_proposal(self, item) -> Tuple:
    """
    Used when the agent recieves "ASK_WHY" after having proposed an item
    :param item: str - name of the item which was proposed
    :return: string - the strongest supportive argument
    """
    return self.list_supporting_proposal(item)[0]

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
elif performative == MessagePerformative.ASK_WHY:
# We get the engine proposed by an agent
engine = message.get_content()

# We send a message with commit performative
argument = Argument(True, engine)
argument.add_premiss_couple_values(*self.support_proposal(engine))

# Keeping argument in memory
self._negotiations.add_argument(expeditor, engine, argument)

self.send_message(Message(
    self.get_name(),
    expeditor,
    MessagePerformative.ARGUE,
    argument
))
elif performative == MessagePerformative.ACCEPT:
# We get the engine proposed by an agent
engine = message.get_content()

# We send a message with commit performative
self.send_message(Message(
    self.get_name(),
    expeditor,
    MessagePerformative.COMMIT,
    engine
))
elif performative == MessagePerformative.COMMIT:
# We get the engine proposed by an agent
engine = message.get_content()

# The agent can now delete the engine from his/her list of engines that have not been negotiated with
# the other agent
# self._negotiations.delete_negotiation_with_interlocutor(expeditor, engine) TODO GERER CE POINT

# We can now remove the interlocutor from our list of interlocutors since we have spoken with him/her
engines_interlocutors.remove(expeditor)