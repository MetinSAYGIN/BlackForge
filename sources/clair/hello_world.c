#include <stdio.h>

// Fonction simple qui retourne la somme de deux entiers
int add(int a, int b) {
    return a + b;
}

// Fonction avec branchement conditionnel
void check_value(int x) {
    if (x > 10) {
        printf("Valeur élevée: %d\n", x);
    } else {
        printf("Valeur basse: %d\n", x);
    }
}

// Fonction avec boucle
void count_down(int start) {
    while (start > 0) {
        printf("%d...\n", start);
        start--;
    }
    printf("Partez!\n");
}

// Fonction principale
int main() {
    printf("Début du programme\n");
    
    int result = add(5, 7);
    printf("5 + 7 = %d\n", result);
    
    check_value(result);
    count_down(3);
    
    printf("Fin du programme\n");
    return 0;
}
