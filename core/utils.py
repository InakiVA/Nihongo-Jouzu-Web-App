import core.traduccion as trad


def bound_page_index(index, max_value):
    if index > max_value // 10:
        index = 0
    elif index < 0:
        index = max_value // 10

    return index


def create_pages_list(index, max_value):
    pages_list = []
    for i in range(max_value):
        pages_list.append({"text": i + 1, "current": index == i})
    pages_list.append({})
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
    for char in ["*", "#", "、", ",", "¿", "?", "¡", "!"]:
        variants.add(input_.replace(char, "").strip())

    # Accent removal
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
        variants.add(input_.replace(a, b).strip())

    # Handle special character "・"
    if "・" in input_:
        i = input_.index("・")
        variants.add(input_[:i].strip())
        variants.add((input_[:i] + input_[i + 1 :]).strip())

    # Handle parentheses
    for l, r in [("(", ")"), ("（", "）")]:
        if l in input_ and r in input_:
            try:
                i = input_.index(l)
                j = input_.index(r)
                variants.add((input_[:i] + input_[j + 1 :]).strip())
                variants.add(input_.replace(l, "").replace(r, "").strip())
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
