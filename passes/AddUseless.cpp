#include <random>
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"

using namespace llvm;

namespace {
    struct AddUseless : public PassInfoMixin<AddUseless> {
        PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
            // Générateur de nombres aléatoires
            std::random_device rd;
            std::default_random_engine generator(rd());
            std::uniform_int_distribution<int> distribution(0, 1);
            
            bool modified = false;
            
			for (auto &BB : F) {
				IRBuilder<> builder(&*BB.getFirstInsertionPt());

				// Force l’ajout (pour test)
				Value *zero = builder.getInt32(0);
				Value *sum = builder.CreateAdd(zero, zero, "AddUseless");

				// Empêcher la suppression : stocker dans un alloca
				AllocaInst *alloca = new AllocaInst(Type::getInt32Ty(F.getContext()), 0, "AddUseless", &*F.getEntryBlock().getFirstInsertionPt());
				builder.CreateStore(sum, alloca);

				modified = true;
			}

            
            return modified ? PreservedAnalyses::none() : PreservedAnalyses::all();
        }
    };
}

// Registering the pass for LLVM 19.x
extern "C" ::llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo() {
    return {
        .APIVersion = 1,
        .PluginName = "AddUseless",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "AddUseless") {
                        FPM.addPass(AddUseless());
                        return true;
                    }
                    return false;
                });
        }
    };
}