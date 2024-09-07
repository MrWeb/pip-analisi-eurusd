import pandas as pd
import time

file_name = 'eurusd.csv' # File da analizzare
start_time = '13:30:00' # Orario inizio
end_time = '14:00:00' # Orario fine
pip_factor = 0.0001 # Fattore pip (modifica questo valore in base allo strumento)

# Lettura file
print(f"Lettura del file...")
df = pd.read_csv(file_name)
print(f"Analisi del file in corso...")
time.sleep(1)

# Converto 'Gmt time' in datetime
df['Gmt time'] = pd.to_datetime(df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')

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
                bullish_count += 1
                bullish_pip_sum += pips_difference
            else:
                result = "BEARISH"
                bearish_count += 1
                bearish_pip_sum += pips_difference

            total_count += 1

            # Stampa il risultato
            print(f"GMT: {row_open['Gmt time']}: [{result}] • O: {open_price}, C: {close_price}, Pips: {pips_difference:.1f}")
        else:
            # Nel caso in cui la differenza di pip sia zero
            print(f"GMT: {row_open['Gmt time']} - Differenza pip pari a zero.")
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
    print(f"\nTotale giorni analizzati: {total_count} ({years:.2f} anni)")
    print(f"Percentuale Bullish: {bullish_percentage:.2f}%, Media pip Bullish: {bullish_pip_avg:.2f}")
    print(f"Percentuale Bearish: {bearish_percentage:.2f}%, Media pip Bearish: {bearish_pip_avg:.2f}")
else:
    print("\nNessuna candela valida trovata.")
