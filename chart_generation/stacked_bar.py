import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from textwrap import wrap

def bucket_data(raw_data, max_bars=12):
    raw_data['date'] = [d.to_pydatetime().date() for d in raw_data['date']]
    print(raw_data['date'].head())
    
    min_date = min(raw_data['date'])
    max_date = max(raw_data['date'])
    print(f"min_date: {min_date}")
    
    date_range = (max_date - min_date).days
    print(f"date_range: {date_range}")
    
    bucket_size = max(1, date_range // max_bars) # integer division because no decimal dates
    print(f"bucket_size: {bucket_size}")
    
    raw_data['bucket'] = (raw_data['date'] - min_date).apply(lambda x: x.days // bucket_size) # calculate bucket for each data point
    raw_data.loc[raw_data['bucket'] >= max_bars, 'bucket'] = max_bars - 1 # counteract small last bucket
    
    # Print the number of entries in each bucket
    print("len(raw_data['bucket'] == 0):", len(raw_data[raw_data['bucket'] == 0]))
    print("len(raw_data['bucket'] == 1):", len(raw_data[raw_data['bucket'] == 1]))
    print("len(raw_data['bucket'] == 2):", len(raw_data[raw_data['bucket'] == 2]))
    print("len(raw_data['bucket'] == 3):", len(raw_data[raw_data['bucket'] == 3]))
    print("len(raw_data['bucket'] == 4):", len(raw_data[raw_data['bucket'] == 4]))
    print("len(raw_data['bucket'] == 5):", len(raw_data[raw_data['bucket'] == 5]))
    print("len(raw_data['bucket'] == 6):", len(raw_data[raw_data['bucket'] == 6]))
    print("len(raw_data['bucket'] == 7):", len(raw_data[raw_data['bucket'] == 7]))
    print("len(raw_data['bucket'] == 8):", len(raw_data[raw_data['bucket'] == 8]))
    print("len(raw_data['bucket'] == 9):", len(raw_data[raw_data['bucket'] == 9]))
    print("len(raw_data['bucket'] == 10):", len(raw_data[raw_data['bucket'] == 10]))
    print("len(raw_data['bucket'] == 11):", len(raw_data[raw_data['bucket'] == 11]))
    
    print("raw_data['bucket'].head():")
    print(raw_data['bucket'].head())
    
    bucket_labels = []
    for i in range(max_bars):
        start_date = min_date + pd.Timedelta(days=i * bucket_size)
        end_date = min_date + pd.Timedelta(days=(i + 1) * bucket_size - 1)
        if i == max_bars - 1:
            end_date = max_date
        bucket_labels.append(f"{start_date} to {end_date}")

    
    sorted_data = raw_data.groupby(['bucket', 'usage_type'])['time_spent'] # bucket the data with buckets, and then within those buckets, bucket the data by usage type
    
    sorted_data = sorted_data.sum() # sum the amount in each usage type for each bucket
    
    sorted_data = sorted_data.reset_index() # add buckets and usage types back as columns
    
    # sorted_data = sorted_data.fillna(0) # fill NaN values with 0 so that there are no errors after pivoting
    
    # sorted_data = sorted_data.pivot(index='bucket', columns='usage_type', values='time_spent') # pivot the data so that each usage type is a column
    
    sorted_data = sorted_data.pivot_table(index='bucket', columns='usage_type', values='time_spent', fill_value=0) # pivot the data so that each usage type is a column
    
    return sorted_data, bucket_labels

def make_chart(chart_data, bucket_labels):
    chart = chart_data.plot(kind='bar', stacked=True)
    
    # configure chart
    plt.title('Water Usage by Date and Type')
    plt.xlabel('Date')
    plt.ylabel('Water Usage (Liters)')
    plt.xticks(ticks=range(len(bucket_labels)), labels=bucket_labels, rotation=45) # use special date bucket labels
    plt.legend(title='Usage Type', loc='upper right')
    
    plt.show()

def plot_usage_bars(json_path, max_bars=12):
    raw_data = pd.read_json(json_path)
    chart_data, bucket_labels = bucket_data(raw_data, max_bars)
    
    print(chart_data.columns)
    
    make_chart(chart_data, bucket_labels)
    
plot_usage_bars('test_data.json')