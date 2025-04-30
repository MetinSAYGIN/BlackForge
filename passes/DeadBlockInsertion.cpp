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
#include "llvm/Transforms/Utils/BasicBlockUtils.h"

using namespace llvm;

namespace {
struct DeadBlockInsertionPass : public PassInfoMixin<DeadBlockInsertionPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        // Ne s'applique qu'aux fonctions non vides
        if (F.empty())
            return PreservedAnalyses::all();

        errs() << "[+] Insertion de dead block dans : " << F.getName() << "\n";

        LLVMContext &Ctx = F.getContext();
        Module *M = F.getParent();

        // Préparation de printf
        FunctionCallee PrintfFunc = M->getOrInsertFunction(
            "printf", FunctionType::get(IntegerType::getInt32Ty(Ctx),
                      PointerType::get(Type::getInt8Ty(Ctx), 0),
                      true);

        // Création d'une chaîne globale opaque
        GlobalVariable *GV = new GlobalVariable(
            *M, ArrayType::get(Type::getInt8Ty(Ctx), 14),
            true, GlobalValue::PrivateLinkage,
            ConstantDataArray::getString(Ctx, "Never reached\n", true),
            ".str.dead");

        // Création du bloc mort
        BasicBlock *DeadBlock = BasicBlock::Create(Ctx, "deadblock", &F);
        IRBuilder<> Builder(DeadBlock);
        
        // Construction d'un pointeur opaque vers la chaîne
        Value *Zero = ConstantInt::get(Type::getInt32Ty(Ctx), 0);
        Value *GEP = Builder.CreateInBoundsGEP(GV->getValueType(), GV, 
                                              {Zero, Zero}, "dead.str.ptr");
        
        // Appel à printf avec des arguments opaques
        Builder.CreateCall(PrintfFunc, {GEP});
        Builder.CreateRetVoid();

        // Insertion d'une branche conditionnelle toujours fausse mais difficile à analyser
        BasicBlock &EntryBB = F.getEntryBlock();
        Instruction *FirstInst = &EntryBB.front();
        
        IRBuilder<> EntryBuilder(FirstInst);
        Value *GlobalAddr = EntryBuilder.CreatePtrToInt(GV, Type::getInt64Ty(Ctx));
        Value *Mask = EntryBuilder.getInt64(0xFFFFFFFF);
        Value *Cond = EntryBuilder.CreateICmpEQ(
            EntryBuilder.CreateAnd(GlobalAddr, Mask),
            EntryBuilder.getInt64(0));
        
        // Création d'un bloc intermédiaire qui mène au bloc mort
        BasicBlock *DummyBB = BasicBlock::Create(Ctx, "dummy", &F);
        BranchInst::Create(DeadBlock, DummyBB);
        
        // Remplacement de la première instruction par un branchement conditionnel
        BranchInst::Create(DummyBB, &EntryBB, Cond, FirstInst);
        FirstInst->eraseFromParent();

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
            
            // S'enregistre aussi pour s'exécuter après les optimisations
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel) {
                    MPM.addPass(createModuleToFunctionPassAdaptor(DeadBlockInsertionPass()));
                });
        }
    };
}
