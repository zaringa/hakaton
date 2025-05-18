## hakaton
sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate
sudo apt install pipx
pip install pandas

Хорошо, давайте разберем предоставленный вами код Python по разделам. Этот код направлен на оптимизацию времени работы светофоров на перекрестках на основе транспортного потока, потребностей пешеходов и некоторых определенных ограничений.

1. Импорт библиотек:

питон

Копировать

import pandas as pd

import json

pandas: Мощная библиотека для обработки и анализа данных. Здесь она используется для чтения и обработки CSV-файлов ( flows_peak.csv, signals_current.csv). Основным объектом в pandas является DataFrame, который похож на таблицу данных.

json: Библиотека для работы с данными JSON (JavaScript Object Notation). Используется для чтения constraints.jsonфайла.

2. adjust_traffic_lightsФункция:

питон

Копировать

def adjust_traffic_lights(flows_file, signals_file, pedestrian_file, constraints_file):

    """

    Adjusts traffic light timings based on traffic flow, current signals,

    pedestrian requirements, and constraints.

    Args:

        flows_file (str): Path to the flows_peak.csv file.

        signals_file (str): Path to the signals_current.csv file.

        pedestrian_file (str): Path to the pedestrian_req.txt file.

        constraints_file (str): Path to the constraints.json file.

    Returns:

        pandas.DataFrame: Updated traffic signal timings.

    """

Это определяет основную функцию, которая выполняет оптимизацию светофора. Она принимает четыре аргумента: пути к четырем входным файлам.

Строка документации (текст в тройных кавычках """Docstring""") объясняет, что делает функция, ожидаемые входные файлы и что она возвращает. Это хорошая практика для документирования кода.

3. Загрузка данных:

питон

Копировать

    # Load data

    flows = pd.read_csv(flows_file)

    signals = pd.read_csv(signals_file)

    with open(constraints_file, 'r') as f:

        constraints = json.load(f)

    # Extract pedestrian green time

    with open(pedestrian_file, 'r') as f:

        pedestrian_line = f.readline()

        pedestrian_green_sec = int(pedestrian_line.split(': ')[1].split(' ')[0]) #or constraints['pedestrian_green_sec']

flows = pd.read_csv(flows_file): Считывает flows_peak.csvфайл в pandas DataFrame с именем flows.

signals = pd.read_csv(signals_file): Считывает signals_current.csvфайл в pandas DataFrame с именем signals. Этот DataFrame содержит начальные временные параметры светофора.

Блок with open(...) as f:открывает constraints.jsonфайл в режиме чтения ( 'r'). json.load(f)Функция считывает данные JSON из файла и сохраняет их в словаре Python с именем constraints. withОператор гарантирует, что файл будет правильно закрыт после использования, даже если возникнут ошибки.

Затем он считывает время зеленого света для пешеходов из pedestrian_req.txtфайла. Он открывает файл, считывает первую строку, а затем извлекает количество секунд с помощью разбиения строки.

Часть split(': ')[1]разделяет строку по знаку «:» и занимает вторую часть (например, «10 секунд»).

Затем часть split(' ')[0]разделяет ее по пробелу и берет первую часть (например, «10»).

int(...)преобразует строку «10» в целое число 10.

4. Извлечение глобальных ограничений:

питон

Копировать

    # Global constraints

    min_cycle_sec = constraints['min_cycle_sec']

    max_cycle_sec = constraints['max_cycle_sec']

    min_green_sec = constraints['min_green_sec']

    lost_time_sec_per_phase = constraints['lost_time_sec_per_phase']

    #Bus priority (handling optional presence)

    bus_priority = constraints.get('bus_priority')  # Use .get() to handle missing key gracefully

В этом разделе глобальные ограничения извлекаются из constraintsсловаря и назначаются отдельным переменным. Эти ограничения будут использоваться для ограничения корректировок, вносимых в тайминги светофоров.

bus_priority = constraints.get('bus_priority'): Это попытка получить bus_priorityнастройку из constraintsсловаря. .get()Метод используется вместо прямого доступа ( constraints['bus_priority']), поскольку bus_priorityявляется необязательным . Если bus_priorityотсутствует в файле JSON, .get()вернет Noneбез возникновения ошибки. Это более безопасный способ обработки необязательных настроек.

