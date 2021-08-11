import logging

from typing import Union, Dict
from os import path

from jisho import Client as JishoClient

from kanji_deck_creator.data.appdata import wanikani_subjects_indexed, character_images_dir
from kanji_deck_creator.kanjigraph.kanji_type import KanjiType


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class KanjiData(object):
    subjects: Dict[str, Dict]
    character_lookup: Dict[str, Dict[str, Union[int, str]]]

    def __init__(self, data_by_characters):
        self.data = data_by_characters
        self.character_lookup = self.data['character_lookup']
        self.subjects = self.data['subjects']

    def get_subject(self, characters: str, kanji_type: KanjiType):
        if characters is None:
            raise ValueError('cannot determine subject from null character')
        try:
            # characters was set to the id already (edge case)
            subject_id = int(characters)
        except ValueError:
            # characters was not the id, but instead the characters (normal case)
            subject_id = self.character_lookup[kanji_type.value].get(characters)

        if subject_id is None:
            try:
                return JishoSubject(query=characters, kanji_type=kanji_type,
                                    jisho_client=JishoClient(), kanji_data=self)
            except RuntimeError:
                log.warning('Could not find data for [{}] using Jisho'.format(characters))
                return None
        return WaniKaniSubject(subject_id, self)


class Subject(object):
    @property
    def subject_id(self) -> int:
        return 0

    @property
    def subject_type(self) -> KanjiType:
        return KanjiType.VOCABULARY

    @property
    def image_path(self):
        return ''

    @property
    def reading(self):
        return ''

    @property
    def meaning(self):
        return ''

    @property
    def reading_mnemonic(self):
        return ''

    @property
    def meaning_mnemonic(self):
        return ''

    @property
    def characters(self):
        return ''

    @property
    def parts_of_speech(self):
        return ''

    @property
    def contained_in(self):
        return []

    @property
    def components(self):
        return []


class JishoSubject(object):
    _JISCHO_CACHE = {}
    _JISHO_ID = 2**31  # not reachable by wanikani

    def __init__(self, query, kanji_type: KanjiType, jisho_client, kanji_data: KanjiData):
        self._kanji_data = kanji_data
        self._kanji_type = kanji_type
        if query in self._JISCHO_CACHE:
            response = self._JISCHO_CACHE[query]
        else:
            response = jisho_client.search(query)
            self._JISCHO_CACHE[query] = response

        if 'data' not in response or not response['data']:
            raise RuntimeError('Jisho returned invalid response for {}'.format(query))

        # use the first (most common) definition since this is for a contextless flash card.
        datum = response['data'][0]
        japanese_words = datum['japanese']
        self._readings = [i.get('reading', '') for i in japanese_words]

        senses = datum['senses']
        self._parts_of_speech = [', '.join(speech_part for speech_part in i.get('parts_of_speech', [])) for i in senses]
        self._meanings = [', '.join(definition for definition in i.get('english_definitions', [])) for i in senses]

        self._characters = datum['slug']

    @property
    def subject_id(self) -> int:
        return self._JISHO_ID

    @property
    def subject_type(self) -> KanjiType:
        return self._kanji_type

    @property
    def image_path(self):
        return ''

    @property
    def reading(self):
        return ', '.join(self._readings)

    @property
    def meaning(self):
        return ', '.join(self._meanings)

    @property
    def reading_mnemonic(self):
        return ''

    @property
    def meaning_mnemonic(self):
        return ''

    @property
    def characters(self):
        return self._characters

    @property
    def parts_of_speech(self):
        return ', '.join(self._parts_of_speech)

    @property
    def contained_in(self):
        return []

    @property
    def components(self):
        if self.subject_type != KanjiType.VOCABULARY:
            # Jisho's radicals/primitives information is inconsistent and limited,
            # so just don't use it to avoid confusion.
            return []
        result = []
        for character in self.characters:
            subject_id = self._kanji_data.character_lookup[KanjiType.KANJI.value].get(character)
            if subject_id:
                result.append(WaniKaniSubject(subject_id, self._kanji_data))
        return result


class WaniKaniSubject(object):
    def __init__(self, subject_id: Union[str, int], kanji_data: KanjiData):
        self._subject_id = subject_id

        self._kanji_data = kanji_data
        self._subject = self._kanji_data.subjects[str(subject_id)]

    @property
    def subject_id(self):
        return self._subject_id

    @property
    def subject_type(self):
        for possible_type in (KanjiType.PRIMITIVE, KanjiType.KANJI, KanjiType.VOCABULARY):
            if self._subject['object'] == possible_type.value:
                return possible_type
        return None

    @property
    def image_path(self):
        image_folder = character_images_dir()
        image_name = self._subject['data'].get('character_images', [''])[0]
        if not image_name:
            return ''

        return path.join(image_folder, image_name)

    @property
    def reading(self):
        return ', '.join(reading['reading'] for reading in self._subject['data'].get('readings', []))

    @property
    def meaning(self):
        return ', '.join(meaning['meaning'] for meaning in self._subject['data']['meanings'])

    @property
    def reading_mnemonic(self):
        return self._subject['data'].get('reading_mnemonic', '')

    @property
    def meaning_mnemonic(self):
        return self._subject['data'].get('meaning_mnemonic', '')

    @property
    def characters(self):
        return self._subject['data']['characters']

    @property
    def parts_of_speech(self):
        return ', '.join(self._subject['data'].get('parts_of_speech', []))

    @property
    def contained_in(self):
        return [WaniKaniSubject(amalgamation_subject_id, self._kanji_data)
                for amalgamation_subject_id in self._subject['data'].get('amalgamation_subject_ids', [])]

    @property
    def components(self):
        return [WaniKaniSubject(component_id, self._kanji_data)
                for component_id in self._subject['data'].get('component_subject_ids', [])]


KANJI_DATA = KanjiData(wanikani_subjects_indexed())
