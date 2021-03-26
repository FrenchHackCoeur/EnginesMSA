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

from typing import List
import random


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent.
    """

    def __init__(self, unique_id, model, name, engine_models: List[Item]):
        super().__init__(unique_id, model, name)
        self.preference = self.generate_preferences(engine_models, CriterionName.to_list())

    def step(self):
        super().step()

        # Checking if the agent received a message

    def get_preference(self):
        return self.preference

    def generate_preferences(self, engine_models: List[Item], criteria: List[CriterionName]) -> Preferences:
        # Creating the preference instance
        preference = Preferences()

        # Setting items used
        preference.add_items(engine_models)

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
        # Alice checks if she has received new messages
        messages = self.get_new_messages()

        print("TEST MESSAGE")
        print(messages)

        if len(messages) > 0:
            # We iterate through the messages
            for message in messages:
                # We have to check that the only message she has received is from Bob
                if message.get_exp() == "Bob" and message.get_performative() == MessagePerformative.ACCEPT:
                    item = message.get_content()
        else:
            # Alice sends a message to Bob so as to propose a random item
            self.send_message(Message(self.get_name(), "Bob", MessagePerformative.PROPOSE, self.preference.choose_item_randomly()))


class BobAgent(ArgumentAgent):
    def __init__(self, unique_id, model, engine_models: List[Item]):
        super().__init__(unique_id, model, "Bob", engine_models)

    def step(self):
        # Bob checks if he has received new messages
        messages = self.get_new_messages()

        print("TESTT BOB")

        if len(messages) > 0:
            # We iterate through the messages
            for message in messages:
                # We have to check that the only message he has received is from Alice
                if message.get_exp() == "Alice" and message.get_performative() == MessagePerformative.PROPOSE:
                    item = message.get_content()

                    # Bob checks that the item that has been sent by Alice is one of his preferred ones (10%)
                    if self.preference.is_item_among_top_10_percent(item, self.preference.get_items()):
                        # Bob accepts the proposed item
                        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, item))
                    else:
                        # Otherwise he will ask Alice why she proposed this item to him
                        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ASK_WHY, item))



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
    argument_model.run_n_step(4)



