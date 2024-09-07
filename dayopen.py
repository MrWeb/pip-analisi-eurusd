import pandas as pd
import time
from config import df, file_name, start_time, end_time, pip_factor

# Filtro orario start
df_start = df[df['Gmt time'].dt.time == pd.to_datetime(start_time).time()]
# Filtro orario end
df_end = df[df['Gmt time'].dt.time == pd.to_datetime(end_time).time()]

# Contatori per BULLISH e BEARISH
bullish_count = 0
bearish_count = 0
total_count = 0

# Somma dei pip per BULLISH e BEARISH
bullish_pip_sum = 0
bearish_pip_sum = 0

# Numero di giorni lavorativi in un anno
trading_days_per_year = 20 * 12  # 20 giorni al mese per 12 mesi

# Assicuriamoci che ci siano candele sia per lo start time sia per l'end time di quel giorno
for index, row_open in df_start.iterrows():
    # Estrai il prezzo di apertura
    open_price = row_open['Open']
    open_time_formatted = row_open['Gmt time'].strftime('%d/%m/%Y %H:%M')
    open_time_formatted_time_only = row_open['Gmt time'].strftime('%H:%M')

    # Trova la candela corrispondente di chiusura nello stesso giorno
    same_day_end = df_end[df_end['Gmt time'].dt.date == row_open['Gmt time'].date()]

    if not same_day_end.empty:
        # Estrai il prezzo di chiusura delle 14:00
        close_price = same_day_end.iloc[0]['Close']
        close_time_formatted = same_day_end.iloc[0]['Gmt time'].strftime('%d/%m/%Y %H:%M')
        close_time_formatted_time_only = same_day_end.iloc[0]['Gmt time'].strftime('%H:%M')

        # Calcola la differenza in pips
        pips_difference = (close_price - open_price) / pip_factor

        # Considera solo i giorni con differenza di pips non zero
        if pips_difference != 0:
            # Determina se la candela end è "BULLISH" o "BEARISH"
            if close_price > open_price:
                result = "\033[92mBULLISH\033[0m"
                bullish_count += 1
                bullish_pip_sum += pips_difference
            else:
                result = "\033[91mBEARISH\033[0m"
                bearish_count += 1
                bearish_pip_sum += pips_difference

            total_count += 1

            # Stampa il risultato
            print(f"[{result}]: {open_time_formatted} - {close_time_formatted} (GMT): O: {open_price}, C: {close_price}, Pips: {pips_difference:.1f}")
        else:
            # Nel caso in cui la differenza di pip sia zero
            print(f"[SKIP]: {open_time_formatted} - {close_time_formatted} (GMT) - Differenza pip pari a zero.")
    else:
        # Nel caso in cui manchi la candela di chiusura per quel giorno
        print(f"GMT: {row_open['Gmt time']} - Candela di chiusura mancante.")

# Calcolo delle percentuali e delle medie pip
if total_count > 0:
    bullish_percentage = (bullish_count / total_count) * 100
    bearish_percentage = (bearish_count / total_count) * 100

    # Media dei pips
    if bullish_count > 0:
        bullish_pip_avg = bullish_pip_sum / bullish_count
    else:
        bullish_pip_avg = 0

    if bearish_count > 0:
        bearish_pip_avg = bearish_pip_sum / bearish_count
    else:
        bearish_pip_avg = 0

    # Calcolo degli anni
    years = total_count / trading_days_per_year

    # Stampa le percentuali, le medie dei pips e gli anni

    print(f"")
    print(f"\nResoconto settimanale per file \033[93m{file_name}\033[0m fascia oraria \033[93m{open_time_formatted_time_only}-{close_time_formatted_time_only}\033[0m:")
    print(f"\033[92m{bullish_percentage:.2f}% Bullish\033[0m [{bullish_pip_avg:.2f} pips]")
    print(f"\033[91m{bearish_percentage:.2f}% Bearish\033[0m [{bearish_pip_avg:.2f} pips]")
else:
    print("\nNessuna candela valida trovata.")

print(f"\nTotale giorni analizzati: {total_count} ({years:.2f} anni)")
