#!/usr/bin/env python3
import os
import shutil
import stat
from pathlib import Path

# === Fonctions utilitaires ===

def remove_dir_content(path):
    """Supprime tous les fichiers et sous-dossiers d'un dossier donné"""
    p = Path(path)
    if p.exists() and p.is_dir():
        for item in p.iterdir():
            if item.is_dir():
                shutil.rmtree(item, onerror=on_rm_error)
            else:
                try:
                    item.unlink()
                except Exception as e:
                    print(f"Erreur lors de la suppression de {item}: {e}")

def on_rm_error(func, path, exc_info):
    """Handler pour les erreurs de permission (par exemple en cas de fichiers protégés)"""
    os.chmod(path, stat.S_IWRITE)
    os.remove(path)

def delete_objects_and_binaries(root_dir):
    """Supprime les fichiers .o et exécutables dans un dossier et ses sous-dossiers"""
    for path in Path(root_dir).rglob("*"):
        if path.is_file():
            if path.suffix == ".o" or os.access(path, os.X_OK) and not path.name.endswith(('.c', '.cpp', '.h', '.ll', '.json')):
                try:
                    path.unlink()
                except Exception as e:
                    print(f"Erreur lors de la suppression de {path}: {e}")

def clear_json_file(filepath):
    """Vide le contenu d'un fichier JSON s'il existe"""
    f = Path(filepath)
    if f.exists():
        try:
            f.write_text('{}\n')
        except Exception as e:
            print(f"Erreur lors du vidage de {f}: {e}")

# === Script principal ===

if __name__ == "__main__":
    print("[*] Nettoyage du projet...")

    # 1. Supprimer le contenu de sources/obfusque/
    print("  - Suppression du contenu de sources/obfusque/")
    remove_dir_content("sources/obfusque")

    # 2. Supprimer les fichiers .o et exécutables dans sources/
    print("  - Suppression des .o et exécutables dans sources/")
    delete_objects_and_binaries("sources")

    # 3. Supprimer le contenu de build/
    print("  - Suppression du contenu de build/")
    remove_dir_content("build")

    # 4. Supprimer le contenu de logs/
    print("  - Suppression du contenu de logs/")
    remove_dir_content("logs")

    # 5. Vider les fichiers benchmark_results.json et binaries_paths.json
    print("  - Vidage des fichiers JSON")
    clear_json_file("benchmark_results.json")
    clear_json_file("binaries_paths.json")

    print("[✓] Nettoyage terminé.")