5. Итерация через пересечения:

питон

Копировать

    # Adjust cycle and green times for each intersection

    for index, row in signals.iterrows():

        intersection_id = row['intersection_id']

        cycle_sec = row['cycle_sec']

        green_main_sec = row['green_main_sec']

        green_secondary_sec = row['green_secondary_sec']

        # Filter flows for the current intersection

        intersection_flows = flows[flows['intersection_id'] == intersection_id]

Это основной цикл, который проходит по каждому пересечению в signalsDataFrame.

signals.iterrows(): Это функция pandas, которая перебирает строки DataFrame. Для каждой строки она возвращает индекс строки ( index) и данные строки в виде серии pandas ( row).

Внутри цикла код извлекает значения intersection_id, cycle_sec, green_main_secи green_secondary_secиз текущей строки.

intersection_flows = flows[flows['intersection_id'] == intersection_id]: фильтрует flowsDataFrame для создания нового DataFrame с именем , intersection_flowsсодержащего только те строки, которые соответствуют текущему пересечению.

6. Расчет интенсивности движения:

питон

Копировать

        # Calculate total intensity for main and secondary directions

        main_directions = ['N', 'S']  # Example, adjust based on your road network

        secondary_directions = ['E', 'W'] # Example, adjust based on your road network

        main_intensity = intersection_flows[intersection_flows['approach'].isin(main_directions)]['intensity_veh_per_hr'].sum()

        secondary_intensity = intersection_flows[intersection_flows['approach'].isin(secondary_directions)]['intensity_veh_per_hr'].sum()

        total_intensity = main_intensity + secondary_intensity

В этом разделе рассчитывается общая интенсивность движения по основным и второстепенным направлениям на текущем перекрестке.

main_directions = ['N', 'S']и secondary_directions = ['E', 'W']: Эти линии определяют списки направлений, которые считаются «главными» и «второстепенными» подходами к перекрестку.   Важно: Возможно, вам придется скорректировать эти списки на основе фактической компоновки вашей дорожной сети.

intersection_flows['approach'].isin(main_directions): Это создает логический ряд, предназначенный Trueдля строк, в которых approachстолбец находится в main_directionsсписке, и Falseв противном случае.

intersection_flows[intersection_flows['approach'].isin(main_directions)]: фильтрует DataFrame intersection_flows, включая только строки, соответствующие основным направлениям.

['intensity_veh_per_hr'].sum(): Это выбирает intensity_veh_per_hrстолбец из отфильтрованного DataFrame и вычисляет сумму значений. Это дает общую интенсивность трафика для основных направлений. Та же логика применяется для вычисления secondary_intensity.

total_intensity = main_intensity + secondary_intensity: Общая интенсивность представляет собой сумму основной и дополнительной интенсивности.

7. Корректировка времени действия зеленого сигнала в зависимости от интенсивности:

питон

Копировать

        # Adjust green times based on intensity ratio

        if total_intensity > 0:

            main_ratio = main_intensity / total_intensity

            secondary_ratio = secondary_intensity / total_intensity

            #Calculate new green times

            new_green_main_sec = (cycle_sec - 2 * lost_time_sec_per_phase) * main_ratio

            new_green_secondary_sec = (cycle_sec - 2 * lost_time_sec_per_phase) * secondary_ratio

            # Apply constraints, including pedestrian time

            new_green_main_sec = max(min_green_sec, new_green_main_sec)

            new_green_secondary_sec = max(min_green_sec, new_green_secondary_sec)

            #Ensure pedestrian minimum

            total_green_time = new_green_main_sec + new_green_secondary_sec

            if total_green_time < pedestrian_green_sec:

                diff = pedestrian_green_sec - total_green_time

                #Distribute the difference (simplest approach: proportionally, but smarter ways exist)

                new_green_main_sec += diff * main_ratio if main_ratio > 0 else diff / 2  #Avoid division by zero

                new_green_secondary_sec += diff * secondary_ratio if secondary_ratio > 0 else diff / 2

            #Bus Priority

            if bus_priority and intersection_id == bus_priority['intersection_id']:

                priority_direction = bus_priority['priority_direction']

                min_extra_green_sec = bus_priority['min_extra_green_sec']

                if priority_direction in main_directions:

                    new_green_main_sec = new_green_main_sec + min_extra_green_sec

                else: #secondary directions

                     new_green_secondary_sec = new_green_secondary_sec + min_extra_green_sec

