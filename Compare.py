#!/usr/bin/env python3
import os
import subprocess
import time
import math
import json
import statistics

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

def run_benchmark(binary_path, runs=5):
    """Exécute un binaire plusieurs fois et retourne les métriques"""
    times = []
    cwd = os.path.dirname(binary_path)
    binary_name = os.path.basename(binary_path)
    
    for _ in range(runs):
        start = time.time()
        subprocess.run(
            f"./{binary_name}",
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        elapsed = time.time() - start
        times.append(elapsed)
    
    return {
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0
    }

def get_binary_segments(path):
    """Retourne la taille des segments ELF avec `size`"""
    try:
        result = subprocess.run(["size", path], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        if len(lines) < 2:
            return {}
        headers = lines[0].split()
        values = lines[1].split()
        
        segment_sizes = {}
        for header, val in zip(headers, values):
            try:
                segment_sizes[header] = int(val, 0)  # base auto : 10 ou 16
            except ValueError:
                segment_sizes[header] = 0
        return segment_sizes
    except subprocess.CalledProcessError:
        return {}

def compare_binaries(clair_path, obf_path):
    """Compare les deux binaires et affiche les résultats"""
    clair_size = os.path.getsize(clair_path)
    obf_size = os.path.getsize(obf_path)
    clair_entropy = calculate_entropy(clair_path)
    obf_entropy = calculate_entropy(obf_path)

    clair_segments = get_binary_segments(clair_path)
    obf_segments = get_binary_segments(obf_path)

    print("\n[+] Benchmark du binaire clair...")
    clair_perf = run_benchmark(clair_path)
    print("[+] Benchmark du binaire obfusqué...")
    obf_perf = run_benchmark(obf_path)

    size_diff = obf_size - clair_size
    size_diff_pct = (size_diff / clair_size) * 100
    entropy_diff = obf_entropy - clair_entropy
    time_diff = obf_perf['avg_time'] - clair_perf['avg_time']
    time_diff_pct = (time_diff / clair_perf['avg_time']) * 100

    print("\n=== RÉSULTATS ===")
    print(">> Taille du binaire final (fichier compilé)")
    print(f"Clair    : {clair_size / 1024:.2f} Ko")
    print(f"Obfusqué : {obf_size / 1024:.2f} Ko ({size_diff_pct:+.2f}%)")

    print("\n>> Taille des segments ELF (mémoire utile)")
    for seg in clair_segments:
        obf_val = obf_segments.get(seg, 0)
        clair_val = clair_segments[seg]
        delta = obf_val - clair_val
        delta_pct = (delta / clair_val * 100) if clair_val > 0 else 0
        print(f"{seg:<6} : {clair_val} → {obf_val} ({delta:+} | {delta_pct:+.2f}%)")

    print("\n>> Entropie du binaire (aléa du contenu)")
    print(f"Clair    : {clair_entropy:.4f}")
    print(f"Obfusqué : {obf_entropy:.4f} ({entropy_diff:+.4f})")

    print("\n>> Temps d'exécution moyen (5 runs)")
    print(f"Clair    : {clair_perf['avg_time']:.4f}s (±{clair_perf['std_dev']:.4f})")
    print(f"Obfusqué : {obf_perf['avg_time']:.4f}s (±{obf_perf['std_dev']:.4f})")
    print(f"Différence : {time_diff:+.4f}s ({time_diff_pct:+.2f}%)")

    return {
        "clair": {
            "size": clair_size,
            "entropy": clair_entropy,
            "performance": clair_perf,
            "segments": clair_segments
        },
        "obf": {
            "size": obf_size,
            "entropy": obf_entropy,
            "performance": obf_perf,
            "segments": obf_segments
        },
        "diffs": {
            "size": size_diff,
            "size_pct": size_diff_pct,
            "entropy": entropy_diff,
            "time": time_diff,
            "time_pct": time_diff_pct
        }
    }

def main():
    if not os.path.exists("binaries_paths.json"):
        print("[!] Fichier binaries_paths.json introuvable. Exécutez d'abord blackforge.py")
        exit(1)
    
    with open("binaries_paths.json") as f:
        binaries = json.load(f)
    
    if not os.path.exists(binaries["clair_bin"]) or not os.path.exists(binaries["obf_bin"]):
        print("[!] Un des binaires est introuvable")
        exit(1)
    
    print(f"[+] Comparaison entre:")
    print(f"- Clair    : {binaries['clair_bin']}")
    print(f"- Obfusqué : {binaries['obf_bin']}")
    
    results = compare_binaries(binaries["clair_bin"], binaries["obf_bin"])
    
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n[+] Résultats sauvegardés dans benchmark_results.json")

if __name__ == "__main__":
    main()
