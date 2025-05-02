#include <random>
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {
    struct AddUseless : public FunctionPass {
        static char ID;
        
        AddUseless() : FunctionPass(ID) {}
        
        bool runOnFunction(Function &F) override {
            // Générateur de nombres aléatoires
            std::random_device rd;
            std::default_random_engine generator(rd());
            std::uniform_int_distribution<int> distribution(0, 1);
            
            bool modified = false;
            
            // Itérer sur tous les blocs de base (BasicBlocks)
            for (auto &BB : F) {
                // Utiliser un IRBuilder pour insérer de nouvelles instructions
                IRBuilder<> builder(&BB);
                
                // Ajouter des instructions inutiles avec une probabilité de 50%
                if (distribution(generator) == 0) {
                    // Création d'une instruction inutile (ajout d'une addition inutile)
                    builder.CreateAdd(builder.getInt32(0), builder.getInt32(0));
                    modified = true;
                }
            }
            
            return modified; // Retourne vrai si la fonction a été modifiée
        }
    };
}

char AddUseless::ID = 0;

// Enregistrement de la passe pour qu'elle soit reconnue par opt
static RegisterPass<AddUseless> X("AddUseless", "Add useless instructions for obfuscation");

// Intégration avec le système de passes standard
static RegisterStandardPasses Y(
    PassManagerBuilder::EP_EarlyAsPossible,
    [](const PassManagerBuilder &Builder, legacy::PassManagerBase &PM) {
        PM.add(new AddUseless());
    }
);