#include "llvm/IR/Function.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Type.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"

#include <map>
#include <vector>

using namespace llvm;

namespace {

struct ControlFlowFlatteningPass : PassInfoMixin<ControlFlowFlatteningPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        if (F.empty() || F.size() <= 1) return PreservedAnalyses::all();

        LLVMContext &Ctx = F.getContext();
        IRBuilder<> Builder(Ctx);

        std::vector<BasicBlock *> Blocks;

        // Skip entry block for now
        for (BasicBlock &BB : F) {
            if (&BB != &F.getEntryBlock()) {
                Blocks.push_back(&BB);
            }
        }

        if (Blocks.empty()) return PreservedAnalyses::all();

        // Create the switch variable in the entry block
        Builder.SetInsertPoint(&F.getEntryBlock(), F.getEntryBlock().getFirstInsertionPt());
        AllocaInst *SwitchVar = Builder.CreateAlloca(Type::getInt32Ty(Ctx), nullptr, "switchVar");
        Builder.CreateStore(ConstantInt::get(Type::getInt32Ty(Ctx), 0), SwitchVar);

        // Create dispatcher block
        BasicBlock *Dispatcher = BasicBlock::Create(Ctx, "dispatcher", &F);
        Builder.SetInsertPoint(Dispatcher);
        LoadInst *LoadSwitch = Builder.CreateLoad(Type::getInt32Ty(Ctx), SwitchVar);
        SwitchInst *Switch = Builder.CreateSwitch(LoadSwitch, Blocks[0], Blocks.size());

        // Map to assign each block an ID
        std::map<BasicBlock *, int> BlockIDs;
        int ID = 1;
        for (BasicBlock *BB : Blocks) {
            BlockIDs[BB] = ID++;
        }

        // Rewire control flow
        for (BasicBlock *BB : Blocks) {
            if (isa<ReturnInst>(BB->getTerminator())) continue;

            Builder.SetInsertPoint(BB->getTerminator());
            Instruction *TI = BB->getTerminator();

            if (BranchInst *BI = dyn_cast<BranchInst>(TI)) {
                if (BI->isConditional()) {
                    BasicBlock *TrueBB = BI->getSuccessor(0);
                    BasicBlock *FalseBB = BI->getSuccessor(1);

                    Builder.SetInsertPoint(BI);
                    Value *Cond = BI->getCondition();

                    // If true, jump to true block ID
                    Builder.CreateCondBr(
                        Cond,
                        BasicBlock::Create(Ctx, "", &F, Dispatcher),
                        BasicBlock::Create(Ctx, "", &F, Dispatcher)
                    );

                    // Cleanup
                    BI->eraseFromParent();
                } else {
                    BasicBlock *Target = BI->getSuccessor(0);
                    Builder.CreateStore(ConstantInt::get(Type::getInt32Ty(Ctx), BlockIDs[Target]), SwitchVar);
                    Builder.CreateBr(Dispatcher);
                    BI->eraseFromParent();
                }
            }
        }

        // Modify entry block to jump to dispatcher
        Builder.SetInsertPoint(F.getEntryBlock().getTerminator());
        Builder.CreateBr(Dispatcher);
        F.getEntryBlock().getTerminator()->eraseFromParent();

        // Populate switch cases
        ID = 1;
        for (BasicBlock *BB : Blocks) {
            Switch->addCase(ConstantInt::get(Type::getInt32Ty(Ctx), ID++), BB);
        }

        errs() << "[CFF] Control flow flattening applied to function: " << F.getName() << "\n";

        return PreservedAnalyses::none();
    }
};

} // namespace

extern "C" ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "ControlFlowFlatteningPass",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "control-flow-flattening") {
                        FPM.addPass(ControlFlowFlatteningPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
