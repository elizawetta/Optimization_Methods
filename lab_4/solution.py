def V(i, n1, n2, nd, cash_c):
    if i >= T:
        total_c = n1 * u1 + n2 * u2 + nd * ud + cash_c
        return total_c, None

    # общая текущая сумма
    total = n1 * u1 + n2 * u2 + nd * ud + cash_c
    max_n1 = min(total // u1 + 1, max_n1_limit)
    max_n2 = min(total // u2 + 1, max_n2_limit)
    max_nd = min(total // ud + 1, max_nd_limit)

    # лимиты продаж
    max_sell_n1, max_sell_n2, max_sell_nd = n1, n2, nd

    # максимальные покупки (потенциальные)
    l_1 = int(max(-max_sell_n1, -search_radius))
    r_1 = int(min(max_n1 - n1, search_radius))

    l_2 = int(max(-max_sell_n2, -search_radius))
    r_2 = int(min(max_n2 - n2, search_radius))

    l_3 = int(max(-max_sell_nd, -search_radius))
    r_3 = int(min(max_nd - nd, search_radius))


    best_EV, best_action = 0, None
    for j in range(l_1, r_1 + 1):
        n1_update = n1 + j
        if n1_update < 0 or n1_update > max_n1_limit:
            continue

        for k in range(l_2, r_2 + 1):
            n2_update = n2 + k
            if n2_update < 0 or n2_update > max_n2_limit or abs(j) + abs(k) > max_package_changes:
                continue

            for l in range(l_3, r_3 + 1):
                if abs(j) + abs(k) + abs(l) > max_package_changes:
                    continue

                nd_update = nd + l
                if nd_update < 0 or nd_update > max_nd_limit:
                    continue

                # стоимость покупок и выручку от продаж
                buy, sell = 0, 0
                if j < 0:
                    sell += round(j * u1 * (c1 - 1))
                elif j > 0:
                    buy += round(j * u1 * (1 + c1))

                if k < 0:
                    sell += round(k * u2 * (c2 - 1))
                elif k > 0:
                    buy += round(k * u2 * (1 + c2))

                if l < 0:
                    sell += round(l * ud * (cd - 1))
                elif l > 0:
                    buy += round(l * ud * (1 + cd))

                update_cash = cash_c - buy + sell

                if update_cash < 0:
                    continue

                EV_acc = 0
                for s in stages[i]:
                    h1 = n1_update * u1 * s[1]
                    h2 = n2_update * u2 * s[2]
                    hd = nd_update * ud * s[3]

                    next_n1 = h1 // u1
                    next_n2 = h2 // u2
                    next_nd = hd // ud

                    rem_1 = round(h1 - next_n1 * u1)
                    rem_2 = round(h2 - next_n2 * u2)
                    rem_d = round(hd - next_nd * ud)

                    next_cash = update_cash + rem_1 + rem_2 + rem_d

                    val_next, _ = V(i + 1, next_n1, next_n2, next_nd, next_cash)
                    EV_acc += s[0] * val_next

                if EV_acc > best_EV:
                    best_EV = EV_acc
                    best_action = n1_update, n2_update, nd_update, update_cash, buy, sell

    return best_EV, best_action


u1, u2, ud = 25, 200, 100
c1, c2, cd = 0.04, 0.07, 0.05
u1 = u1 * 100
u2 = u2 * 100
ud = ud * 100
stages = [
    [(0.60, 1.20, 1.10, 1.07), (0.30, 1.05, 1.02, 1.03), (0.10, 0.80, 0.95, 1.00)],
    [(0.30, 1.40, 1.15, 1.01), (0.50, 1.05, 1.01, 1.00), (0.20, 0.60, 0.90, 1.00)],
    [(0.40, 1.15, 1.12, 1.05), (0.40, 1.05, 1.01, 1.01), (0.20, 0.70, 0.94, 1.00)]
]

n1_0 = 100 // 25
n2_0 = 800 // 200
nd_0 = 400 // 100
cash0 = 60000

T = 3
search_radius = 2
max_package_changes = 5

max_n1_limit = 100
max_n2_limit = 40
max_nd_limit = 50
ev_c, action = V(0, n1_0, n2_0, nd_0, cash0)
ev = ev_c / 100
print(f"EV = {ev:.2f}")
print("начальное действие:", action)
