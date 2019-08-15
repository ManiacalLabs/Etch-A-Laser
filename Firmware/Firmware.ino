#define ENCODER_OPTIMIZE_INTERRUPTS
#include "Encoder.h"

#define X_A 2
#define X_B 3
#define Y_A 11
#define Y_B 12


Encoder enc_x(X_A, X_B);
Encoder enc_y(Y_A, Y_B);

long x, y;


void setup()
{
    Serial.begin(115200);
}

void loop()
{
    if (Serial.available())
    {
        Serial.read();
        if(true){
            x = enc_x.read();
            y = enc_y.read();

            Serial.print(x);
            Serial.print(",");
            Serial.print(y);
            Serial.print("\n");

            // reset encoder values
            enc_x.write(0);
            enc_y.write(0);
        }

        Serial.flush();
    }
}
