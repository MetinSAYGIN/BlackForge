#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct NoOpPass : public PassInfoMixin<NoOpPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        // Cette passe ne fait rien, elle préserve toutes les analyses.
        return PreservedAnalyses::all();
    }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "Nothing",  // Nom de la passe
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "NoOpPass") {
                        FPM.addPass(NoOpPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
