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
        if (F.empty()) return PreservedAnalyses::all();

        Module *M = F.getParent();
        LLVMContext &Ctx = F.getContext();

        // 1. Préparer les éléments essentiels
        FunctionCallee PrintfFunc = M->getOrInsertFunction(
            "printf", FunctionType::get(Type::getInt32Ty(Ctx),
                      {Type::getInt8PtrTy(Ctx)}, true));

        // 2. Créer des variables globales opaques
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
        BasicBlock *EntryBB = &F.getEntryBlock();
        BasicBlock *DeadBB = BasicBlock::Create(Ctx, "dead_block", &F);
        BasicBlock *RealBB = EntryBB->splitBasicBlock(
            &EntryBB->front(), "real_code");

        // 4. Construction du bloc mort
        IRBuilder<> DeadBuilder(DeadBB);
        
        // a) Effet de bord impossible à supprimer
        Value *FormatStr = DeadBuilder.CreateGlobalStringPtr("DEAD_BLOCK_ACTIVATED\n");
        CallInst *PrintCall = DeadBuilder.CreateCall(PrintfFunc, {FormatStr});
        PrintCall->setCannotBeOmitted(true);

        // b) Opération mémoire opaque
        Value *CounterVal = DeadBuilder.CreateLoad(Type::getInt32Ty(Ctx), OpaqueCounter);
        Value *NewCounter = DeadBuilder.CreateAdd(CounterVal, DeadBuilder.getInt32(1));
        DeadBuilder.CreateStore(NewCounter, OpaqueCounter);

        // c) Boucle avec condition opaque
        BasicBlock *LoopBB = BasicBlock::Create(Ctx, "dead_loop", &F);
        DeadBuilder.CreateBr(LoopBB);

        IRBuilder<> LoopBuilder(LoopBB);
        Value *ShouldExit = LoopBuilder.CreateLoad(Type::getInt1Ty(Ctx), OpaqueCond);
        LoopBuilder.CreateCondBr(ShouldExit, RealBB, LoopBB);

        // 5. Modifier l'entrée originale
        IRBuilder<> EntryBuilder(&EntryBB->front());
        EntryBuilder.CreateStore(EntryBuilder.getInt1(false), OpaqueCond);
        EntryBuilder.CreateBr(DeadBB);

        // 6. Empêcher la suppression des éléments
        OpaqueCond->setUnnamedAddr(GlobalValue::UnnamedAddr::None);
        OpaqueCounter->setUnnamedAddr(GlobalValue::UnnamedAddr::None);

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
                    if (Name == "dead-block-insert") {
                        FPM.addPass(DeadBlockInsertionPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
