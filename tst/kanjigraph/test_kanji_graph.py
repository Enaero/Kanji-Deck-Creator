import json


from kanji_deck_creator.kanjigraph.kanji_graph import KanjiGraph
from kanji_deck_creator.kanjigraph.kanji_node import KanjiNode
from kanji_deck_creator.kanjigraph.kanji_type import KanjiType
from kanji_deck_creator.data.kanji_data import KanjiData, KANJI_DATA

SIMPLE_DATA = {
  "character_lookup": {
    "vocabulary": {
      "\u4eba\u5f62": 3420
    },
    "kanji": {
      "\u4eba": 444,
      "\u5f62": 589
    },
    "radical": {
      "\u4eba": 9,
      "\u5f00": 171,
      "\u5f61": 38
    }
  },
  "subjects": {
    "3420": {
      "id": 3420,
      "object": "vocabulary",
      "data": {
        "characters": "\u4eba\u5f62",
        "component_subject_ids": [
          444,
          589
        ]
      }
    },
    "444": {
      "id": 444,
      "object": "kanji",
      "data": {
        "characters": "\u4eba",
        "component_subject_ids": [
          9
        ]
      }
    },
    "589": {
      "id": 589,
      "object": "kanji",
      "data": {
        "characters": "\u5f62",
        "component_subject_ids": [
          171,
          38
        ]
      }
    },
    "9": {
      "id": 9,
      "object": "radical",
      "data": {
        "characters": "\u4eba"
      }
    },
    "171": {
      "id": 171,
      "object": "radical",
      "data": {
        "characters": "\u5f00"
      }
    },
    "38": {
      "id": 38,
      "object": "radical",
      "data": {
        "characters": "\u5f61"
      }
    }
  }
}


# Making up nonsense words
SIMPLE_VOCAB = ["人形", "人"]


def test_create_kanji_graph():
    KanjiGraph(KANJI_DATA)


def test_add_word():
    kg = KanjiGraph(KanjiData(SIMPLE_DATA))
    kg.add('hi')

    assert ('hi', KanjiType.VOCABULARY) in kg.nodes
    assert ('h', KanjiType.KANJI) in kg.nodes
    assert ('i', KanjiType.KANJI) in kg.nodes


def test_add_compound_word():
    kg = KanjiGraph(KanjiData(SIMPLE_DATA))
    compound_word = ('bing', 'bong')

    kg.add_compound_word(compound_word)
    assert ('bing', KanjiType.VOCABULARY) in kg.nodes
    assert ('bong', KanjiType.VOCABULARY) in kg.nodes
    assert ('bingbong', KanjiType.VOCABULARY) in kg.nodes

    for c in 'bingbong':
        assert (c, KanjiType.KANJI) in kg.nodes

    assert len(kg.vocabs) == 3


def test_connections():
    kg = KanjiGraph(KanjiData(SIMPLE_DATA))

    for word in SIMPLE_VOCAB:
        kg.add(word)

    assert len(kg.vocabs) == 2
    assert len(kg.kanji) == 2
    assert len(kg.primitives) == 3

    for word in SIMPLE_VOCAB:
        assert (word, KanjiType.VOCABULARY) in kg.nodes

        word_node = kg.nodes[word, KanjiType.VOCABULARY]
        assert len(word) >= len(word_node.dependencies)

        for character in word:
            assert KanjiNode(character, KanjiType.KANJI) in word_node.dependencies


def test_vocab_list_by_frequency():
    kg = KanjiGraph(KanjiData(SIMPLE_DATA))

    for word in ["人形", "人", "形"]:
        kg.add(word)
    compound_word_list = ['人形', '人人']

    '''
    words: 
        人形人人: 1
        人形: 2
        人人: 1
        人: 1
        形: 1
    kanji:
        人: 5
        形: 3
    radical:
        人: 5
        hair radical: 3
        lantern radical: 3
    '''
    kg.add_compound_word(compound_word_list)

    freq_list = kg.sort_by_frequency(kg.nodes.values())

    vocab_list = [i.value for i in freq_list if i.type == KanjiType.VOCABULARY]
    kanji_list = [i.value for i in freq_list if i.type == KanjiType.KANJI]
    radical_list = [i.value for i in freq_list if i.type == KanjiType.PRIMITIVE]

    assert len(vocab_list) == 5
    assert vocab_list[0] == '人形'

    assert len(kanji_list) == 2
    assert kanji_list == ['人', '形']

    assert len(radical_list) == 3
    assert radical_list[0] == '人'


def test_vocab_list_by_complexity():
    kg = KanjiGraph(KanjiData(SIMPLE_DATA))

    for word in ["人形", "人", "形"]:
        kg.add(word)
    compound_word_list = ['人形', '人人']

    kg.add_compound_word(compound_word_list)
    complexity_list = kg.sort_by_complexity(kg.nodes.values())

    vocab_list = [i.value for i in complexity_list if i.type == KanjiType.VOCABULARY]
    kanji_list = [i.value for i in complexity_list if i.type == KanjiType.KANJI]
    radical_list = [i.value for i in complexity_list if i.type == KanjiType.PRIMITIVE]

    assert vocab_list == ['人', '人人', '形', '人形', '人形人人']
    assert kanji_list == ['人', '形']
    assert len(radical_list) == 3
