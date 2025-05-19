// fonctions.c
#include <stdio.h>
#include "fonctions.h"

void dire_bonjour(const char *nom) {
    printf("Bonjour, %s !\n", nom);
}

int addition(int a, int b) {
    return a + b;
}
