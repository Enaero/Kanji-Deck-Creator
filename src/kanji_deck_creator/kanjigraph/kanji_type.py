import enum


class KanjiType(enum.Enum):
    # The values are chosen to match WaniKani's 'object' field.
    PRIMITIVE = 'radical'
    KANJI = 'kanji'
    VOCABULARY = 'vocabulary'

    @classmethod
    def from_string(cls, s):
        if s == cls.PRIMITIVE.value:
            return cls.PRIMITIVE
        elif s == cls.KANJI.value:
            return cls.KANJI
        elif s == cls.VOCABULARY.value:
            return cls.VOCABULARY
        else:
            raise ValueError('{} is not a valid KanjiType'.format(s))
