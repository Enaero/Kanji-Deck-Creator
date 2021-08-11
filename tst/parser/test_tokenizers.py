from kanji_deck_creator.parser.tokenizer import DefaultTokenizer


DOCUMENT = '''
法律関係のムズカシイ本が
イヤというほど並んでいる。
これからは、ぼくが
読まなくちゃいけないのかな‥‥。
ニューヨーク
'''


def test_default_tokenizer():
    tokenizer = DefaultTokenizer()

    actual_words = tokenizer.tokenize(DOCUMENT)

    expected_words = ['法律', '関係', 'ムズカシイ', '法律関係', '本', 'イヤ', 'いう', '並ぶ',
                      'いる', 'これから', 'ぼく', '読む', 'ない', 'いける', 'ない', 'の', 'ニューヨーク']

    assert expected_words == actual_words
