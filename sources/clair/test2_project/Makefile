CC = clang
CFLAGS = -O1 -Wall -Wextra -std=c11

SRC = main.c fonctions.c
OBJ = main.o fonctions.o
LLS = main.ll fonctions.ll
EXEC = test2_project

.PHONY: all clean

all: $(EXEC)

$(EXEC): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

main.o: main.c operations.h
	$(CC) $(CFLAGS) -c main.c

operations.o: operations.c operations.h
	$(CC) $(CFLAGS) -c operations.c

clean:
	rm -f $(OBJ) $(EXEC)
