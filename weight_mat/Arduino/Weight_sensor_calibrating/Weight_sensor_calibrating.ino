#include <HX711.h>

HX711 scale;
int calibrate = 10;
float vessel_weight;

void setup() {
//  Serial.begin(38400);
  Serial.begin(115200);
  //  Serial.println("HX711 Demo");
  //  Serial.println("Initializing the scale");
  // parameter "gain" is ommited; the default value 128 is used by the library
  // HX711.DOUT  - pin #3
  // HX711.PD_SCK - pin #2
  scale.begin(3, 2);
  scale.set_scale(-26.2); 
  //  scale.tare();
  // Serial.println("Readings:");
  vessel_weight = scale.get_units(calibrate);
}

void loop() {
  Serial.println(scale.get_units(1)-vessel_weight);
}
