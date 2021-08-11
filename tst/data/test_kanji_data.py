from kanji_deck_creator.data.kanji_data import KANJI_DATA
from kanji_deck_creator.kanjigraph.kanji_type import KanjiType


def test_all_subjects_can_be_instantiated():
    for subject in KANJI_DATA.subjects.values():
        kanji_type = KanjiType.from_string(subject['object'])

        characters = subject['data']['characters'] or str(subject['id'])
        KANJI_DATA.get_subject(characters, kanji_type)
