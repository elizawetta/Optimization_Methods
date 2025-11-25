import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ALLOWED_FUNCS = {
    "sin": np.sin,
    "cos": np.cos,
    "log": np.log,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "pi": np.pi,
    "tg": np.tanh
}


def constant_estimation(f, a, b, n):
    x_s = np.linspace(a, b, n)
    y_s = np.asarray(f(x_s))
    dy = np.abs(np.diff(y_s))
    dx = (b - a) / (n - 1)
    L = (dy / dx).max()
    return max(L, 1e-9) * 1.2


def piyavskii_shubert(f, a, b, L, eps, max_iters):
    num = 0
    x_borders = [a, b]
    y_borders = [f(a), f(b)]
    f_min = min(y_borders)
    x_min = x_borders[np.argmin(y_borders)]
    history = []
    t_start = time.time()
    while num < max_iters:
        num += 1
        xs, ys = [], []
        for i in np.argsort(x_borders):
            xs.append(x_borders[i])
            ys.append(y_borders[i])
        x_borders, y_borders = xs, ys

        candidates = []
        for i in range(1, len(x_borders)):
            xi, xj = x_borders[i - 1], x_borders[i]
            fi, fj = y_borders[i - 1], y_borders[i]
            x_star = 0.5 * (xi + xj) - (fi - fj) / (2 * L)
            x_star = min(max(x_star, xi), xj)
            m_val = max([yi - L * abs(xi - x_star) for xi, yi in zip(x_borders, y_borders)])
            candidates.append((m_val, x_star, i - 1))

        lower_bound = max([c[0] for c in candidates])
        gap = f_min - lower_bound
        history.append((num, f_min, lower_bound, gap))
        if gap <= eps:
            break

        m_val, x_new, idx = max(candidates)
        y_new = f(x_new)
        x_borders += [x_new]
        y_borders += [y_new]
        if y_new < f_min:
            f_min, x_min = y_new, x_new

    t_elapsed = time.time() - t_start
    hist_df = pd.DataFrame(history, columns=['iter', 'f_upper', 'f_lower', 'gap'])

    stat = {'x_borders': np.array(x_borders),'y_borders': np.array(y_borders),  'x_min': x_min, 'f_min': f_min, 'iterations': num,
            'time': t_elapsed, 'L': L, 'history': hist_df,
    }
    return stat


def plot(f, a, b, result, func_str, file_name="result.png"):
    x_dense = np.linspace(a, b, 1000)
    y_dense = np.asarray(f(x_dense), dtype=float)
    xi_samples = result["x_borders"]
    yi_samples = result["y_borders"]
    envelope = np.max(
        [yi_samples[i] - result["L"] * np.abs(x_dense - xi_samples[i]) for i in range(len(xi_samples))],
        axis=0
    )
    plt.plot(x_dense, y_dense, label="f(x)")
    plt.plot(x_dense, envelope,color="green", label="нижняя огибающая", linestyle="--")
    plt.scatter(xi_samples, yi_samples, color="green", label="испытанные точки")
    plt.scatter([result["x_min"]],
                [result["f_min"]],
                color="red", marker="x", s=75, label="найденный минимум")
    plt.title(
        "Метод Пиявского–Шуберта\n" + func_str +
        f"\nНайдено x ≈ {result['x_min']:.6g}, "
        f"f(x) ≈ {result['f_min']:.6g}, "
        f"итераций = {result['iterations']}, время ≈ {result['time']:.3f} секунд"
    )
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(file_name)


def report(func_str, a, b, eps, result, file_name="result.txt"):
    with open(file_name, "w") as f_out:
        f_out.write(f"Глобальный поиск минимума методом Пиявского–Шуберта\n"
        f"f(x) = {func_str} на отрезке [{a}, {b}]\n"
        f"Точность eps: {eps}\n"
        f"Оценка L (Липшиц): {result['L']:.6g}\n\n"
        "Результаты:\n"
        f"Приближённый аргумент минимума x ≈ {result['x_min']:.8g}\n"
        f"Приближённое значение f(x) ≈ {result['f_min']:.8g}\n"
        f"Количество итераций: {result['iterations']}\n"
        f"Примерное время вычислений (сек): {result['time']:.8f}\n\n"
        "Таблица итераций: (iter, f_upper, f_lower, gap)\n")
        for row in result["history"].itertuples(index=False):
            f_out.write(f"{row.iter:4d} | {row.f_upper:11f} | {row.f_lower:11f} | {row.gap:11f}\n")


def main():
    func = input("Введите f(x) = ").strip().replace('^', '**')
    a, b, eps = map(float, input("Введите через пробел границы a, b и eps: ").split())
    report_name = input("Введите название файла для отчета(.txt): ")
    gr_name = input("Введите название файла для графика(.png): ")
    f = lambda x: eval(compile(func, "<string>", "eval"), ALLOWED_FUNCS, {'x': x})

    n = 2000
    L_est = constant_estimation(f, a, b, n)
    res = piyavskii_shubert(f, a, b, L_est, eps, n)

    plot(f, a, b, res, func, file_name=gr_name)
    report(func, a, b, eps, res, file_name=report_name)


    print(f"Найденный минимум: x ≈ {res['x_min']:.8g}, f ≈ {res['f_min']:.8g}")
    print(f"Итераций: {res['iterations']}, время: {res['time']:.6f} s")
    print("result_plot.png — график функции и итераций")
    print("result.txt — результат поиска")
    print()


main()
