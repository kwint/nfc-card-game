#include <Arduino.h>
#include <MFRC522.h>
#include <SPI.h>

#define SS_PIN 15
#define RESET_PIN 0


MFRC522 nfc(SS_PIN, RESET_PIN);

void setup(){
    Serial.begin(115200);
    Serial.println("HELLO!!");
    SPI.begin();
    nfc.PCD_Init();

}

void loop(){
    if(! nfc.PICC_IsNewCardPresent()){
        return;
    }

    if(! nfc.PICC_ReadCardSerial()){
        return;
    }

    // nfc.PICC_DumpMifareUltralightToSerial();

    MFRC522::StatusCode status;

    byte buffer[18];
    byte buffer_len = 18;
    String data = "";


    for(byte page = 4; page < 16; page += 1){
        nfc.MIFARE_Read(page, buffer, &buffer_len);
        for(byte i=0; i < 4; i++){
            // Serial.print(buffer[i] < 0x10 ? " 0" : " ");
            // Serial.print(buffer[i], HEX);
            data.concat(String(buffer[i] < 0x10 ? " 0" : " "));
            data.concat(String(buffer[i], HEX));
        }
        // Serial.println();
    }


    Serial.println(data);
}