from typing import List, Set, Union, TYPE_CHECKING
import random
from preferences.Item import Item


class DialogTopics:
    def __init__(self, topics: List['Item']):
        self._topics = self.__initialize(topics)

    def __initialize(self, topics: List) -> Set['Item']:
        """
        Permits to fill _topics
        """
        topics_ = set()

        for topic in topics:
            topics_.add(topic)

        return topics_

    def get_random_topic(self) -> Union[None, 'Item']:
        """
        Return a topic that has been chosen randomly
        """
        topics_ = list(self._topics)

        if len(topics_) == 0:
            return None

        return random.choice(topics_)

    def delete_topic(self, topic: 'Item'):
        """
        Delete a topic that has been discussed
        """
        self._topics.remove(topic)


if __name__ == '__main__':
    plane = Item("Plane", "Plane")
    car = Item("Car", "Car")
    topics = DialogTopics([plane, car])

    topic = topics.get_random_topic()

    assert topic is not None
    assert type(topic) == Item
    print("[INFO] Checking choosing random topic... OK")

    topics.delete_topic(car)
    topics.delete_topic(plane)

    topic = topics.get_random_topic()

    assert topic is None
    print("[INFO] Checking delete function... OK")