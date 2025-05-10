#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include <unordered_map>

using namespace llvm;

namespace {
struct RenameFunctionsPass : public PassInfoMixin<RenameFunctionsPass> {
    bool shouldRenameFunction(Function &F) {
        // 1. La fonction DOIT avoir un corps (sinon c'est une déclaration externe)
        // IMPORTANT: Ne pas renommer les fonctions déclarées mais non définies
        if (F.isDeclaration())
            return false;
            
        // 2. Ne pas renommer 'main' (optionnel, mais recommandé)
        if (F.getName() == "main")
            return false;
            
        // 3. Ne pas renommer les fonctions déjà obfusquées
        if (F.getName().starts_with("obf_"))
            return false;
            
        // 4. Ne pas renommer les fonctions intrinsèques LLVM (optionnel)
        if (F.getName().starts_with("llvm."))
            return false;
            
        // 5. Ne pas renommer les fonctions qui sont disponibles globalement
        // Les fonctions de bibliothèque standard ont typiquement un linkage externe
        if (F.hasExternalLinkage() && !F.hasExactDefinition()) {
            return false;
        }
        
        // 6. Vérifier si le nom est celui d'une fonction connue de la libc
        // Ici, plutôt que d'utiliser une liste préétablie, on vérifie l'origine
        // On peut examiner les métadonnées de debug pour savoir si la fonction vient
        // d'un fichier d'en-tête système
        if (const DISubprogram *SP = F.getSubprogram()) {
            if (const DIFile *File = SP->getFile()) {
                StringRef Filename = File->getFilename();
                StringRef Directory = File->getDirectory();
                // Si la fonction vient d'un répertoire système (/usr/include, etc.)
                // ou d'un en-tête standard (stdio.h, stdlib.h, etc.)
                if (Directory.contains("/usr/include") || 
                    Directory.contains("/usr/lib") ||
                    Filename.endswith(".h")) {
                    return false;
                }
            }
        }
            
        // Si on arrive ici, la fonction est définie dans le module et peut être renommée
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
            newF->getBasicBlockList().splice(newF->begin(), F->getBasicBlockList());
            
            // Remplacer tous les appels à l'ancienne fonction par des appels à la nouvelle
            // Cela inclut également les fonctions déclarées mais non définies
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