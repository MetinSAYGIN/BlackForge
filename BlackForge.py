#!/usr/bin/env python3

import os
import subprocess
import time
import math
import re
import shutil
from pathlib import Path

def calculate_entropy(filepath):
    """Calcule l'entropie d'un fichier binaire"""
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

def setup_project_environment(project_path, pass_so, pass_name):
    """Configure un projet avec cible d'obfuscation"""
    makefile_path = os.path.join(project_path, "Makefile")
    
    # Vérifier et ajouter la cible obfuscate si nécessaire
    if os.path.exists(makefile_path):
        with open(makefile_path, "r+") as f:
            content = f.read()
            if "obfuscate:" not in content:
                f.write(f"\n# Cible obfuscation générée automatiquement\n")
                f.write(f"obfuscate:\n")
                f.write(f"\t@echo '[*] Génération du IR obfusqué...'\n")
                f.write(f"\topt -load-pass-plugin {pass_so} -passes='{pass_name}' -S main.ll -o main_obf.ll -disable-verify\n")
                f.write(f"\t@echo '[*] Compilation du binaire obfusqué...'\n")
                f.write(f"\tclang -O1 -fno-inline -mllvm -disable-llvm-optzns main_obf.ll -o main_obf\n")
                return True
    return False

def run_with_metrics(command, cwd=None):
    """Exécute une commande et mesure les ressources"""
    start_time = time.time()
    process = subprocess.run(command, shell=True, cwd=cwd, 
                           capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    if process.returncode != 0:
        print(f"[!] Erreur exécution: {process.stderr}")
        return None
    
    return {
        "time": elapsed,
        "returncode": process.returncode,
        "output": process.stdout
    }

# ===== Configuration des chemins =====
PASSES_DIR = "passes"
BUILD_DIR = "build"
SOURCE_DIR = "sources/clair"
OBF_DIR = "sources/obfusque"
LOG_DIR = "logs"

os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(OBF_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ===== Sélection du projet/fichier =====
entries = sorted(os.listdir(SOURCE_DIR))
projects = [e for e in entries if os.path.isdir(os.path.join(SOURCE_DIR, e))]
files = [e for e in entries if e.endswith(('.c', '.cpp')) and os.path.isfile(os.path.join(SOURCE_DIR, e))]

if not projects and not files:
    print("[!] Aucun projet ou fichier source trouvé")
    exit(1)

print("[?] Sélectionnez un projet ou fichier source:")
for i, p in enumerate(projects):
    print(f"  {i}) [PROJET] {p}")
for i, f in enumerate(files, len(projects)):
    print(f"  {i}) [FICHIER] {f}")

choice = int(input("→ Choix (numéro): "))
selected = projects + files
target = selected[choice]
is_project = choice < len(projects)
base_name = os.path.splitext(target)[0] if not is_project else target

# ===== Sélection de la passe =====
passes = [f for f in os.listdir(PASSES_DIR) if f.endswith('.cpp')]
if not passes:
    print("[!] Aucune passe disponible")
    exit(1)

print("\n[?] Sélectionnez une passe d'obfuscation:")
for i, p in enumerate(passes):
    print(f"  {i}) {os.path.splitext(p)[0]}")

pass_choice = int(input("→ Choix (numéro): "))
pass_name = os.path.splitext(passes[pass_choice])[0]
pass_so = os.path.join(BUILD_DIR, f"{pass_name}.so")

# ===== Compilation de la passe =====
print(f"\n[+] Compilation de la passe {pass_name}...")
cmd = f"clang++ -fPIC -shared {os.path.join(PASSES_DIR, passes[pass_choice])} " \
      f"-o {pass_so} `llvm-config --cxxflags --ldflags --system-libs --libs core passes` -std=c++17"
result = run_with_metrics(cmd)
if not result or result['returncode'] != 0:
    exit(1)

# ===== Traitement selon le type de cible =====
if is_project:
    # Mode projet avec Makefile
    project_path = os.path.join(SOURCE_DIR, target)
    obf_project_path = os.path.join(OBF_DIR, target)
    
    # Configuration du projet
    setup_project_environment(project_path, pass_so, pass_name)
    
    # Compilation propre
    print("\n[+] Compilation du projet original...")
    run_with_metrics("make clean && make", cwd=project_path)
    
    # Génération du IR
    run_with_metrics("make main.ll", cwd=project_path)
    
    # Obfuscation via Makefile
    print("\n[+] Obfuscation du projet...")
    run_with_metrics("make obfuscate", cwd=project_path)
    
    # Déplacement des résultats
    shutil.copytree(project_path, obf_project_path, dirs_exist_ok=True)
    clair_bin = os.path.join(project_path, "main")
    obf_bin = os.path.join(obf_project_path, "main_obf")
else:
    # Mode fichier individuel
    source_file = os.path.join(SOURCE_DIR, target)
    clair_ll = os.path.join(SOURCE_DIR, f"{base_name}.ll")
    clair_bin = os.path.join(SOURCE_DIR, base_name)
    obf_dir = os.path.join(OBF_DIR, base_name)
    os.makedirs(obf_dir, exist_ok=True)
    obf_ll = os.path.join(obf_dir, f"{base_name}_obf.ll")
    obf_bin = os.path.join(obf_dir, base_name)

    # Compilation originale
    print("\n[+] Compilation du fichier source...")
    run_with_metrics(f"clang -emit-llvm -S -O1 -Xclang -disable-llvm-passes {source_file} -o {clair_ll}")
    run_with_metrics(f"clang -O1 {source_file} -o {clair_bin}")

    # Obfuscation
    print("\n[+] Application de la passe d'obfuscation...")
    cmd = f"opt -load-pass-plugin {pass_so} -passes='default<O1>,{pass_name}' -S {clair_ll} -o {obf_ll}"
    print(cmd)
    run_with_metrics(cmd)
    
    # Compilation finale
    run_with_metrics(f"clang -O1 -fno-inline -mllvm -disable-llvm-optzns {obf_ll} -o {obf_bin}")

# ===== Analyse des résultats =====
def collect_metrics(bin_path):
    return {
        "size": os.path.getsize(bin_path),
        "entropy": calculate_entropy(bin_path),
        "time": run_with_metrics(f"./{os.path.basename(bin_path)}", 
                               cwd=os.path.dirname(bin_path))["time"]
    }

clair_metrics = collect_metrics(clair_bin)
obf_metrics = collect_metrics(obf_bin)

# Calcul des variations
def calc_variation(orig, new):
    return ((new - orig) / orig) * 100

variations = {
    "size": calc_variation(clair_metrics["size"], obf_metrics["size"]),
    "time": calc_variation(clair_metrics["time"], obf_metrics["time"]),
    "entropy": calc_variation(clair_metrics["entropy"], obf_metrics["entropy"])
}

# ===== Affichage des résultats =====
print("\n=== 📊 RÉSULTATS ===")
print("+----------------+----------------+----------------+")
print("| Métrique       | Clair          | Obfusqué       |")
print("+----------------+----------------+----------------+")
print(f"| Taille (Ko)   | {clair_metrics['size']/1024:14.2f} | {obf_metrics['size']/1024:14.2f} |")
print(f"| Temps (s)     | {clair_metrics['time']:14.4f} | {obf_metrics['time']:14.4f} |")
print(f"| Entropie      | {clair_metrics['entropy']:14.4f} | {obf_metrics['entropy']:14.4f} |")
print("+----------------+----------------+----------------+")
print("| Variation (%) |")
print(f"| Taille: {variations['size']:6.2f}% | Temps: {variations['time']:6.2f}% | Entropie: {variations['entropy']:6.2f}% |")
print("+----------------+----------------+----------------+")
