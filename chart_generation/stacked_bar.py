import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from textwrap import wrap

raw_data = pd.read_json('test_data.json')

# print(raw_data)

usage_type = raw_data.iloc[:, 0]
time_spent = raw_data.iloc[:, 1]
date = raw_data.iloc[:, 2]

usage_dict = {
    # 'date': {
    #   "usage_type": "sum_time_spent_for_usage_type"
    # }
}

for d in date:
    d = str(d)
    usage_dict[d] = {}
    # Filter the DataFrame for the given date and iterate over its rows.
    for index, r in raw_data[raw_data["date"] == d].iterrows():
        ut = r['usage_type']
        if ut in usage_dict[d]:
            usage_dict[d][ut] += r['time_spent']
        else:
            usage_dict[d][ut] = r['time_spent']

counter = 0
for day in date:
    day = str(day)
    if (day in usage_dict):
        for type in range(len(usage_dict[day][0])):
            if usage_type[counter] == usage_dict[day][0][type]:
                usage_dict[day][1][type] += time_spent[counter]
    counter += 1

plt.figure(figsize=(10,7))

total_height = 0
index = np.arange(len(usage_dict))

for day in usage_dict:
    day = str(day)
    for type in range(len(usage_dict[day][0])):
        graph = plt.bar(x = index, height = usage_dict[day][1][type], width = 0.4, bottom = total_height)
        total_height += usage_dict[day][1][type]

plt.xlabel('Day')
plt.ylabel('Water Usage')

plt.show()