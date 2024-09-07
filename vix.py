import pandas as pd
from config import df, file_name, start_time, end_time, pip_factor
import os

# Leggi il file vix.csv e assicurati che la colonna 'Gmt time' sia in formato datetime
if os.path.exists('vix.csv'):
    vix_df = pd.read_csv('vix.csv', parse_dates=['Gmt time'])
# Se non esiste, prova a caricarlo da 'data/' + file_name
elif os.path.exists('data/vix.csv'):
    vix_df = pd.read_csv('data/vix.csv', parse_dates=['Gmt time'])
else:
    raise FileNotFoundError(f"\033[91mFile vix.csv non trovato ne qui né nella cartella 'data'\033[0m")

vix_df['Gmt time'] = pd.to_datetime(vix_df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')

# Filtra orario start e end
df['Gmt time'] = pd.to_datetime(df['Gmt time'])
df_start = df[df['Gmt time'].dt.time == pd.to_datetime(start_time).time()]
df_end = df[df['Gmt time'].dt.time == pd.to_datetime(end_time).time()]

# Aggiungi una colonna per il giorno della settimana
df_start['Weekday'] = df_start['Gmt time'].dt.day_name()

# Inizializza dizionari per le statistiche
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
day_stats = {day: {'bullish_count': 0, 'bearish_count': 0, 'total_count': 0, 'vix_score_sum': 0} for day in days}
bullish_pip_sum = {day: 0 for day in days}
bearish_pip_sum = {day: 0 for day in days}

# Variabili per la percentuale più alta
highest_percentage = -1
highest_percentage_day = None

missing_vix_days = 0
vix_score_total = 0
vix_count = 0

# Assicuriamoci che ci siano candele sia per lo start time sia per l'end time di quel giorno
for index, row_open in df_start.iterrows():
    open_time = row_open['Gmt time']
    open_price = row_open['Open']
    weekday = row_open['Weekday']

    same_day_end = df_end[df_end['Gmt time'].dt.date == open_time.date()]
    if same_day_end.empty:
        print(f"GMT: {open_time} - Candela di chiusura mancante. VIX O: {vix_open_price if 'vix_open_price' in locals() else 'missing'}, VIX C: {vix_close_price if 'vix_close_price' in locals() else 'missing'}.")
        continue

    close_price = same_day_end.iloc[0]['Close']
    vix_open_value = vix_df[(vix_df['Gmt time'].dt.date == open_time.date()) & (vix_df['Gmt time'].dt.time == open_time.time())]['Open']
    vix_close_value = vix_df[(vix_df['Gmt time'].dt.date == open_time.date()) & (vix_df['Gmt time'].dt.time == same_day_end.iloc[0]['Gmt time'].time())]['Close']

    vix_open_price = vix_open_value.iloc[0] if not vix_open_value.empty else None
    vix_close_price = vix_close_value.iloc[0] if not vix_close_value.empty else None

    if vix_open_price == vix_close_price:
        vix_open_price = None

    if not same_day_end.empty:
        pips_difference = (close_price - open_price) / pip_factor

        if pips_difference != 0:
            if close_price > open_price:
                result = "\033[92mBULLISH\033[0m"
                day_stats[weekday]['bullish_count'] += 1
                bullish_pip_sum[weekday] += pips_difference
            else:
                result = "\033[91mBEARISH\033[0m"
                bearish_pip_sum[weekday] += pips_difference
                day_stats[weekday]['bearish_count'] += 1

            day_stats[weekday]['total_count'] += 1

            if vix_open_price is not None and vix_close_price is not None:
                vix_score = -1 if (close_price > open_price) == (vix_close_price > vix_open_price) else 1 if (close_price > open_price) != (vix_close_price > vix_open_price) else 0
                day_stats[weekday]['vix_score_sum'] += vix_score
                vix_score_total += vix_score
                vix_count += 1

                print(f"[{result}]: {open_time.strftime('%d/%m/%Y %H:%M')} - {same_day_end.iloc[0]['Gmt time'].strftime('%d/%m/%Y %H:%M')} (GMT): O: {open_price}, C: {close_price}, pips: {pips_difference:.1f} - VIX O: {vix_open_price}, VIX C: {vix_close_price}, VIX Score: {vix_score}")
            else:
                missing_vix_days += 1
                print(f"[{result}]: {open_time.strftime('%d/%m/%Y %H:%M')} - {same_day_end.iloc[0]['Gmt time'].strftime('%d/%m/%Y %H:%M')} (GMT): O: {open_price}, C: {close_price}, Pips: {pips_difference:.1f} - VIX data missing.")
        else:
            if vix_open_price is not None and vix_close_price is not None:
                print(f"[SKIP]: {open_time.strftime('%d/%m/%Y %H:%M')} - {same_day_end.iloc[0]['Gmt time'].strftime('%d/%m/%Y %H:%M')} (GMT) - Differenza pip pari a zero. VIX O: {vix_open_price}, VIX C: {vix_close_price}.")
            else:
                print(f"[SKIP]: {open_time.strftime('%d/%m/%Y %H:%M')} - {same_day_end.iloc[0]['Gmt time'].strftime('%d/%m/%Y %H:%M')} (GMT) - Differenza pip pari a zero. VIX non si è mosso.")
    else:
        print(f"GMT: {open_time} - Candela di chiusura mancante. VIX O: {vix_open_price if 'vix_open_price' in locals() else 'missing'}, VIX C: {vix_close_price if 'vix_close_price' in locals() else 'missing'}.")

# Stampa il resoconto settimanale
print(f"\nResoconto settimanale per file \033[93m{file_name}\033[0m fascia oraria \033[93m{start_time}-{end_time}\033[0m:")

if file_name == 'vix.csv':
    print(f"\033[93mATTENZIONE: STAI CONFRONTANDO IL VIX CON IL VIX STESSO, I DATI SONO CORRETTI MA I PUNTEGGI VIX VANNO IGNORATI \033[0m")

total_count = sum(stats['total_count'] for stats in day_stats.values())

for day, stats in day_stats.items():
    if stats['total_count'] > 0:
        bullish_percentage = (stats['bullish_count'] / stats['total_count']) * 100
        bearish_percentage = (stats['bearish_count'] / stats['total_count']) * 100

        bullish_pip_avg = bullish_pip_sum[day] / stats['bullish_count'] if stats['bullish_count'] > 0 else 0
        bearish_pip_avg = bearish_pip_sum[day] / stats['bearish_count'] if stats['bearish_count'] > 0 else 0

        vix_score_avg = stats['vix_score_sum'] / stats['total_count']

        extraordinary = abs(bullish_percentage - bearish_percentage) > 29
        prefix = "🎉" if extraordinary else ""

        if bullish_percentage > bearish_percentage:
            print(f"{day}: \033[92m{bullish_percentage:.2f}% Bullish\033[0m [{bullish_pip_avg:.2f} pip] • punteggio VIX: {stats['vix_score_sum']:.2f}, media VIX: {vix_score_avg:.2f} {prefix}")
            if bullish_percentage > highest_percentage:
                highest_percentage = bullish_percentage
                highest_percentage_day = day
                highest_action = f"\033[92m{highest_percentage_day}: BUY at {start_time} close at {end_time} GMT\033[0m"
        else:
            print(f"{day}: \033[91m{bearish_percentage:.2f}% Bearish\033[0m [{bearish_pip_avg:.2f} pip] • punteggio VIX: {stats['vix_score_sum']:.2f}, media VIX: {vix_score_avg:.2f} {prefix}")
            if bearish_percentage > highest_percentage:
                highest_percentage = bearish_percentage
                highest_percentage_day = day
                highest_action = f"\033[91m{highest_percentage_day}: SELL at {start_time} close at {end_time} GMT\033[0m"
    else:
        print(f"{day}: Nessun dato valido trovato.")

if highest_percentage_day:
    print(f"\n{highest_action}")

if missing_vix_days > 0:
    print(f"\033[93mVIX assente in alcuni giorni: {missing_vix_days} ({missing_vix_days / total_count * 100:.2f}% dei dati analizzati senza VIX)\033[0m")

if total_count > 0:
    years = total_count / (20 * 12)
    print(f"\nTotale giorni analizzati: {total_count} ({years:.2f} anni)")
else:
    print("\nNessun dato valido trovato.")
