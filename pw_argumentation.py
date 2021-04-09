from mesa import Model
from mesa.time import RandomActivation
from typing import List, Tuple, Union

from agent.CommunicatingAgent import CommunicatingAgent
from message.MessageService import MessageService
from message.Message import Message
from message.MessagePerformative import MessagePerformative

from preferences.Preferences import Preferences
from preferences.CriterionName import CriterionName
from preferences.CriterionValue import CriterionValue
from preferences.Item import Item
from preferences.Value import Value

from arguments.Argument import Argument
from arguments.CoupleValue import CoupleValue
from arguments.Comparison import Comparison

from negociation.Negotiation import Negotiation

from role.Role import Role
from role.DirectoryFaciliator import DirectoryFacilitator

import random


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent.
    """

    def __init__(self, unique_id, model: 'ArgumentModel', name, engine_models: List[Item]):
        super().__init__(unique_id, model, name)
        self._engines = engine_models
        self.preference = self.generate_preferences(engine_models, CriterionName.to_list())
        self.announce_existence_to_the_world = False
        self._df = model.get_directory_facilitator()
        self._negotiations = model.get_negotiations()

    def get_preference(self):
        return self.preference

    def generate_preferences(self, engine_models: List[Item], criteria: List[CriterionName]) -> Preferences:
        # Creating the preference instance
        preference = Preferences()

        # Shuffling criteria preferences
        random.shuffle(criteria)

        # Setting the order of preferences for this agent
        preference.set_criterion_name_list(criteria)

        # Attributing a value for each characteristic of each engine model
        for engine_model in engine_models:
            for criterion in criteria:
                preference.add_criterion_value(CriterionValue(
                    engine_model,
                    criterion,
                    random.choice(Value.to_list())
                ))

        return preference

    def support_proposal(self, item) -> Tuple:
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        return self.list_supporting_proposal(item)[0]

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

    def try_get_counter_argument(self, argument: Argument, interlocutor_id: str) -> Union[Argument, None]:
        def criterion_argument(premiss: CoupleValue, engine: Item, interlocutor_id: str) -> Union[Argument, None]:
            bad_values = self.list_attacking_proposal(engine)
            base_criterion = premiss.get_criterion_name()

            # We iterate through our possible counter arguments to find if we could use one of them
            for criterion_name, criterion_val in bad_values:

                if self.preference.is_preferred_criterion(criterion_name, base_criterion) and base_criterion != criterion_name:
                    argument = Argument(False, engine)
                    # One has to remember that list_attacking_proposal and list_proposal both return a tuple of
                    # the form (preference, value)
                    argument.add_premiss_couple_values(criterion_name, criterion_val)
                    argument.add_premiss_comparison(criterion_name, premiss.get_criterion_name())

                    if not self._negotiations.is_argument_already_used(self.get_name(), interlocutor_id, argument):
                        return argument
            return None

        def better_criterion_value(premiss: CoupleValue, interlocutor_id:str) -> Union[Argument, None]:
            preferred_engine = self.preference.most_preferred(self._engines)
            value_for_criterion = self.preference.get_criterion_value_for_item(preferred_engine)[
                premiss.get_criterion_name()]

            if value_for_criterion > premiss.get_value():
                argument = Argument(True, preferred_engine)
                argument.add_premiss_couple_values(premiss.get_criterion_name(), value_for_criterion)
                argument.add_premiss_comparison(value_for_criterion, premiss.get_value())

                if not self._negotiations.is_argument_already_used(self.get_name(), interlocutor_id, argument):
                    return argument

            return None

        def worst_criterion_value(engine: Item, premiss: CoupleValue, interlocutor_id:str) -> Union[Argument, None]:
            preferred_engine = self.preference.most_preferred(self._engines)
            value_for_criterion = self.preference.get_criterion_value_for_item(preferred_engine)[
                premiss.get_criterion_name()]

            if value_for_criterion < premiss.get_value():
                argument = Argument(False, engine)
                argument.add_premiss_couple_values(premiss.get_criterion_name(), value_for_criterion)
                argument.add_premiss_comparison(premiss.get_value(), value_for_criterion)

                if not self._negotiations.is_argument_already_used(self.get_name(), interlocutor_id, argument):
                    return argument

            return None

        conclusion, premisses = Argument.argument_parsing(argument)

        # Getting engine mentioned in the argument
        engine = conclusion[1]

        # Checking if the argument was in favor of a specific engine or not
        if conclusion[0]:
            if len(premisses) == 2:
                premiss: CoupleValue = premisses[0]

                # We try to find a criterion that has a higher rank in our table of preferences and prove that the value
                # is not great
                counter_argument = criterion_argument(premiss, engine, interlocutor_id)
                if counter_argument:
                    return counter_argument

                # Otherwise we could counter this argument by mentioning that for us this engine is not great for this
                # criterion
                counter_argument = worst_criterion_value(engine, premiss, interlocutor_id)
                if counter_argument:
                    return counter_argument

                # Otherwise we could propose our preferred engine because the value for this criterion is better
                counter_argument = better_criterion_value(premiss, interlocutor_id)
                if counter_argument:
                    return counter_argument

            else:
                premiss: CoupleValue = premisses[0]

                # We try to find a criterion that has a higher rank in our table of preferences and prove that the value
                # is not great
                counter_argument = criterion_argument(premiss, engine, interlocutor_id)
                if counter_argument:
                    return counter_argument

                # Otherwise we could counter an argument mentioning that for the same criterion our engine has a better
                # value
                counter_argument = better_criterion_value(premiss, interlocutor_id)
                if counter_argument:
                    return counter_argument
        else:
            # First we need to get the comparison used by the other agent
            comparison: Comparison = premisses[1]

            # Getting proposals that we could use to defend our engine
            proposals = self.list_supporting_proposal(engine)

            # Then we need to check if the comparison is based on criterion
            if type(comparison.get_best_criterion_name()) == CriterionName:
                # Now we will iterate through the proposals to find one that we could be used to counter the argument
                # used the other agent
                base_criterion = comparison.get_best_criterion_name()

                # We iterate through our possible counter arguments to find if we could use one of them
                for criterion_name, criterion_val in proposals:
                    # We check if the criterion that the criterion mentioned by the other agent
                    if self.preference.is_preferred_criterion(criterion_name, base_criterion) and criterion_name != base_criterion:
                        argument = Argument(True, engine)
                        # One has to remember that list_attacking_proposal and list_proposal both return a tuple of
                        # the form (preference, value)
                        argument.add_premiss_couple_values(criterion_name, criterion_val)
                        argument.add_premiss_comparison(criterion_name, base_criterion)

                        return argument

            # Otherwise we will try to find a criterion that has not been used yet
            for criterion_name, criterion_val in proposals:
                argument = Argument(True, engine)
                argument.add_premiss_couple_values(criterion_name, criterion_val)

                # We check if the argument has been used in the negotiation
                if not self._negotiations.is_argument_already_used(self.get_name(), interlocutor_id, argument):
                    return argument

        return None

    def step(self):
        # Get a list of interlocutors with which the agent can talk about engines
        engines_interlocutors = self._df.get_agents_with_specific_role(self.get_name(), Role.EnginesTalker)

        # We then iterate through the messages
        new_messages = self.get_new_messages()

        for message in new_messages:
            # We retrieve the expeditor
            expeditor = message.get_exp()

            # We now check the performative of the message and answer
            performative = message.get_performative()

            if performative == MessagePerformative.PROPOSE:
                # We get the engine proposed by an agent
                engine = message.get_content()

                # We check if the engine proposed is one of our preferred ones
                if self.preference.is_item_among_top_10_percent(engine, self._engines):
                    # We then need to check if the engine is our preferred one
                    most_preferred_engine = self.preference.most_preferred(self._engines)

                    if most_preferred_engine.get_name() == engine.get_name():
                        self.send_message(Message(
                            self.get_name(),
                            expeditor,
                            MessagePerformative.ACCEPT,
                            engine
                        ))
                    else:
                        self.send_message(Message(
                            self.get_name(),
                            expeditor,
                            MessagePerformative.PROPOSE,
                            most_preferred_engine
                        ))
                else:
                    # Otherwise the agent will ask why the other agent proposed this engine
                    self.send_message(Message(
                        self.get_name(),
                        expeditor,
                        MessagePerformative.ASK_WHY,
                        engine
                    ))
            elif performative == MessagePerformative.ASK_WHY:
                # We get the engine proposed by an agent
                engine = message.get_content()

                # We send a message with commit performative
                argument = Argument(True, engine)
                argument.add_premiss_couple_values(*self.support_proposal(engine))

                # Keeping argument in memory
                self._negotiations.add_argument(self.get_name(), expeditor, argument)

                self.send_message(Message(
                    self.get_name(),
                    expeditor,
                    MessagePerformative.ARGUE,
                    argument
                ))
            elif performative == MessagePerformative.ARGUE:
                # Getting the argument used by the other agent.
                argument: Argument = message.get_content()

                # Trying to get a counter argument
                counter_argument = self.try_get_counter_argument(argument, expeditor)

                if not counter_argument:
                    # If the conclusion of the argument is in favor of a specific engine we have to accept it
                    if Argument.argument_parsing(argument)[0][0]:
                        self.send_message(Message(
                            self.get_name(),
                            expeditor,
                            MessagePerformative.ACCEPT,
                            Argument.argument_parsing(argument)[0][1]
                        ))
                    # We cannot argue anymore
                    return

                # Adding counter argument in our list of arguments used for negotiation
                self._negotiations.add_argument(self.get_name(), expeditor, counter_argument)

                # Sending counter argument
                self.send_message(Message(
                    self.get_name(),
                    expeditor,
                    MessagePerformative.ARGUE,
                    counter_argument
                ))
            elif performative == MessagePerformative.ACCEPT:
                # We get the engine proposed by an agent
                engine = message.get_content()

                # We save in memory the engine that has been accepted by the two agents
                self._negotiations.set_accepted_engine(self.get_name(), expeditor, engine)

                # We send a message with commit performative
                self.send_message(Message(
                    self.get_name(),
                    expeditor,
                    MessagePerformative.COMMIT,
                    engine
                ))
            elif performative == MessagePerformative.COMMIT:
                # We get the engine that we are talking about
                engine = message.get_content()

                # The agent indicates that he/she is ok to end the negotiation
                self._negotiations.accept_ending_negotiation(self.get_name(), expeditor)

                # We have to check if the other agent has agreed to end the negotiation too
                if not self._negotiations.is_negotiation_ended(self.get_name(), expeditor):
                    self.send_message(Message(
                        self.get_name(),
                        expeditor,
                        MessagePerformative.COMMIT,
                        engine
                    ))

        # We now iterate through the list of interlocutors for which we have not received a message
        for interlocutor in engines_interlocutors:
            # We check if a _negotiation has already started between the two agents
            if not self._negotiations.has_started_negotiation(self.get_name(), interlocutor):
                # If it's not the case, we initiate a negotiation between the two agents
                self._negotiations.start_negotiation(self.get_name(), interlocutor)

                # The current agent will propose his/her best engine based on his/her preferences
                self.send_message(Message(
                    self.get_name(),
                    interlocutor,
                    MessagePerformative.PROPOSE,
                    self.preference.most_preferred(self._engines)
                ))


class ArgumentModel(Model):
    """
    ArgumentModel which inherit from Model.
    """

    def __init__(self, agents_name: List[str]):
        super().__init__()
        self._negotiations = Negotiation(agents_name)
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self._df = DirectoryFacilitator()
        self._df.add_role(Role.EnginesTalker)
        self.running = True

        for index, agent_name in enumerate(agents_name):
            agent = ArgumentAgent(index, self, agent_name, engines)
            self.schedule.add(agent)
            self._df.attach_a_role_to_agent(Role.EnginesTalker, agent.get_name())

    def get_directory_facilitator(self):
        return self._df

    def get_negotiations(self):
        return self._negotiations

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def run_n_step(self, number_of_steps: int):
        for i in range(number_of_steps):
            self.__messages_service.dispatch_messages()
            self.schedule.step()


if __name__ == "__main__":
    # Creating a list that will contain the different engines used
    engines = [
        Item("Electric Engine", "An engine that works with electricity"),
        Item("Diesel Engine", "An engine that works with fuel"),
        Item("Hydrogen Engine", "An engine that works with hydrogen"),
        Item("Nuclear Engine", "To be used with caution")
    ]

    # Creating our agents
    agents_name = [
        "Alice",
        "Bob"
    ]

    # Creating our model
    argument_model = ArgumentModel(agents_name)

    # Running
    argument_model.run_n_step(10)
