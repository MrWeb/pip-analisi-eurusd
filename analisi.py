import pandas as pd
import argparse
import importlib

def main():
    # Configurazione dell'argomento della riga di comando
    parser = argparse.ArgumentParser(description='Analisi dei dati di trading.')
    parser.add_argument('-f', '--function', type=str, required=True, help='Nome della funzione da chiamare')
    parser.add_argument('-o', '--output', type=str, required=False, help='Output di tutti i dati')
    args = parser.parse_args()

    # Nome del file da analizzare
    file_name = 'eurusd.csv'
    start_time = '13:30:00'
    end_time = '14:00:00'
    pip_factor = 0.0001

    # Lettura del file
    print(f"Lettura del file...")
    df = pd.read_csv(file_name)
    df['Gmt time'] = pd.to_datetime(df['Gmt time'], format='%d.%m.%Y %H:%M:%S.%f')
    print(f"Analisi del file...")

    # Carica e chiama la funzione richiesta
    function_name = args.function
    output = args.output
    module = importlib.import_module(function_name)
    function = getattr(module, function_name)

    # Passa i dati alla funzione
    function(df, start_time, end_time, pip_factor, output)

if __name__ == '__main__':
    main()