Это основная логика корректировки времени действия зеленого сигнала светофора.

if total_intensity > 0:: Эта проверка предотвращает деление на ноль, если на перекрестке нет движения.

main_ratio = main_intensity / total_intensityи secondary_ratio = secondary_intensity / total_intensity: Они рассчитывают долю трафика, текущего в основных и второстепенных направлениях.

new_green_main_sec = (cycle_sec - 2 * lost_time_sec_per_phase) * main_ratioи new_green_secondary_sec = (cycle_sec - 2 * lost_time_sec_per_phase) * secondary_ratio: Они вычисляют новое время зеленого света на основе коэффициентов трафика. Он вычитает общее потерянное время из длины цикла и распределяет оставшееся время пропорционально. Потерянное время умножается на 2, поскольку есть две фазы.

new_green_main_sec = max(min_green_sec, new_green_main_sec)и new_green_secondary_sec = max(min_green_sec, new_green_secondary_sec): Они гарантируют, что новое время зеленого света не будет меньше минимального времени зеленого света, указанного в ограничениях.

Затем код проверяет, меньше ли общее время зеленого света, чем минимальное время зеленого света для пешеходов. Если это так, он добавляет разницу к основному и второстепенному времени зеленого света, распределяя ее пропорционально их коэффициентам трафика. Часть if main_ratio > 0 else diff / 2обрабатывает случай, когда в одном направлении нет трафика (чтобы избежать деления на ноль).

Приоритет автобуса :

if bus_priority and intersection_id == bus_priority['intersection_id']:: Проверяет, включен ли приоритет автобусов ( bus_priorityне включен None) и является ли текущий перекресток тем, на котором должен применяться приоритет автобусов.

if priority_direction in main_directions:и else:: Проверяет, является ли priority_direction(определено в constraints.jsonфайле) основным направлением или второстепенным направлением.

new_green_main_sec = new_green_main_sec + min_extra_green_secили new_green_secondary_sec = new_green_secondary_sec + min_extra_green_sec: Это добавляет дополнительное время зеленого света в соответствующем направлении.   Важное примечание: этот код всегда добавляет дополнительное время зеленого света, независимо от того, присутствует ли автобус на самом деле. Более сложная система будет использовать датчики или другие данные для обнаружения автобусов и добавлять дополнительное время только при необходимости.

8. Обновление времени цикла и применение ограничений:

питон

Копировать

            # Update cycle time if needed based on changes to green times, prioritizing pedestrian and min green.

            new_cycle_sec = new_green_main_sec + new_green_secondary_sec + 2 * lost_time_sec_per_phase

            new_cycle_sec = max(new_cycle_sec, pedestrian_green_sec + 2 * lost_time_sec_per_phase)  #Ensure cycle long enough for pedestrians

            new_cycle_sec = max(new_cycle_sec, 2 * min_green_sec + 2 * lost_time_sec_per_phase ) #Ensure cycle long enough for min_green * 2

            new_cycle_sec = min(max_cycle_sec, new_cycle_sec)

            if new_cycle_sec != cycle_sec: #Redistribute any leftover

                 new_green_main_sec = (new_cycle_sec - 2 * lost_time_sec_per_phase) * main_ratio

                 new_green_secondary_sec = (new_cycle_sec - 2 * lost_time_sec_per_phase) * secondary_ratio

            # Apply Cycle time limits

            cycle_sec = min(max_cycle_sec, new_cycle_sec)

            cycle_sec = max(min_cycle_sec, cycle_sec) #Apply minimum cycle time

            # Update signals DataFrame

            signals.loc[index, 'cycle_sec'] = cycle_sec

            signals.loc[index, 'green_main_sec'] = new_green_main_sec

            signals.loc[index, 'green_secondary_sec'] = new_green_secondary_sec

В этом разделе обновляется время цикла, гарантируя, что оно соответствует минимальным требованиям для пешеходов и времени действия зеленого сигнала светофора, а также применяются общие ограничения времени цикла.

