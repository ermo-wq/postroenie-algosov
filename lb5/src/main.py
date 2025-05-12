class Node:
    def __init__(self, alphabet_size):
        self.next = [None] * alphabet_size
        self.jump = [None] * alphabet_size
        self.parent = None
        self.suff_link = None
        self.term_link = None
        self.is_leaf = False
        self.char = ''
        self.leaf_pattern_number = []
        self.pattern = ''

class AhoCorasick:
    def __init__(self):
        self.alphabet = ['A', 'C', 'G', 'T', 'N']
        self.alphabet_size = len(self.alphabet)
        self.root = Node(self.alphabet_size)
        self.root.parent = self.root
        self.root.suff_link = self.root
        self.root.term_link = self.root
        self.patterns = []
        self.node_count = 1

    def get_char(self, v):
        return f"{v.char if v.char != '' else 'root'}"

    def get_suff(self, v):
        if v.char == '':
            return 'root'
        result = v.char
        while v.parent is not self.root:
            result += v.parent.char
            v = v.parent
        return result[::-1]

    def jump(self, v, c_index):
        if v.jump[c_index] is None:
            if v.next[c_index] is not None:
                v.jump[c_index] = v.next[c_index]
                print(f"\t -> Перейдем по бору {self.get_suff(v)} ---> {self.get_char(v.jump[c_index])}.")
            elif v == self.root:
                print(f"\t -> Перешли в root.")
                v.jump[c_index] = self.root
            else:
                v.jump[c_index] = self.jump(self.get_suff_link(v), c_index)
                # print(f"\t -> Перейдем по суффиксной ссылке {self.get_suff(v)} ---> {self.get_suff(v.jump[c_index])}.")
        else: print(f"\t -> Переход по автомату {self.get_suff(v)} ---> {self.get_suff(v.jump[c_index])}.")
        return v.jump[c_index]

    def get_suff_link(self, v):
        if v.suff_link is None:
            if v == self.root or v.parent == self.root:
                v.suff_link = self.root
            else:
                print(f"\tИщем суффикс в боре:")
                c_index = self.alphabet.index(v.parent.char)
                v.suff_link = self.jump(self.get_suff_link(v.parent), c_index)
                if v.suff_link != self.root: print("\tСуффикс найден.")
                else: print("\tМаксимальный суффикс пустой.")
            print(f"\t -> Строим суффиксную ссылку {self.get_suff(v)} ---> {self.get_suff(v.suff_link)}")
        else: print(f"\t -> Переходим по суффиксной ссылке {self.get_suff(v)} ---> {self.get_suff(v.suff_link)}.")
        return v.suff_link

    def get_term_link(self, v):
        if v.term_link is None:
            suff_link = self.get_suff_link(v)
            if suff_link.is_leaf:
                v.term_link = suff_link
            elif suff_link == self.root:
                v.term_link = self.root
            else:
                v.term_link = self.get_term_link(suff_link)
            print(f"\t -> Строим терминальную ссылку {self.get_suff(v)} ---> {self.get_suff(v.term_link)}.")
        else: print(f"\t -> Переходим по терминальной ссылке {self.get_suff(v)} ---> {self.get_suff(v.term_link)}.")
        return v.term_link

    def add_string(self, s, pattern_number):
        print(f"Добавим строку '{s}' в бор:")
        cur = self.root
        for c in s:
            c_index = self.alphabet.index(c)
            if cur.next[c_index] is None:
                print(f"\t -> Символ '{c}' отсутствует в боре, добавляем его.")
                new_node = Node(self.alphabet_size)
                new_node.char = c
                new_node.parent = cur
                new_node.parent.char = c
                cur.next[c_index] = new_node
                self.node_count += 1
            else: print(f"\t -> Символ '{c}' уже существует в боре.")
            cur = cur.next[c_index]
        print(f"\t -> Помечаем символ '{c}' терминальным.")
        cur.is_leaf = True
        cur.leaf_pattern_number.append(pattern_number)
        cur.pattern = s
        self.patterns.append(s)

    def process_text(self, text):
        result = []
        current = self.root

        for i, c in enumerate(text):
            print(f"Рассмотрим вершину {c} на позиции {i + 1} в тексте {text}:")
            c_index = self.alphabet.index(c)
            current = self.jump(current, c_index)
            if current.char == '': print("\t -> Подстрока не встречается в тексте.")
            else: print(f"\tПерешли в состояние {self.get_suff(current)}.")

            temp = current
            while temp != self.root:
                term = self.get_term_link(temp)
                if temp.is_leaf:
                    for pattern_num in temp.leaf_pattern_number:
                        pattern_length = len(self.patterns[pattern_num])
                        start_pos = i - pattern_length + 1
                        result.append((start_pos, pattern_num))
                    print(f"\t -> Вершина {c} терминальная, обнаружено вхождение подстроки {temp.pattern}.")
                    print(f"\t -> Переходим по терминальной ссылке {self.get_suff(temp)} ---> {self.get_suff(term)}.")
                temp = term

        print(f"Количество вершин в автомате = {self.node_count}.")
        return result

    def process_text_with_mask(self, pattern, text, wildcard):
        print(f"----------------\nШаг 0. Проверка, что шаблон не состоит только из масок.")
        if all(ch == wildcard for ch in pattern):
            print(" -> Шаблон состоит только из масок.")
            return []

        print("Шаг 1. Разобьем строку на подстроки без маскок.")
        substrings = []
        substring_positions = []
        i = 0
        while i < len(pattern):
            if pattern[i] == wildcard:
                i += 1
                continue
            start = i
            while i < len(pattern) and pattern[i] != wildcard:
                i += 1
            substrings.append(pattern[start:i])
            substring_positions.append(start)
        print(f"Подстроки без масок: {", ".join(substrings)} на позициях: {", ".join(map(str, substring_positions))}.")

        print("----------------\nШаг 2. Добавим подстроки в бор.")
        for i, substring in enumerate(substrings):
            self.add_string(substring, i)

        counter = [0] * len(text)
        current = self.root
        print(f"----------------\nШаг 3. Инициализируем счетчик совпадений: {counter}")

        print(f"----------------\nШаг 4. Подсчитаем вхождения подстрок.")
        for i, c in enumerate(text):
            print(f"Рассмотрим вершину {c} на позиции {i + 1} в тексте {text}:")
            c_index = self.alphabet.index(c)
            current = self.jump(current, c_index)
            if current.char == '': print("\t -> Подстрока не встречается в тексте.")
            else: print(f"\tПерешли в состояние {self.get_suff(current)}.")

            temp = current
            while temp != self.root:
                term = self.get_term_link(temp)
                if temp.is_leaf:
                    for pattern_num in temp.leaf_pattern_number:
                        substring_position = substring_positions[pattern_num]
                        substring_length = len(substrings[pattern_num])
                        start_pos = i - substring_length - substring_position + 1
                        counter[start_pos] += 1
                    print(f"\t -> Вершина {temp.char} терминальная, обнаружено вхождение подстроки {temp.pattern}.")
                temp = term

        print(f"----------------\nШаг 5. Найдем вхождения шаблона.")
        print(f"Получившийся счетчик совпадений: {counter}.")
        result = []
        for i, count in enumerate(counter):
            if count == len(substrings):
                result.append(i + 1)
                print(f"\t -> Количество вхождений совпало для позиции {i + 1} с числом {count}.")
        return result

