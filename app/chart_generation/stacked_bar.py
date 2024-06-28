from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from textwrap import wrap

def bucket_data(raw_data, days, max_bars=12):
    raw_data['date'] = [d.to_pydatetime().date() for d in raw_data['timestamp']]
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    filtered_data = raw_data[(raw_data['date'] >= start_date) & (raw_data['date'] <= end_date)]
    
    if len(filtered_data) == 1:
        filtered_data['bucket'] = 0
        bucket_labels = [f"{filtered_data['date'].iloc[0].strftime('%m/%d')}"]
        sorted_data = filtered_data.groupby(['bucket', 'usage_type'])['amount'].sum().reset_index()
        sorted_data = sorted_data.pivot_table(index='bucket', columns='usage_type', values='amount', fill_value=0)
        return sorted_data, bucket_labels
    
    min_date = min(filtered_data['date'])
    max_date = max(filtered_data['date'])
    
    date_range = (max_date - min_date).days
    
    bucket_size = max(1, date_range // max_bars) # integer division because no decimal dates
    
    filtered_data['bucket'] = (filtered_data['date'] - min_date).apply(lambda x: x.days // bucket_size) # calculate bucket for each data point
    filtered_data.loc[filtered_data['bucket'] >= max_bars, 'bucket'] = max_bars - 1 # counteract small last bucket
    
    # Print the number of entries in each bucket
    # print("len(filtered_data['bucket'] == 0):", len(filtered_data[filtered_data['bucket'] == 0]))
    # print("len(filtered_data['bucket'] == 1):", len(filtered_data[filtered_data['bucket'] == 1]))
    # print("len(filtered_data['bucket'] == 2):", len(filtered_data[filtered_data['bucket'] == 2]))
    # print("len(filtered_data['bucket'] == 3):", len(filtered_data[filtered_data['bucket'] == 3]))
    # print("len(filtered_data['bucket'] == 4):", len(filtered_data[filtered_data['bucket'] == 4]))
    # print("len(filtered_data['bucket'] == 5):", len(filtered_data[filtered_data['bucket'] == 5]))
    # print("len(filtered_data['bucket'] == 6):", len(filtered_data[filtered_data['bucket'] == 6]))
    # print("len(filtered_data['bucket'] == 7):", len(filtered_data[filtered_data['bucket'] == 7]))
    # print("len(filtered_data['bucket'] == 8):", len(filtered_data[filtered_data['bucket'] == 8]))
    # print("len(filtered_data['bucket'] == 9):", len(filtered_data[filtered_data['bucket'] == 9]))
    # print("len(filtered_data['bucket'] == 10):", len(filtered_data[filtered_data['bucket'] == 10]))
    # print("len(filtered_data['bucket'] == 11):", len(filtered_data[filtered_data['bucket'] == 11]))
    
    # print("filtered_data['bucket'].head():")
    # print(filtered_data['bucket'].head())
    
    bucket_labels = []
    for i in range(max_bars):
        start_date = min_date + pd.Timedelta(days=i * bucket_size)
        end_date = min_date + pd.Timedelta(days=(i + 1) * bucket_size - 1)
        if i == max_bars - 1:
            end_date = max_date
        bucket_labels.append(f"{start_date.strftime('%m/%d')} to {end_date.strftime('%m/%d')}")

    
    sorted_data = filtered_data.groupby(['bucket', 'usage_type'])['amount'] # bucket the data with buckets, and then within those buckets, bucket the data by usage type
    
    sorted_data = sorted_data.sum() # sum the amount in each usage type for each bucket
    
    sorted_data = sorted_data.reset_index() # add buckets and usage types back as columns
    
    # sorted_data = sorted_data.fillna(0) # fill NaN values with 0 so that there are no errors after pivoting
    
    # sorted_data = sorted_data.pivot(index='bucket', columns='usage_type', values='time_spent') # pivot the data so that each usage type is a column
    
    sorted_data = sorted_data.pivot_table(index='bucket', columns='usage_type', values='amount', fill_value=0) # pivot the data so that each usage type is a column
    
    return sorted_data, bucket_labels

def save_chart(chart_data, bucket_labels, type, user_id):
    chart = chart_data.plot(kind='bar', stacked=True)
    
    # configure chart
    plt.title('Water Usage by Date and Type')
    plt.xlabel('Date')
    plt.ylabel('Water Usage (Liters)')
    plt.xticks(ticks=range(len(bucket_labels)), labels=bucket_labels, rotation=45) # use special date bucket labels
    plt.subplots_adjust(bottom=0.25) # make room for x-axis labels
    plt.legend(title='Usage Type', loc='upper right')
    
    chart_path = f'app/static/charts/personal_{user_id}_{str(datetime.now().date())}_{type}.png'
    
    plt.savefig(chart_path)
    plt.close('all')
    
    return chart_path.replace('static/', '')

def plot_usage_bars(json_path, max_bars=12):
    raw_data = pd.read_json(json_path)
    chart_data, bucket_labels = bucket_data(raw_data, max_bars)
    
    # print(chart_data.columns)
    
    save_chart(chart_data, bucket_labels)
    
if __name__ == '__main__':
    plot_usage_bars('test_data.json')