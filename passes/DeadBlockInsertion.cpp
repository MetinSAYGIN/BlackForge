// DeadBlockInsertion.cpp
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct DeadBlockInsertion : public FunctionPass {
    static char ID;
    DeadBlockInsertion() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
        LLVMContext &Ctx = F.getContext();

        // On va ajouter un dead block à chaque fonction
        BasicBlock *deadBlock = BasicBlock::Create(Ctx, "dead_block", &F);
        IRBuilder<> builder(deadBlock);

        // Instructions sans effet
        Value *A = builder.getInt32(5);
        Value *B = builder.getInt32(7);
        Value *C = builder.CreateMul(A, B, "dead_mul");
        builder.CreateRet(C); // Retourne 35, mais jamais atteint

        // Ne branche PAS vers le dead block -> il est mort
        return true;
    }
};
}

char DeadBlockInsertion::ID = 0;
static RegisterPass<DeadBlockInsertion> X("insert-dead", "Insert a dead basic block");
