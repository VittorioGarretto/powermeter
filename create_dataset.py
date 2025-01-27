import time
import csv
import pandas as pd

pd.options.display.float_format = "{:.4f}".format

data_df = pd.read_csv('data.csv')
labels_df = pd.read_csv('labels.csv')

indexes = list(data_df['timestamp'].apply(lambda target: (labels_df['timestamp'] - target).abs().idxmin()))

y_train = {'gpu_power': [], 'timestamp': []}
y_train_df = pd.DataFrame(y_train)

y_train_df = y_train_df.assign(timestamp=labels_df.loc[indexes, 'timestamp'])
y_train_df = y_train_df.assign(gpu_power=labels_df.loc[indexes, 'gpu_power'])

print(y_train_df, '\n',  data_df)

# Convert then the dataframes in torch/tf tensors

## Output ##
#     gpu_power       timestamp
#127    11.1700 1737997546.1713
#142    11.0500 1737997547.2067
#206    11.0900 1737997551.5728
#286    10.1100 1737997556.5911
#378    10.1400 1737997561.5631
#450    11.2800 1737997566.5725 

#    ac_frequency  current  device_temperature  energy  linkquality  power  ...  ram_power  nvme_power  storage_power  nic_power  cpu_power       timestamp
#0            50   1.0100                  33 26.4200          216    198  ...    29.3606      0.0000         9.1344    70.4050   102.3271 1737997546.1566
#1            50   1.0000                  33 26.4200          216    196  ...    29.4310      0.0000         9.1563    70.5738   101.1118 1737997547.1937
#2            50   1.0300                  33 26.4200          216    202  ...    29.2271      0.0000         9.0929    70.0849    96.8175 1737997551.5817
#3            50   1.0000                  33 26.4200          216    197  ...    29.3958      0.0000         9.1453    70.4893    98.3778 1737997556.5856
#4            50   1.0200                  33 26.4200          216    198  ...    29.3606      0.0000         9.1344    70.4050   100.4350 1737997561.5900
#5            50   1.0100                  33 26.4200          216    199  ...    29.3255      0.0000         9.1235    70.3209   104.3337 1737997566.5953
