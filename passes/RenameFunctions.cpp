#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct RenameFunctionsPass : public PassInfoMixin<RenameFunctionsPass> {
    bool shouldRenameFunction(Function &F) {
        // 1. La fonction DOIT avoir un corps (sinon c'est une déclaration externe)
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

        // Si on arrive ici, la fonction est définie dans le module et peut être renommée
        return true;
    }

    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        for (Function &F : M) {
            if (!shouldRenameFunction(F))
                continue;

            std::string newName = "obf_" + F.getName().str();
            errs() << "Renaming: " << F.getName() << " → " << newName << "\n";
            F.setName(newName);
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