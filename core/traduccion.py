import re
import jaconv as jac


# recibe texto raw y lo formatea para poder convertirse bien a hira o kata
def format_text(input_):
    input_ = input_.lower().replace("si", "shi")
    input_ = input_.replace("ci", "chi")
    input_ = input_.replace("xn", "n|")
    input_ = input_.replace("nn", "n|")
    input_ = input_.replace("l", "x")
    return input_


def romaji_to_hiragana(romaji_text):
    text = jac.alphabet2kana(format_text(romaji_text))
    text = text.replace("|", "")
    return text


def romaji_to_katakana(romaji_text):
    text = jac.alphabet2kata(format_text(romaji_text))
    text = text.replace("|", "")
    return text


def hiragana_to_romaji(hira_text):
    text = jac.kana2alphabet(format_text(hira_text))
    return text


def is_kanji(char):
    # Check if the character falls within the ranges for Kanji
    return (
        "\u4e00" <= char <= "\u9fff"  # CJK Unified Ideographs
        or "\u3400" <= char <= "\u4dbf"  # CJK Unified Ideographs Extension A
        or "\uf900" <= char <= "\ufaff"
    )  # CJK Compatibility Ideographs


def extract_kanji(text):
    # Define the Unicode range for Kanji characters
    kanji_regex = re.compile(r"[\u4E00-\u9FFF]")

    # Find all Kanji characters in the string
    kanji_list = kanji_regex.findall(text)

    return kanji_list
