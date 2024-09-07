import pandas as pd
from config import df, file_name, start_time, end_time, pip_factor

# Filtro orario start
df_start = df[df['Gmt time'].dt.time == pd.to_datetime(start_time).time()].copy()
# Filtro orario end
df_end = df[df['Gmt time'].dt.time == pd.to_datetime(end_time).time()].copy()

# Aggiungi una colonna per il giorno della settimana
df_start.loc[:, 'Weekday'] = df_start['Gmt time'].dt.day_name()

# Inizializza dizionari per contare i bullish e bearish per ogni giorno della settimana
day_stats = {day: {'bullish_count': 0, 'bearish_count': 0, 'total_count': 0} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}

# Somma dei pip per BULLISH e BEARISH
bullish_pip_sum = {day: 0 for day in day_stats}
bearish_pip_sum = {day: 0 for day in day_stats}

# Assicuriamoci che ci siano candele sia per lo start time sia per l'end time di quel giorno
for index, row_open in df_start.iterrows():
    # Estrai il prezzo di apertura
    open_price = row_open['Open']
    weekday = row_open['Weekday']

    # Trova la candela corrispondente di chiusura nello stesso giorno
    same_day_end = df_end[df_end['Gmt time'].dt.date == row_open['Gmt time'].date()]

    if not same_day_end.empty:
        # Estrai il prezzo di chiusura delle 14:00
        close_price = same_day_end.iloc[0]['Close']

        # Calcola la differenza in pips
        pips_difference = (close_price - open_price) / pip_factor

        # Considera solo i giorni con differenza di pips non zero
        if pips_difference != 0:
            # Determina se la candela end è "BULLISH" o "BEARISH"
            if close_price > open_price:
                result = "BULLISH"
                day_stats[weekday]['bullish_count'] += 1
                bullish_pip_sum[weekday] += pips_difference
            else:
                result = "BEARISH"
                bearish_pip_sum[weekday] += pips_difference
                day_stats[weekday]['bearish_count'] += 1

            day_stats[weekday]['total_count'] += 1

            # Stampa il risultato
            print(f"GMT: {row_open['Gmt time']}: [{result}] • O: {open_price}, C: {close_price}, Pips: {pips_difference:.1f}")
        else:
            # Nel caso in cui la differenza di pip sia zero
            print(f"GMT: {row_open['Gmt time']} - Differenza pip pari a zero.")
    else:
        # Nel caso in cui manchi la candela di chiusura per quel giorno
        print(f"GMT: {row_open['Gmt time']} - Candela di chiusura mancante.")

# Stampa il resoconto finale per ogni giorno della settimana
print("\nResoconto settimanale:")
for day in day_stats:
    stats = day_stats[day]
    if stats['total_count'] > 0:
        bullish_percentage = (stats['bullish_count'] / stats['total_count']) * 100
        bearish_percentage = (stats['bearish_count'] / stats['total_count']) * 100

        # Media dei pips
        bullish_pip_avg = bullish_pip_sum[day] / stats['bullish_count'] if stats['bullish_count'] > 0 else 0
        bearish_pip_avg = bearish_pip_sum[day] / stats['bearish_count'] if stats['bearish_count'] > 0 else 0

        # Stampa le percentuali e le medie dei pips
        print(f"-")
        print(f"{day}: Percentuale Bullish: {bullish_percentage:.2f}%, Media pip Bullish: {bullish_pip_avg:.2f}")
        print(f"{day}: Percentuale Bearish: {bearish_percentage:.2f}%, Media pip Bearish: {bearish_pip_avg:.2f}")
    else:
        print(f"{day}: Nessun dato valido trovato.")
