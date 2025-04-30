#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

namespace {
struct ControlFlowFlatteningPass : public PassInfoMixin<ControlFlowFlatteningPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        errs() << "Running Control Flow Flattening on function: " << F.getName() << "\n";
        // Ton obfuscation ici
        return PreservedAnalyses::all();
    }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "ControlFlowFlatteningPass",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "ControlFlowFlattening") {
                        FPM.addPass(ControlFlowFlatteningPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
