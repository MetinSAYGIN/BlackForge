# Makefile simple pour projet multi-fichiers
CC = gcc
CFLAGS = -Wall -Wextra -std=c11
OBJ = main.o operations.o
EXEC = multiplicateur

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