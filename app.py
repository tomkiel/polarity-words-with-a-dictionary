from pathlib import Path
from textblob import TextBlob
from googletrans import Translator
from termcolor import colored
import os
import sys

translator = Translator()

filename: str = "input.txt"
src_lang = "es"
dest_lang = "en"


def generate_file(filename: str, content: str):
    """
    Generate a new file with content
    """
    with open(filename, "w") as f:
        f.write("[{}]".format(("]\n[").join(content)))
        f.close()


def get_word_polarity(word: str):
    """
    Determine the word polarity and return true or false.
    True = positive
    False = negative
    """
    if src_lang != "en":
        word = translator.translate(text=word, dest=dest_lang, src=src_lang)

    polarity = TextBlob(word.text).sentiment.polarity
    if polarity >= 0:
        return True
    else:
        return False


def progress_bar(len: int, count: int, size=50):
    """
    Show a progress bar for the progress.
    """
    progress = int(size * count / len)
    print(
        colored(
            f"[{u'█' * progress}{('.' * (size - progress))}] {count}/{len}", "green"
        ),
        end="\r",
        file=sys.stdout,
        flush=True,
    )


def parse_file():
    """
    Get content from file and checking the word polarity
    """
    words = {
        "verbs": {"positives": [], "negatives": []},
        "adjectives": {"positives": [], "negatives": []},
        "adverbs": {"positives": [], "negatives": []},
    }
    
    print("")
    print(colored("#" * 31, "green"))
    print(colored("# Stage 1: checking the words #", "green"))

    txt = Path(filename).read_text(encoding="UTF8")
    numbers_lines = len(txt.split("\n"))
    count = 0
    for line in txt.split("\n"):
        words_in_line = line.split("\t")
        word_type = words_in_line[2]

        if word_type == "verb" or word_type == "verb-basic":
            verbs = words_in_line[1].split(";")
            for verb in verbs:
                word = verb.replace(" ", "")
                polarity = get_word_polarity(word)
                if polarity:
                    words["verbs"]["positives"].append(word)
                else:
                    words["verbs"]["negatives"].append(word)

        if (
            word_type == "adjective"
            or word_type == "adjective-people"
            or word_type == "adjective-basic"
        ):
            adjectives = words_in_line[1].split(";")
            for adjective in adjectives:
                word = adjective.replace(" ", "")
                polarity = get_word_polarity(word)
                if polarity:
                    words["adjectives"]["positives"].append(word)
                else:
                    words["adjectives"]["negatives"].append(word)

        if word_type == "adverb":
            adverbs = words_in_line[1].split(";")
            for adverb in adverbs:
                word = adverb.replace(" ", "")
                polarity = get_word_polarity(word)
                if polarity:
                    words["adverbs"]["positives"].append(word)
                else:
                    words["adverbs"]["negatives"].append(word)

        count += 1
        progress_bar(numbers_lines, count)

    print("\n")
    print(colored("#" * 27, "green"))
    print(colored("# Stage 2: Generate files #", "green"))
    print("\n")

    dist = os.path.isdir("dist/{}".format(src_lang))
    if not dist:
      os.makedirs("dist/{}".format(src_lang))
    
    count = 0
    total = len(words)
    for word_group in words:
      positives = words[word_group]["positives"]
      negatives = words[word_group]["negatives"]
      generate_file(filename="dist/{lang}/{name}_Positivos.txt".format(lang=src_lang, name=word_group), content=positives)
      generate_file(filename="dist/{lang}/{name}_Negativos.txt".format(lang=src_lang, name=word_group), content=negatives)
      count+=1
      progress_bar(total, count)

    print("\n")
    print(colored("#" * 42, "green"))
    print(colored("# Stage 3: All words have been processed #", "green"))

if __name__ == "__main__":
    parse_file()
