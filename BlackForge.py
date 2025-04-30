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




# === Étape 1 : Compilation des passes ===
print("[+] Compilation des passes...")
os.makedirs(BUILD_DIR, exist_ok=True)

pass_files = [f for f in os.listdir(PASSES_DIR) if f.endswith(".cpp")]
so_files = []

for pf in pass_files:
    pass_name = pf.replace(".cpp", "")
    so_path = f"{BUILD_DIR}/{pass_name}.so"
    full_cmd = f"clang++ -fPIC -shared -o {so_path} {PASSES_DIR}/{pf} `llvm-config --cxxflags --ldflags --system-libs --libs core passes` -std=c++17"
    result = subprocess.run(full_cmd, shell=True)
    if result.returncode == 0:
        print(f"  [OK] {pf} → {so_path}")
        so_files.append((pass_name, so_path))
    else:
        print(f"  [FAIL] {pf}")

if not so_files:
    print("[!] Aucune passe compilée, arrêt.")
    exit(1)

# === Étape 2 : Sélection de la passe ===
print("\n[?] Quelle passe veux-tu appliquer ?")
for idx, (name, _) in enumerate(so_files):
    print(f"  {idx}) {name}")
choice = int(input("→ Choix (numéro) : "))
chosen_pass, chosen_so = so_files[choice]

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

size_clair = os.path.getsize(clair_exe)
size_obfusque = os.path.getsize(obfusque_exe)

# Mesure du temps clair
print("[*] Exécution version claire...")
start = time.time()
subprocess.run(f"{SOURCE_DIR}/{BASE_NAME}", shell=True)
end = time.time()
time_clair = end - start
print(f"[📦] Taille (clair)     : {size_clair / 1024:.2f} Ko")
print(f"[✓] Temps clair : {time_clair:.4f} sec")
print(f"[🔐] Entropie (clair)     : {entropy_clair:.4f}")

# Mesure du temps obfusqué
print("[*] Exécution version obfusquée...")
start = time.time()
subprocess.run(f"{OBF_DIR}/{BASE_NAME}", shell=True)
end = time.time()
time_obf = end - start
print(f"[📦] Taille (obfusqué) : {size_obfusque / 1024:.2f} Ko")
print(f"[✓] Temps obfusqué : {time_obf:.4f} sec")
print(f"[🔐] Entropie (obfusqué) : {entropy_obfusque:.4f}")

# === Résumé final ===
print("\n=== Résumé ===")
print(f"→ Temps version claire    : {time_clair:.4f} sec")
print(f"→ Temps version obfusquée : {time_obf:.4f} sec")
gain = ((time_obf - time_clair) / time_clair) * 100
print(f"→ Variation de temps       : {gain:+.2f}%")
