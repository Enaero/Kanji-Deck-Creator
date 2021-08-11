

def is_hiragana(character):
    return 0x3040 <= ord(character) <= 0x309F


def is_katakana(character):
    return 0x30A0 <= ord(character) <= 0x30FF


def is_all_kana(word):
    return all(is_katakana(character) or is_hiragana(character) for character in word)
