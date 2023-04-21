import csv
import pandas as pd
from html import unescape

TOTAL_SAMPLES = 50

df = pd.read_csv('../dados/amostra.csv')
df['parte_nome'] = df['parte_nome'].apply(str).apply(unescape)

percent = 1 / 100
num_rows = round(len(df) * percent)

for SAMPLE in range(6, TOTAL_SAMPLES + 1):
    sample_data = df.sample(n=num_rows, random_state=SAMPLE)
    sample_data.to_csv(f'../dados/amostra.sample.{SAMPLE}.csv', index=False, encoding='utf-8', quotechar='"',
                       quoting=csv.QUOTE_NONNUMERIC)
