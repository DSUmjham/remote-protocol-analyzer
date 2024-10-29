#include <Arduino.h>
#include "nectransmitter.h"

// function helpers
#define RESET_PIN 4
#define SEND_PIN 7
#define DIT 300
#define DAH 900
#define PAUSE 1500

// RGB IR commands
#define ADDRESS 0x00
#define POWER 0x40
#define RED 0x58
#define GREEN 0x59
#define WHITE 0x44
#define BLUE 0x45

NECTransmitter necTransmitter(SEND_PIN);

void setup() {
	Serial.begin(115200);

	// set up reset button
	digitalWrite(RESET_PIN, HIGH);
	pinMode(RESET_PIN, OUTPUT);

	delay(200);
	Serial.println("Setting up the Arduino.");

	// turn on light and set to green
	necTransmitter.SendNEC(ADDRESS, POWER);
	necTransmitter.SendNEC(ADDRESS, GREEN);
}

void blink(int len, uint8_t color, bool last) {
	necTransmitter.SendNEC(ADDRESS, color);
	delay(len);

	if (!last) {
		necTransmitter.SendNEC(ADDRESS, POWER);
		delay(DIT);
		necTransmitter.SendNEC(ADDRESS, POWER);
		delay(10);
	}
}

void pause(int len) {
	necTransmitter.SendNEC(ADDRESS, WHITE);
	delay(len);
}

void loop() {
	char command = 0;
	if (Serial.available()) {
		command = Serial.read();
		Serial.write(command);
	}

	switch (command) {
		case '1':
			transmit();
			blink(DIT, GREEN, true);
			break;
		case '2':
			reset();
			break;
	}
}

void transmit() {
	Serial.println("Tx...");
	// D -..
	blink(DAH, BLUE, false);
	blink(DIT, BLUE, false);
	blink(DIT, BLUE, true);

	// S ...
	blink(DIT, WHITE, false);
	blink(DIT, WHITE, false);
	blink(DIT, WHITE, true);

	// U ..-
	blink(DIT, BLUE, false);
	blink(DIT, BLUE, false);
	blink(DAH, BLUE, true);
}

void reset() {
	Serial.println("Reset pressed...");
	delay(1000);
	digitalWrite(RESET_PIN, LOW);
}