#!/usr/bin/env python3

import os
import subprocess
import time
import math
import re

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

def add_obfuscate_target(makefile_path, pass_so, pass_name):
    # Vérifier si la cible 'obfuscate' existe déjà
    with open(makefile_path, "r") as f:
        lines = f.readlines()
    
    # Recherche de la cible 'obfuscate' dans le Makefile
    for line in lines:
        if line.strip().startswith("obfuscate:"):
            print("[*] La cible 'obfuscate' existe déjà dans le Makefile.")
            return
    
    # Si elle n'existe pas, on l'ajoute à la fin du fichier
    with open(makefile_path, "a") as f:
        f.write(f"\n# Cible obfuscate générée dynamiquement\n")
        f.write(f"obfuscate:\n")
        f.write(f"\topt -load-pass-plugin {pass_so} -passes='{pass_name}' -S main.ll -o main_obf.ll -disable-verify\n")
        f.write(f"\tclang -O1 -fno-inline -mllvm -disable-llvm-optzns main_obf.ll -o main_obf\n")
    
    print("[+] Cible 'obfuscate' ajoutée au Makefile.")

# === Chemins ===
PASSES_DIR = "passes"
BUILD_DIR = "build"
SOURCE_DIR = "sources/clair"
OBF_DIR = "sources/obfusque"

# Détection des projets dans sources/clair
source_projects = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
if not source_projects:
    print("[!] Aucun projet trouvé dans sources/clair/")
    exit(1)

print("[?] Choisissez un projet ou un fichier .c à obfusquer :")

# Choisir entre un projet ou un fichier C
source_choices = source_projects + [f for f in os.listdir(SOURCE_DIR) if f.endswith(".c")]
for idx, name in enumerate(source_choices):
    print(f"  {idx}) {name}")

choice = int(input("→ Choix (numéro) : "))

# Déterminer s'il s'agit d'un projet ou d'un fichier .c
if choice < len(source_projects):
    PROJECT_NAME = source_choices[choice]
    PROJECT_PATH = os.path.join(SOURCE_DIR, PROJECT_NAME)
    IS_PROJECT = True
else:
    FILE_NAME = source_choices[choice]
    FILE_PATH = os.path.join(SOURCE_DIR, FILE_NAME)
    IS_PROJECT = False
    BASE_NAME = FILE_NAME.replace(".c", "")

# === Étape 1 : Sélection de la passe ===
print("\n[?] Quelle passe veux-tu appliquer ?")
pass_files = [f for f in os.listdir(PASSES_DIR) if f.endswith(".cpp")]

if not pass_files:
    print("[!] Aucun fichier .cpp trouvé dans le dossier 'passes'.")
    exit(1)

for idx, pf in enumerate(pass_files):
    pass_name = pf.replace(".cpp", "")
    print(f"  {idx}) {pass_name}")

while True:
    try:
        choice = int(input("→ Choix (numéro) : "))
        if 0 <= choice < len(pass_files):
            break
        else:
            print("[!] Choix invalide.")
    except ValueError:
        print("[!] Veuillez entrer un numéro valide.")

chosen_pass = pass_files[choice].replace(".cpp", "")
chosen_so = f"{BUILD_DIR}/{chosen_pass}.so"

# === Étape 2 : Compilation de la passe ===
print(f"\n[+] Compilation de la passe {chosen_pass}...")
os.makedirs(BUILD_DIR, exist_ok=True)
full_cmd = f"clang++ -fPIC -shared -o {chosen_so} {PASSES_DIR}/{pass_files[choice]} `llvm-config --cxxflags --ldflags --system-libs --libs core passes` -std=c++17"
print(f"[+] Commande : {full_cmd}")
result = subprocess.run(full_cmd, shell=True)
if result.returncode != 0:
    print("[!] Échec compilation passe")
    exit(1)

