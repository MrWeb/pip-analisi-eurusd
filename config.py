import pandas as pd
import os

# Configurazione delle variabili
file_name = 'GBPJPY.csv'
start_time = '14:00:00' # GMT
end_time = '18:00:00' # GMT
pip_factor = 0.01 # Da cambiare a seconda dello strumento

# Funzione per leggere il file
print(f"Lettura del file {file_name}...")
if os.path.exists(file_name):
    df = pd.read_csv(file_name)
# Se non esiste, prova a caricarlo da 'data/' + file_name
elif os.path.exists('data/' + file_name):
    df = pd.read_csv('data/' + file_name)
else:
    raise FileNotFoundError(f"\033[91mFile {file_name} non trovato ne qui né nella cartella 'data'\033[0m")

print(f"Analisi del file...")
df['Gmt time'] = pd.to_datetime(df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')
