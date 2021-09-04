# Kanji Deck Creator
## What is it?
This is a tool for creating Anki decks for kanji words in Japanese text.
The decks are ordered based on dependencies, similar to how WaniKani or Remember the Kanji order their data, 
except the deck will only contain the vocab/kanji found in your source text. This way you don't have to learn 2000+ 
kanji to start reading your favorite material.

It uses WaniKani to determine component data (so you will need a WaniKani api token) and will fall back
to Jisho when a word is not found in Wanikani.

## Installing
You can just do `pip install .` from the root of the project folder. If you want to modify the code,
you should install it in a virtual environment using `pip install -e .` 

Later on this might get uploaded to pypi, but for now its just a repo.

## How to use it?
First you need to build your kanji data cache 
(because WaniKani does not allow distributing their data for obvious reasons). You can do this with
the script found at `bin/build_wanikani_index.py`. Simply run it and it will ask you for a WaniKani 
API token. Then it should take care of the rest automatically.

Afterwards, you can start building decks using `bin/create_deck.py`. You can run it with `--help` to see
usage. Example:
```
bin/create_deck.py --source-file Chapter1.txt --deck-name "My favorite chapter" --output-folder ../../anki-decks/
```

## Contributing
Feel free to open pull requests. The development process is straight forward: 
* Check out the code
* Create a virtual environment using something like virtualenv
* To run your changes, you can do a development install using `pip install -e .` (in the virutal env)
* Make sure to run the tests before opening a PR using `python -m pytest tst/` (in the virtual env)
