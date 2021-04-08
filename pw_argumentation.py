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

from role.Role import Role
from role.DirectoryFaciliator import DirectoryFacilitator

from negociation.EnginesNegotiation import EnginesNegotiation

import random


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent.
    """

    def __init__(self, unique_id, model: 'ArgumentModel', name, engine_models: List[Item]):
        super().__init__(unique_id, model, name)
        self.preference = self.generate_preferences(engine_models, CriterionName.to_list())
        self._negotiations = EnginesNegotiation(engine_models)
        self.announce_existence_to_the_world = False
        self._df = model.get_directory_facilitator()

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

    def step(self):
        # Get a list of interlocutors with which the agent can talk about engines
        engines_interlocutors = self._df.get_agents_with_specific_role(self.get_name(), Role.EnginesTalker)

        # We iterate through the interlocutors
        for interlocutor in engines_interlocutors:
            # We check if we have already discussed with this interlocutor before
            if self._negotiations.is_not_an_interlocutor(interlocutor):
                self._negotiations.add_interlocutor(interlocutor)

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
                if self.preference.is_item_among_top_10_percent(engine, self._negotiations.get_engines()):
                    # We then need to check if the engine is our preferred one
                    most_preferred_engine = self.preference.most_preferred(self._negotiations.get_engines())

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

        # We now iterate through the list of interlocutors we have not received a message
        for interlocutor in engines_interlocutors:
            # We check if we should send a PROPOSE message by checking the latest message receive from this agent
            messages = self.get_messages_from_exp(interlocutor)

            if len(messages) == 0 or messages[0].get_performative() == MessagePerformative.COMMIT:
                # We now check if we can talk about an engine that has not been discussed before
                engine = self._negotiations.get_random_negotiation_topic(interlocutor)

                if engine is not None:
                    self.send_message(Message(
                        self.get_name(),
                        interlocutor,
                        MessagePerformative.PROPOSE,
                        engine
                    ))


class ArgumentModel(Model):
    """
    ArgumentModel which inherit from Model.
    """

    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self._df = DirectoryFacilitator()
        self._df.add_role(Role.EnginesTalker)
        self.running = True

    def get_directory_facilitator(self):
        return self._df

    def add_agent(self, agent: ArgumentAgent):
        self.schedule.add(agent)
        self._df.attach_a_role_to_agent(Role.EnginesTalker, agent.get_name())

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
        Item("Hydrogen Engine", "An engine that works with hydrogen")
    ]

    # Creating our model
    argument_model = ArgumentModel()

    # Creating our agents
    alice = ArgumentAgent(1, argument_model, "Alice", engines)
    bob = ArgumentAgent(2, argument_model, "Bob", engines)

    # Adding our agents to our model
    argument_model.add_agent(alice)
    argument_model.add_agent(bob)

    # Running
    argument_model.run_n_step(6)
