import pandas as pd
from config import df, file_name, start_time, end_time, pip_factor

# Leggi il file vix.csv e assicurati che la colonna 'Gmt time' sia in formato datetime
vix_df = pd.read_csv('vix2.csv', parse_dates=['Gmt time'])
vix_df['Gmt time'] = pd.to_datetime(vix_df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')

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

# Numero di giorni lavorativi in un anno
trading_days_per_year = 20 * 12  # 20 giorni al mese per 12 mesi

# Variabili per tenere traccia della percentuale più alta
highest_percentage = -1
highest_percentage_day = None

missing_vix_days = 0

# Assicuriamoci che ci siano candele sia per lo start time sia per l'end time di quel giorno
for index, row_open in df_start.iterrows():
    # Estrai il prezzo di apertura
    open_price = row_open['Open']
    weekday = row_open['Weekday']
    open_time_formatted = row_open['Gmt time'].strftime('%d/%m/%Y %H:%M')
    open_time_formatted_time_only = row_open['Gmt time'].strftime('%H:%M')

    # Trova la candela corrispondente di chiusura nello stesso giorno
    same_day_end = df_end[df_end['Gmt time'].dt.date == row_open['Gmt time'].date()]

    # Trova il valore di apertura del VIX per la stessa ora e giorno
    vix_open_value = vix_df[
        (vix_df['Gmt time'].dt.date == row_open['Gmt time'].date()) &
        (vix_df['Gmt time'].dt.time == row_open['Gmt time'].time())
    ]['Open']
    vix_open_price = vix_open_value.iloc[0] if not vix_open_value.empty else None

    # Trova il valore di chiusura del VIX per la stessa data e ora di chiusura del prezzo
    vix_close_value = vix_df[
        (vix_df['Gmt time'].dt.date == row_open['Gmt time'].date()) &
        (vix_df['Gmt time'].dt.time == same_day_end.iloc[0]['Gmt time'].time())
    ]['Close']
    vix_close_price = vix_close_value.iloc[0] if not vix_close_value.empty else None

    # Imposta vix_open_price a None se apertura e chiusura sono uguali
    if vix_open_price is not None and vix_close_price is not None and vix_open_price == vix_close_price:
        vix_open_price = None

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
                day_stats[weekday]['bullish_count'] += 1
                bullish_pip_sum[weekday] += pips_difference
            else:
                result = "\033[91mBEARISH\033[0m"
                bearish_pip_sum[weekday] += pips_difference
                day_stats[weekday]['bearish_count'] += 1

            day_stats[weekday]['total_count'] += 1

            # Stampa il risultato con i valori di apertura e chiusura del VIX
            if vix_open_price is not None and vix_close_price is not None:
                print(f"[{result}]: {open_time_formatted} - {close_time_formatted} (GMT): O: {open_price}, C: {close_price}, VIX O: {vix_open_price}, VIX C: {vix_close_price}, Pips: {pips_difference:.1f}")
            else:
                missing_vix_days += 1
                print(f"[{result}]: {open_time_formatted} - {close_time_formatted} (GMT): O: {open_price}, C: {close_price}, Pips: {pips_difference:.1f} - VIX data missing.")
        else:
            # Nel caso in cui la differenza di pip sia zero
            if vix_open_price is not None and vix_close_price is not None:
                print(f"[SKIP]: {open_time_formatted} - {close_time_formatted} (GMT) - Differenza pip pari a zero. VIX O: {vix_open_price}, VIX C: {vix_close_price}.")
            else:
                print(f"[SKIP]: {open_time_formatted} - {close_time_formatted} (GMT) - Differenza pip pari a zero. VIX non si è mosso.")
    else:
        # Nel caso in cui manchi la candela di chiusura per quel giorno
        if vix_open_price is not None and vix_close_price is not None:
            print(f"GMT: {row_open['Gmt time']} - Candela di chiusura mancante. VIX O: {vix_open_price}, VIX C: {vix_close_price}.")
        else:
            print(f"GMT: {row_open['Gmt time']} - Candela di chiusura mancante. VIX data missing.")

# Stampa il resoconto settimanale
print("\nResoconto settimanale:")
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

# VIX data missing
if missing_vix_days > 0:
    print(f"\033[91mVIX assente in alcuni giorni: {missing_vix_days} ({missing_vix_days / total_count * 100:.2f}% dei dati analizzati senza VIX)\033[0m")

# Calcolo degli anni e stampa finale
if total_count > 0:
    years = total_count / trading_days_per_year
    print(f"\nTotale giorni analizzati: {total_count} ({years:.2f} anni)")
else:
    print("\nNessun dato valido trovato.")
