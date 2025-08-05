import core.traduccion as trad


# == aquí van las funciones generales
def set_alternate_inputs(input_list):
    values = set()
    for input_ in input_list:
        values.add(input_.strip())
        values.add(input_.lower().strip())
        values.add(input_.upper().strip())
        values.add(input_.capitalize().strip())

        values.add(input_.replace("*", "").strip())
        values.add(input_.replace("#", "").strip())
        values.add(input_.replace("、", "").strip())
        values.add(input_.replace(",", "").strip())
        values.add(input_.replace("¿", "").strip())
        values.add(input_.replace("?", "").strip())
        values.add(input_.replace("¡", "").strip())
        values.add(input_.replace("!", "").strip())

        if "・" in input_:
            i = input_.index("・")
            values.add(input_[:i].strip())
            values.add((input_[:i] + input_[i + 1 :]).strip())

        if "(" in input_ and ")" in input_:
            i = input_.index("(")
            j = input_.index(")")
            values.add((input_[:i] + input_[j + 1 :]).strip())
            values.add(input_.replace("(", "").replace(")", "").strip())

        if "（" in input_ and "）" in input_:
            i = input_.index("(")
            j = input_.index(")")
            values.add((input_[:i] + input_[j + 1 :]).strip())
            values.add(input_.replace("(", "").replace(")", "").strip())

    values_list = list(values)

    for input_ in values_list:
        values.add(trad.hiragana_to_romaji(input_))
        values.add(trad.romaji_to_hiragana(input_))
        values.add(trad.romaji_to_katakana(input_))

    values_list = list(values)
    values_list.sort()

    return values_list


def check_answer(answer, correct_answers):
    correct_set = set(correct_answers)
    answer = answer.strip()
    romaji_answer = trad.hiragana_to_romaji(answer)
    hiragana_answer = trad.romaji_to_hiragana(answer)
    katakana_answer = trad.romaji_to_katakana(answer)
    for a in [answer, romaji_answer, hiragana_answer, katakana_answer]:
        if a in correct_set:
            return True
    return False
