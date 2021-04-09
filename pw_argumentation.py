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

            # # We check if we should send a PROPOSE message by checking the latest message receive from this agent
            # messages = self.get_messages_from_exp(interlocutor)
            #
            # if len(messages) == 0 or messages[0].get_performative() == MessagePerformative.COMMIT:
            #     # We now check if we can talk about an engine that has not been discussed before
            #     engine = self._negotiations.get_random_negotiation_topic(interlocutor)
            #
            #     if engine is not None:
            #         self.send_message(Message(
            #             self.get_name(),
            #             interlocutor,
            #             MessagePerformative.PROPOSE,
            #             engine
            #         ))


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
        Item("Hydrogen Engine", "An engine that works with hydrogen")
    ]

    # Creating our agents
    agents_name = [
        "Alice",
        "Bob"
    ]

    # Creating our model
    argument_model = ArgumentModel(agents_name)

    # Running
    argument_model.run_n_step(2)