new_cycle_sec = new_green_main_sec + new_green_secondary_sec + 2 * lost_time_sec_per_phase: Это вычисляет новое время цикла на основе нового зеленого времени и потерянного времени на фазу.

Функции max()гарантируют, что время цикла будет достаточно продолжительным, чтобы обеспечить минимальное время зеленого света для пешеходов и минимальное время зеленого света для обоих направлений.

new_cycle_sec = min(max_cycle_sec, new_cycle_sec): Это ограничивает время цикла до максимально допустимого времени цикла.

Если новое время цикла отличается от исходного, зеленое время пересчитывается в соответствии с новым циклом.

Затем код применяет максимальные и минимальные ограничения времени цикла.

signals.loc[index, 'cycle_sec'] = cycle_sec, signals.loc[index, 'green_main_sec'] = new_green_main_sec, и signals.loc[index, 'green_secondary_sec'] = new_green_secondary_sec: Эти строки обновляют значения cycle_sec, green_main_sec, и green_secondary_secв signalsDataFrame новыми вычисленными значениями.   signals.loc[index, column_name]— это правильный способ изменения DataFrame pandas.

9. Возврат обновленных сигналов:

питон

Копировать

    return signals

Функция возвращает signalsDataFrame, который теперь содержит обновленное время работы светофоров.

10. Пример использования:

питон

Копировать

# Example Usage

flows_file = 'flows_peak.csv'

signals_file = 'signals_current.csv'

pedestrian_file = 'pedestrian_req.txt'

constraints_file = 'constraints.json'

updated_signals = adjust_traffic_lights(flows_file, signals_file, pedestrian_file, constraints_file)

print(updated_signals)

# Optionally, save the updated signals to a new CSV file

#updated_signals.to_csv('signals_updated.csv', index=False)

В этом разделе показано, как использовать эту adjust_traffic_lightsфункцию.

Он определяет пути к входным файлам.

Он вызывает adjust_traffic_lightsфункцию с указанием путей к файлам и сохраняет результат в updated_signalsDataFrame.

Он выводит updated_signalsDataFrame на консоль.

Закомментированная строка #updated_signals.to_csv('signals_updated.csv', index=False)показывает, как можно сохранить обновленные сигналы в новый CSV-файл.   index=Falseне позволяет pandas записывать индекс DataFrame в CSV-файл.

В итоге:

Этот код реализует относительно простой алгоритм оптимизации светофора. Он считывает данные о транспортном потоке, текущее время сигнала, требования к пешеходам и ограничения из внешних файлов. Затем он проходит по каждому перекрестку, корректирует время зеленого света на основе коэффициентов потока движения и обеспечивает соответствие полученного времени указанным ограничениям. Функция приоритета автобуса добавляет дополнительное время зеленого света в указанном направлении на указанном перекрестке. Затем возвращается обновленное время сигнала светофора.

Ключевые улучшения, которые следует учитывать:

Обнаружение автобусов: реализуйте фактическое обнаружение автобусов (например, с использованием данных транспортных агентств), чтобы активировать функцию приоритета автобусов только при их наличии.

Более сложная оптимизация: изучите более продвинутые алгоритмы оптимизации светофоров, например, основанные на длине очереди, времени в пути или машинном обучении.

Динамическая настройка:   сделать систему динамической, регулируя время работы светофоров в реальном времени в зависимости от меняющихся условий дорожного движения. Для этого потребуется непрерывный поток данных о дорожном движении.

Координация между перекрестками: рассмотрите возможность координации времени работы светофоров на соседних перекрестках, чтобы создать «зеленые волны», обеспечивающие бесперебойное движение транспорта.

Обработка ошибок: добавьте более надежную обработку ошибок для случаев, когда входные файлы отсутствуют, неправильно отформатированы или содержат недопустимые данные.

Данные по полосам: если возможно, используйте данные о транспортном потоке по полосам, чтобы оптимизировать время движения по отдельным полосам.

Корректировка времени суток:   создавайте разные наборы flows_peak.csvфайлов для разного времени суток (например, утренний пик, дневной пик, непиковый период), чтобы лучше отражать меняющиеся схемы движения.

