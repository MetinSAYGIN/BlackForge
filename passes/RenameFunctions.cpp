#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include <unordered_map>
#include <set>

using namespace llvm;

namespace {
struct RenameFunctionsPass : public PassInfoMixin<RenameFunctionsPass> {
    bool shouldRenameFunction(Function &F) {
        // 1. La fonction DOIT avoir un corps (sinon c'est une déclaration externe)
        // Les fonctions de bibliothèque sont généralement des déclarations externes
        if (F.isDeclaration()) {
            errs() << "Skipping declaration: " << F.getName() << "\n";
            return false;
        }
            
        // 2. Ne pas renommer 'main' (optionnel, mais recommandé)
        if (F.getName() == "main") {
            errs() << "Skipping main function\n";
            return false;
        }
            
        // 3. Ne pas renommer les fonctions déjà obfusquées
        if (F.getName().starts_with("obf_")) {
            errs() << "Skipping already obfuscated: " << F.getName() << "\n";
            return false;
        }
            
        // 4. Ne pas renommer les fonctions intrinsèques LLVM
        if (F.getName().starts_with("llvm.")) {
            errs() << "Skipping LLVM intrinsic: " << F.getName() << "\n";
            return false;
        }
            
        // 5. Liste explicite des fonctions C standard à ne JAMAIS renommer
        // Ajout d'une liste de noms de fonctions C standard les plus courantes
        static const std::set<std::string> cStdFunctions = {
            // Standard I/O
            "printf", "scanf", "puts", "gets", "putchar", "getchar", "fprintf", "fscanf",
            "fputc", "fgetc", "fputs", "fgets", "fopen", "fclose", "fread", "fwrite",
            "fseek", "ftell", "rewind", "fflush", "ferror", "feof", "clearerr", "remove",
            "rename",
            
            // String handling
            "strcpy", "strncpy", "strcat", "strncat", "strcmp", "strncmp", "strchr", "strrchr",
            "strstr", "strlen", "strerror", "strspn", "strcspn", "strpbrk", "strtok",
            
            // Memory management
            "malloc", "calloc", "realloc", "free", "memcpy", "memmove", "memset", "memcmp",
            "memchr",
            
            // Conversion
            "atoi", "atol", "atof", "strtol", "strtoul", "strtod", "strtof", "strtold",
            
            // Math
            "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "sinh", "cosh", "tanh",
            "exp", "log", "log10", "pow", "sqrt", "ceil", "floor", "fabs", "ldexp", "frexp",
            "modf", "fmod",
            
            // Utility
            "rand", "srand", "qsort", "bsearch", "abs", "labs", "div", "ldiv",
            
            // Time
            "time", "clock", "difftime", "mktime", "asctime", "ctime", "gmtime", "localtime",
            "strftime",
            
            // Environment
            "getenv", "system", "exit", "abort",
            
            // Signal handling
            "signal", "raise"
        };
        
        if (cStdFunctions.find(F.getName().str()) != cStdFunctions.end()) {
            errs() << "Skipping C standard function: " << F.getName() << "\n";
            return false;
        }
        
        // 6. Vérifier si c'est une fonction utilisateur ou non
        // Si la fonction a le type de linkage d'une fonction importée ou externe,
        // et qu'elle n'est pas dans notre module actuel, ne pas la renommer
        if (!F.hasLocalLinkage() && !F.hasInternalLinkage()) {
            if (F.getParent()->getFunction(F.getName())->isDeclaration()) {
                errs() << "Skipping external function: " << F.getName() << "\n";
                return false;
            }
        }
            
        // Si on arrive ici, la fonction est définie dans le module et peut être renommée
        errs() << "Will rename: " << F.getName() << "\n";
        return true;
    }

    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        // Première étape: Créer une carte des fonctions à renommer et leurs nouveaux noms
        std::unordered_map<Function*, std::string> functionRenameMap;
        
        // Identifier toutes les fonctions à renommer
        for (Function &F : M) {
            if (shouldRenameFunction(F)) {
                std::string newName = "obf_" + F.getName().str();
                functionRenameMap[&F] = newName;
            }
        }
        
        // Deuxième étape: Renommer les fonctions et mettre à jour tous les appels
        for (auto &renameInfo : functionRenameMap) {
            Function* F = renameInfo.first;
            std::string newName = renameInfo.second;
            
            errs() << "Renaming: " << F->getName() << " → " << newName << "\n";
            
            // Créer une nouvelle fonction avec le nouveau nom
            Function* newF = Function::Create(F->getFunctionType(),
                                             F->getLinkage(),
                                             newName,
                                             &M);
            
            // Copier les attributs de la fonction
            newF->copyAttributesFrom(F);
            
            // Déplacer les blocs de base de l'ancienne fonction à la nouvelle
            // Utiliser la méthode correcte pour manipuler les blocs de base
            newF->splice(newF->begin(), F);
            
            // Remplacer tous les appels à l'ancienne fonction par des appels à la nouvelle
            F->replaceAllUsesWith(newF);
            
            // Supprimer l'ancienne fonction
            F->eraseFromParent();
        }
        
        return PreservedAnalyses::none();
    }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "RenameFunctions",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM, ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "RenameFunctions") {
                        MPM.addPass(RenameFunctionsPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}