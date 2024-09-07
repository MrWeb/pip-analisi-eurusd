import pandas as pd

# Configurazione delle variabili
file_name = 'eurusd.csv'
start_time = '13:30:00'
end_time = '14:00:00'
pip_factor = 0.0001

# Funzione per leggere il file
print(f"Lettura del file {file_name}...")
df = pd.read_csv(file_name)
print(f"Analisi del file...")
df['Gmt time'] = pd.to_datetime(df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')
