#include <stdio.h>
#include <stdlib.h>

int somme(int a, int b) {
    return a + b;
}

int produit(int a, int b) {
    return a * b;
}

int main() {
    int x = 5, y = 3;
    printf("Somme : %d\n", somme(x, y));
    printf("Produit : %d\n", produit(x, y));
    return 0;
}
