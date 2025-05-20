# Makefile LLVM-compatible avec obfuscation

CC = clang
CFLAGS = -Wall -Wextra -std=c11 -O1
SRCS = main.c fonctions.c
OBJS = main.o fonctions.o
LL = programme.ll
OBF_LL = programme_obf.ll
EXEC = programme
OBF_EXEC = programme_obf

# Par défaut, compilation normale avec -O1
all: $(EXEC)

$(EXEC): $(OBJS)
	$(CC) $(CFLAGS) -o $(EXEC) $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Génération du fichier LLVM IR
$(LL): $(SRCS)
	$(CC) $(CFLAGS) -emit-llvm -S $(SRCS) -o $(LL)

# Application de la passe LLVM (à fournir dynamiquement)
obfuscate: $(LL)
	opt -load-pass-plugin $(PASS_SO) -passes='$(PASS_NAME)' -S $(LL) -o $(OBF_LL)
	$(CC) $(CFLAGS) $(OBF_LL) -o $(OBF_EXEC)

clean:
	rm -f *.o *.ll $(EXEC) $(OBF_EXEC)
