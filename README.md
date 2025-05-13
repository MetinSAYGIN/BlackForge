# BlackForge

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Python-green.svg)
![LLVM](https://img.shields.io/badge/LLVM-compatible-orange.svg)

BlackForge is an advanced binary obfuscation framework that leverages LLVM passes to transform and protect your C/C++ source code. It provides comprehensive metrics and analysis to measure the effectiveness of various obfuscation techniques.

## 🛡️ Features

- **Custom LLVM Pass Integration**: Compile and apply your own LLVM obfuscation passes
- **Project & File Support**: Works with both individual source files and complete projects with Makefiles
- **Detailed Analysis**: Measures and compares key metrics between original and obfuscated binaries:
  - Binary size changes
  - Execution time impact
  - CPU utilization
  - Shannon entropy (obfuscation effectiveness)
- **Comprehensive Logging**: Detailed logs for debugging and analysis
- **Interactive Interface**: Simple CLI interface for selecting targets and passes

## 📋 Requirements

- Python 3.6+
- LLVM toolchain (clang, opt)
- psutil Python library
- C/C++ compiler toolchain
- make (for project mode)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BlackForge.git
cd BlackForge
```

2. Install Python dependencies:
```bash
pip install psutil
```

3. Ensure LLVM toolchain is installed:
```bash
# For Debian/Ubuntu
sudo apt-get install llvm clang
# For Fedora
sudo dnf install llvm clang
# For macOS
brew install llvm
```

## 📁 Project Structure

```
BlackForge/
├── BlackForge.py       # Main script
├── passes/             # LLVM obfuscation passes
│   ├── pass1.cpp
│   ├── pass2.cpp
│   └── ...
├── sources/            # Source code to be obfuscated
│   ├── clair/          # Original source files
│   │   ├── project1/
│   │   ├── project2/
│   │   └── file.c
│   └── obfusque/       # Output obfuscated files
├── build/              # Compiled passes (.so files)
└── logs/               # Logs directory
```

## 🔧 Usage

Run the main script:

```bash
python BlackForge.py
```

Follow the interactive prompts to:
1. Choose a target (project or file)
2. Select an obfuscation pass
3. Wait for the obfuscation and analysis to complete

### For Individual Files

Individual C/C++ files can be placed directly in the `sources/clair/` directory.

### For Projects

Projects should be organized as directories inside `sources/clair/` with a Makefile that supports:
- Regular compilation
- `make clean`
- Generation of `.ll` files

The script will automatically add an `obfuscate` target to your Makefile if needed.

## 📊 Example Output

```
=== 📊 RÉSULTATS DE L'ANALYSE ===
+----------------+----------------+----------------+
| Métrique       | Binaire clair  | Binaire obfusqué |
+----------------+----------------+----------------+
| Taille (Ko)    |         12.50  |          16.24  |
| Temps (s)      |       0.0021   |        0.0043   |
| CPU (%)        |       2.50     |        3.75     |
| Entropie       |       5.6745   |        6.1243   |
+----------------+----------------+----------------+
| Variation (%)  |
| Taille:    29.92%
| Temps:    104.76%
| CPU:       50.00%
| Entropie:   7.93%
+----------------+
```

## 📝 Creating Custom Obfuscation Passes

1. Create a new C++ file in the `passes/` directory
2. Implement your pass using the LLVM Pass infrastructure
3. Run BlackForge and select your pass

Example of a simple pass structure:

```cpp
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

namespace {
  struct MyObfuscationPass : public PassInfoMixin<MyObfuscationPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
      // Implement your obfuscation logic here
      return PreservedAnalyses::none();
    }
  };
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "MyObfuscationPass", "v0.1",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "my-obfuscation-pass") {
            FPM.addPass(MyObfuscationPass());
            return true;
          }
          return false;
        });
    }
  };
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LLVM Project for their amazing compiler infrastructure
- All contributors who have helped shape this project

## 🔍 Use Cases

### Software Protection for Commercial Applications

BlackForge can be used to protect proprietary algorithms and intellectual property in commercial software:

```bash
# Obfuscate a key algorithm before shipping
$ python BlackForge.py 
[?] Sélectionnez un projet ou fichier source:
  0) [FICHIER] license_check.c
→ Choix (numéro): 0

[?] Sélectionnez une passe d'obfuscation:
  0) control_flow_flattening
  1) string_encryption
→ Choix (numéro): 1

[+] Compilation de la passe string_encryption...
...
=== 📊 RÉSULTATS DE L'ANALYSE ===
+----------------+----------------+----------------+
| Métrique       | Binaire clair  | Binaire obfusqué |
+----------------+----------------+----------------+
| Taille (Ko)    |          8.25  |          10.45  |
| Temps (s)      |       0.0015   |        0.0018   |
| Entropie       |       5.4532   |        6.2143   |
+----------------+----------------+----------------+
```

### Academic Research on Obfuscation Techniques

Researchers can use BlackForge to measure the effectiveness of different obfuscation techniques:

```bash
# Run multiple passes on the same file and compare results
$ python BlackForge.py  # Run with first pass
...
$ python BlackForge.py  # Run with second pass
...
$ python BlackForge.py  # Run with combined passes
...

# Compare the logs and metrics to evaluate effectiveness vs. performance impact
```

## 📝 To Do

* Improved integration with complex projects (with multiple source files)
* Implement a lightweight web interface for a more user-friendly experience
* Add batch processing mode for evaluating multiple passes at once
* Support for more diverse metrics and analysis tools
* Add pre-built common obfuscation passes library
