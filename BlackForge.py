#!/usr/bin/env python3

import os
import subprocess
import time

# === Chemins ===
PASSES_DIR = "passes"
BUILD_DIR = "build"
SOURCE_DIR = "sources/clair"
OBF_DIR = "sources/obfusque"
# Détection automatique du fichier .c dans sources/clair
source_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".c")]
if not source_files:
    print("[!] Aucun fichier .c trouvé dans sources/clair/")
    exit(1)

SOURCE_FILE = os.path.join(SOURCE_DIR, source_files[0])
BASE_NAME = os.path.splitext(source_files[0])[0]
print(f"[+] Fichier source détecté : {SOURCE_FILE}")


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
subprocess.run(f"clang {SOURCE_FILE} -o {SOURCE_DIR}/{BASE_NAME}", shell=True)

# Mesure du temps clair
print("[*] Exécution version claire...")
start = time.time()
subprocess.run(f"{SOURCE_DIR}/{BASE_NAME}", shell=True)
end = time.time()
time_clair = end - start
print(f"[✓] Temps clair : {time_clair:.4f} sec")

# === Étape 4 : Obfuscation et compilation version obfusquée ===
print("\n[+] Obfuscation...")
obf_ll = f"{OBF_DIR}/{BASE_NAME}_obf.ll"
cmd = f"opt -load-pass-plugin {chosen_so} -passes={chosen_pass} -S {SOURCE_DIR}/{BASE_NAME}.ll -o {obf_ll}"
subprocess.run(cmd, shell=True)

# Compilation binaire obfusqué
subprocess.run(f"clang {obf_ll} -o {OBF_DIR}/{BASE_NAME}", shell=True)

# Mesure du temps obfusqué
print("[*] Exécution version obfusquée...")
start = time.time()
subprocess.run(f"{OBF_DIR}/{BASE_NAME}", shell=True)
end = time.time()
time_obf = end - start
print(f"[✓] Temps obfusqué : {time_obf:.4f} sec")

# === Résumé final ===
print("\n=== Résumé ===")
print(f"→ Temps version claire    : {time_clair:.4f} sec")
print(f"→ Temps version obfusquée : {time_obf:.4f} sec")
gain = ((time_obf - time_clair) / time_clair) * 100
print(f"→ Variation de temps       : {gain:+.2f}%")
