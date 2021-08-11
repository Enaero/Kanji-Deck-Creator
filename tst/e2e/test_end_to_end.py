import genanki

from kanji_deck_creator.deckbuilder.deck_builder import AnkiPackageBuilder
from kanji_deck_creator.data.kanji_data import KANJI_DATA
from kanji_deck_creator.kanjigraph.kanji_graph import KanjiGraph
from kanji_deck_creator.parser.tokenizer import JanomeTokenizer


def test_deck_creation_has_consistent_guids():
    text = '''「おれの方ほうが強つよい。」
    「いいや、ぼくの方ほうが強つよい。」
    北風きたかぜと太陽たいようの声こえが聞きこえます。二人ふたりはどちらの力ちからが強つよいかでケンカをしているようです。
    「太陽たいようが毎日まいにち元げん気きだから、暑あつくてみんな困こまっているよ。
    おれが涼すずしい風かぜを吹ふくと、みんな嬉うれしそうだ。おれの方ほうがみんなの役やくに立たっているよ。」
    「でも、ぼくがいないと、木きや野や菜さいは育そだたないよ。
    冬ふゆは北風きたかぜの吹ふく風かぜが冷つめたくて、とても寒さむかった。みんな外そとに出でられなかったよね？
    最近さいきんは暖あたたかいから、みんな喜よろこんでいるよ。」「いいや、あそこを見みて。
    太陽たいようが強つよく照てらすから、
    川かわの水みずがもうすぐ無なくなりそうだ。水みずがないと、みんな生活せいかつできないよ。」'''

    tokenizer = JanomeTokenizer()
    kanji_graph = KanjiGraph(KANJI_DATA)
    package_builder = AnkiPackageBuilder(tokenizer=tokenizer, kanji_graph=kanji_graph)

    package = package_builder.build(text, 'test_deck', mode='riffled')

    assert len(package.decks) == 1
    assert len(package.media_files) > 2

    deck: genanki.Deck = package.decks[0]

    assert deck.notes
    assert len(deck.notes) > 100

    first_guids = [note.guid for note in deck.notes]

    package2 = package_builder.build(text, 'test_deck', mode='riffled')
    second_guids = [note.guid for note in package2.decks[0].notes]

    assert first_guids == second_guids
