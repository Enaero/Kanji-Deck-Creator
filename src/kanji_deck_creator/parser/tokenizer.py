import jaconv

from typing import List, Iterator
from abc import ABC, abstractmethod

from janome.tokenizer import Token as JToken, Tokenizer as JTokenizer
from janome.analyzer import Analyzer as JAnalyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenfilter import POSStopFilter, LowerCaseFilter, TokenFilter

from kanji_deck_creator.unicode.util import is_all_kana


class Tokenizer(ABC):
    def tokenize(self, document) -> List[str]:
        return self._tokenize(document)

    @abstractmethod
    def _tokenize(self, document) -> List[str]:
        pass


# Janome's Token class does not work with copy.deepcopy so we have to write this hacky copy instead
class CopyToken(object):
    def __init__(self, token: JToken):
        self.part_of_speech = token.part_of_speech
        self.surface = token.surface
        self.base_form = token.base_form
        self.reading = token.reading
        self.phonetic = token.phonetic


class ConvertKatakanaWordsToHiragana(TokenFilter):
    def __init__(self, tokenizer: JTokenizer):
        self._tokenizer = tokenizer

    def apply(self, tokens: Iterator[JToken]) -> Iterator[JToken]:
        for token in tokens:
            # This will convert katakana characters to hiragana, otherwise leaves it alone
            hira_tokens = [t for t in self._tokenizer.tokenize(jaconv.kata2hira(token.surface))]

            if len(hira_tokens) > 1:
                # Transcribing to hiragana has changed the meaning, so just leave it as is
                yield token
            elif hira_tokens[0].surface == token.surface:
                # No katakana so there's nothing to do. Also, sometimes tokenizing a single word changes its
                # part of speech
                yield token
            else:
                # Katakana words are always nouns in janome for some reason. This will try to change it to
                # hiragana so janome can recognize japanese words that were written in katakana for emphaiss.
                token.part_of_speech = hira_tokens[0].part_of_speech
                yield token


class InclusiveCompoundNounFilter(TokenFilter):
    """
    This generates compound nouns as well as the component nouns.

    This Filter joins contiguous nouns, and also returns the individual nouns.
    For example, '形態素解析器' is splitted three noun tokens '形態素/解析/器' by Tokenizer and then re-joined by this filter.
    Generated tokens are associated with the special part-of-speech tag '名詞,複合,*,*'

    """
    @staticmethod
    def _make_compound_token(contiguous_nouns):
        compound_token = CopyToken(contiguous_nouns[0])
        compound_token.part_of_speech = '名詞,複合,*,*'

        for noun in contiguous_nouns[1:]:
            compound_token.surface += noun.surface
            compound_token.base_form += noun.base_form
            compound_token.reading += noun.reading
            compound_token.phonetic += noun.phonetic
        return compound_token

    def apply(self, tokens: Iterator[JToken]) -> Iterator[JToken]:
        contiguous_nouns = []
        for token in tokens:
            yield token

            if token.part_of_speech.startswith('名詞') and '自立' not in token.part_of_speech:
                if not is_all_kana(token.surface):
                    # skip nouns that are pure hiragana. Those are typically not part of the compound
                    contiguous_nouns.append(token)
            elif len(contiguous_nouns) > 1:
                compound_token = self._make_compound_token(contiguous_nouns)
                yield compound_token
                contiguous_nouns = []
            else:
                # If finished finding nouns but only found 1, throw it away because its already been yielded
                contiguous_nouns = []
        if len(contiguous_nouns) > 1:
            yield self._make_compound_token(contiguous_nouns)


class JanomeTokenizer(Tokenizer):

    def _tokenize(self, document) -> List[str]:
        """

        :type document: strr
        :return: list of vocabulary words in the document as str.
        """
        tokenizer = JTokenizer()
        char_filters = [
            UnicodeNormalizeCharFilter(),
            RegexReplaceCharFilter(
                # https://gist.github.com/terrancesnyder/1345094
                r'[^一-龯ぁ-んァ-ンｧ-ﾝﾞﾟぁ-ゞァ-ヶｦ-ﾟ\sー]',
                '。')]
        token_filters = [
            POSStopFilter(['記号', '助詞']),
            LowerCaseFilter(),
            ConvertKatakanaWordsToHiragana(JTokenizer()),
            InclusiveCompoundNounFilter()]

        analyzer = JAnalyzer(char_filters=char_filters, tokenizer=tokenizer, token_filters=token_filters)

        return [token.base_form for token in analyzer.analyze(document)]


DefaultTokenizer = JanomeTokenizer
