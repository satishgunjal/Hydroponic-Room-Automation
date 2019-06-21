# Hydroponic-Room-Automation

## What is Hydropnic?
- Hydroponics is a subset of hydroculture, which is a method of growing plants without soil by instead using water
- Hydroponic room is any room where hydroponic fodder is grown in controlled condition
- Hydroponic fodder is a cultivation of nutritious green fodder (grass) in water medium with added nutrients in it
- We can use seeds like Barley, Oats, Maize, Wheat, Jowar, Bajra to grow hydroponic fodder

## Why Automation is required?
- Since we are not using soil medium, to grow healthy fodder we have to control below important parameters
  Temperature
  Humidity
  Watering interval and time
  Ventilation
  Air circulation
- We cant maintain all above paramaters by mannual labour
- Using Raspberry pi and few sensors we can easily automate the whole process.

## List of material
- Raspberry Pi
- 5V 10A 8 channel relay (For resistive load)
- 5V 30A single relay baord (For indusctive load)
- Adafruit  DHT22 temperature & humidity sensor
- Optocoupler EL817
- USB hub
- 0.5 HP submersible water pump
- Four 60W exhaust fans
- Two 50W ventilation fan
- One 130W Air Cooler ( A.C is better than cooler)
- UPS (To save RPi from electricity outage and for safe shutdown)
  I have design my ouwn UPS but there are many solutions available in market

# How it works
- Please refer hydropnic.py for source code
- Raspberry pi will start the hydroponic.py on boot
- All the configurations and stats are stored in SQLite DB file (hydroponic.db)
- Table 'exhaustonofftime' contains timing for exhaust fans on and off state
- Table 'inletfanonofftime' conatins the timings for inlet fan on and off state
- Table 'pumponofftime' contains the timings for pump on and off state
- Table 'ventilationfanonofftime' contains the timings for ventilation fans on and off state
- Table 'deviceid' contains the details of the devices.
- Table 'sensors' contains the sensor details
- Table 'sensordata' in transactional table where all the sensor readings are stored
- Table 'pistats' is transactional table whwere pi usage details are stored.
- 

