def read_data(file_name):
    f = open(file_name)
    is_max = f.readline().strip() == 'max'
    func_coeffs = list(map(float, f.readline().split()))
    table = []
    while i := f.readline().strip():
        raw = i.split()
        b, sign = float(raw[-1]), raw[-2]
        if sign not in ["=", ">=", "<="]:
            raise "знак в равенстве/неравенстве должен быть один из: =, >=, <="
        coeffs = list(map(float, raw[:-2]))
        table.append((coeffs, sign, b))
    f.close()

    return is_max, func_coeffs, table


def canonization(table):
    coeff_table = []
    b_col = []

    for i in range(len(table)):
        c, sign, b = table[i]
        not_c = [-v for v in c]
        if sign == '=':
            coeff_table.append(c)
            coeff_table.append(not_c)
            b_col += [b, -b]
        elif sign == '<=':
            coeff_table.append(c)
            b_col += [b]
        else:
            coeff_table.append(not_c)
            b_col += [-b]

    return coeff_table, b_col


def simplex(func_coeffs, constraints, b_col, is_max):
    n, m = len(func_coeffs), len(constraints)

    simplex_table = []
    for i in range(m + 1):
        simplex_table.append([0 for _ in range(n + m + 1)])
    if not is_max:
        func_coeffs = [-x for x in func_coeffs]
    # заполнение z-строки
    for i in range(n):
        simplex_table[0][i] = -func_coeffs[i]

    # заполнение коэффициентов ограничений
    for j in range(n):
        for i in range(m):
            if j < len(constraints[i]):
                simplex_table[i + 1][j] = constraints[i][j]

    for i in range(m):
        simplex_table[i + 1][-1] = b_col[i]

    # единичные столбцы для базисных переменных
    for i in range(m):
        for j in range(m):
            if j == i:
                simplex_table[i + 1][j + n] = 1

    basis = [n + i for i in range(m)]
    # проверка отрицательных коэффициентов в строке z
    flag =  not all(x >= 0 for x in simplex_table[0][:-1])
    z = 0
    while flag:
        # выбор ведущего столбца (самый отрицательный коэффициент в z)
        col, min_val  = -1, 1e18
        for i in range(n + m):
            if simplex_table[0][i] < min_val:
                min_val = simplex_table[0][i]
                col = i
        if col == -1:
            raise "нет свободного столбца, симплекс метод применять нельзя"

        # выбор ведущей строку (минимальное отношение b / коэффициент)
        key_row, min_ratio = -1, 1e18
        for i in range(m):
            if simplex_table[i + 1][col] > 0:
                ratio = simplex_table[i + 1][-1] / simplex_table[i+ 1][col]
                if 0 <= ratio < min_ratio:
                    min_ratio, key_row = ratio, i + 1

        if key_row == -1:
            raise "неограниченное решение, симплекс метод применять нельзя"

        # нормировка ведущей строки
        pivot = simplex_table[key_row][col]
        for i in range(n + m + 1):
            simplex_table[key_row][i] = simplex_table[key_row][i] / pivot

        # обнуляем остальные строки по ведущему столбцу
        for i in range(m + 1):
            if i != key_row:
                div = simplex_table[i][col]
                for j in range(n + m + 1):
                    simplex_table[i][j] = simplex_table[i][j] - div * simplex_table[key_row][j]

        basis[key_row - 1] = col
        z = simplex_table[0][-1]
        # проверка, остались ли отрицательные коэффициенты в строке z
        flag = not all(x >= 0 for x in simplex_table[0][:-1])

    ans = [0] * n
    for i in range(m):
        if basis[i] < n:
            ans[basis[i]] = simplex_table[i + 1][-1]

    return z, ans


def print_answer():
    print('max' if is_max else 'min', end=' ')
    print(f"z =", " + ".join(
        [f"{func_coeffs[i] if int(func_coeffs[i]) != func_coeffs[i] else int(func_coeffs[i])}*x{i + 1}"
         for i in range(len(func_coeffs))]
    ))
    for i in range(len(coeff_table)):
        print(' + '.join(
            [f'{c if int(c) != c else int(c)}*x{j + 1}' for j, c in enumerate(coeff_table[i]) if c]
        ), "<=",  b_col[i])

    if is_max:
        print("max z =", z)
    else:
        print("min z =", -z)
    for i in range(len(ans)):
        print(f"x{i + 1} =", ans[i])

file_name = 'lab_1/data.txt'
is_max, func_coeffs, table = read_data(file_name)
coeff_table, b_col = canonization(table)
z, ans = simplex(func_coeffs, coeff_table, b_col, is_max)
print_answer()
