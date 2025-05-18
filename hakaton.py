import pandas as pd
import json

def adjust_traffic_lights(flows_file, signals_file, pedestrian_file, constraints_file):

    # Load data
    flows = pd.read_csv(flows_file)
    signals = pd.read_csv(signals_file)
    with open(constraints_file, 'r') as f:
        constraints = json.load(f)

    # Extract pedestrian green time
    with open(pedestrian_file, 'r') as f:
        pedestrian_line = f.readline()
        pedestrian_green_sec = int(pedestrian_line.split(': ')[1].split(' ')[0]) #or constraints['pedestrian_green_sec']
    # Global constraints
    min_cycle_sec = constraints['min_cycle_sec']
    max_cycle_sec = constraints['max_cycle_sec']
    min_green_sec = constraints['min_green_sec']
    lost_time_sec_per_phase = constraints['lost_time_sec_per_phase']

    #Bus priority (handling optional presence)
    bus_priority = constraints.get('bus_priority')  # Use .get() to handle missing key gracefully

    # Adjust cycle and green times for each intersection
    for index, row in signals.iterrows():
        intersection_id = row['intersection_id']
        cycle_sec = row['cycle_sec']
        green_main_sec = row['green_main_sec']
        green_secondary_sec = row['green_secondary_sec']

        # Filter flows for the current intersection
        intersection_flows = flows[flows['intersection_id'] == intersection_id]

        # Calculate total intensity for main and secondary directions
        main_directions = ['N', 'S']  # Example, adjust based on your road network
        secondary_directions = ['E', 'W'] # Example, adjust based on your road network

        main_intensity = intersection_flows[intersection_flows['approach'].isin(main_directions)]['intensity_veh_per_hr'].sum()
        secondary_intensity = intersection_flows[intersection_flows['approach'].isin(secondary_directions)]['intensity_veh_per_hr'].sum()

        total_intensity = main_intensity + secondary_intensity

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

    return signals

# Example Usage
flows_file = 'flows_peak.csv'
signals_file = 'signals_current.csv'
pedestrian_file = 'pedestrian_req.txt'
constraints_file = 'constraints.json'

updated_signals = adjust_traffic_lights(flows_file, signals_file, pedestrian_file, constraints_file)
print(updated_signals)
