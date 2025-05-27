#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Type.h"

using namespace llvm;

namespace {
struct PrintfPrependPass : public PassInfoMixin<PrintfPrependPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
        Function *printfFunc = getOrCreatePrintf(M);
        if (!printfFunc) {
            errs() << "Failed to get printf function\n";
            return PreservedAnalyses::all();
        }

        for (Function &F : M) {
            if (&F == printfFunc) continue;

            for (BasicBlock &BB : F) {
                processBasicBlock(BB, printfFunc);
            }
        }

        return PreservedAnalyses::none();
    }

private:
    Function* getOrCreatePrintf(Module &M) {
        // Try different variants of printf names
        if (Function *f = M.getFunction("printf"))
            return f;
        if (Function *f = M.getFunction("__printf"))
            return f;

        // Declare printf if not found
        LLVMContext &Ctx = M.getContext();
        FunctionType *printfType = FunctionType::get(
            Type::getInt32Ty(Ctx),
            {PointerType::getUnqual(Type::getInt8Ty(Ctx))},
            true
        );
        return cast<Function>(M.getOrInsertFunction("printf", printfType).getCallee());
    }

    void processBasicBlock(BasicBlock &BB, Function *printfFunc) {
        SmallVector<Instruction*, 16> ToInsertBefore;

        for (Instruction &I : BB) {
            if (CallInst *callInst = dyn_cast<CallInst>(&I)) {
                Function *calledFunc = callInst->getCalledFunction();
                if (calledFunc && isOutputFunction(calledFunc->getName())) {
                    ToInsertBefore.push_back(&I);
                }
            }
        }

        for (Instruction *I : ToInsertBefore) {
            IRBuilder<> Builder(I);
            Value *formatStr = Builder.CreateGlobalStringPtr("########\n");
            Builder.CreateCall(printfFunc, {formatStr});
        }
    }

    bool isOutputFunction(StringRef name) {
        // Match printf and puts variants using correct LLVM 19 API
        return name == "printf" || 
               name == "__printf" ||
               name == "puts" ||
               name == "_IO_puts" ||
               name.starts_with("printf") ||
               name.starts_with("puts");
    }
};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "PrintfPrependPass",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM, ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "PrintfPrependPass") {
                        MPM.addPass(PrintfPrependPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
