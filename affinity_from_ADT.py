import os
import re
import matplotlib.pyplot as plt
import pandas as pd

"""
Plik odczytuje affinity ze wszystkich plikow log wygenerowanych przez AutoDock Vina.
Modyfkuje nazwy plikow log, np. z 'log_4XMB_CBD-SUL_opt_config1_10' na 'CBD-SUL_config1_10'.
Dla kazdej wartosci mod generuje barplot.
Wyniki zapisuje w fomacie pliku Excel.
"""

def extract_affinity(file_path):
    """
    Odczytuje wartości affinity z plikow TXT.
    """
    affinities = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Szukamy sekcji z wartosciami numerycznymi
    for line in lines:
        match = re.match(r"^\s*(\d+)\s+(-\d+\.\d+)", line)
        if match:
            mode = int(match.group(1))  # Pierwsza liczba - mode
            affinity = float(match.group(2))  # Druga liczba - affinity
            affinities[mode] = affinity

    return affinities

# Znalezienie wszystkich plików TXT w katalogu
txt_files = [f for f in os.listdir() if f.endswith(".txt")]

# Sortowanie plikow - najpierw te z "SUL", potem reszta
txt_files.sort(key=lambda x: (not "SUL" in x, x))

# Odczytanie wartosci affinity dla kazdego pliku
all_affinities = {file: extract_affinity(file) for file in txt_files}

# Tworzenie wykresow dla kazdego mode oraz zapisywanie do Excela
modes = sorted(set(mode for affinities in all_affinities.values() for mode in affinities))

# Tworzymy pusty slownik do przechowywania danych dla Excela
excel_data = {mode: [] for mode in modes}

for mode in modes:
    plt.figure(figsize=(10, 5))
    
    filenames = []
    values = []
    
    for file in txt_files:
        if mode in all_affinities[file]:
            # Skracanie nazwy pliku (usuwanie "log_4XMB_" i "opt_config")
            short_name = re.sub(r"log_4XMB_|opt_config", "", file.replace(".txt", ""))
            filenames.append(short_name)
            values.append(all_affinities[file][mode])
            excel_data[mode].append([short_name, all_affinities[file][mode]])

    # Tworzenie wykresu
    plt.bar(filenames, values, color='skyblue')
    plt.xlabel("Pliki")
    plt.ylabel("Affinity (kcal/mol)")
    plt.title(f"Affinity dla Mode {mode}")
    plt.xticks(rotation=45, ha="right")
    
    plt.savefig(f"mode_{mode}.png")  # Zapis wykresu do pliku
    plt.close()

# Tworzenie i zapis pliku Excel
with pd.ExcelWriter("affinity_results.xlsx") as writer:
    for mode, data in excel_data.items():
        df = pd.DataFrame(data, columns=["File", "Affinity"])
        df.to_excel(writer, sheet_name=f"Mode_{mode}", index=False)

print("Wszystkie wykresy wygenerowane i zapisane, dane zapisane do affinity_results.xlsx.")
