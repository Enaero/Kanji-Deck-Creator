import genanki
import html
from os import path

from kanji_deck_creator.data.kanji_data import KANJI_DATA, Subject, WaniKaniSubject, JishoSubject
from kanji_deck_creator.kanjigraph.kanji_graph import KanjiGraph
from kanji_deck_creator.kanjigraph.kanji_node import KanjiNode
from kanji_deck_creator.parser.tokenizer import Tokenizer


KANJI_DECK_CREATOR_MODEL = genanki.Model(
  1426979736,  # randomly generated
  'Kanji Deck Creator Model',
  fields=[
    {'name': 'JapaneseText'},
    {'name': 'Information'},
  ],
  templates=[
    {
      'name': 'Kanji Deck Creator Card',
      'qfmt': '<h1><center>{{JapaneseText}}</center></h1>',
      'afmt': '{{FrontSide}}<hr id="answer"><body>{{Information}}</body>',
    },
  ])


class AnkiPackageBuilder(object):
    tokenizer: Tokenizer

    def __init__(self, tokenizer: Tokenizer, kanji_graph: KanjiGraph):
        self.tokenizer = tokenizer
        self.kanji_graph = kanji_graph

    def build(self, source_text, name, mode='riffled') -> genanki.Package:
        """
        Builds the anki deck in the chosen mode
        """
        if not mode or mode not in ('riffled', 'layered'):
            raise ValueError('mode must be one of riffled or layered')

        tokens = self.tokenizer.tokenize(source_text)
        for token in tokens:
            self.kanji_graph.add(token)

        deck = genanki.Deck(deck_id=hash(name), name=name)
        package = genanki.Package(deck)

        if mode.strip().lower() == 'riffled':
            vocabs = self.kanji_graph.sort_by_complexity(self.kanji_graph.vocabs)
            vocabs_with_dependencies = []
            vocabs_with_dependencies_set = set()
            for node in vocabs:
                self._get_riffled_nodes(node, result=vocabs_with_dependencies, seen_nodes=vocabs_with_dependencies_set)

            self._build_deck(package, deck, vocabs_with_dependencies)

        else:
            nodes = self._get_layered_nodes()
            self._build_deck(package, deck, nodes)

        return package

    def _get_dependencies_as_list(self, node: KanjiNode):
        nodes = []
        for dependency in node.dependencies:
            nodes.append(dependency)
            nodes += self._get_dependencies_as_list(dependency)
        return nodes

    def _get_riffled_nodes(self, node, result, seen_nodes):
        if node in seen_nodes:
            return
        seen_nodes.add(node)

        sorted_dependencies = self.kanji_graph.sort_by_complexity(node.dependencies)
        for dependency in sorted_dependencies:
            self._get_riffled_nodes(dependency, result, seen_nodes)

        result.append(node)

    def _get_layered_nodes(self):
        return self.kanji_graph.sort_by_complexity(self.kanji_graph.nodes.values())

    def _build_deck(self, package: genanki.Package, deck: genanki.Deck, nodes):
        """
        Builds the anki deck ordering all nodes by complexity, resultsing in a layered stack:
        radicals notes, then kanji notes, then vocab notes.
        """
        subjects = [KANJI_DATA.get_subject(node.value, node.type) for node in nodes]

        for subject in subjects:
            # subjects can be None if they are not found in the dataset.
            # TODO: Use jisho in those cases, but that can still return None if jisho can't find anything either.
            if not subject:
                continue

            if subject.image_path:
                package.media_files.append(subject.image_path)

            front = self._get_front(subject)
            back = self._get_back(subject)
            guid = genanki.guid_for(subject.characters or subject.subject_id, subject.subject_type)
            note = genanki.Note(
                model=KANJI_DECK_CREATOR_MODEL,
                fields=[front, back],
                tags=['kanji_deck_creator'],
                guid=guid
            )
            deck.add_note(note)

    @staticmethod
    def _get_character_visual(subject):
        if subject.characters:
            return str(html.escape(subject.characters))
        else:
            # Because we are exporting images in the package, the notes must reference them by basename only
            # Using the filepath will not work.
            basename = path.basename(subject.image_path)
            return '<img src="{}" alt="{}" height="32">'.format(basename, basename)

    @classmethod
    def _get_front(cls, subject: Subject):
        """
        :type node: KanjiNode
        :return: html of the word + primitive or not
        """
        character_visual = cls._get_character_visual(subject)
        return character_visual + '<br>' + str(subject.subject_type.value)

    @staticmethod
    def _wanikani_parse(text: str):
        """
        WaniKani will have things like <radical>ground</radical> which look ugly in Anki.
        Let's just get rid of those.
        :param text:
        :return: cleaned up text
        """
        if not text:
            return ''
        text = html.escape(text)
        return text.replace('&lt;radical&gt;', '<b>')\
            .replace('&lt;/radical&gt;', '</b>')\
            .replace('&lt;kanji&gt;', '<b>')\
            .replace('&lt;/kanji&gt;', '</b>')\
            .replace('&lt;vocabulary&gt;', '<b>')\
            .replace('&lt;/vocabulary&gt;', '</b>')\
            .replace('&lt;reading&gt;', '<b>')\
            .replace('&lt;/reading&gt;', '</b>')\
            .replace('&lt;ja&gt;', '<b>')\
            .replace('&lt;/ja&gt;', '</b>')

    @classmethod
    def _get_back(cls, subject: Subject):
        meaning_mnemonic = AnkiPackageBuilder._wanikani_parse(subject.meaning_mnemonic)
        reading_mnemonic = AnkiPackageBuilder._wanikani_parse(subject.reading_mnemonic)

        section = '<font color="blue"><b>{}: </b></font>'

        lines = [
            section.format('meaning') + html.escape(str(subject.meaning)),
            section.format('reading') + html.escape(str(subject.reading)),
            section.format('components') + ', '.join(cls._get_character_visual(i) for i in subject.components),
            section.format('parts of speech') + html.escape(subject.parts_of_speech),
            section.format('meaning mnemonic') + meaning_mnemonic,
            section.format('reading mnemonic') + reading_mnemonic,
            section.format('source') + ('WaniKani' if type(subject) is WaniKaniSubject else 'Jisho')
        ]
        return '<br>'.join(line for line in lines if not line.endswith(': </b></font>'))
