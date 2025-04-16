#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"

using namespace llvm;

namespace {
struct DeadBlockInsertionPass : public PassInfoMixin<DeadBlockInsertionPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        errs() << "Running DeadBlockInsertion on function: " << F.getName() << "\n";
        // Ta logique d'obfuscation ici
        return PreservedAnalyses::all();
    }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "DeadBlockInsertion",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "insert-dead") {
                        FPM.addPass(DeadBlockInsertionPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
