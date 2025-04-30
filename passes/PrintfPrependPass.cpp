#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/IRBuilder.h"

using namespace llvm;

namespace {
struct PrintfPrependPass : public PassInfoMixin<PrintfPrependPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        // Création d'un IRBuilder pour insérer de nouvelles instructions
        IRBuilder<> Builder(M.getContext());

        // Récupère la fonction printf
        Function *printfFunc = M.getFunction("printf");
        if (!printfFunc) {
            errs() << "La fonction printf n'a pas été trouvée\n";
            return PreservedAnalyses::all();
        }

        // Parcours toutes les fonctions du module
        for (Function &F : M) {
            for (BasicBlock &BB : F) {
                for (Instruction &I : BB) {
                    // Vérifie si l'instruction est un appel à printf
                    if (CallInst *callInst = dyn_cast<CallInst>(&I)) {
                        if (callInst->getCalledFunction() == printfFunc) {
                            // Ajoute un printf("########") avant chaque appel printf
                            // Création de l'instruction printf("########")
                            std::vector<Value *> args;
                            args.push_back(Builder.CreateGlobalStringPtr("########"));
                            Builder.SetInsertPoint(&BB, ++Builder.GetInsertPoint());
                            Builder.CreateCall(printfFunc, args);
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
                [](StringRef Name, FunctionPassManager &FPM, ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "PrintfPrependPass") {
                        FPM.addPass(PrintfPrependPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
