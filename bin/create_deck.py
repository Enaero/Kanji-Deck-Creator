import os
import argparse

from kanji_deck_creator.deckbuilder.deck_builder import AnkiPackageBuilder
from kanji_deck_creator.data.kanji_data import KANJI_DATA
from kanji_deck_creator.kanjigraph.kanji_graph import KanjiGraph
from kanji_deck_creator.parser.tokenizer import JanomeTokenizer


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    argparser.add_argument('--source-file', action='store', required=True,
                           help='The source (utf-8 encoded) file to extract vocab from.')
    argparser.add_argument('--deck-name', action='store', required=True,
                           help='The name of the Anki deck that will be created.')
    argparser.add_argument('--output-folder', action='store', required=False,
                           help='The folder to create the deck in')
    argparser.add_argument('--deck-order', action='store', required=False,
                           choices=('riffled', 'layered'), default='riffled',
                           help='What order the deck should be in. Defaults to riffled, which will show you vocab '
                                'words as soon as you know the words. You can pass in "layered" to have a system '
                                'similar to WaniKani, which is all radicals first, then all kanji, then all vocab.')

    args = argparser.parse_args()

    output_folder = args.output_folder or '.'
    output_path = os.path.join(output_folder, args.deck_name)
    if not output_path.endswith('.apkg'):
        output_path += '.apkg'

    with open(args.source_file, 'rt', encoding='utf-8') as fp:
        input_text = fp.read()

    tokenizer = JanomeTokenizer()
    kanji_graph = KanjiGraph(KANJI_DATA)
    package_builder = AnkiPackageBuilder(tokenizer=tokenizer, kanji_graph=kanji_graph)

    package = package_builder.build(input_text, args.deck_name, mode=args.deck_order)
    package.write_to_file(output_path)
