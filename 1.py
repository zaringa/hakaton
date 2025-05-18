import math


def delay_per_approach(C, G_phase, q, s):
    """
    Вычисляет задержку для одного направления с использованием формулы HCM.
    """
    if G_phase <= 0 or C <= 0:
        return float("inf")
    lambda_ = G_phase / C
    if lambda_ >= 1:
        return float("inf")
    c = s * lambda_
    if c <= 0:
        return float("inf")
    X = q / c
    if 2 * q * (1 - X) == 0:
        return float("inf")
    d = (
        (0.5 * C * (1 - lambda_) ** 2) / 2 * (1 - X * lambda_)
        + (X**2) / (2 * q * (1 - X))
        - 0.65 * ((C / (q**2)) ** 1 / 3) * (X ** (2 + 5 * lambda_))
    )
    return d


def total_delay(C, G_NS, G_EW, q_bus, s=1800, L=8):
    """
    Вычисляет общую задержку для перекрестка, разделяя на NS и EW.
    """
    if C != G_NS + G_EW + L:
        return float("inf"), float("inf")
    D_NS = 0
    D_EW = 0
    for dir in ["N", "S"]:
        q, bus_share = q_bus[dir]
        s_dir = s / (1 + bus_share)
        d = delay_per_approach(C, G_NS, q, s_dir)
        if d == float("inf"):
            return float("inf"), float("inf")
        D_NS += q * d
    for dir in ["E", "W"]:
        q, bus_share = q_bus[dir]
        s_dir = s / (1 + bus_share)
        d = delay_per_approach(C, G_EW, q, s_dir)
        if d == float("inf"):
            return float("inf"), float("inf")
        D_EW += q * d
    return D_NS, D_EW


def optimize_intersection(C, q_bus, s=1800, L=8, is_intersection_2=False):
    """
    Находит оптимальные G_NS и G_EW для заданного C.
    """
    min_D_total = float("inf")
    best_G_NS = None
    best_G_EW = None
    best_D_NS = None
    best_D_EW = None
    min_G_NS = 15 if not is_intersection_2 else max(15, math.ceil((C - 3) / 2))
    max_G_NS = C - 23
    for G_NS in range(min_G_NS, max_G_NS + 1):
        min_G_EW = 15
        max_G_EW = C - G_NS - L
        if max_G_EW < min_G_EW:
            continue
        for G_EW in range(min_G_EW, max_G_EW + 1):
            if C != G_NS + G_EW + L:
                continue
            D_NS, D_EW = total_delay(C, G_NS, G_EW, q_bus, s, L)
            D_total = D_NS + D_EW
            if D_total < min_D_total:
                min_D_total = D_total
                best_G_NS = G_NS
                best_G_EW = G_EW
                best_D_NS = D_NS
                best_D_EW = D_EW
    return best_G_NS, best_G_EW, best_D_NS, best_D_EW, min_D_total


# Данные о трафике
intersections = [
    {
        "N": (1000, 0.05),
        "S": (950, 0.05),
        "E": (450, 0.02),
        "W": (400, 0.02),
    },  # Перекресток 1
    {
        "N": (1100, 0.15),
        "S": (1050, 0.15),
        "E": (500, 0.03),
        "W": (480, 0.03),
    },  # Перекресток 2
    {
        "N": (900, 0.05),
        "S": (850, 0.05),
        "E": (420, 0.02),
        "W": (400, 0.02),
    },  # Перекресток 3
]

# Оптимизация для общей длины цикла
min_total_D = float("inf")
best_C = None
best_G_NS_list = [None] * 3
best_G_EW_list = [None] * 3
best_D_NS_list = [None] * 3
best_D_EW_list = [None] * 3

for C in range(60, 181):
    total_D = 0
    current_G_NS_list = []
    current_G_EW_list = []
    current_D_NS_list = []
    current_D_EW_list = []
    feasible = True
    for i, inter in enumerate(intersections):
        is_intersection_2 = i == 1
        G_NS, G_EW, D_NS, D_EW, D_total = optimize_intersection(
            C, inter, s=1800, L=8, is_intersection_2=is_intersection_2
        )
        if D_total == float("inf"):
            feasible = False
            break
        total_D += D_total
        current_G_NS_list.append(G_NS)
        current_G_EW_list.append(G_EW)
        current_D_NS_list.append(D_NS)
        current_D_EW_list.append(D_EW)
    if not feasible:
        continue
    if total_D < min_total_D:
        min_total_D = total_D
        best_C = C
        best_G_NS_list = current_G_NS_list
        best_G_EW_list = current_G_EW_list
        best_D_NS_list = current_D_NS_list
        best_D_EW_list = current_D_EW_list

# Вычисление сдвигов фаз для зеленой волны
travel_time_per_segment = 36  # секунд
offsets = [0]  # Перекресток 1
for i in range(1, 3):
    offset = (travel_time_per_segment * i) % best_C
    offsets.append(offset)

# Вывод результатов
print(f"Оптимальная общая длина цикла: {best_C} секунд")
for i in range(3):
    print(f"Перекресток {i + 1}:")
    print(f"  Время зеленого для С-Ю: {best_G_NS_list[i]} секунд")
    print(f"  Время зеленого для В-З: {best_G_EW_list[i]} секунд")
    print(f"  Задержка для С-Ю: {best_D_NS_list[i]:.2f} авт-секунд в час")
    print(f"  Задержка для В-З: {best_D_EW_list[i]:.2f} авт-секунд в час")
    print(f"  Сдвиг фазы: {offsets[i]} секунд")
print(f"Общая минимальная задержка: {min_total_D:.2f} авт-секунд в час")
