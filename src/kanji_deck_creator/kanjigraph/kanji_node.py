import re
from typing import Set, Any

from kanji_deck_creator.kanjigraph.kanji_type import KanjiType


class KanjiNode(object):
    # The character(s) represented by this node. Can be an integer (as a string) in which case it refers to
    # the subject id, because there is not character representation.
    value: str
    type: KanjiType
    dependencies: Set[Any]  # Set[KanjiNode]
    contained_in: Set[Any]  # Set[KanjiNode]
    total_num_dependencies: int
    count: int

    def __init__(self, value, node_type):
        """
        :type value: str
        :type node_type: KanjiType
        :type kanji_data: KanjiData
        """
        assert value is not None, '({}, {}) is an invalid node'.format(value, node_type)

        self.value = value
        self.type = node_type
        self.dependencies = set()
        self.contained_in = set()
        self.total_num_dependencies = 0
        self.count = 1

    def is_encoded(self):
        return re.match(r'[A-Za-z0-9]+[A-Za-z0-9\-]+', self.value) is not None

    def __eq__(self, other):
        return type(other) is KanjiNode and self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((self.value, self.type))

    def __str__(self):
        return '{value}: numd: {numd} d:{dependencies} c:{contained_in} p:{node_type}'.format(
            numd=self.total_num_dependencies,
            value=self.value, dependencies=[i.value for i in self.dependencies],
            contained_in=[i.value for i in self.contained_in], node_type=self.type)
