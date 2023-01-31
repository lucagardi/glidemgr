#!/usr/bin/python3
import json
import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def mirror(seq):
    output = list(seq[::-1])
    output.extend(seq[1:])
    return output
    
DATA_FILE = '../data/up_kibo_sm.json'

glider_json         = json.load(open(DATA_FILE, 'r'))
glider_measurements = glider_json['measurements']
# pretty-print the data 
# print(json.dumps(glider_json, indent=4, sort_keys=True))

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
# Calculate diff
df['diff'] = df.apply(lambda x: np.array(x['measured']) - \
                                np.array(x['expected']), axis=1)
# print(df)

# print(df[['expected', 'measured']].values)
max_len = max(len(row) for row in df['diff'].values)

for riser, row in df['diff'].items():
    diff_len = max_len - len(row)
    print(diff_len, riser, row)
    for i in range(0, diff_len//2):
        print('insert in %s' % riser)
        df['diff'][riser] = np.append(df['diff'][riser], 0)
        df['diff'][riser] = np.insert(df['diff'][riser], 0, 0)
    print(diff_len, riser, row)

print(df.values)

# import plotly.graph_objects as go
# feature_x = np.arange(0, 50, 2)
# feature_y = np.arange(0, 50, 3)
  
# # Creating 2-D grid of features
# [X, Y] = np.meshgrid(feature_x, feature_y)
  
# Z = np.cos(X / 2) + np.sin(Y / 4)
  
# fig = go.Figure(data=go.Heatmap(
#   x=feature_x, y=feature_y, z=Z,))
  
# fig.update_layout(
#     margin=dict(t=200, r=200, b=200, l=200),
#     showlegend=False,
#     width=700, height=700,
#     autosize=False)
  
  
# fig.show()