#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Fonction avec beaucoup de boucles imbriquées et de blocs conditionnels
// qui sera significativement impactée par l'ajout d'instructions inutiles

void traitement_intensif(int taille) {
    int* tableau = (int*)malloc(taille * sizeof(int));
    
    // Initialisation du tableau
    for (int i = 0; i < taille; i++) {
        tableau[i] = rand() % 100;
    }
    
    // Traitement avec beaucoup de blocs de base
    for (int i = 0; i < taille; i++) {
        for (int j = 0; j < taille; j++) {
            if (tableau[i] < tableau[j]) {
                // Premier bloc conditionnel
                int temp = tableau[i];
                tableau[i] = tableau[j];
                tableau[j] = temp;
            } else if (tableau[i] == tableau[j] && i != j) {
                // Deuxième bloc conditionnel
                tableau[i]++;
            } else {
                // Troisième bloc conditionnel
                if (tableau[i] % 2 == 0) {
                    tableau[i] /= 2;
                } else {
                    tableau[i] = 3 * tableau[i] + 1;
                }
            }
        }
    }
    
    // Statistiques sur le tableau
    int somme = 0;
    int min = tableau[0];
    int max = tableau[0];
    
    for (int i = 0; i < taille; i++) {
        somme += tableau[i];
        
        if (tableau[i] < min) {
            min = tableau[i];
        }
        
        if (tableau[i] > max) {
            max = tableau[i];
        }
        
        // Traitements conditionnels supplémentaires
        if (i % 3 == 0) {
            // Bloc 1
            tableau[i] = tableau[i] ^ 0xFF;
        } else if (i % 3 == 1) {
            // Bloc 2
            tableau[i] = ~tableau[i];
        } else {
            // Bloc 3
            tableau[i] = (tableau[i] << 2) | (tableau[i] >> 30);
        }
    }
    
    // Affichage des résultats
    printf("Somme: %d\n", somme);
    printf("Min: %d\n", min);
    printf("Max: %d\n", max);
    printf("Moyenne: %.2f\n", (float)somme / taille);
    
    free(tableau);
}

int main(int argc, char *argv[]) {
    clock_t debut, fin;
    double temps_cpu;
    int taille = 1000; // Taille par défaut
    
    // Permet de changer la taille via un argument
    if (argc > 1) {
        taille = atoi(argv[1]);
    }
    
    srand(time(NULL));
    
    printf("Traitement d'un tableau de taille %d...\n", taille);
    
    debut = clock();
    traitement_intensif(taille);
    fin = clock();
    
    temps_cpu = ((double) (fin - debut)) / CLOCKS_PER_SEC;
    printf("Temps d'exécution: %.6f secondes\n", temps_cpu);
    
    return 0;
}