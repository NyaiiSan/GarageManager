#include <ESP8266WiFi.h>
#include <WiFiClient.h>

#include <U8g2lib.h>
#include <Wire.h>

#include <SPI.h>
#include <MFRC522.h>

// WIFI
#define WIFISSID "SGXY-1"
#define PASSWD  "SGXY666666"

// Socket
#define SERVER "192.168.1.168"
#define PORT 8777

// RFID
#define SS_PIN D8
#define RST_PIN D0

MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

// OLED
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, /* clock=*/ SCL, /* data=*/ SDA, /* reset=*/ U8X8_PIN_NONE); // All Boards without Reset of the Display

// ioInfo
char pin_state[5];

void wifi_init(){
  u8g2.drawStr(0,14,"Waiting WiFi..."); // 设置坐标 x=0，y=20 输出内容，0表示最左端
  u8g2.sendBuffer(); // 将缓存输出到屏幕

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFISSID,PASSWD); // change it to your ussid and password
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }

  u8g2.clearBuffer();
  u8g2.drawStr(0,14, "WiFi connected.");
  u8g2.sendBuffer(); // 将缓存输出到屏幕
}

// 初始化RFID
void rfid_init(){
  SPI.begin(); // 初始化SPI
 	rfid.PCD_Init(); // 初始化 MFRC522
 	rfid.PCD_DumpVersionToSerial();
    // 初始化key
 	for (byte i = 0; i < 6; i++) {
 			key.keyByte[i] = 0xFF;
 	}
}

// 初始化OLED
void oled_init(){
  u8g2.begin();
  u8g2.setFont(u8g2_font_lubB12_te); // 设置字体
}

// 初始化GPIO
void gpio_init(){
  pinMode(D3, INPUT);
  pinMode(D9, INPUT);
  pinMode(D10, INPUT);
  for(int i=0; i<5; i++){
    pin_state[i] = 0;
  }
}

// 扫描GPIO口
void io_scan(){
  pin_state[0] = digitalRead(D3);
  pin_state[1] = digitalRead(D10);
  pin_state[2] = digitalRead(D9);
}

// 扫描卡片ID
int scanCard(unsigned int *id){
  if ( ! rfid.PICC_IsNewCardPresent()){
    return -1;
  }
  // Verify if the NUID has been readed
  if ( ! rfid.PICC_ReadCardSerial())
    return -2;
  
  // 卡片类型
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  // Check is the PICC of Classic MIFARE type
  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI && piccType != MFRC522::PICC_TYPE_MIFARE_1K && piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    return -3;
  }
  *id = 0;
  char *p = (char *)id;
  for (byte i = 0; i < 4; i++) {
      *(p+i) = rfid.uid.uidByte[i];
  }
  // Halt PICC
  rfid.PICC_HaltA();
  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();

  return 0;
}

// 初始化Socket连接
WiFiClient tcpInit(){
  WiFiClient client;
  if (client.connect(SERVER, PORT))//连接的IP地址和
  {
    client.setTimeout(500);
  }
  return client;
}

// 在屏幕上显示一个字符串
void showStr(String str, int line){
  char buf[64];
  int y = 16 * line;
  strcpy(buf, str.c_str());
  char *p = buf, *q = buf;
  while(*p != '\0'){
    if(*p == '\n'){
      *p = '\0';
      u8g2.drawStr(0, y, q);
      y += 16;
      q = p + 1;
    }
    p++;
  }
  u8g2.drawStr(0, y, q);
  u8g2.sendBuffer(); // 将缓存输出到屏幕
}

void setup() {
  oled_init();
  wifi_init();
 	rfid_init();
  gpio_init();
}

void loop() {

  WiFiClient client = tcpInit();

  while(client.connected()){
    // 设置本次循环延迟时间
    unsigned long dt = 800;
    // 清空显示
    u8g2.clearBuffer();

    // 显示IO口状态
    char io_str[4] = {0};
    for(int i=0; i<3; i++){
      io_str[i] = pin_state[i] ? '0' : '1';
    }
    u8g2.drawStr(0, 64, io_str);

    // 尝试读取卡片
    unsigned int id;
    char *p = (char *)&id;
    int scan_res = scanCard(&id);

    // 发送传感器shuju
    char io_data[16];
    char dp = 0;
    io_data[dp++] = 0x0c;
    // 获取传感器数据
    // 更新IO口数据
    io_scan();
    for(int i=0; i<3; i++){
      io_data[dp++] = pin_state[i] ? '0' : '1';
    }
    io_data[dp++] = 0x0c;
    io_data[dp++] = '\0';
    client.print(io_data);

    if(scan_res == 0){ // 如果读卡成功      
      // 生成卡号数据包
      char data[16];
      char dp = 0;
      data[dp++] = 0xc0;
      p = (char *)&id;
      for(int i=0; i<4; i++){
        data[dp++] = *(p+i);
      }
      data[dp++] = 0xc0;
      data[dp++] = '\0';

      // 向服务器发送
      // 连接服务器
      client.print(data);
      // 接收车辆信息并显示
      String recvStr = client.readString();
      while(recvStr.length() == 0){
        recvStr = client.readString();
      }
      client.print("get: " + recvStr);
      showStr(recvStr, 2);
      dt = 2000;
    }
    // 刷新屏幕
    u8g2.sendBuffer();
    // 延时
    delay(dt);

  }

  u8g2.clearBuffer();
  u8g2.drawStr(0, 14, "Con Lost");
  u8g2.sendBuffer();
  delay(3000);
}
