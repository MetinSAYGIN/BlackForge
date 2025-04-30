#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/GlobalVariable.h"
#include "llvm/IR/Module.h"

using namespace llvm;

namespace {
struct DeadBlockInsertionPass : public PassInfoMixin<DeadBlockInsertionPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        // Ne s'applique que sur les fonctions avec au moins un bloc
        if (F.empty() || F.getReturnType()->isVoidTy() == false)
            return PreservedAnalyses::all();

        errs() << "[+] Insertion de dead block dans : " << F.getName() << "\n";

        LLVMContext &Ctx = F.getContext();
        Module *M = F.getParent();

        // Crée une chaîne constante globale
        Constant *NeverReachedStr = ConstantDataArray::getString(Ctx, "Never reached\n", true);
        GlobalVariable *GV = new GlobalVariable(
            *M, NeverReachedStr->getType(), true, GlobalValue::PrivateLinkage,
            NeverReachedStr, ".str.dead");

        // Crée un pointeur vers la chaîne
        Constant *Zero = ConstantInt::get(Type::getInt32Ty(Ctx), 0);
        Constant *Indices[] = {Zero, Zero};
        Constant *PrintfArg = ConstantExpr::getGetElementPtr(NeverReachedStr->getType(), GV, Indices);

        // Déclare printf s'il n'existe pas
        FunctionCallee PrintfFunc = M->getOrInsertFunction(
            "printf", FunctionType::get(IntegerType::getInt32Ty(Ctx),
                                        PointerType::get(Type::getInt8Ty(Ctx), 0), true));

        // Crée le bloc mort
        BasicBlock *DeadBlock = BasicBlock::Create(Ctx, "deadblock", &F);
        IRBuilder<> Builder(DeadBlock);
        Builder.CreateCall(PrintfFunc, {PrintfArg});
        Builder.CreateRetVoid();

        // C'est un dead block non connecté, donc ne sera jamais exécuté

        return PreservedAnalyses::none();
    }
};
} // namespace

// Point d'entrée pour LLVM
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "DeadBlockInsertion",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "DeadBlockInsertion") {
                        FPM.addPass(DeadBlockInsertionPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
