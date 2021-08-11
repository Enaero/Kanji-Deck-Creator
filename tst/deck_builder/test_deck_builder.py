from unittest.mock import Mock

from kanji_deck_creator.data.kanji_data import KANJI_DATA
from kanji_deck_creator.kanjigraph.kanji_type import KanjiType
from kanji_deck_creator.deckbuilder.deck_builder import AnkiPackageBuilder


# noinspection PyProtectedMember
def test_subjects_without_characters_are_parseable():
    subjects_ids_without_chars = [
        '8761', '8762', '8763', '8764', '8765', '8766',
        '8767', '8768', '8769', '8770', '8771', '8772', '8773',
        '8774', '8775', '8776', '8777', '8778', '8779', '8780',
        '8781', '8782', '8783', '8784', '8785', '8786', '8787',
        '8788', '8789', '8790', '8791', '8792', '8793', '8794',
        '8795', '8796', '8797', '8798', '8799', '8819'
    ]

    for subject_id in subjects_ids_without_chars:
        subject = KANJI_DATA.get_subject(subject_id, KanjiType.PRIMITIVE)
        AnkiPackageBuilder._get_front(subject)
        AnkiPackageBuilder._get_back(subject)


# noinspection PyProtectedMember
def test_subject_without_characters():
    subject = KANJI_DATA.get_subject('8761', KanjiType.PRIMITIVE)

    front = AnkiPackageBuilder._get_front(subject)
    assert '<img src="{}"'.format('8761.png') in front or \
           '<img src="{}"'.format('8761.svg') in front


# noinspection PyProtectedMember
def test_subject_with_image_components():
    subject = Mock()
    '''
                section.format('meaning') + html.escape(str(subject.meaning)),
            section.format('reading') + html.escape(str(subject.reading)),
            section.format('components') + ', '.join(cls._get_character_visual(i) for i in subject.components),
            section.format('parts of speech') + html.escape(subject.parts_of_speech),
            section.format('meaning mnemonic') + meaning_mnemonic,
            section.format('reading mnemonic') + reading_mnemonic,
            section.format('source') + ('WaniKani' if type(subject) is WaniKaniSubject else 'Jisho')
    '''
    component1 = Mock()
    component1.characters = '人'

    component2 = Mock()
    component2.characters = ''
    component2.image_path = 'idontexist.jpg'

    subject.meaning = 'meaning is blah'
    subject.reading = 'reading is blah '
    subject.meaning_mnemonic = 'blip blop'
    subject.reading_mnemonic = 'blop bloop'
    subject.parts_of_speech = 'verb'
    subject.source = 'Mock'
    subject.components = [component1, component2]

    # noinspection PyTypeChecker
    generated_back = AnkiPackageBuilder._get_back(subject)

    expected_components = '<font color="blue"><b>components: </b></font>人, <img src="idontexist.jpg" ' \
                          'alt="idontexist.jpg" height="32">'

    assert expected_components in generated_back
