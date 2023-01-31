#!/usr/bin/python3
import json
import numpy  as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')

# Use TkAgg backend for matplotlib
# This will make sure that charts are rendered properly on some systems
matplotlib.use('TkAgg')

# Read the glider JSON data
DATA_FILE = '../data/up_kibo_sm.json'
glider_json         = json.load(open(DATA_FILE, 'r'))
glider_measurements = glider_json['measurements']

# Define pandas data structure
data = {'expected': {}, 'measured': {}}

# Loop through each riser and its data in glider_measurements
for riser, riser_data in glider_measurements.items():
    # For each riser, process the measurements for each side
    for side in ["expected", "right", "left"]:
        for i in reversed(range(1, len(glider_measurements[riser][side]) + 1)):
            # print('Processing %s measurements (%s%s)' % (side, riser, i))
            # Extract the measurement
            measure = glider_measurements[riser][side][str(i)]
            
            # Add expected data (only half, mirrored later)
            if side == 'expected':
                # Set keys for the risers if they're missing
                if riser not in data['expected'].keys():
                    data['expected'][riser] = []
                    data['measured'][riser] = []

                # Append the expected measurements for the left side, they'll be
                # mirrored afterwards
                data[side][riser].append(measure)
                continue

            if side == 'left':
                # Add the elements at the end of the right side
                n_measures = len(glider_measurements[riser][side])
                data['measured'][riser].insert(n_measures, measure)
                continue

            # Add the right side measurements
            data['measured'][riser].append(measure)

        # Mirror and append left side expected measurements       
        if side == 'expected':
            data[side][riser].extend(data[side][riser][::-1])


# Create a data frame
df = pd.DataFrame(data)

# Compute the difference between the measured and expected data
df['diff'] = df.apply(lambda x: np.array(x['measured']) - np.array(x['expected']), axis=1)

# Pad the data to ensure all rows have the same length
for df_row in ['measured', 'diff', 'expected']:
    # Find the longest row in the data frame
    max_len = max(len(row) for row in df[df_row].values)

    # Find the sum of all row lengths
    sum_len = sum(len(row) for row in df[df_row].values)

    # Find the average value of all elements
    average = sum(sum(row) for row in df[df_row].values) / sum_len

    # Choose the appropriate value to use when padding
    rep_val = 0 if df_row == 'diff' else average

    # Pad each row in the data frame
    for riser, row in df[df_row].items():
        # Calculate how much padding is necessary
        diff_len = max_len - len(row)

        # Append and/or insert padding elements as needed
        for i in range(0, diff_len//2):
            df[df_row][riser] = np.append(df[df_row][riser], rep_val)
            df[df_row][riser] = np.insert(df[df_row][riser], 0, rep_val)


# Stacking the 'expected', 'measured', and 'diff' columns from the 'df' dataframe
nump = {} 
nump['expected'] = np.stack(df['expected'].values)
nump['measured'] = np.stack(df['measured'].values)
nump['diff']     = np.stack(df['diff'].values)

# Plotting a 3-Row subplot based on the values in 'nump'
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(9, 6), subplot_kw={'xticks': [], 'yticks': []})

# Iterating through each of the subplots
for ax, chart in zip(axs.flat, nump):
    # Get the specified chart from the nump dict and display it 
    ax.imshow(nump[chart], interpolation='lanczos', cmap='RdYlGn')
    # Add the title for each chart
    ax.set_title(str(chart))

plt.show()