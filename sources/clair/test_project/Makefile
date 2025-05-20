# Makefile simple LLVM pour projet avec plusieurs fichiers

CC = clang
CFLAGS = -O1 -Wall -Wextra -std=c11

SRC = main.c fonctions.c
OBJ = main.o fonctions.o
LLS = main.ll fonctions.ll
EXEC = test_project

.PHONY: all clean ll

all: $(EXEC)

# Compilation exécutable
$(EXEC): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

# Compilation des .o
%.o: %.c %.h
	$(CC) $(CFLAGS) -c $< -o $@

# Pour main.c (sans header)
main.o: main.c
	$(CC) $(CFLAGS) -c main.c -o main.o

# Génération des fichiers LLVM IR (.ll)
ll: main.ll fonctions.ll

%.ll: %.c
	$(CC) -O1 -emit-llvm -S $< -o $@

clean:
	rm -f $(OBJ) $(EXEC) $(LLS)
