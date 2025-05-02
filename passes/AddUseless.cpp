#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Constants.h"
#include "llvm/Support/RandomNumberGenerator.h"
#include "llvm/IR/RandomNumberGenerator.h"

using namespace llvm;

namespace {
struct AddUselessPass : public PassInfoMixin<AddUselessPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        Module *M = F.getParent();
        LLVMContext &Ctx = F.getContext();

        // Créer un générateur de nombres aléatoires par fonction
        std::unique_ptr<RandomNumberGenerator> RNG = M->createRNG(F.getName());

        for (auto &BB : F) {
            // 50% de chances d'ajouter une instruction inutile
            if (RNG->next() % 2 == 0) {
                IRBuilder<> Builder(&BB.front());

                // Crée deux constantes entières
                Value *C1 = Builder.getInt32(42);
                Value *C2 = Builder.getInt32(1337);

                // Addition inutile
                Value *Add = Builder.CreateAdd(C1, C2, "useless_add");

                // Empêche LLVM de l'éliminer trop facilement
                Builder.CreateCall(Intrinsic::getDeclaration(M, Intrinsic::donothing));
            }
        }

        return PreservedAnalyses::none(); // on modifie le code
    }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "AddUseless",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "AddUseless") {
                        FPM.addPass(AddUselessPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
