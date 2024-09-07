import pandas as pd

# Configurazione delle variabili
file_name = 'CHFJPY.csv'
start_time = '13:00:00' # GMT
end_time = '19:00:00' # GMT
pip_factor = 0.01 # Da cambiare a seconda dello strumento

# Funzione per leggere il file
print(f"Lettura del file {file_name}...")
df = pd.read_csv(file_name)
print(f"Analisi del file...")
df['Gmt time'] = pd.to_datetime(df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')
