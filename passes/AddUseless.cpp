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
            
            // Itérer sur tous les blocs de base
            for (auto &BB : F) {
                IRBuilder<> builder(&BB);
                
                // Ajouter des instructions inutiles avec une probabilité de 50%
                if (distribution(generator) == 0) {
                    // Création d'une instruction inutile
                    builder.CreateAdd(builder.getInt32(0), builder.getInt32(0));
                    modified = true;
                }
            }
            
            return modified ? PreservedAnalyses::none() : PreservedAnalyses::all();
        }
    };
}

// Registering the pass for LLVM 19.x
extern "C" ::llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo() {
    return {
        .APIVersion = 0,
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