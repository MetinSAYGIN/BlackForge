#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct RenameFunctionsPass : public PassInfoMixin<RenameFunctionsPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        for (Function &F : M) {
            // Ignorer les fonctions déclarées (externes), "main" et les fonctions qui commencent déjà par "obf_"
            if (F.isDeclaration() || F.getName() == "main" || F.getName().starts_with("obf_")) {
                continue;
            }

            // Générer un nouveau nom pour la fonction
            std::string oldName = F.getName().str();
            std::string newName = "obf_" + oldName;

            // Renommer la fonction
            F.setName(newName);
            errs() << "Renommé : " << oldName << " → " << newName << "\n";
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