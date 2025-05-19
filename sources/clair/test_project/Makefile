# Makefile
CC = gcc
CFLAGS = -Wall -Wextra -std=c11
OBJ = main.o fonctions.o
EXEC = programme

all: $(EXEC)

$(EXEC): $(OBJ)
	$(CC) $(CFLAGS) -o $(EXEC) $(OBJ)

main.o: main.c fonctions.h
	$(CC) $(CFLAGS) -c main.c

fonctions.o: fonctions.c fonctions.h
	$(CC) $(CFLAGS) -c fonctions.c

clean:
	rm -f *.o $(EXEC)
