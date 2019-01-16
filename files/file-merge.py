import pandas as pd
import glob
import os
import datetime as dt
import time
import timing

# creates timestamp for filename
timestamp = dt.datetime.fromtimestamp(time.time()).strftime('%m-%d--%H-%M--')

# gets all .csv files from the output folder
path = r'C:\Users\jeffb\Documents\Python\webPrograms\webScraping\yt-stats\output'
files = glob.glob(os.path.join(path, "*.csv"))

# generates dataframes for every file in the output folder
# sort=False: prevents columns from being sorted A->Z
df_gen = (pd.read_csv(f) for f in files)
all_df = pd.concat(df_gen, ignore_index=True, sort=False)

# exports combined dataframes to a single csv
all_df.to_csv('output/' + timestamp + 'Combined-Stats.csv', index=False, encoding='utf-8-sig')
