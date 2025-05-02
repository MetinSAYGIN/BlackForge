#include <random>
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Module.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"

using namespace llvm;

namespace {
    struct AddUseless : public PassInfoMixin<AddUseless> {
        PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
            // Générateur de nombres aléatoires
            std::random_device rd;
            std::default_random_engine generator(rd());
            std::uniform_int_distribution<int> distribution(0, 1);
            
            // Itérer sur tous les blocs de base (BasicBlocks)
            for (auto &BB : F) {
                IRBuilder<> builder(&BB);
                
                // Ajouter des instructions inutiles avec une probabilité de 50%
                if (distribution(generator) == 0) {
                    // Création d'une instruction inutile (ajout d'une addition inutile)
                    builder.CreateAdd(builder.getInt32(0), builder.getInt32(0));
                }
            }
            return PreservedAnalyses::all();
        }
    };
} // namespace

// Enregistrement du plugin - utilisation d'une approche compatible avec différentes versions
extern "C" LLVM_ATTRIBUTE_WEAK 
void llvmGetPassPluginInfo(PassPluginLibraryInfo &Info) {
    Info.APIVersion = LLVM_PLUGIN_API_VERSION;
    Info.PluginName = "AddUseless";
    Info.PluginVersion = LLVM_VERSION_STRING;
    Info.RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
        PB.registerPipelineParsingCallback(
            [](StringRef Name, FunctionPassManager &FPM,
               ArrayRef<PassBuilder::PipelineElement>) {
                if (Name == "AddUseless") {
                    FPM.addPass(AddUseless());
                    return true;
                }
                return false;
            });
    };
}