# === Étape 3 : Si un PROJECT est sélectionné, utiliser le Makefile ===
if IS_PROJECT:
    # Vérification du Makefile
    makefile_path = os.path.join(PROJECT_PATH, "Makefile")
    
    if os.path.exists(makefile_path):
        add_obfuscate_target(makefile_path, chosen_so, chosen_pass)
    else:
        print("[!] Aucun Makefile trouvé dans le projet.")
        exit(1)

    # === Étape 4 : Compilation via Makefile (si projet sélectionné) ===
    print("\n[+] Compilation via Makefile...")
    res = subprocess.run("make obfuscate", cwd=PROJECT_PATH, shell=True)
    if res.returncode != 0:
        print("[!] Échec compilation du projet clair.")
        exit(1)

    clair_ll = os.path.join(PROJECT_PATH, f"{BASE_NAME}.ll")
    clair_bin = os.path.join(PROJECT_PATH, BASE_NAME)
else:
    clair_ll = FILE_PATH
    clair_bin = BASE_NAME

# === Étape 5 : Obfuscation ===
print("\n[+] Obfuscation...")
OBF_PROJ_DIR = os.path.join(OBF_DIR, PROJECT_NAME if IS_PROJECT else BASE_NAME)
os.makedirs(OBF_PROJ_DIR, exist_ok=True)
obf_ll = os.path.join(OBF_PROJ_DIR, f"{BASE_NAME}_obf.ll")
obf_bin = os.path.join(OBF_PROJ_DIR, BASE_NAME)

cmd = f"opt -load-pass-plugin {chosen_so} -passes='{chosen_pass}' -S {clair_ll} -o {obf_ll} -disable-verify -debug-pass-manager 2> logs/obf_compil.txt"
print(f"[+] Commande : {cmd}")
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
if res.returncode != 0:
    print(f"[!] Erreur obfuscation : {res.stderr}")
    exit(1)

with open(obf_ll, "r+") as f:
    content = f.read()
    content = re.sub(r'source_filename\s*=\s*\".*?\"', f'source_filename = \"{BASE_NAME}_obf.ll\"', content)
    content = re.sub(r"ModuleID = '([^']+)'", f"ModuleID = '{obf_ll}'", content)
    f.seek(0)
    f.write(content)
    f.truncate()

subprocess.run(f"clang -O1 -fno-inline -mllvm -disable-llvm-optzns {obf_ll} -o {obf_bin}", shell=True)

# === Métriques ===
entropy_clair = calculate_entropy(clair_bin)
entropy_obf = calculate_entropy(obf_bin)
size_clair = os.path.getsize(clair_bin)
size_obf = os.path.getsize(obf_bin)
size_ll_clair = os.path.getsize(clair_ll)
size_ll_obf = os.path.getsize(obf_ll)

print("[*] Exécution clair...")
start = time.time()
subprocess.run(clair_bin, shell=True)
time_clair = time.time() - start

print("[*] Exécution obfusqué...")
start = time.time()
subprocess.run(obf_bin, shell=True)
time_obf = time.time() - start

size_var = ((size_obf - size_clair) / size_clair) * 100
ll_var = ((size_ll_obf - size_ll_clair) / size_ll_clair) * 100
entropy_var = ((entropy_obf - entropy_clair) / entropy_clair) * 100
time_var = ((time_obf - time_clair) / time_clair) * 100

print("\n=== 📊 Résumé comparatif ===")
print("+--------------+--------------+--------------+------------+------------+")
print("| Version      | Taille (Ko) | Taille LL(Ko)| Temps (s)  | Entropie   |")
print("+--------------+--------------+--------------+------------+------------+")
print(f"| Clair        | {size_clair/1024:<12.2f} | {size_ll_clair/1024:<12.2f} | {time_clair:<10.4f} | {entropy_clair:<10.4f} |")
print(f"| Obfusqué     | {size_obf/1024:<12.2f} | {size_ll_obf/1024:<12.2f} | {time_obf:<10.4f} | {entropy_obf:<10.4f} |")
print("+--------------+--------------+--------------+------------+------------+")
print(f"| Variation %  | {size_var:<12.2f} | {ll_var:<12.2f} | {time_var:<10.2f} | {entropy_var:<10.2f} |")
print("+--------------+--------------+--------------+------------+------------+")

print(f"Passe utilisée : {chosen_pass}")
