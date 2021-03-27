from mesa import Model
from mesa.time import RandomActivation

from agent.CommunicatingAgent import CommunicatingAgent
from message.MessageService import MessageService
from message.Message import Message
from message.MessagePerformative import MessagePerformative

from preferences.Preferences import Preferences
from preferences.CriterionName import CriterionName
from preferences.CriterionValue import CriterionValue
from preferences.Item import Item
from preferences.Value import Value

from dialog.EnginesDialog import EnginesDialog

from typing import List
import random


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent.
    """

    def __init__(self, unique_id, model, name, engine_models: List[Item]):
        super().__init__(unique_id, model, name)
        self.preference = self.generate_preferences(engine_models, CriterionName.to_list())
        self._dialog = EnginesDialog(engine_models)
        self.announce_existence_to_the_world = False

    def step(self):
        super().step()

        # Checking if the agent received a message

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


class AliceAgent(ArgumentAgent):
    def __init__(self, unique_id, model, engine_models: List[Item]):
        super().__init__(unique_id, model, "Alice", engine_models)

    def step(self):
        # Alice first checks if she already discuses with Bob
        if self._dialog.is_not_an_interlocutor("Bob"):
            self._dialog.add_interlocutor("Bob")

        # Alice checks if she has received new messages
        messages = self.get_new_messages()

        if len(messages) > 0:
            # We iterate through the messages
            for message in messages:
                # We have to check that the only message she has received is from Bob
                if message.get_exp() == "Bob":
                    # She will now determine the current step of the protocol she has established with Bob
                    performative = message.get_performative()

                    if performative == MessagePerformative.ACCEPT:
                        # We get the engine Alice has been talking about with Bob
                        engine = message.get_content()

                        # She will notify Bob with a commit message
                        self.send_message(Message(
                            self.get_name(),
                            message.get_exp(),
                            MessagePerformative.COMMIT,
                            engine
                        ))

                        # She can now update her believe base (discussion items)
                        self._dialog.get_dialog_with_agent(message.get_exp()).delete_topic(engine)
                    elif performative == MessagePerformative.ASK_WHY:
                        # She should begin to argue
                        pass

        else:
            # Alice sends a message to Bob to propose an engine that has not been discussed yet
            engine = self._dialog.get_dialog_with_agent("Bob").get_random_topic()

            if engine is not None:
                self.send_message(
                    Message(
                        self.get_name(),
                        "Bob",
                        MessagePerformative.PROPOSE,
                        engine
                    )
                )


class BobAgent(ArgumentAgent):
    def __init__(self, unique_id, model, engine_models: List[Item]):
        super().__init__(unique_id, model, "Bob", engine_models)

    def step(self):
        # Bob checks if he has received new messages
        messages = self.get_new_messages()

        if len(messages) > 0:
            # We iterate through the messages
            for message in messages:
                # Bob first checks the expeditor of the message to determine if it's an interlocutor with which he has
                # discussed
                interlocutor = message.get_exp()

                if self._dialog.is_not_an_interlocutor(interlocutor):
                    self._dialog.add_interlocutor(interlocutor)

                # Then he checks if it's Alice:
                if interlocutor == "Alice":
                    # If it's the case, he should determine what he has to do
                    performative = message.get_performative()

                    if performative == MessagePerformative.PROPOSE:
                        # Bob is about to check if the engine proposed by Alice is one of his preferred ones
                        engine = message.get_content()

                        if self.preference.is_item_among_top_10_percent(engine, self._dialog.get_engines()):
                            self.send_message(Message(
                                self.get_name(),
                                message.get_exp(),
                                MessagePerformative.ACCEPT,
                                engine
                            ))
                        else:
                            # Otherwise he will ask Alice to justify her choice
                            self.send_message(Message(
                                self.get_name(),
                                message.get_exp(),
                                MessagePerformative.ASK_WHY,
                                engine
                            ))
                    elif performative == MessagePerformative.COMMIT:
                        engine = message.get_content()

                        # Bob notifies Alice that he will update his topics of discussion with her
                        self.send_message(Message(
                            self.get_name(),
                            message.get_exp(),
                            MessagePerformative.COMMIT,
                            engine
                        ))

                        # Bob can update his topics of discussion with Alice
                        self._dialog.get_dialog_with_agent(message.get_exp()).delete_topic(engine)


class ArgumentModel(Model):
    """
    ArgumentModel which inherit from Model.
    """

    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.running = True

    def add_agent(self, agent: ArgumentAgent):
        self.schedule.add(agent)

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
    alice = AliceAgent(1, argument_model, engines)
    bob = BobAgent(2, argument_model, engines)

    # Adding our agents to our model
    argument_model.add_agent(alice)
    argument_model.add_agent(bob)

    # Running
    argument_model.run_n_step(10)
