import logging
from typing import Set, Dict, Tuple, Iterable, List

from kanji_deck_creator.unicode.util import is_hiragana, is_katakana
from kanji_deck_creator.data.kanji_data import WaniKaniSubject
from kanji_deck_creator.kanjigraph.kanji_node import KanjiNode
from kanji_deck_creator.data.kanji_data import KanjiData
from kanji_deck_creator.kanjigraph.kanji_type import KanjiType


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class KanjiGraph:
    primitives: Set[KanjiNode]
    kanji: Set[KanjiNode]
    nodes: Dict[Tuple[str, KanjiType], KanjiNode]
    vocabs: Set[KanjiNode]
    kanji_data = KanjiData

    def __init__(self, kanji_data):
        """
        :type kanji_data: KanjiData
        """
        # keys in this dict are tuples of (character (str), KanjiType)
        self.kanji_data = kanji_data
        self.nodes = {}
        self.primitives = set()
        self.vocabs = set()
        self.kanji = set()

    def _add_subject_components(self, subject, node):
        for component in subject.components:
            text = component.characters
            # In the case of radicals/primitives (which do not have a representation in unicode), pass in their id
            # as the value.
            if not text:
                text = str(component.subject_id)
            dependency_node = self._add(text, component.subject_type)
            dependency_node.contained_in.add(node)
            node.dependencies.add(dependency_node)

        return node

    def _update_total_num_dependencies(self, node):
        """
        Counts all the dependencies this node has and stores it in self.total_num_dependencies.
        Will also update the counts of all of its dependencies.
        :type node: KanjiNode
        """
        total = 0
        for dependency in node.dependencies:
            if (dependency.value, dependency.type) not in self.nodes or node == dependency:
                continue
            self._update_total_num_dependencies(dependency)
            total += dependency.total_num_dependencies + 1
        node.total_num_dependencies = total

    def _add_vocab_connections(self, node) -> KanjiNode:
        """
        :type node: KanjiNode
        """
        subject = self.kanji_data.get_subject(node.value, node.type)
        if type(subject) is not WaniKaniSubject:
            for character in node.value:
                if is_hiragana(character) or is_katakana(character):
                    # Skip non-kanji characters (assuming input is all japanese)
                    continue
                dependency_node = self._add(character, KanjiType.KANJI)
                dependency_node.contained_in.add(node)
                node.dependencies.add(dependency_node)
            return node
        else:
            return self._add_subject_components(subject, node)

    def _add_kanji_connections(self, node):
        """
        :type node: KanjiNode
        """
        # TODO handle case where the kanji is not found in database
        subject = self.kanji_data.get_subject(node.value, node.type)
        if not subject:
            log.warning("[{}] as a {} not found in kanji dataset".format(node.value, node.type))
            return node
        return self._add_subject_components(subject, node)

    def add_compound_word(self, component_words):
        """
        Adds the compound word made up of component words. So if you want to add
        '形態素解析器' you would pass in [形態素, '解析', '器'].

        :type component_words: Iterable[str]
        :param component_words: list of words that make up the compound word.
        :return: The added node, or None if it was not added because the word is invalid.
        """
        assert type(component_words) is not str, 'component_words should be an Iterable of strings, not a string'

        if any(self._has_no_kanji(word) for word in component_words):
            return None

        # [A, B, C] -> ABC
        compound_word = ''.join(component_words)

        # Check for existing node
        if (compound_word, KanjiType.VOCABULARY) in self.nodes:
            self.nodes[compound_word, KanjiType.VOCABULARY].count += 1
            return self.nodes[compound_word, KanjiType.VOCABULARY]

        # Create and register node in graph
        compound_node = KanjiNode(compound_word, KanjiType.VOCABULARY)
        self.nodes[compound_word, KanjiType.VOCABULARY] = compound_node
        self.vocabs.add(compound_node)

        for component_word in component_words:
            # Create/Register/Get component
            component_node = self._add(component_word, KanjiType.VOCABULARY)

            # Set up connections between compound node and its components.
            compound_node.dependencies.add(component_node)
            component_node.contained_in.add(compound_node)

        return compound_node

    def _add(self, word, word_type) -> KanjiNode:
        """
        :param word: string to add
        :param word_type: the type of the word, defaults to vocab

        :type word: str
        :type word_type: KanjiType
        :return: the added node
        """
        if (word, word_type) in self.nodes:
            self.nodes[word, word_type].count += 1
            return self.nodes[word, word_type]

        node = KanjiNode(word, word_type)
        self.nodes[word, word_type] = node

        if word_type == KanjiType.KANJI:
            node = self._add_kanji_connections(node)
            self.kanji.add(node)
        elif word_type == KanjiType.VOCABULARY:
            node = self._add_vocab_connections(node)
            self.vocabs.add(node)
        elif word_type == KanjiType.PRIMITIVE:
            # Don't need to do anything extra if its a primitive, the things its contained in will add it.
            self.primitives.add(node)

        return node

    def _has_no_kanji(self, word):
        return all(is_katakana(i) or is_hiragana(i) for i in word)

    def add(self, word):
        """"
        Return the added node or None if the word is not kanji
        """
        # The kanji graph is just for kanji stuff.
        if self._has_no_kanji(word):
            return None

        return self._add(word, KanjiType.VOCABULARY)

    def sort_by_complexity(self, nodes: Iterable[KanjiNode]) -> List[KanjiNode]:
        """
        Returns vocab words by order of dependencies, ascending
        """
        class ComplexitySortableNode(object):
            kanji_node: KanjiNode

            def __init__(self, kanji_node):
                self.kanji_node = kanji_node

            def __lt__(self, other):
                if self.kanji_node.total_num_dependencies != other.kanji_node.total_num_dependencies:
                    return self.kanji_node.total_num_dependencies < other.kanji_node.total_num_dependencies
                else:
                    return self.kanji_node.value < other.kanji_node.value

        for node in nodes:
            self._update_total_num_dependencies(node)
        sortable_node_list = list(ComplexitySortableNode(node) for node in nodes)
        sortable_node_list.sort()
        return [i.kanji_node for i in sortable_node_list]

    # noinspection PyMethodMayBeStatic
    def sort_by_frequency(self, nodes: Iterable[KanjiNode]) -> List[KanjiNode]:
        """
        Returns vocab words by order of frequency, descending
        """
        node_list = list(nodes)
        node_list.sort(key=lambda i: i.count, reverse=True)
        return node_list

    def __repr__(self):
        return '\n'.join(str(node) for node in self.nodes.values())
