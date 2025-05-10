#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct RenameFunctionsPass : public PassInfoMixin<RenameFunctionsPass> {
    bool shouldSkipFunction(Function &F) {
        // 1. Ne jamais renommer 'main'
        if (F.getName() == "main")
            return true;

        // 2. Ne pas renommer les fonctions déjà obfusquées
        if (F.getName().starts_with("obf_"))
            return true;

        // 3. Ne pas renommer les fonctions externes/libc (3 vérifications redondantes)
        if (F.isDeclaration() || 
            F.getLinkage() == GlobalValue::ExternalLinkage || 
            F.hasExternalLinkage())
            return true;

        // 4. Protection supplémentaire pour les fonctions spéciales
        if (F.getName().starts_with("llvm.") ||  // Fonctions intrinsèques
            F.getName().starts_with("__"))       // Fonctions système
            return true;

        return false;
    }

    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        // D'abord vérifier qu'aucune fonction critique n'est touchée
        for (Function &F : M) {
            if ((F.getName() == "atoi" || F.getName() == "printf") && !shouldSkipFunction(F)) {
                errs() << "ERREUR: La fonction système '" << F.getName() 
                       << "' serait renommée par erreur!\n";
                return PreservedAnalyses::all();
            }
        }

        // Ensuite appliquer le renommage
        for (Function &F : M) {
            if (shouldSkipFunction(F))
                continue;

            std::string newName = "obf_" + F.getName().str();
            errs() << "Renommage OK: " << F.getName() << " → " << newName << "\n";
            F.setName(newName);
        }
        return PreservedAnalyses::none();
    }
};
} // namespace

/* Le reste du code (PassPluginInfo) reste identique */

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