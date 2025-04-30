#!/usr/bin/env python3

import os
import subprocess
import time
import math

def calculate_entropy(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    if not data:
        return 0
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    entropy = 0.0
    for f in freq:
        if f > 0:
            p = f / len(data)
            entropy -= p * math.log2(p)
    return entropy


# === Chemins ===
PASSES_DIR = "passes"
BUILD_DIR = "build"
SOURCE_DIR = "sources/clair"
OBF_DIR = "sources/obfusque"
# Détection des fichiers .c et .cpp dans sources/clair
source_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith((".c", ".cpp"))]
if not source_files:
    print("[!] Aucun fichier .c ou .cpp trouvé dans sources/clair/")
    exit(1)

print("[?] Fichier source à compiler :")
for idx, fname in enumerate(source_files):
    print(f"  {idx}) {fname}")

choice = int(input("→ Choix (numéro) : "))
SOURCE_FILE = os.path.join(SOURCE_DIR, source_files[choice])
BASE_NAME = os.path.splitext(source_files[choice])[0]
IS_CPP = source_files[choice].endswith(".cpp")
print(f"[+] Fichier choisi : {SOURCE_FILE}")




# === Étape 1 : Sélection de la passe ===
print("\n[?] Quelle passe veux-tu appliquer ?")
pass_files = [f for f in os.listdir(PASSES_DIR) if f.endswith(".cpp")]

if not pass_files:
    print("[!] Aucun fichier .cpp trouvé dans le dossier 'passes'.")
    exit(1)

# Affichage des passes disponibles
for idx, pf in enumerate(pass_files):
    pass_name = pf.replace(".cpp", "")
    print(f"  {idx}) {pass_name}")

# Demander le choix de la passe
choice = int(input("→ Choix (numéro) : "))
chosen_pass = pass_files[choice].replace(".cpp", "")
chosen_so = f"{BUILD_DIR}/{chosen_pass}.so"

# === Étape 2 : Compilation de la passe sélectionnée ===
print(f"\n[+] Compilation de la passe {chosen_pass}...")
os.makedirs(BUILD_DIR, exist_ok=True)

# Compiler la passe sélectionnée
full_cmd = f"clang++ -fPIC -shared -o {chosen_so} {PASSES_DIR}/{pass_files[choice]} `llvm-config --cxxflags --ldflags --system-libs --libs core passes` -std=c++17"
result = subprocess.run(full_cmd, shell=True)

if result.returncode == 0:
    print(f"  [OK] {pass_files[choice]} → {chosen_so}")
else:
    print(f"  [FAIL] {pass_files[choice]}")

# === Étape 3 : Compilation en LLVM IR puis binaire ===
print("\n[+] Compilation du fichier source...")
os.makedirs(OBF_DIR, exist_ok=True)

# LLVM IR clair
subprocess.run(f"clang -emit-llvm -S {SOURCE_FILE} -o {SOURCE_DIR}/{BASE_NAME}.ll", shell=True)

# Compilation version claire
compiler = "clang++" if IS_CPP else "clang"
subprocess.run(f"{compiler} {SOURCE_FILE} -o {SOURCE_DIR}/{BASE_NAME}", shell=True)

# === Étape 4 : Obfuscation et compilation version obfusquée ===
print("\n[+] Obfuscation...")
obf_ll = f"{OBF_DIR}/{BASE_NAME}_obf.ll"
cmd = f"opt -load-pass-plugin {chosen_so} -passes={chosen_pass} -S {SOURCE_DIR}/{BASE_NAME}.ll -o {obf_ll}"
subprocess.run(cmd, shell=True)

# Compilation binaire obfusqué
subprocess.run(f"{compiler} {obf_ll} -o {OBF_DIR}/{BASE_NAME}", shell=True)

entropy_clair = calculate_entropy(os.path.join(SOURCE_DIR, BASE_NAME))
entropy_obfusque = calculate_entropy(os.path.join(OBF_DIR, BASE_NAME))

size_clair = os.path.getsize(os.path.join(SOURCE_DIR, BASE_NAME))
size_obfusque = os.path.getsize(os.path.join(OBF_DIR, BASE_NAME))

# Exécution version claire
print("[*] Exécution version claire...")
start = time.time()
subprocess.run(f"{SOURCE_DIR}/{BASE_NAME}", shell=True)
end = time.time()
time_clair = end - start

# Exécution version obfusquée
print("[*] Exécution version obfusquée...")
start = time.time()
subprocess.run(f"{OBF_DIR}/{BASE_NAME}", shell=True)
end = time.time()
time_obf = end - start

# Calcul des variations en pourcentage
size_variation = ((size_obfusque - size_clair) / size_clair) * 100
time_variation = ((time_obf - time_clair) / time_clair) * 100
entropy_variation = ((entropy_obfusque - entropy_clair) / entropy_clair) * 100

# Construction du tableau avec formatage
header = f"| {'Version':<12} | {'Taille (Ko)':<15} | {'Temps (s)':<10} | {'Entropie':<10} |"
separator = "+" + "-"*14 + "+" + "-"*17 + "+" + "-"*12 + "+" + "-"*12 + "+"

row_clair = f"| {'Clair':<12} | {size_clair / 1024:<15.2f} | {time_clair:<10.4f} | {entropy_clair:<10.4f} |"
row_obfusque = f"| {'Obfusqué':<12} | {size_obfusque / 1024:<15.2f} | {time_obf:<10.4f} | {entropy_obfusque:<10.4f} |"
row_variation = f"| {'Variation (%)':<12} | {size_variation:<15.2f} | {time_variation:<10.2f} | {entropy_variation:<10.2f} |"

# Affichage du tableau
print("\n=== 📊 Résumé comparatif ===")
print(separator)
print(header)
print(separator)
print(row_clair)
print(row_obfusque)
print(separator)
print(row_variation)
print(separator)

print(f"Passe utilisée : {chosen_pass}")

