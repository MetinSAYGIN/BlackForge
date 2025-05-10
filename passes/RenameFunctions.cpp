#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct RenameFunctionsPass : public PassInfoMixin<RenameFunctionsPass> {
    bool shouldSkipFunction(Function &F) {
        // 1. Ne pas renommer 'main'
        if (F.getName() == "main")
            return true;

        // 2. Ne pas renommer les fonctions déjà préfixées
        if (F.getName().starts_swith("obf_"))
            return true;

        // 3. Ne pas renommer les fonctions externes (même si isDeclaration() échoue)
        if (F.getLinkage() == GlobalValue::ExternalLinkage || F.getLinkage() == GlobalValue::AvailableExternallyLinkage)
            return true;

        return false;
    }

    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        for (Function &F : M) {
            if (shouldSkipFunction(F))
                continue;

            // Renommage sécurisé
            std::string newName = "obf_" + F.getName().str();
            F.setName(newName);
            errs() << "Renamed: " << F.getName() << " → " << newName << "\n";
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