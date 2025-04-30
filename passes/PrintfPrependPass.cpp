#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"

using namespace llvm;

namespace {
struct PrintfPrependPass : public PassInfoMixin<PrintfPrependPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        // Récupère la fonction printf
        Function *printfFunc = M.getFunction("printf");
        if (!printfFunc) {
            errs() << "La fonction printf n'a pas été trouvée\n";
            return PreservedAnalyses::all();
        }

        // Parcours toutes les fonctions du module
        for (Function &F : M) {
            for (BasicBlock &BB : F) {
                for (auto it = BB.begin(); it != BB.end(); ++it) {
                    if (CallInst *callInst = dyn_cast<CallInst>(&*it)) {
                        if (callInst->getCalledFunction() == printfFunc) {
                            // Création d'un nouveau builder avant l'instruction actuelle
                            IRBuilder<> Builder(&*it);
                            
                            // Ajoute un printf("########") avant chaque appel printf
                            Value *formatStr = Builder.CreateGlobalStringPtr("########\n");
                            Builder.CreateCall(printfFunc, {formatStr});
                            
                            errs() << "Ajout de printf(\"########\") avant un printf existant.\n";
                        }
                    }
                }
            }
        }

        return PreservedAnalyses::all();
    }
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "PrintfPrependPass",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM, ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "printf-prepend") {
                        MPM.addPass(PrintfPrependPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
