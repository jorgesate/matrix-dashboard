#include <stdio.h>
#include <wiringPi.h>

#define R1 0 
#define G1 1
#define B1 3
#define R2 4
#define G2 5
#define B2 6
#define R12 26
#define G12 21
#define B12 22
#define R22 24
#define G22 23
#define B22 28
#define R13 15
#define G13 8
#define B13 9
#define R23 16
#define G23 25
#define B23 29
#define CLK 14
#define STB 7
#define OE 2

int main()
{
    if (wiringPiSetup() < 0)
        return 1;

    pinMode(R1, OUTPUT);
    pinMode(G1, OUTPUT);
    pinMode(B1, OUTPUT);
    pinMode(R2, OUTPUT);
    pinMode(G2, OUTPUT);
    pinMode(B2, OUTPUT);
    pinMode(R12, OUTPUT);
    pinMode(G12, OUTPUT);
    pinMode(B12, OUTPUT);
    pinMode(R22, OUTPUT);
    pinMode(G22, OUTPUT);
    pinMode(B22, OUTPUT);
    pinMode(R13, OUTPUT);
    pinMode(G13, OUTPUT);
    pinMode(B13, OUTPUT);
    pinMode(R23, OUTPUT);
    pinMode(G23, OUTPUT);
    pinMode(B23, OUTPUT);
    pinMode(CLK, OUTPUT);
    pinMode(STB, OUTPUT);
    pinMode(OE, OUTPUT);

    digitalWrite(OE, 1);
    digitalWrite(STB, 0);
    digitalWrite(CLK, 0);

    int MaxLed = 64;
    int C12[16] = {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
    int C13[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0};

    for (int l = 0; l < MaxLed; l++)
    {
        int y = l % 16;
        digitalWrite(R1, 0);
        digitalWrite(G1, 0);
        digitalWrite(B1, 0);
        digitalWrite(R2, 0);
        digitalWrite(G2, 0);
        digitalWrite(B2, 0);
        digitalWrite(R12, 0);
        digitalWrite(G12, 0);
        digitalWrite(B12, 0);
        digitalWrite(R22, 0);
        digitalWrite(G22, 0);
        digitalWrite(B22, 0);
        digitalWrite(R13, 0);
        digitalWrite(G13, 0);
        digitalWrite(B13, 0);
        digitalWrite(R23, 0);
        digitalWrite(G23, 0);
        digitalWrite(B23, 0);
        if (C12[y] == 1)
        {
            digitalWrite(R1, 1);
            digitalWrite(G1, 1);
            digitalWrite(B1, 1);
            digitalWrite(R2, 1);
            digitalWrite(G2, 1);
            digitalWrite(B2, 1);
            digitalWrite(R12, 1);
            digitalWrite(G12, 1);
            digitalWrite(B12, 1);
            digitalWrite(R22, 1);
            digitalWrite(G22, 1);
            digitalWrite(B22, 1);
            digitalWrite(R13, 1);
            digitalWrite(G13, 1);
            digitalWrite(B13, 1);
            digitalWrite(R23, 1);
            digitalWrite(G23, 1);
            digitalWrite(B23, 1);
        }
        if (l > MaxLed - 12)
        {
            digitalWrite(STB, 1);
        }
        else
        {
            digitalWrite(STB, 0);
        }
        digitalWrite(CLK, 1);
        delayMicroseconds(2);
        digitalWrite(CLK, 0);
    }
    digitalWrite(STB, 0);
    digitalWrite(CLK, 0);
    for (int l = 0; l < MaxLed; l++)
    {
        int y = l % 16;
        digitalWrite(R1, 0);
        digitalWrite(G1, 0);
        digitalWrite(B1, 0);
        digitalWrite(R2, 0);
        digitalWrite(G2, 0);
        digitalWrite(B2, 0);

        digitalWrite(R12, 0);
        digitalWrite(G12, 0);
        digitalWrite(B12, 0);
        digitalWrite(R22, 0);
        digitalWrite(G22, 0);
        digitalWrite(B22, 0);
        
        digitalWrite(R13, 0);
        digitalWrite(G13, 0);
        digitalWrite(B13, 0);
        digitalWrite(R23, 0);
        digitalWrite(G23, 0);
        digitalWrite(B23, 0);
        if (C13[y] == 1)
        {
            digitalWrite(R1, 1);
            digitalWrite(G1, 1);
            digitalWrite(B1, 1);
            digitalWrite(R2, 1);
            digitalWrite(G2, 1);
            digitalWrite(B2, 1);

            digitalWrite(R12, 1);
            digitalWrite(G12, 1);
            digitalWrite(B12, 1);
            digitalWrite(R22, 1);
            digitalWrite(G22, 1);
            digitalWrite(B22, 1);

            digitalWrite(R13, 1);
            digitalWrite(G13, 1);
            digitalWrite(B13, 1);
            digitalWrite(R23, 1);
            digitalWrite(G23, 1);
            digitalWrite(B23, 1);
        }
        if (l > MaxLed - 13)
        {
            digitalWrite(STB, 1);
        }
        else
        {
            digitalWrite(STB, 0);
        }
        digitalWrite(CLK, 1);
        delayMicroseconds(2);
        digitalWrite(CLK, 0);
    }
    digitalWrite(STB, 0);
    digitalWrite(CLK, 0);
}