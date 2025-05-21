#!/usr/bin/env python3
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json
import re

# Configuration des chemins
PASSES_DIR = "passes"
BUILD_DIR = "build"
SOURCE_DIR = "sources/clair"
OBF_DIR = "sources/obfusque"
LOG_DIR = "logs"
OBF_COMPIL_LOG = os.path.join(LOG_DIR, "obf_compil.txt")

os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(OBF_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def run_command(cmd, cwd=None):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr
        }

def setup_environment():
    """Configure l'environnement pour l'obfuscation"""
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

    # Sélection de la passe
    passes = [f for f in os.listdir(PASSES_DIR) if f.endswith('.cpp')]
    if not passes:
        print("[!] Aucune passe disponible")
        exit(1)

    print("\n[?] Sélectionnez une passe d'obfuscation:")
    for i, p in enumerate(passes):
        print(f"  {i}) {os.path.splitext(p)[0]}")

    pass_choice = int(input("→ Choix (numéro): "))
    pass_name = os.path.splitext(passes[pass_choice])[0]
    
    return {
        "target": target,
        "is_project": is_project,
        "base_name": base_name,
        "pass_name": pass_name
    }

def compile_pass(pass_name):
    """Compile la passe LLVM"""
    pass_so = os.path.join(BUILD_DIR, f"{pass_name}.so")
    print(f"\n[+] Compilation de la passe {pass_name}...")
    
    cmd = f"clang++ -fPIC -shared {os.path.join(PASSES_DIR, pass_name+'.cpp')} " \
          f"-o {pass_so} `llvm-config --cxxflags --ldflags --system-libs --libs core passes` -std=c++17"
    
    result = run_command(cmd)
    if not result["success"]:
        print(f"[!] Échec de compilation de la passe:\n{result['stderr']}")
        exit(1)
    
    return pass_so

def process_target(config):
    """Traite la cible sélectionnée"""
    if config["is_project"]:
        return process_project(config)
    else:
        return process_file(config)

import os
import shutil
import re

def process_project(config):
    """Version finale avec gestion robuste des chemins"""
    project_path = os.path.join(SOURCE_DIR, config["target"])
    obf_project_path = os.path.join(OBF_DIR, config["target"])
    exec_name = os.path.basename(project_path)
    
    # 1. Copie du projet avec résolution des liens symboliques
    shutil.copytree(project_path, obf_project_path, dirs_exist_ok=True, symlinks=True)
    
    # 2. Conversion du chemin en absolu et vérification
    pass_so = Path(config['pass_so']).resolve()
    if not pass_so.exists():
        raise FileNotFoundError(f"Fichier .so introuvable: {pass_so}")

    # 3. Modification du Makefile
    makefile_path = os.path.join(obf_project_path, "Makefile")
    if os.path.exists(makefile_path):
        with open(makefile_path, "r+") as f:
            content = f.read()
            
            # Ajout des règles avec chemin ABSOLU
            obf_rules = f"""
# === Obfuscation LLVM ===
PASS_SO = {pass_so}
PASS_NAME ?= $(error Spécifiez PASS_NAME: make obfuscate PASS_NAME=NomPasse)

# Fichiers intermédiaires
OBF_OBJS = $(patsubst %.c,%_obf.o,$(wildcard *.c))

.PHONY: obfuscate
obfuscate: {exec_name}_obf

# Règle générique d'obfuscation
%_obf.o: %.c
\t@echo "[+] Traitement de $<"
\t$(CC) -emit-llvm -S $(CFLAGS) $< -o $*.ll
\t$(shell which opt) -load-pass-plugin $(PASS_SO) -passes=$(PASS_NAME) -S $*.ll -o $*_obf.ll
\t$(CC) -c $*_obf.ll -o $@
\t@rm -f $*.ll $*_obf.ll

# Édition des liens finale
{exec_name}_obf: $(OBF_OBJS)
\t@echo "[+] Édition des liens obfusquée"
\t$(CC) $(CFLAGS) -o $@ $^
"""
            # Insertion avant clean
            if "clean:" in content:
                content = content.replace("clean:", obf_rules + "\nclean:")
            else:
                content += obf_rules
                
            f.seek(0)
            f.write(content)
            f.truncate()

    # 4. Compilation
    print("\n[1/3] Compilation normale...")
    run_command("make clean && make", cwd=project_path)
    
    print("\n[2/3] Obfuscation...")
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(pass_so.parent)  # Pour le chargement .so
    run_command(
        f"make obfuscate PASS_NAME={config['pass_name']}", 
        cwd=obf_project_path,
        env=env
    )
    
    return {
        "clair_bin": os.path.join(project_path, exec_name),
        "obf_bin": os.path.join(obf_project_path, f"{exec_name}_obf")
    }



def process_file(config):
    """Traite un fichier individuel"""
    source_file = os.path.join(SOURCE_DIR, config["target"])
    clair_ll = os.path.join(SOURCE_DIR, f"{config['base_name']}.ll")
    clair_bin = os.path.join(SOURCE_DIR, config["base_name"])
    obf_dir = os.path.join(OBF_DIR, config["base_name"])
    os.makedirs(obf_dir, exist_ok=True)
    obf_ll = os.path.join(obf_dir, f"{config['base_name']}_obf.ll")
    obf_bin = os.path.join(obf_dir, config["base_name"])

    print("\n[+] Compilation en LLVM IR (niveau O1)...")
    run_command(f"clang -emit-llvm -S -O1 {source_file} -o {clair_ll}")

    print("\n[+] Compilation du binaire clair...")
    run_command(f"clang -O1 {source_file} -o {clair_bin}")

    print("\n[+] Application de la passe d'obfuscation...")
    cmd = f"opt -load-pass-plugin {config['pass_so']} -passes='{config['pass_name']}' -S {clair_ll} -o {obf_ll}"
    run_command(cmd)

    print("\n[+] Compilation du binaire obfusqué...")
    run_command(f"clang -O1 {obf_ll} -o {obf_bin}")

    return {
        "clair_bin": clair_bin,
        "obf_bin": obf_bin
    }

def main():
    """Point d'entrée principal"""
    config = setup_environment()
    config["pass_so"] = compile_pass(config["pass_name"])
    
    print("\n[+] Traitement de la cible...")
    binaries = process_target(config)
    
    print("\n[+] Génération terminée avec succès!")
    print(f"Binaire clair: {binaries['clair_bin']}")
    print(f"Binaire obfusqué: {binaries['obf_bin']}")
    
    # Écriture des chemins pour le script compare.py
    with open("binaries_paths.json", "w") as f:
        json.dump(binaries, f)

if __name__ == "__main__":
    main() 
