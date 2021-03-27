from typing import List, Set, Union, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from preferences import Item


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
