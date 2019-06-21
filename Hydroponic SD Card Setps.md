## Raspbian Setup
- Installed Raspbian Strech Lite on 32 Gb SD Card. Followed Raspberry pi installation guide. https://www.raspberrypi.org/documentation/installation/installing-images/README.md
- Before putting card in RPI I have enabled it for wifi connection and enabled SSH. https://core-electronics.com.au/tutorials/raspberry-pi-zerow-headless-wifi-setup.html
- Create blank file 'ssh' this will enable remote login
- Create file 'wpa_supplicant.conf' for wifi ssid’s
- wpa_supplicant.conf file content:
```
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
    country=IN

    network={
            ssid="Nandanvan"
            psk="Nandanvan@1"
            key_mgmt=WPA-PSK
    }

    network={
            ssid="OnePlus3"
            psk="satish1234"
            key_mgmt=WPA-PSK
    }
```
- Note: After login, Can use command "sudo nano /etc/wpa_supplicant/wpa_supplicant.conf" toedit/update ssid’s
- Using command 'sudo raspi-config' update country, localisation, hostname, password, expand fileset.
- Interfacing Options" / "Pi Serial". It is then necessary to answer as follows:
       ```
   		 "Would you like a login shell to be accessible over serial?" - No
   		 "Would you like the serial port hardware to be enabled?" - Yes
       ```
- Reboot pi

## Development Setup
- Then Run below command
```
  sudo apt-get update
  sudo apt-get upgrade
  sudo apt-get install python-dev
  sudo apt-get install python-setuptools
  sudo easy_install rpi.gpio
```

## Sqlite3 installation
-- Ref http://raspberrywebserver.com/sql-databases/set-up-an-sqlite-database-on-a-raspberry-pi.html

## GPIO Connections
```

Device                                    RPI GPIO        PIN

Common ground                             GND             39
Common 3.3V                               3V3             17
exhaust fan 1 & 2- 1channel_5V_30Amp (1)  5               29
inlet fan 1 & 2- 1channel_5V_30Amp (2)    6               31
cooler 1- 8channel_5V_10Amp (3)           13              33
water pump 1- 1channel_5V_30Amp (4)       19              35
Am2303- Red                               3V3             17
Am2303- Black                             Ground          39
Am2303- Signal                            27              13
DHT22- Red                                3V3             17
DHT22- Black                              Ground          39
DHT22- Signal                             17              11
```

## DHT22 and Raspberry pi wiring
- Can use 3.3 or 5v. If wires are long then 5V is better

## AM2302 and Raspberry pi wiring
- Same like DHT22. Since there is a 5.1K resistor inside the sensor connecting VCC and DATA so you do not need any additional pullup resistors
- Adafruit AM2302 has three wires (Red: power(3.3v/ 5V), Black: Ground, Yellow: Signal (Any GPIO pin)
- Can use 3.3 or 5v. 
- If wires are long then 5V is better

## Installing Adafruit DHT Library
- Execute below commands from an appropriate location (ex. "/home/pi"):
```
  sudo apt-get install git
  git clone https://github.com/adafruit/Adafruit_Python_DHT.git
  cd Adafruit_Python_DHT
  sudo apt-get update
  sudo apt-get install build-essential python-dev python-openssl
  sudo python setup.py install
```
- Testing the library
  - First navigate to the examples folder by executing:
  - cd examples
  - Now to run the example on a Raspberry Pi with an AM2302 sensor connected to GPIO #7, execute:
  - sudo ./AdafruitDHT.py 2302 4
  - Now to run the example on a Raspberry Pi with an DHT22 sensor connected to GPIO #8, execute:
  - sudo ./AdafruitDHT.py 22 8
- Ref. https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated

## Pi Stats
- Install psutil using below commands
```
sudo apt-get install python-pip python-dev
sudo pip install psutil
```
- Ref. https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=22180

## Using 8 channel relay with external power supply
- Make sure your external power supply for relay is 5V and minimum 0.7A
- Connect +ve wire of external power supply and attach to JD-VCC pin of 8 Channel relay
- Connect -ve wire of external power supply and attach to Ground pin of 8 channel relay
- Connect jumper cable to VCC of 8 channel relay and 3.3V of RPI. This will allow RPI to turn on and off the switches.
- Ref. https://youtu.be/Ur0w7VeLX08
 
## Using Adafruit PiRTC - PCF8523 Real Time Clock for Raspberry Pi
- Set up I2C on your Pi
  - run sudo raspi-config and under Interfacing Options or Advanced select I2C and turn it on.
  - Reboot once you've done that with sudo reboot
- Verify Wiring (I2C scan)
  - Run below cmd to to install the helper software
    sudo apt-get install python-smbus i2c-tools
  - And then sudo i2cdetect -y 1 at the command line, you should see ID #68 show up - that's the address of the DS1307, PCF8523 or DS3231!
  - Since we are using PiRTC PCF8523. Run cmd ‘sudo nano /boot/config.txt’ and add  ‘dtoverlay=i2c-rtc,pcf8523’ at the end
  - Save it and run sudo reboot to start again. Log in and run sudo i2cdetect -y 1 to see the UU show up where 0x68 should be
  - Disable the "fake hwclock" which interferes with the 'real' hwclock
  ```
  sudo apt-get -y remove fake-hwclock
  sudo update-rc.d -f fake-hwclock remove
  sudo systemctl disable fake-hwclock
  ```  
  - Now with the fake-hw clock off, you can start the original 'hardware clock' script.
  - Run sudo nano /lib/udev/hwclock-set and comment out these three lines:
  ```
  #if [ -e /run/systemd/system ] ; then
  # exit 0
  #fi
  ```
  - Sync time from Pi to RTC
    - When you first plug in the RTC module, it's going to have the wrong time because it has to be set once. You can always read the time directly from the RTC with sudo hwclock -D -r
    - You can see, the date at first is invalid! You can set the correct time easily. First run ‘date’ to verify the time is correct. Plug in Ethernet or WiFi to let the Pi sync the right time from the Internet. Once that's done, run ‘sudo hwclock -w’ to write the time, and another ‘sudo hwclock -r’ to read the time
  - Ref. https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-up-and-test-i2c
    http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
    
 ## Using UPS
 - Ref. https://github.com/satishgunjal/UPS-for-Pi.git
  






