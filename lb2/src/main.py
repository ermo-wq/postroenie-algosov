import random

def generate_matrix(n):
    matrix = [[-1] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = random.randint(1, 100)
    return matrix

def save_matrix_to_file(matrix, filename):
    with open(filename, 'w') as file:
        file.write(f"{len(matrix)}\n")
        for row in matrix:
            file.write(" ".join(map(str, row)) + "\n")

def load_matrix_from_file(filename):
    with open(filename, 'r') as file:
        n = int(file.readline())
        matrix = []
        for _ in range(n):
            row = list(map(int, file.readline().split()))
            matrix.append(row)
    return matrix

def calculate_total_cost(path, cost_matrix):
    total_cost = 0.0
    n = len(path)
    for i in range(n):
        total_cost += cost_matrix[path[i]][path[(i + 1) % n]]
    return total_cost

def amr_algorithm(cost_matrix):
    n = len(cost_matrix)
    initial_path = list(range(n))
    best_path = initial_path.copy()
    best_cost = calculate_total_cost(initial_path, cost_matrix)
    
    m = True
    iterations = 0
    F = n
    
    print(f"Начальный путь: {print_path(best_path)} со стоимостью: {best_cost}.")
    
    while m and iterations < F:
        m = False
        
        for i in range(1, n):
            for j in range(1, n):
                new_path = best_path[:]
                new_path[i], new_path[j] = new_path[j], new_path[i]
                new_cost = calculate_total_cost(new_path, cost_matrix)
                
                if new_cost < best_cost:
                    print(f"\tМеняем местами города {best_path[i]} и {best_path[j]}.")
                    print(f"Было обнаружено лучшее решение {print_path(new_path)} со стоимостью {new_cost} (улучшение на {best_cost - new_cost}).")
                    
                    best_path = new_path
                    best_cost = new_cost
                    m = True
                    
                    iterations += 1
                    break 
            
    print(f"Все города были посещены в порядке: {print_path(best_path)}. Стоимость найденного пути = {best_cost}.")
    return best_path, best_cost

def get_allowed_edges(path, remaining_cities):
    allowed_edges = []
    last_city = path[-1]
    for city in remaining_cities:
        allowed_edges.append((last_city, city))
    return allowed_edges

def calculate_mst(cost_matrix, path, remaining_cities):
    chunks = [path] + [[city] for city in remaining_cities]

    print("\tОценим оставшийся путь с помощью МОД для оставшихся кусков:")
    print(f"\t{" | ".join([", ".join(map(str, chunk)) for chunk in chunks])}.")
    print(f"\tВсе доступные ребра:")
    
    edges = []
    for i in range(len(chunks)):
        for j in range(len(chunks)):
            if i != j:
                start = chunks[i][-1]
                end = chunks[j][0]
                cost = cost_matrix[start][end]
                if cost != -1:
                    print(f"\t\t{start} -> {end}, стоимость = {cost}")
                    edges.append((cost, start, end))
    
    edges.sort()
    parent = {city: city for chunk in chunks for city in chunk}
    
    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    
    mst_weight = 0
    for cost, u, v in edges:
        root_u = find(u)
        root_v = find(v)
        if root_u != root_v:
            print(f"\tДобавляем к каркасу ребро {u} -> {v} со стоимостью {cost}.")
            mst_weight += cost
            parent[root_v] = root_u
    
    return mst_weight

def calculate_half_sum(cost_matrix, path, remaining_cities):
    chunks = [path] + [[city] for city in remaining_cities]
    half_sum = 0

    print("\n\tОценим оставшийся путь с помощью полусуммы весов двух легчайших рёбер по всем кускам:")
    print(f"\t{" | ".join([", ".join(map(str, chunk)) for chunk in chunks])}.")
    
    for chunk in chunks:
        incoming_edges = []
        for other_chunk in chunks:
            if other_chunk != chunk:
                start = other_chunk[-1]
                end = chunk[0]
                cost = cost_matrix[start][end]
                if cost != -1:
                    incoming_edges.append(cost)
        min_incoming = min(incoming_edges) if incoming_edges else 0
        
        outgoing_edges = []
        for other_chunk in chunks:
            if other_chunk != chunk:
                start = chunk[-1]
                end = other_chunk[0]
                cost = cost_matrix[start][end]
                if cost != -1:
                    outgoing_edges.append(cost)
        min_outgoing = min(outgoing_edges) if outgoing_edges else 0
        
        print(f"\tРассматриваем кусок {chunk}. Легчайшее входящее ребро = {min_incoming}, а исходящее = {min_outgoing}.")
        half_sum += (min_incoming + min_outgoing) / 2
    
    return half_sum

def calculate_lower_bound(path, remaining_cities, cost_matrix):
    mst_estimate = calculate_mst(cost_matrix, path, remaining_cities)
    half_sum_estimate = calculate_half_sum(cost_matrix, path, remaining_cities)
    print(f"\tДля оставшегося пути вес минимального каркаса = {mst_estimate}, минимальная полусумма = {half_sum_estimate}\n\t=> Берем максимальную из двух оценок = {max(mst_estimate, half_sum_estimate)}.\n")
    return max(mst_estimate, half_sum_estimate)

def branch_and_bound(cost_matrix):
    n = len(cost_matrix)
    best_path = None
    best_cost = float('inf')

    def backtrack(path, current_cost, remaining_cities):
        nonlocal best_path, best_cost

        if not remaining_cities:
            total_cost = current_cost + cost_matrix[path[-1]][path[0]]
            print(f"Все города были посещены в порядке: {print_path(path)}. Стоимость найденного пути = {total_cost}.\n-------------------------")
            if total_cost < best_cost:
                best_cost = total_cost
                best_path = path[:]
            return

        for u, v in get_allowed_edges(path, remaining_cities):
            new_cost = current_cost + cost_matrix[u][v]
            lower_bound = calculate_lower_bound(path + [v], remaining_cities - {v}, cost_matrix)
            if new_cost + lower_bound < best_cost:
                backtrack(path + [v], new_cost, remaining_cities - {v})
            else:
                print("\t=> Данное решение заведомо плохое и не подходит. Обрубаем ветку.\n")

    backtrack([0], 0, set(range(1, n)))
    return best_path, best_cost

def print_matrix(matrix):
    print("Матрица стоимости путей:")
    for i in range(len(matrix[0])):
        print("\t".join(map(str, matrix[i])))
    print()

def print_path(path):
    p = ""
    for i in range(len(path) - 1):
        p += f"{path[i]} -> "
    return p + f"{path[-1]}"

cost_matrix = []
opt = int(input("Хотите ли вы:\n\t1. Сгенерировать матрицу и сохранить ее в файл;\n\t2. Загрузить матрицу из файла;\n\t3. Ввести матрицу вручную.\n"))

if opt == 1:
    n = int(input("Введите размер матрицы стоимости путей: "))
    cost_matrix = generate_matrix(n)
    save_matrix_to_file(cost_matrix, "matrix.txt")
elif opt == 2:
    try:
        cost_matrix = load_matrix_from_file("matrix.txt")
    except FileNotFoundError:
        print("Файл с матрицей не существует, генерируем матрицу размера 3.")
        cost_matrix = generate_matrix(3)
        save_matrix_to_file(cost_matrix, "matrix.txt")
else:
    n = int(input("Введите размер матрицы стоимости путей: "))
    cost_matrix = []
    for i in range(n):
        row = list(map(float, input().split()))
        cost_matrix.append(row)

opt = int(input("Какой из методов решения использовать?\n\t1. МВиГ;\n\t2. АМР.\n"))
best_path, best_cost = branch_and_bound(cost_matrix) if opt == 1 else amr_algorithm(cost_matrix)
print(f"Лучшее решение:\nВсе города были посещены в порядке: {print_path(best_path)}. Стоимость найденного пути = {best_cost}.")