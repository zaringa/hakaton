import math
import pandas as pd

def veber(C, G_phase, q, s):
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
    """  Вычисляет общую задержку для перекрестка, разделяя на NS и EW.  """
    if C != G_NS + G_EW + L:
        return float("inf"), float("inf")
    D_NS = 0
    D_EW = 0
    for dir in ["N", "S"]:
        q, bus_share = q_bus[dir]
        s_dir = s / (1 + bus_share)
        d = veber(C, G_NS, q, s_dir)
        if d == float("inf"):
            return float("inf"), float("inf")
        D_NS += q * d
    for dir in ["E", "W"]:
        q, bus_share = q_bus[dir]
        s_dir = s / (1 + bus_share)
        d = veber(C, G_EW, q, s_dir)
        if d == float("inf"):
            return float("inf"), float("inf")
        D_EW += q * d
    return D_NS, D_EW


def optimize_intersection(C, q_bus, s=1800, L=8, is_intersection_2=False):
    """    Находит оптимальные G_NS и G_EW для заданного C.  """
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


df_flows = pd.read_csv("flows_peak.csv")
df_signals = pd.read_csv("signals_current.csv")

intersections = []
for intersection_id, group in df_flows.groupby("intersection_id"):
    directions = {
        row["approach"]: (row["intensity_veh_per_hr"], row["bus_share"])
        for _, row in group.iterrows()
    }
    intersections.append(directions)

n = 0
for intersection_id in df_signals.groupby("intersection_id"):
    n += 1


min_total_D = float("inf")
best_C = None
best_G_NS_list = [None] * 3
best_G_EW_list = [None] * 3
best_D_NS_list = [None] * 3
best_D_EW_list = [None] * 3


# Определяем диапазон общей длины цикла для каждого перекрестка
C_ranges = [(60, 180)] * n  # Для каждого перекрестка один и тот же диапазон (60-180)

# Хранилища для результатов
best_results = []

# Оптимизируем каждый перекресток независимо
for i, inter in enumerate(intersections):
    best_C = None
    best_G_NS = None
    best_G_EW = None
    best_D_NS = None
    best_D_EW = None
    min_total_D = float("inf")

    C_start, C_end = C_ranges[i]
    for C in range(C_start, C_end + 1):
        is_intersection_2 = i == 1  # Условие для второго перекрестка
        G_NS, G_EW, D_NS, D_EW, D_total = optimize_intersection(
            C, inter, s=1800, L=8, is_intersection_2=is_intersection_2
        )

        if D_total < min_total_D and D_total != float("inf"):
            min_total_D = D_total
            best_C = C
            best_G_NS = G_NS
            best_G_EW = G_EW
            best_D_NS = D_NS
            best_D_EW = D_EW

    best_results.append(
        {
            "intersection_id": i + 1,
            "C": best_C,
            "G_NS": best_G_NS,
            "G_EW": best_G_EW,
            "D_NS": best_D_NS,
            "D_EW": best_D_EW,
            "D_total": min_total_D,
        }
    )

# Вычисление сдвигов фаз для зеленой волны (остается прежним)
travel_time_per_segment = 36  # секунд
# Возьмем длину цикла первого перекрестка для расчета сдвигов
first_intersection_cycle = best_results[0]["C"] if best_results else 60
offsets = [0]  # Перекресток 1
for i in range(1, n):
    offset = (travel_time_per_segment * i) % first_intersection_cycle
    offsets.append(offset)

# Вывод результатов
print("Оптимизированные параметры для каждого перекрестка:")
for i, result in enumerate(best_results):
    print(f"Перекресток {result['intersection_id']}:")
    print(f"  Оптимальная длина цикла: {result['C']} секунд")
    print(f"  Время зеленого для С-Ю: {result['G_NS']} секунд")
    print(f"  Время зеленого для В-З: {result['G_EW']} секунд")
    print(f"  Задержка для С-Ю: {result['D_NS']:.2f} авт-секунд в час")
    print(f"  Задержка для В-З: {result['D_EW']:.2f} авт-секунд в час")
    print(f"  Сдвиг фазы: {offsets[i]} секунд")
    print(f"  Общая задержка для перекрестка: {result['D_total']:.2f} авт-секунд в час")