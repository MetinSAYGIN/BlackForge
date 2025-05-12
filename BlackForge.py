#!/usr/bin/env python3

import os
import subprocess
import time
import math
import re
import shutil
from pathlib import Path
import math
import psutil
import platform
import json
import shlex
import signal
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import math
import psutil
import platform
import json
import shlex
import signal
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import math
import psutil
import platform
import json
import shlex
import signal
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path


def run_with_metrics(command: Union[str, List[str]], 
                    cwd: Optional[str] = None,
                    timeout: Optional[float] = None,
                    env: Optional[Dict[str, str]] = None,
                    description: Optional[str] = None,
                    check_output: bool = False,
                    verbose: bool = True,
                    log_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Exécute une commande et mesure les ressources et performances.
    
    Args:
        command: La commande à exécuter (chaîne ou liste)
        cwd: Répertoire de travail pour l'exécution
        timeout: Temps maximum d'exécution en secondes
        env: Variables d'environnement supplémentaires
        description: Description explicite de l'opération 
        check_output: Vérifier la sortie pour erreurs
        verbose: Afficher les informations pendant l'exécution
        log_file: Chemin du fichier pour journaliser les métriques
    
    Returns:
        Un dictionnaire contenant les métriques et résultats d'exécution
        avec la structure compatible avec le code existant:
        {
            "time": temps_d'exécution,
            "returncode": code_de_retour,
            "output": stdout,
            ...autres métriques supplémentaires...
        }
    """
    # Préparation pour le logging
    log_dir = None
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Conversion de la commande en chaîne pour l'affichage
    cmd_str = command if isinstance(command, str) else " ".join(shlex.quote(str(arg)) for arg in command)
    
    # Récupérer les métriques système avant l'exécution
    start_disk_io = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
    start_mem = psutil.virtual_memory()
    cpu_times_start = psutil.cpu_times()
    
    # Mesure de l'utilisation CPU au démarrage (moyenne sur 0.1s)
    cpu_percent_start = psutil.cpu_percent(interval=0.1)
    
    # Préparation de l'environnement
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    
    # Affichage de départ
    if verbose:
        if description:
            print(f"\n[+] {description}")
        print(f"[*] Exécution: {cmd_str}")
    
    # Capture du temps de départ
    start_time = time.time()
    start_datetime = datetime.now().isoformat()
    
    # Valeurs par défaut en cas d'exception
    stdout = ""
    stderr = ""
    returncode = None
    timed_out = False
    error_msg = None
    
    try:
        # Exécution de la commande
        process = subprocess.run(
            command,
            shell=isinstance(command, str),
            cwd=cwd,
            env=process_env,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Récupération des résultats
        stdout = process.stdout
        stderr = process.stderr
        returncode = process.returncode
        
    except subprocess.TimeoutExpired as e:
        elapsed = timeout
        timed_out = True
        stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
        stderr = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""
        stderr += f"\n[TIMEOUT] La commande a dépassé le délai de {timeout} secondes"
        returncode = -1
        error_msg = f"Timeout après {timeout}s"
        
    except Exception as e:
        elapsed = time.time() - start_time
        stdout = ""
        stderr = f"Erreur d'exécution: {str(e)}"
        returncode = -2
        error_msg = str(e)
        
    else:
        elapsed = time.time() - start_time
    
    # Récupérer les métriques système après l'exécution
    end_disk_io = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
    end_mem = psutil.virtual_memory()
    cpu_times_end = psutil.cpu_times()
    cpu_percent_end = psutil.cpu_percent(interval=0.1)
    
    # Calcul des différences de métriques système
    system_metrics = {
        "platform": platform.platform(),
        "cpu": {
            "count": psutil.cpu_count(),
            "percent": {
                "start": cpu_percent_start,
                "end": cpu_percent_end,
                "delta": cpu_percent_end - cpu_percent_start
            },
            "times": {
                "user": cpu_times_end.user - cpu_times_start.user,
                "system": cpu_times_end.system - cpu_times_start.system,
                "idle": cpu_times_end.idle - cpu_times_start.idle
            }
        },
        "memory": {
            "total_mb": start_mem.total / (1024**2),
            "available_mb": {
                "start": start_mem.available / (1024**2),
                "end": end_mem.available / (1024**2),
                "delta": (end_mem.available - start_mem.available) / (1024**2)
            },
            "used_percent": {
                "start": start_mem.percent,
                "end": end_mem.percent,
                "delta": end_mem.percent - start_mem.percent
            }
        }
    }
    
    # Ajout des métriques d'I/O si disponibles
    if start_disk_io and end_disk_io:
        system_metrics["disk_io"] = {
            "read_mb": (end_disk_io.read_bytes - start_disk_io.read_bytes) / (1024**2),
            "write_mb": (end_disk_io.write_bytes - start_disk_io.write_bytes) / (1024**2),
            "read_count": end_disk_io.read_count - start_disk_io.read_count,
            "write_count": end_disk_io.write_count - start_disk_io.write_count
        }
    
    # Détermination du succès de l'exécution
    success = returncode == 0 and not timed_out
    if not success and check_output and stderr:
        if verbose:
            print(f"[!] Erreur: {stderr[:500]}{'...' if len(stderr) > 500 else ''}")
    
    # Construction du résultat complet
    result = {
        "command": cmd_str,
        "description": description,
        "cwd": cwd if cwd else os.getcwd(),
        "execution": {
            "start_time": start_datetime,
            "elapsed_seconds": elapsed,
            "returncode": returncode,
            "success": success,
            "timed_out": timed_out,
            "error": error_msg
        },
        "system": system_metrics,
        "output": {
            "stdout": stdout,
            "stderr": stderr,
            "stdout_lines": len(stdout.splitlines()) if stdout else 0,
            "stderr_lines": len(stderr.splitlines()) if stderr else 0
        },
        # Compatibilité avec le code existant
        "time": elapsed,
        "returncode": returncode,
        "output": stdout
    }
    
    # Affichage du résultat si verbose
    if verbose:
        _print_metrics_summary(result)
    
    # Journalisation des métriques si demandé
    if log_file:
        _append_to_log(result, log_file)
    
    return result


def run_batch_with_metrics(commands: List[Dict], 
                         global_timeout: Optional[float] = None,
                         log_file: Optional[str] = None,
                         continue_on_error: bool = False) -> List[Dict[str, Any]]:
    """
    Exécute une séquence de commandes avec métriques.
    
    Args:
        commands: Liste de dictionnaires contenant les paramètres pour run_with_metrics
        global_timeout: Timeout global pour l'ensemble des commandes
        log_file: Fichier pour journaliser les métriques
        continue_on_error: Continuer l'exécution même si une commande échoue
        
    Returns:
        Liste des résultats de chaque commande
    """
    results = []
    batch_start = time.time()
    
    for i, cmd_params in enumerate(commands):
        # Vérifier si on a dépassé le timeout global
        if global_timeout and (time.time() - batch_start) > global_timeout:
            if 'command' in cmd_params:
                cmd_str = cmd_params['command'] if isinstance(cmd_params['command'], str) else " ".join(cmd_params['command'])
                print(f"[!] Timeout global dépassé avant l'exécution de: {cmd_str}")
            break
        
        # Exécuter la commande
        result = run_with_metrics(**cmd_params)
        results.append(result)
        
        # Arrêter si erreur et continue_on_error est False
        if not result['execution']['success'] and not continue_on_error:
            print(f"[!] Arrêt du batch après échec de la commande {i+1}/{len(commands)}")
            break
    
    # Statistiques globales
    total_time = time.time() - batch_start
    success_count = sum(1 for r in results if r['execution']['success'])
    
    print(f"\n=== Résumé du batch ===")
    print(f"Commandes: {len(results)}/{len(commands)} exécutées")
    print(f"Réussites: {success_count}/{len(results)}")
    print(f"Temps total: {total_time:.2f}s")
    
    return results


def calculate_binary_entropy(filepath: str) -> float:
    """
    Calcule l'entropie de Shannon d'un fichier binaire.
    Une entropie plus élevée indique généralement plus d'obfuscation.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        
    Returns:
        Valeur d'entropie entre 0 et 8 (bits)
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        
        if not data:
            return 0
            
        # Calcul des fréquences
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
            
        # Calcul de l'entropie de Shannon
        entropy = 0.0
        for f in freq:
            if f > 0:
                p = f / len(data)
                entropy -= p * math.log2(p)
                
        return entropy
    except Exception as e:
        print(f"[!] Erreur lors du calcul d'entropie: {e}")
        return 0.0


def compare_binaries(original_path: str, modified_path: str, 
                   run_perf_test: bool = True) -> Dict[str, Any]:
    """
    Compare deux binaires et retourne des métriques de comparaison.
    
    Args:
        original_path: Chemin vers le binaire original
        modified_path: Chemin vers le binaire modifié
        run_perf_test: Exécuter les binaires pour comparer les performances
        
    Returns:
        Dictionnaire avec les métriques de comparaison
    """
    orig_size = os.path.getsize(original_path)
    mod_size = os.path.getsize(modified_path)
    
    orig_entropy = calculate_binary_entropy(original_path)
    mod_entropy = calculate_binary_entropy(modified_path)
    
    results = {
        "size": {
            "original": orig_size,
            "modified": mod_size,
            "delta_bytes": mod_size - orig_size,
            "delta_percent": ((mod_size - orig_size) / orig_size) * 100 if orig_size > 0 else float('inf')
        },
        "entropy": {
            "original": orig_entropy,
            "modified": mod_entropy,
            "delta": mod_entropy - orig_entropy,
            "delta_percent": ((mod_entropy - orig_entropy) / orig_entropy) * 100 if orig_entropy > 0 else float('inf')
        }
    }
    
    if run_perf_test and os.access(original_path, os.X_OK) and os.access(modified_path, os.X_OK):
        # Exécuter chaque binaire plusieurs fois pour obtenir une moyenne
        runs = 3
        orig_times = []
        mod_times = []
        
        for _ in range(runs):
            orig_result = run_with_metrics(
                f"./{os.path.basename(original_path)}", 
                cwd=os.path.dirname(original_path),
                verbose=False
            )
            orig_times.append(orig_result["execution"]["elapsed_seconds"])
            
            mod_result = run_with_metrics(
                f"./{os.path.basename(modified_path)}", 
                cwd=os.path.dirname(modified_path),
                verbose=False
            )
            mod_times.append(mod_result["execution"]["elapsed_seconds"])
        
        # Calculer les temps moyens
        orig_avg = sum(orig_times) / len(orig_times)
        mod_avg = sum(mod_times) / len(mod_times)
        
        results["performance"] = {
            "original_avg_time": orig_avg,
            "modified_avg_time": mod_avg,
            "delta_seconds": mod_avg - orig_avg,
            "delta_percent": ((mod_avg - orig_avg) / orig_avg) * 100 if orig_avg > 0 else float('inf'),
            "original_runs": orig_times,
            "modified_runs": mod_times
        }
    
    return results


def _print_metrics_summary(metrics: Dict[str, Any]) -> None:
    """Affiche un résumé formaté des métriques d'exécution"""
    status = "✓" if metrics["execution"]["success"] else "✗" 
    desc = f" - {metrics['description']}" if metrics.get('description') else ""
    
    print(f"\n{'-' * 60}")
    print(f"Résultat: {status} (code: {metrics['execution']['returncode']}){desc}")
    print(f"Temps: {metrics['execution']['elapsed_seconds']:.3f}s")
    
    if 'system' in metrics:
        if 'cpu' in metrics['system']:
            print(f"CPU: {metrics['system']['cpu']['percent']['delta']:.1f}% (variation)")
        
        if 'memory' in metrics['system']:
            mem_delta = metrics['system']['memory']['used_percent']['delta']
            mem_sign = "+" if mem_delta > 0 else ""
            print(f"Mémoire: {mem_sign}{mem_delta:.1f}% (variation d'utilisation)")
    
    if metrics["execution"]["timed_out"]:
        print(f"[!] TIMEOUT après {metrics['execution']['elapsed_seconds']:.1f}s")
    
    if not metrics["execution"]["success"]:
        print(f"[!] Erreur: {metrics['output']['stderr'][:250]}{'...' if len(metrics['output']['stderr']) > 250 else ''}")


def _append_to_log(metrics: Dict[str, Any], log_file: str) -> None:
    """Ajoute les métriques à un fichier de log au format JSON"""
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            # Ajouter timestamp pour le log
            log_entry = metrics.copy()
            log_entry["log_time"] = datetime.now().isoformat()
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"[!] Erreur d'écriture dans le fichier log: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple simple
    result = run_with_metrics("ls -la", description="Liste des fichiers")
    
    # Exemple avec batch
    commands = [
        {"command": "echo 'Test 1'", "description": "Premier test"},
        {"command": "sleep 2", "description": "Attente", "timeout": 3},
        {"command": "echo 'Fin des tests'", "description": "Finalisation"}
    ]
    batch_results = run_batch_with_metrics(commands, log_file="metrics_log.jsonl")
    
    # Exemple comparaison de binaires
    if os.path.exists("./original") and os.path.exists("./modified"):
        comparison = compare_binaries("./original", "./modified")
        print("\n=== Comparaison des binaires ===")
        print(f"Taille: {comparison['size']['delta_percent']:.2f}% ({comparison['size']['delta_bytes']} octets)")
        print(f"Entropie: {comparison['entropy']['delta_percent']:.2f}% ({comparison['entropy']['delta']:.4f} bits)")
        if 'performance' in comparison:
            print(f"Performance: {comparison['performance']['delta_percent']:.2f}% ({comparison['performance']['delta_seconds']:.4f}s)")


def calculate_binary_entropy(filepath: str) -> float:
    """
    Calcule l'entropie de Shannon d'un fichier binaire.
    Une entropie plus élevée indique généralement plus d'obfuscation.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        
    Returns:
        Valeur d'entropie entre 0 et 8 (bits)
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        
        if not data:
            return 0
            
        # Calcul des fréquences
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
            
        # Calcul de l'entropie de Shannon
        entropy = 0.0
        for f in freq:
            if f > 0:
                p = f / len(data)
                entropy -= p * math.log2(p)
                
        return entropy
    except Exception as e:
        print(f"[!] Erreur lors du calcul d'entropie: {e}")
        return 0.0


def compare_binaries(original_path: str, modified_path: str, 
                   run_perf_test: bool = True) -> Dict[str, Any]:
    """
    Compare deux binaires et retourne des métriques de comparaison.
    
    Args:
        original_path: Chemin vers le binaire original
        modified_path: Chemin vers le binaire modifié
        run_perf_test: Exécuter les binaires pour comparer les performances
        
    Returns:
        Dictionnaire avec les métriques de comparaison
    """
    orig_size = os.path.getsize(original_path)
    mod_size = os.path.getsize(modified_path)
    
    orig_entropy = calculate_binary_entropy(original_path)
    mod_entropy = calculate_binary_entropy(modified_path)
    
    results = {
        "size": {
            "original": orig_size,
            "modified": mod_size,
            "delta_bytes": mod_size - orig_size,
            "delta_percent": ((mod_size - orig_size) / orig_size) * 100 if orig_size > 0 else float('inf')
        },
        "entropy": {
            "original": orig_entropy,
            "modified": mod_entropy,
            "delta": mod_entropy - orig_entropy,
            "delta_percent": ((mod_entropy - orig_entropy) / orig_entropy) * 100 if orig_entropy > 0 else float('inf')
        }
    }
    
    if run_perf_test and os.access(original_path, os.X_OK) and os.access(modified_path, os.X_OK):
        # Exécuter chaque binaire plusieurs fois pour obtenir une moyenne
        runs = 3
        orig_times = []
        mod_times = []
        
        for _ in range(runs):
            orig_result = run_with_metrics(
                f"./{os.path.basename(original_path)}", 
                cwd=os.path.dirname(original_path),
                verbose=False
            )
            orig_times.append(orig_result["execution"]["elapsed_seconds"])
            
            mod_result = run_with_metrics(
                f"./{os.path.basename(modified_path)}", 
                cwd=os.path.dirname(modified_path),
                verbose=False
            )
            mod_times.append(mod_result["execution"]["elapsed_seconds"])
        
        # Calculer les temps moyens
        orig_avg = sum(orig_times) / len(orig_times)
        mod_avg = sum(mod_times) / len(mod_times)
        
        results["performance"] = {
            "original_avg_time": orig_avg,
            "modified_avg_time": mod_avg,
            "delta_seconds": mod_avg - orig_avg,
            "delta_percent": ((mod_avg - orig_avg) / orig_avg) * 100 if orig_avg > 0 else float('inf'),
            "original_runs": orig_times,
            "modified_runs": mod_times
        }
    
    return results


def _print_metrics_summary(metrics: Dict[str, Any]) -> None:
    """Affiche un résumé formaté des métriques d'exécution"""
    status = "✓" if metrics["execution"]["success"] else "✗" 
    desc = f" - {metrics['description']}" if metrics.get('description') else ""
    
    print(f"\n{'-' * 60}")
    print(f"Résultat: {status} (code: {metrics['execution']['returncode']}){desc}")
    print(f"Temps: {metrics['execution']['elapsed_seconds']:.3f}s")
    
    if 'system' in metrics:
        if 'cpu' in metrics['system']:
            print(f"CPU: {metrics['system']['cpu']['percent']['delta']:.1f}% (variation)")
        
        if 'memory' in metrics['system']:
            mem_delta = metrics['system']['memory']['used_percent']['delta']
            mem_sign = "+" if mem_delta > 0 else ""
            print(f"Mémoire: {mem_sign}{mem_delta:.1f}% (variation d'utilisation)")
    
    if metrics["execution"]["timed_out"]:
        print(f"[!] TIMEOUT après {metrics['execution']['elapsed_seconds']:.1f}s")
    
    if not metrics["execution"]["success"]:
        print(f"[!] Erreur: {metrics['output']['stderr'][:250]}{'...' if len(metrics['output']['stderr']) > 250 else ''}")


def _append_to_log(metrics: Dict[str, Any], log_file: str) -> None:
    """Ajoute les métriques à un fichier de log au format JSON"""
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            # Ajouter timestamp pour le log
            log_entry = metrics.copy()
            log_entry["log_time"] = datetime.now().isoformat()
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"[!] Erreur d'écriture dans le fichier log: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple simple
    result = run_with_metrics("ls -la", description="Liste des fichiers")
    
    # Exemple avec batch
    commands = [
        {"command": "echo 'Test 1'", "description": "Premier test"},
        {"command": "sleep 2", "description": "Attente", "timeout": 3},
        {"command": "echo 'Fin des tests'", "description": "Finalisation"}
    ]
    batch_results = run_batch_with_metrics(commands, log_file="metrics_log.jsonl")
    
    # Exemple comparaison de binaires
    if os.path.exists("./original") and os.path.exists("./modified"):
        comparison = compare_binaries("./original", "./modified")
        print("\n=== Comparaison des binaires ===")
        print(f"Taille: {comparison['size']['delta_percent']:.2f}% ({comparison['size']['delta_bytes']} octets)")
        print(f"Entropie: {comparison['entropy']['delta_percent']:.2f}% ({comparison['entropy']['delta']:.4f} bits)")
        if 'performance' in comparison:
            print(f"Performance: {comparison['performance']['delta_percent']:.2f}% ({comparison['performance']['delta_seconds']:.4f}s)")

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
    
    print(f"clang -emit-llvm -S -O1 -Xclang -disable-llvm-passes {source_file} -o {clair_ll}")
    run_with_metrics(f"clang -emit-llvm -S -O1 -Xclang -disable-llvm-passes {source_file} -o {clair_ll}")
    
    print(f"clang -O1 {source_file} -o {clair_bin}")
    run_with_metrics(f"clang -O1 {source_file} -o {clair_bin}")

    # Obfuscation
    print("\n[+] Application de la passe d'obfuscation...")
    cmd = f"opt -load-pass-plugin {pass_so} -passes='{pass_name}' -S {clair_ll} -o {obf_ll}"
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
