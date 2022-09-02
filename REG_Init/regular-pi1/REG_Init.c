#include <stdio.h>
#include <wiringPi.h>

#define R1 14
#define G1 29
#define B1 11
#define R2 10
#define G2 13
#define B2 12
#define CLK 0
#define STB 7
#define OE 1

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
        if (C12[y] == 1)
        {
            digitalWrite(R1, 1);
            digitalWrite(G1, 1);
            digitalWrite(B1, 1);
            digitalWrite(R2, 1);
            digitalWrite(G2, 1);
            digitalWrite(B2, 1);
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
        if (C13[y] == 1)
        {
            digitalWrite(R1, 1);
            digitalWrite(G1, 1);
            digitalWrite(B1, 1);
            digitalWrite(R2, 1);
            digitalWrite(G2, 1);
            digitalWrite(B2, 1);
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