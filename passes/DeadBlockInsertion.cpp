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
#include "llvm/IR/Intrinsics.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"

using namespace llvm;

namespace {
struct DeadBlockInsertionPass : public PassInfoMixin<DeadBlockInsertionPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        // Logging pour le débogage
        errs() << "DeadBlockInsertion: Traitement de la fonction " << F.getName() << "\n";
        
        if (F.empty()) {
            errs() << "  La fonction est vide, ignorée\n";
            return PreservedAnalyses::all();
        }
        
        Module *M = F.getParent();
        LLVMContext &Ctx = F.getContext();
        
        // 1. Préparer printf correctement
        FunctionType *PrintfTy = FunctionType::get(
            Type::getInt32Ty(Ctx),
            {Type::getInt8PtrTy(Ctx)},  // Correction ici: c'est un pointeur de char, pas un char
            true /* variadic */);
        
        errs() << "  Configuration de printf\n";
        FunctionCallee PrintfFunc = M->getOrInsertFunction("printf", PrintfTy);
        
        // 2. Créer des variables globales opaques
        errs() << "  Création des variables globales\n";
        GlobalVariable *OpaqueCond = new GlobalVariable(
            *M, Type::getInt1Ty(Ctx), false,
            GlobalValue::PrivateLinkage,
            ConstantInt::getTrue(Ctx), "dead_cond");
        
        GlobalVariable *OpaqueCounter = new GlobalVariable(
            *M, Type::getInt32Ty(Ctx), false,
            GlobalValue::PrivateLinkage,
            ConstantInt::get(Type::getInt32Ty(Ctx), 0),
            "dead_counter");
        
        // 3. Créer la structure du bloc mort
        errs() << "  Création de la structure des blocs\n";
        BasicBlock *EntryBB = &F.getEntryBlock();
        BasicBlock *DeadBB = BasicBlock::Create(Ctx, "dead_block", &F);
        BasicBlock *RealBB = EntryBB->splitBasicBlock(
            EntryBB->getFirstNonPHI(), "real_code");
        
        // 4. Construction du bloc mort
        errs() << "  Construction du bloc mort\n";
        IRBuilder<> DeadBuilder(DeadBB);
        
        // a) Effet de bord persistant
        Value *FormatStr = DeadBuilder.CreateGlobalStringPtr("DEAD_BLOCK_ACTIVATED\n");
        CallInst *PrintCall = DeadBuilder.CreateCall(PrintfFunc, {FormatStr});
        PrintCall->setDoesNotThrow();
        
        // b) Opération mémoire opaque
        LoadInst *CounterVal = DeadBuilder.CreateLoad(Type::getInt32Ty(Ctx), OpaqueCounter);
        Value *NewCounter = DeadBuilder.CreateAdd(CounterVal, DeadBuilder.getInt32(1));
        DeadBuilder.CreateStore(NewCounter, OpaqueCounter);
        
        // c) Boucle avec condition opaque
        BasicBlock *LoopBB = BasicBlock::Create(Ctx, "dead_loop", &F);
        DeadBuilder.CreateBr(LoopBB);
        
        IRBuilder<> LoopBuilder(LoopBB);
        LoadInst *CondLoad = LoopBuilder.CreateLoad(Type::getInt1Ty(Ctx), OpaqueCond);
        LoopBuilder.CreateCondBr(CondLoad, RealBB, LoopBB);
        
        // 5. Modifier l'entrée originale
        errs() << "  Modification du bloc d'entrée\n";
        // Supprimer la branche d'origine
        EntryBB->getTerminator()->eraseFromParent();
        
        IRBuilder<> EntryBuilder(EntryBB);
        EntryBuilder.CreateStore(ConstantInt::getFalse(Ctx), OpaqueCond);
        EntryBuilder.CreateBr(DeadBB);
        
        errs() << "  Transformation terminée\n";
        return PreservedAnalyses::none();
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
                    if (Name == "DeadBlockInsertion") {
                        FPM.addPass(DeadBlockInsertionPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}