# var = int(input("Выберите вариант:\n\t1. Поиск набора образцов.\n\t2. Поиск образца с джокером.\n"))
var = 2

# Задание 1
if var == 1:
    text = input().strip()
    n = int(input())
    patterns = [input() for _ in range(n)]

    ac = AhoCorasick()
    print("Шаг 1. Добавим все строки в бор.")
    for i, pattern in enumerate(patterns):
        ac.add_string(pattern, i)

    print("----------------\nШаг 2. Преобразуем бор.")
    matches = ac.process_text(text)

    print("----------------\nШаг. 3. Вывод вхождений в текст.")
    matches.sort()
    for pos, pattern_num in matches:
        print(f" -> Шаблон {patterns[pattern_num]} встречается в тексте {text} на позиции {pos}.")

    print("----------------\nШаг. 4. Вывод найденных пересечений.")
    positions = [-1 for _ in range(len(text))]
    for pos, pattern_num in matches:
        length = len(patterns[pattern_num])
        for i in range(length):
            if positions[pos + i] != -1:
                print(f" -> Шаблон {patterns[pattern_num]} пересекается с шаблоном {patterns[positions[pos + i]]}.")
                break
            positions[pos + i] = pattern_num

# Задание 2
else:
    text = input()
    wildcard_pattern = input()
    wildcard = input()

    ac = AhoCorasick()
    matches = ac.process_text_with_mask(wildcard_pattern, text, wildcard)

    print(f"----------------\nШаг 6. Вывод найденных вхождений шаблона.")
    print(f" -> Шаблон {wildcard_pattern} встречается в тексте {text} на позициях: {", ".join(map(str, matches))}.")