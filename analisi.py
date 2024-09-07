import pandas as pd

print(f"Lettura file...")

df = pd.read_csv('input.csv')

# Converto 'Gmt time' in datetime
df['Gmt time'] = pd.to_datetime(df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')

start_time = '13:30:00'
end_time = '14:00:00'

# Filtro orario start
df_start = df[df['Gmt time'].dt.time == pd.to_datetime(start_time).time()]
# Filtro orario end
df_end = df[df['Gmt time'].dt.time == pd.to_datetime(end_time).time()]

# Contatori per BULLISH e BEARISH
bullish_count = 0
bearish_count = 0
total_count = 0

# Assicuriamoci che ci siano candele sia per lo start time sia per l'end time di quel giorno
for index, row_open in df_start.iterrows():
    # Estrai il prezzo di apertura
    open_price = row_open['Open']

    # Trova la candela corrispondente di chiusura nello stesso giorno
    same_day_end = df_end[df_end['Gmt time'].dt.date == row_open['Gmt time'].date()]

    if not same_day_end.empty:
        # Estrai il prezzo di chiusura delle 14:00
        close_price = same_day_end.iloc[0]['Close']

        # Determina se la candela end è "BULLISH" o "BEARISH"
        if close_price > open_price:
            result = "BULLISH"
            bullish_count += 1
        else:
            result = "BEARISH"
            bearish_count += 1

        total_count += 1

        # Stampa il risultato
        print(f"GMT: {row_open['Gmt time']}: [{result}] • O: {open_price}, C: {close_price}")
    else:
        # Nel caso in cui manchi la candela di chiusura per quel giorno
        print(f"GMT: {row_open['Gmt time']} - Candela di chiusura mancante.")

# Calcolo delle percentuali
if total_count > 0:
    bullish_percentage = (bullish_count / total_count) * 100
    bearish_percentage = (bearish_count / total_count) * 100

    # Stampa le percentuali
    print(f"\nTotale giorni analizzati: {total_count}")
    print(f"Percentuale Bullish: {bullish_percentage:.2f}%")
    print(f"Percentuale Bearish: {bearish_percentage:.2f}%")
else:
    print("\nNessuna candela valida trovata.")
