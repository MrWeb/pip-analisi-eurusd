import pandas as pd
import os
from datetime import time

# Configurazione delle variabili
file_name = 'GBPUSD240.csv'
start_time = time(0, 0)  # 00:00 GMT
end_time = time(20, 0)    # 20:00 GMT
pip_factor = 0.0001 # Da cambiare a seconda dello strumento

# Funzione per leggere il file
print(f"Lettura del file {file_name}...")
if os.path.exists(file_name):
    df = pd.read_csv(file_name, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
elif os.path.exists('data/' + file_name):
    df = pd.read_csv('data/' + file_name, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
else:
    raise FileNotFoundError(f"\033[91mFile {file_name} non trovato ne qui né nella cartella 'data'\033[0m")

# Combina le colonne Date e Time e converte in datetime
df['Gmt time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')

# Filtro orario start e end
df['hour'] = df['Gmt time'].dt.hour
df_filtered = df[(df['hour'] >= start_time.hour) & (df['hour'] <= end_time.hour)].copy()

# Aggiungi una colonna per il giorno della settimana
df_filtered.loc[:, 'Weekday'] = df_filtered['Gmt time'].dt.day_name()

# Inizializza dizionari per contare i bullish e bearish per ogni giorno della settimana
day_stats = {day: {'bullish_count': 0, 'bearish_count': 0, 'total_count': 0} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}

# Somma dei pip per BULLISH e BEARISH
bullish_pip_sum = {day: 0 for day in day_stats}
bearish_pip_sum = {day: 0 for day in day_stats}

# Numero di giorni lavorativi in un anno
trading_days_per_year = 20 * 12  # 20 giorni al mese per 12 mesi

# Variabili per tenere traccia della percentuale più alta
highest_percentage = -1
highest_percentage_day = None

# Inizializza le variabili per il formato dell'ora
open_time_formatted_time_only = start_time.strftime('%H:%M')
close_time_formatted_time_only = end_time.strftime('%H:%M')

# Assicuriamoci che ci siano candele sia per lo start time sia per l'end time di quel giorno
print("\nInizio del ciclo principale...")
for date, group in df_filtered.groupby(df_filtered['Gmt time'].dt.date):
    if len(group) >= 2:
        row_open = group.iloc[0]
        row_close = group.iloc[-1]

        open_price = row_open['Open']
        close_price = row_close['Close']
        weekday = row_open['Weekday']
        open_time_formatted = row_open['Gmt time'].strftime('%d/%m/%Y %H:%M')
        close_time_formatted = row_close['Gmt time'].strftime('%d/%m/%Y %H:%M')

        # Calcola la differenza in pips
        pips_difference = (close_price - open_price) / pip_factor

        # Considera solo i giorni con differenza di pips non zero
        if pips_difference != 0:
            # Determina se la candela end è "BULLISH" o "BEARISH"
            if close_price > open_price:
                result = "\033[92mBULLISH\033[0m"
                day_stats[weekday]['bullish_count'] += 1
                bullish_pip_sum[weekday] += pips_difference
            else:
                result = "\033[91mBEARISH\033[0m"
                bearish_pip_sum[weekday] += pips_difference
                day_stats[weekday]['bearish_count'] += 1

            day_stats[weekday]['total_count'] += 1

            # Stampa il risultato
            print(f"[{result}]: {open_time_formatted} - {close_time_formatted} (GMT): O: {open_price}, C: {close_price}, Pips: {pips_difference:.1f}")
        else:
            # Nel caso in cui la differenza di pip sia zero
            print(f"[SKIP]: {open_time_formatted} - {close_time_formatted} (GMT) - Differenza pip pari a zero.")
    else:
        # Nel caso in cui manchi la candela di chiusura per quel giorno
        print(f"[SKIP]: {date} - Dati insufficienti per l'analisi.")

# Stampa il resoconto settimanale
print(f"\nResoconto settimanale per file \033[93m{file_name}\033[0m fascia oraria \033[93m{open_time_formatted_time_only}-{close_time_formatted_time_only}\033[0m:")
total_count = 0  # Contatore totale per calcolare gli anni

for day in day_stats:
    stats = day_stats[day]
    if stats['total_count'] > 0:
        bullish_percentage = (stats['bullish_count'] / stats['total_count']) * 100
        bearish_percentage = (stats['bearish_count'] / stats['total_count']) * 100

        # Media dei pips
        bullish_pip_avg = bullish_pip_sum[day] / stats['bullish_count'] if stats['bullish_count'] > 0 else 0
        bearish_pip_avg = bearish_pip_sum[day] / stats['bearish_count'] if stats['bearish_count'] > 0 else 0

        # Somma il numero totale di giorni analizzati
        total_count += stats['total_count']

        # Differenza straordinaria
        diff = 29
        extraordinary = False
        if abs(bullish_percentage - bearish_percentage) > diff:
            extraordinary = True

        # Aggiungi l'asterisco se extraordinary è True
        prefix = "🎉" if extraordinary else ""

        # Stampa le percentuali e le medie dei pips
        if bullish_percentage > bearish_percentage:
            print(f"{day}: \033[92m{bullish_percentage:.2f}% Bullish\033[0m [{bullish_pip_avg:.2f} pip] {prefix}")
            # Aggiorna la percentuale più alta se necessario
            if bullish_percentage > highest_percentage:
                highest_percentage = bullish_percentage
                highest_percentage_day = day
                highest_action = f"\033[92m{highest_percentage_day}: BUY at {open_time_formatted_time_only} close at {close_time_formatted_time_only} GMT\033[0m"
        else:
            print(f"{day}: \033[91m{bearish_percentage:.2f}% Bearish\033[0m [{bearish_pip_avg:.2f} pip] {prefix}")
            # Aggiorna la percentuale più alta se necessario
            if bearish_percentage > highest_percentage:
                highest_percentage = bearish_percentage
                highest_percentage_day = day
                highest_action = f"\033[91m{highest_percentage_day}: SELL at {open_time_formatted_time_only} close at {close_time_formatted_time_only} GMT\033[0m"
    else:
        print(f"{day}: Nessun dato valido trovato.")

# Stampa il giorno con la percentuale più alta
if highest_percentage_day:
    print(f"\n{highest_action}")

# Calcolo degli anni e stampa finale
if total_count > 0:
    years = total_count / trading_days_per_year
    print(f"\033[93mTotale giorni analizzati: {total_count} ({years:.2f} anni) \033[0m\n")
else:
    print("\nNessun dato valido trovato.")
