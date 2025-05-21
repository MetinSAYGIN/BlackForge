#include "operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    srand(time(NULL));  // Initialisation du générateur aléatoire
    
    printf("Génération de 5 multiplications aléatoires :\n");
    effectuer_multiplications(5);
    
    return 0;
}
