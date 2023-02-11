
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);



char* ssid = "YOUS_SSID";
const char* password = "YOUR_SSID_PASSWORD";
const char* api_host = "YOUR_TUNNELED_HOST";
const char simboli[2][10] = {"BTCUSDT","ETHUSDT"};
//const char  simboli[2][10] = {"ETHUSDT","ETHUSDT"};
const int buzzerPin = 18; 



String richiesta(String endpoint){ 
  if (WiFi.status() == WL_CONNECTED) { //Check WiFi connection status
    HTTPClient http;    //Object of class HTTPClient
  
    http.begin(endpoint);  //Specify request destination
    int httpCode = http.GET();                 //Send the request
    String payload = http.getString();       //Get the response payload
  
    Serial.println(httpCode);   //Print HTTP return code
    Serial.println(payload);    //Print request response payload
  
    http.end();  //Close connection
    delay(2000);
    return payload;
  } else {
    String errore = "Error in WiFi connection";
    Serial.println("Error in WiFi connection");
    return errore;
  }
  
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(buzzerPin, OUTPUT);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  delay(2000);
  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
}

void loop() {
  
  int lunghezza_array = sizeof(simboli)/sizeof(simboli[0]);
  // put your main code here, to run repeatedly:
  for (int i = 0; i < lunghezza_array; i++){
    
    String endpoint_vwap_strat = String(api_host) + "/" + String(simboli[i]) + "/5m" + "/vwap_3";
    String endpoint_st_1h = String(api_host) + "/" + String(simboli[i]) + "/1h" + "/supertrend_strat";
    String endpoint_st_4h = String(api_host) + "/" + String(simboli[i]) + "/4h" + "/supertrend_strat";

    Serial.println(endpoint_st_4h);
    Serial.println(endpoint_st_1h);
    Serial.println(endpoint_vwap_strat);

    String bool_vwap = richiesta(endpoint_vwap_strat);
    String bool_st1 = richiesta(endpoint_st_1h);
    String bool_st4 = richiesta(endpoint_st_4h);

    if (bool_vwap == "true" || bool_st1 == "true" || bool_st4 == "true"){
      digitalWrite(buzzerPin, HIGH);
      delay(1000);
      // turn off buzzer for 1 second
      digitalWrite(buzzerPin, LOW);
      delay(1000);  digitalWrite(buzzerPin, HIGH);
      delay(1000);
      // turn off buzzer for 1 second
      digitalWrite(buzzerPin, LOW);
      delay(1000);  digitalWrite(buzzerPin, HIGH);
      delay(1000);
      // turn off buzzer for 1 second
      digitalWrite(buzzerPin, LOW);
      delay(1000);  
      Serial.println("GUARDA IL GRAFICO!!!!");


    }  
  
    String st_1h = String(simboli[i]) + String(" supertrend 1h: ") + bool_st1;
    String vwap_5m = String(simboli[i])+ String(+ " vwap: ") + bool_vwap;
    String st_4h = String(simboli[i]) + String(" supertrend 4h: ") + bool_st4;

    Serial.println(st_1h);
    Serial.println(st_4h);
    Serial.println(vwap_5m);  
    
    display.clearDisplay();

    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 10);
    
    display.println(st_1h);
    display.println(st_4h);
    display.println(vwap_5m);
    display.display();
    
  }
  delay(1000);
}
