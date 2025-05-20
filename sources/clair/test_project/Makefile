# Makefile pour obfuscation LLVM
CC = clang
LLVM_BIN = $(shell dirname $$(which opt))/
CFLAGS = -Wall -Wextra -std=c11 -O1
OBJ = main.o fonctions.o
EXEC = test_project

# Variables d'obfuscation
ifndef PASS_NAME
$(error PASS_NAME must be specified (e.g. make obfuscate PASS_NAME=PrintfPrependPass))
endif
PASS_SO = $(PASS_NAME).so

# Règles classiques
all: $(EXEC)

$(EXEC): $(OBJ)
	$(CC) $(CFLAGS) -o $(EXEC) $(OBJ)

main.o: main.c fonctions.h
	$(CC) $(CFLAGS) -c main.c

fonctions.o: fonctions.c fonctions.h
	$(CC) $(CFLAGS) -c fonctions.c

# Obfuscation LLVM
IR_FILES = $(patsubst %.c,%.ll,$(wildcard *.c))
OBF_IR = $(EXEC)_obf.ll
OBF_OUT = $(EXEC)_obf

.PHONY: obfuscate
obfuscate: $(OBF_OUT)

$(OBF_OUT): $(OBF_IR)
	$(LLVM_BIN)opt -load $(PASS_SO) -$(PASS_NAME) < $< | $(LLVM_BIN)llc -filetype=obj -o $(EXEC)_obf.o
	$(CC) $(EXEC)_obf.o -o $@

$(OBF_IR): $(IR_FILES)
	$(LLVM_BIN)llvm-link $(IR_FILES) -o $@

%.ll: %.c
	$(CC) -emit-llvm -S $(CFLAGS) $< -o $@

clean:
	rm -f *.o $(EXEC) *.ll $(EXEC)_obf *.bc