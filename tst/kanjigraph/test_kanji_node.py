from kanji_deck_creator.kanjigraph.kanji_type import KanjiType
from kanji_deck_creator.kanjigraph.kanji_node import KanjiNode


def test_creating_kanji_node():
    text = 'ばかみたい'
    node = KanjiNode(text, KanjiType.VOCABULARY)
    assert node.value == text
    assert node.type == KanjiType.VOCABULARY


def test_kanji_node_is_encoded_when_encoded():
    node = KanjiNode('BD-123-bd-23', KanjiType.PRIMITIVE)

    assert node.is_encoded() is True


def test_kanji_node_is_encoded_when_not_encoded():
    node = KanjiNode('人', KanjiType.KANJI)

    assert node.is_encoded() is False


def test_kanji_node_equality_when_equal():
    node = KanjiNode('blah', KanjiType.KANJI)

    assert node != KanjiNode('blah', KanjiType.PRIMITIVE)
    assert node == KanjiNode('blah', KanjiType.KANJI)
    assert node != KanjiNode('a', KanjiType.KANJI)
