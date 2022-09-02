REG_Init_Demo:REG_Init.o
	gcc -Wall -o REG_Init_Demo REG_Init.o -lwiringPi -lm -std=gnu99
REG_Init.o: REG_Init.c 
	gcc -Wall -c REG_Init.c -lwiringPi -lm -std=gnu99
clean:
	rm REG_Init.o REG_Init_Demo