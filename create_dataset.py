import pandas as pd
import numpy as np

# Data load
data_df = pd.read_csv('data/data_3060ti.csv')
labels_df = pd.read_csv('data/labels_3060ti.csv')

# Timestamp to float
data_df['timestamp'] = pd.to_numeric(data_df['timestamp'], errors='raise', downcast='float')
labels_df['timestamp'] = pd.to_numeric(labels_df['timestamp'], errors='raise', downcast='float')

data_timestamps = data_df['timestamp'].values
labels_timestamps = labels_df['timestamp'].values

idx = np.searchsorted(labels_timestamps, data_timestamps)
idx_before = np.clip(idx - 1, 0, len(labels_timestamps) - 1)
idx_after = np.clip(idx, 0, len(labels_timestamps) - 1)

mask = (np.abs(labels_timestamps[idx_after] - data_timestamps) <
        np.abs(labels_timestamps[idx_before] - data_timestamps))

closest_idx = np.where(mask, idx_after, idx_before)

y_train_df = labels_df.iloc[closest_idx]

y_train_df.to_csv('Y_train_3060ti.csv', sep=',', index=False, header=True)
data_df.to_csv('X_train_3060ti.csv', sep=',', index=False, header=True)