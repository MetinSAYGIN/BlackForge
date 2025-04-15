# BlackForge - LLVM C/C++ Obfuscator

**BlackForge** est un obfuscateur de code C/C++ basé sur **LLVM**. Il permet de transformer du code source en un binaire obfusqué difficile à analyser ou à décompiler. Ce projet vise à démontrer mes compétences en sécurité informatique, compilation et développement logiciel. 

### Fonctionnalités

- **Obfuscation du code source C/C++** via passes LLVM personnalisées.
- Support des cibles **x86_64**, **ARMv7**, et **AArch64**.
- Choix des passes d’obfuscation : **Control Flow Flattening**, **Opaque Predicates**, **Dead Code Insertion**, etc.
- Exécution rapide et fiable avec des résultats téléchargeables.
- **CLI** et **API** REST disponibles pour une intégration facile dans des outils CI/CD.

### Comment utiliser

1. Clonez ce repository.
2. Exécutez le script `build.sh` pour installer les dépendances.
3. Utilisez la CLI pour obfusquer un fichier C :

   ```bash
   ./blackforge.py -i input.c -t x86_64 -o output
