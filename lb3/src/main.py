def print_dist(D):
    dist = ""
    for i in range(len(D)):
        dist += f"\t{' '.join(map(str, D[i]))}\n" if i != len(D) - 1 else f"\t{' '.join(map(str, D[i]))}"
    return dist

def levenstein(s1, s2, replace_cost, insert_cost, delete_cost, cursed):
    print(f"Построим матрицу редакционного расстояния для слов {s1} и {s2}:")
    s1 = ' ' + s1
    s2 = ' ' + s2
    cursed = [i + 1 for i in cursed]

    n, m = len(s1), len(s2)
    D = [[0 for x in range(m)] for y in range(n)]

    for x in range(1, m):
        D[0][x] = D[0][x - 1] + insert_cost
    print(f"Заполним первый ряд матрицы:\n{print_dist(D)}")

    for y in range(1, n):
        D[y][0] = D[y - 1][0] + delete_cost
        print(f"-------------------\nБыл заполнен {y-1}-ый ряд матрицы:\n{print_dist(D)}")

        for x in range (1, m):
            print(f"-------------------\nСравним буквы '{s1[y]}' из слова '{s1[1:]}' и '{s2[x]}' из слова '{s2[1:]}'.")
            if s1[y] != s2[x]:
                delete, insert, replace = D[y - 1][x] + delete_cost, D[y][x - 1] + insert_cost, D[y - 1][x - 1] + replace_cost
                D[y][x] = min(delete, insert, replace)
                print(f"\tСтоимость добавления символа: {insert}.\n\tСтоимость удаления символа: {delete}.\n\t" \
                            f"Стоимость замены символа: {replace}.\n\t => Значение в клетке ({y} {x}) = {D[y][x]}.")
            else:
                D[y][x] = D[y - 1][x - 1]
                print(f"\tБуквы равны. => Значение в клетке ({y} {x}) = {D[y][x]}.")

    print(f"-------------------\nРедакционное расстояние = {D[n - 1][m - 1]}. Полученна матрица редакционного расстояния:\n{print_dist(D)}")
    return D

def redact(s1, s2, D, cursed):
    print(f"-------------------\nПолучим редакционное предписание для матрицы редакционного расстояния:")
    s1 = ' ' + s1
    s2 = ' ' + s2

    n = len(s1)
    m = len(s2)

    redact = ""
    cursed = [s1[i + 1] for i in cursed]

    y, x = n - 1, m - 1

    while y > 0 or x > 0:
        if y < 0 or x < 0:
            print(f"-------------------\nПреобразовать строку {s1[1:]} к строке {s2[1:]} невозможно.")
            return

        delete, insert, replace = D[y - 1][x], D[y][x - 1], D[y - 1][x - 1]
        min_operation = min(insert, delete, replace)

        print(f"-------------------\nСравним буквы '{s1[y]}' из слова '{s1[1:]}' и '{s2[x]}' из слова '{s2[1:]}'.")
        print(f"\tСтоимость вставки символа: {insert}.\n\tСтоимость удаления символа: {delete}.\n\t" \
                f"Стоимость замены символа: {replace}.\n\t=> Наименьшая стоимость = {min_operation}.")

        if s1[y] in cursed:
            if s1[y] == s2[x]:
                redact += 'M'
                print(f"Символы совпадают, добавляем 'M'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                x -= 1
                y -= 1
            elif s1[y].upper() == 'U':
                print(f"Символ '{s1[y]}' из слова '{s1[1:]}' проклят, однако является исключением.")
                if delete <= insert:
                    redact += 'D'
                    print(f"Наименьшую стоимость имеет операция удаления символа, добавляем 'D'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                    y -= 1
                else:
                    redact += 'I'
                    print(f"Наименьшую стоимость имеет операция вставки символа, добавляем 'I'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                    x -= 1
            else:
                redact += 'I'
                print(f"Символ '{s1[y]}' из слова '{s1[1:]}' проклят, добавляем 'I'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                x -= 1

        else:
            if min_operation == replace:
                if s1[y] != s2[x]:
                    redact += 'R'
                    print(f"Наименьшую стоимость имеет операция замены символа, добавляем 'R'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                else:
                    redact += 'M'
                    print(f"Символы совпадают, добавляем 'M'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                y -= 1
                x -= 1
            elif min_operation == insert:
                redact += 'I'
                print(f"Наименьшую стоимость имеет операция вставки символа, добавляем 'I'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                x -= 1
            elif min_operation == delete:
                redact += 'D'
                print(f"Наименьшую стоимость имеет операция удаления символа, добавляем 'D'.\nПолученное на данном этапе редакционное предписание = {redact}.")
                y -= 1

    redact = redact[::-1]
    print(f"-------------------\nПолученное редакционное предписание = {redact}.")
    return redact

s1 = input("Введите первую строку: ")
s2 = input("Введите вторую строку: ")

costs = input("Введите стоимость каждой из операций в виде 'замена вставка удаление': ")
cursed = input("Введите индексы проклятых элементов первой строки: ")

try:
    if len(costs) < 1:
        raise
    costs = list(map(int, costs.split(' ')))
    if len(cursed) > 0:
        cursed = list(map(int, cursed.split(' ')))
    if len(costs) != 3:
        raise
except:
    print("Введенные данные ошибочны.")
else:
    dist = levenstein(s1, s2, costs[0], costs[1], costs[2], cursed)
    redact(s1, s2, dist, cursed)