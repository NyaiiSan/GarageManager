#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <Ticker.h> 

#include <U8g2lib.h>
#include <Wire.h>

#include <SPI.h>
#include <MFRC522.h>

// WIFI
#define WIFISSID "SGXY-1"
#define PASSWD  "SGXY666666"

// Socket
#define SERVER "192.168.1.153"
#define PORT 8777

// RFID
#define SS_PIN D8
#define RST_PIN D0

MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

// OLED
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, /* clock=*/ SCL, /* data=*/ SDA, /* reset=*/ U8X8_PIN_NONE); // All Boards without Reset of the Display

// Timer
Ticker timer1;

// tcp Client
WiFiClient client;

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

// 初始化定时器
void timer_init(){
  timer1.attach(1, timer_cb);
}

// 同步传感器信息
void timer_cb(){
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
  if(client.connected()){
    client.print(io_data);
  }
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
    client.setTimeout(100);
  }
  else{
    
  }
  return client;
}

// 在屏幕上显示一个字符串
void showStr(String str){
  char buf[64];
  strcpy(buf, str.c_str());
  // 清空显示区域内容
  u8g2.setDrawColor(0);
  u8g2.drawBox(0, 17, 128, 48);
  u8g2.setDrawColor(1);

  // 分割字符串
  char *p = strtok(buf, "\n");
  int i = 0;
  while(p != NULL){
    u8g2.drawStr(0,32+i*16,p);
    p = strtok(NULL, "\n");
    i++;
  }
  u8g2.sendBuffer(); // 将缓存输出到屏幕
}

void setup() {
  oled_init();
  wifi_init();
 	rfid_init();
  timer_init();
  gpio_init();
}

void loop() {
  // 连接服务器
  client = tcpInit();
  while(client.connected()){
    // 设置本次循环延迟时间
    unsigned long dt = 500;
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
    if(scan_res == 0){ // 如果读卡成功

      // 显示卡片ID
      char id_str[16] = {0};
      for(int i=0; i<4; i++){
        sprintf(id_str+(i*3), "%02x ", *(p+i));
      }
      
      // 生成数据包
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
      if(client.connected()){
        client.print(data);
        // 接收车辆信息并显示
        char recv[16] = {0};
        strcpy(recv, client.readString().c_str()); 
        u8g2.drawStr(0, 32, recv);
        dt = 3000;
      }
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
