#include "operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int generer_nombre_aleatoire(int min, int max) {
    return rand() % (max - min + 1) + min;
}

void effectuer_multiplications(int nombre) {
    for(int i = 1; i <= 5; i++) {
        int a = generer_nombre_aleatoire(1, 10);
        int b = generer_nombre_aleatoire(1, 10);
        printf("%d x %d = %d\n", a, b, a * b);
    }
}