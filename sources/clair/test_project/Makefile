# Makefile pour obfuscation LLVM
CC = clang
CFLAGS = -Wall -Wextra -std=c11 -O1
OBJ = main.o fonctions.o
EXEC = programme

# Variables d'obfuscation (PASS_NAME à spécifier en ligne de commande)
PASS_NAME ?= 
PASS_SO = $(PASS_NAME).so       # Génération automatique du .so

# Règles classiques
all: $(EXEC)

$(EXEC): $(OBJ)
	$(CC) $(CFLAGS) -o $(EXEC) $(OBJ)

main.o: main.c fonctions.h
	$(CC) $(CFLAGS) -c main.c

fonctions.o: fonctions.c fonctions.h
	$(CC) $(CFLAGS) -c fonctions.c

# Obfuscation LLVM
IR_FILES = main.ll fonctions.ll
OBF_IR = $(EXEC).ll
OBF_OUT = $(EXEC)_obf

obfuscate: $(OBF_OUT)

$(OBF_OUT): $(OBF_IR)
	opt -load $(PASS_SO) -$(PASS_NAME) < $< | llc -filetype=obj -o $(EXEC)_obf.o
	$(CC) $(EXEC)_obf.o -o $@

$(OBF_IR): $(IR_FILES)
	llvm-link $(IR_FILES) -o $@

%.ll: %.c
	$(CC) -emit-llvm -S $(CFLAGS) $< -o $@

clean:
	rm -f *.o $(EXEC) *.ll $(EXEC)_obf
