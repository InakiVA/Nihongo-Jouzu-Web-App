import core.traduccion as trad
import re

def sort_key(dictionary, key):
    # Extract the numeric part of the string from the specified field
    match = re.search(r'(\d+)', dictionary[key])
    return int(match.group(1))

def max_page_possible(max_value):
    max_page = max_value // 10
    if max_value % 10 == 0:
        max_page -= 1
    return max_page


def bound_page_index(index, max_value):
    max_page = max_page_possible(max_value)
    if index > max_page:
        index = 0
    elif index < 0:
        index = max_page
    return index


def create_pages_list(index, max_value):
    max_page = max_page_possible(max_value)
    pages_list = []
    # -- de 1 a index
    if index > 3:
        pages_list.append({"text": 1, "value": 0, "current": index == 0})
        pages_list.append({})
        for i in range(index - 1, index):
            pages_list.append({"text": i + 1, "value": i, "current": index == i})
    else:
        for i in range(index):
            pages_list.append({"text": i + 1, "value": i, "current": index == i})
    # -- de index a max_page
    if index < max_page - 3:
        for i in range(index, index + 2):
            pages_list.append({"text": i + 1, "value": i, "current": index == i})
        pages_list.append({})
        pages_list.append(
            {
                "text": max_page + 1,
                "value": max_page,
                "current": index == max_page,
            }
        )
    else:
        for i in range(index, max_page + 1):
            pages_list.append({"text": i + 1, "value": i, "current": index == i})

    return pages_list


def cambiar_progreso(progreso, action):
    if action == "plus":
        progreso += 5
    elif action == "minus":
        progreso -= 5
    progreso = min(100, progreso)
    progreso = max(0, progreso)

    return progreso


# () function, list
# {} sorted list
# -- Apply a transformation fn to either a single input or a list
def apply_to_inputs(fn, inputs):
    values = set()
    if isinstance(inputs, list):
        for input_ in inputs:
            values.update(fn(input_))
    else:
        values.update(fn(inputs))
    return sorted(values)


# () str
# {} sorted list
def transcribe_input(input_):
    values = set()
    values.add(input_)
    values.add(trad.hiragana_to_romaji(input_))
    values.add(trad.romaji_to_hiragana(input_))
    values.add(trad.romaji_to_katakana(input_))
    return sorted(values)


# () str
# {} sorted list
def clean_input(input_):
    input_ = input_.strip()
    variants = set()

    # Basic variants
    variants.update(
        [
            input_,
            input_.lower().strip(),
            input_.upper().strip(),
            input_.capitalize().strip(),
        ]
    )

    # Punctuation removal
    punctuation_variants = list(variants)
    for variant in punctuation_variants:
        for char in ["*", "#", "、", ",", "¿", "?", "¡", "!", "<", ">"]:
            variant_2 = variant.replace(char, "").strip()
            if variant_2 not in variants:
                punctuation_variants.append(variant_2)
                variants.add(variant_2)

    # Accent removal
    for variant in list(variants):
        for a, b in [
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ñ", "n"),
            ("Á", "A"),
            ("É", "E"),
            ("Í", "I"),
            ("Ó", "O"),
            ("Ú", "U"),
            ("Ñ", "N"),
        ]:
            variants.add(variant.replace(a, b).strip())

    # Handle special character "・"
    for variant in list(variants):
        if "・" in variant:
            i = variant.index("・")
            variants.add(variant[:i].strip())
            variants.add((variant[:i] + variant[i + 1 :]).strip())

    # Handle parentheses
    for variant in list(variants):
        for l, r in [("(", ")"), ("（", "）")]:
            if l in variant and r in variant:
                try:
                    i = variant.index(l)
                    j = variant.index(r)
                    variants.add((variant[:i] + variant[j + 1 :]).strip())
                    variants.add(variant.replace(l, "").replace(r, "").strip())
                except ValueError:
                    pass  # skip malformed cases

    return sorted(variants)


# () list
# {} list
def set_alternate_inputs(input_list):
    clean_values = apply_to_inputs(clean_input, input_list)
    transcribed_values = apply_to_inputs(transcribe_input, clean_values)

    return transcribed_values


# () str, list
# {} bool
def check_answer(answer, correct_answers):
    correct_set = set(correct_answers)
    answer = answer.strip()
    transcribed_answers = transcribe_input(answer)
    for a in transcribed_answers:
        if a in correct_set:
            return True
    return False
