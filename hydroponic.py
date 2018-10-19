import RPi.GPIO as GPIO
import logging.config
from datetime import datetime
import time
import sys
import os
import json
import signal
import MySQLdb
from subprocess import PIPE, Popen
import psutil
import Adafruit_DHT

# When we stop the service using "systemctl stop" command, it sends a SIGTERM to the service
# 'handler' function will be called on SIGTERM signal and raise SystemExit exception
# SystemExit exception will be catched on main thread to cleanup work
def handler(signum, frame):
    logger.info("handler()> Got SIGTERM!")
    sys.exit(0) # raises a SystemExit exception
 
# Register a handler (function) for the SIGTERM signal
signal.signal(signal.SIGTERM, handler)

# Initialization for Humidity and Temperature
sensor  = Adafruit_DHT.DHT22
gpioPin = 4

# Initialization for Relay Board
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# store lastTempReading to calculate average of last 10 minutes of temp readings(2 readings)
lastTempReading = 0.0

# global varibale
# The 'global' keyword does not create a global variable. It is used to pull in a variable that already exists outside of its scope
iState = 'off'  # state of inlet fan.  on/off
eState = 'off'  # state of exhaust fan.  on/off
vState = 'off'  # state of ventilation fan.  on/off
pState = 'off'  # state of pump.  on/off
cState = 'off'  # state of cooler.  on/off

# dictionary objects to store select query results
sensorsDict = None
deviceIdDict = None
exhaustFanOnOffTimeDict = None
inletFanOnOffTimeDict = None
ventilationFanOnOffTimeDict = None
pumpOnOffTimeDict = None
gpioPinsDict = None

def setup_logging(default_path, default_level, env_key):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        
logger = logging.getLogger(__name__)
setup_logging('/home/pi/logging.json', logging.INFO, 'LOG_CFG')

def selSensors():
    global sensorDict
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("selSensors()> DB connection is open")
    # prepare a cursor object using cursor() method
    # By default the cursor() method returns a tuple so we are using mysql.cursor.DictCursor as the argument so our data will be  dictionary.
    cursor = db.cursor(MySQLdb.cursors.DictCursor)      
    try:
       # Execute the SQL command
       cursor.execute('SELECT * FROM sensors')
       sensorDict = cursor.fetchall()     
       logger.info("selSensors()> sensorDict= "+ str(sensorDict))      
    except Exception as e:
        logger.error("selSensors()>", exc_info = True)
    # disconnect from server
    db.close()
    logger.info("selSensors()> DB connection is closed")

def selDeviceId():
    global deviceIdDict
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("selDeviceId()> DB connection is open")
    # prepare a cursor object using cursor() method
    # By default the cursor() method returns a tuple so we are using mysql.cursor.DictCursor as the argument so our data will be  dictionary.
    cursor = db.cursor(MySQLdb.cursors.DictCursor)      
    try:
       # Execute the SQL command
       cursor.execute('SELECT * FROM deviceid')
       deviceIdDict = cursor.fetchall()     
       logger.info("selDeviceId()> deviceIdDict= "+ str(deviceIdDict))
       for pins in deviceIdDict:
           GPIO.setup(pins['pin'], GPIO.OUT)
           GPIO.output(pins['pin'], GPIO.HIGH)
           logger.info("selDeviceId()> " + str(pins['pin']) + " set as GPIO.OUT and  GPIO.HIGH")
    except Exception as e:
        logger.error("selDeviceId()>", exc_info = True)
    # disconnect from server
    db.close()
    logger.info("selDeviceId()> DB connection is closed")

def selExhaustFanOnOffTime():
    global exhaustFanOnOffTimeDict
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("selExhaustFanOnOffTime()> DB connection is open")
    # prepare a cursor object using cursor() method
    # By default the cursor() method returns a tuple so we are using mysql.cursor.DictCursor as the argument so our data will be  dictionary.
    cursor = db.cursor(MySQLdb.cursors.DictCursor)    
      
    try:
       # Execute the SQL command
       cursor.execute('SELECT * FROM exhaustfanonofftime')
       exhaustFanOnOffTimeDict = cursor.fetchall()  
       logger.info("selExhaustFanOnOffTime()> exhaustFanOnOffTimeDict= "+ str(exhaustFanOnOffTimeDict))   
    except Exception as e:
        logger.error("selExhaustFanOnOffTime()>", exc_info = True)
    # disconnect from server
    db.close()
    logger.info("selExhaustFanOnOffTime()> DB connection is closed")

def selInletFanOnOffTime():
    global inletFanOnOffTimeDict
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("selInletFanOnOffTime()> DB connection is open")
    # prepare a cursor object using cursor() method
    # By default the cursor() method returns a tuple so we are using mysql.cursor.DictCursor as the argument so our data will be  dictionary.
    cursor = db.cursor(MySQLdb.cursors.DictCursor)   
       
    try:
       # Execute the SQL command
       cursor.execute('SELECT * FROM inletfanonofftime')
       inletFanOnOffTimeDict = cursor.fetchall() 
       logger.info("selInletFanOnOffTime()> inletFanOnOffTimeDict= "+ str(inletFanOnOffTimeDict))  
    except Exception as e:
        logger.error("selInletFanOnOffTime()>", exc_info = True)
    # disconnect from server
    db.close()
    logger.info("selInletFanOnOffTime()> DB connection is closed")

def selVentilationFanOnOffTime():
    global ventilationFanOnOffTimeDict
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("selVentilationFanOnOffTime()> DB connection is open")
    # prepare a cursor object using cursor() method
    # By default the cursor() method returns a tuple so we are using mysql.cursor.DictCursor as the argument so our data will be  dictionary.
    cursor = db.cursor(MySQLdb.cursors.DictCursor)      
    try:
       # Execute the SQL command
       cursor.execute('SELECT * FROM ventilationfanonofftime')
       ventilationFanOnOffTimeDict = cursor.fetchall() 
       logger.info("selVentilationFanOnOffTime()> ventilationFanOnOffTimeDict= "+ str(ventilationFanOnOffTimeDict))
    except Exception as e:
        logger.error("selVentilationFanOnOffTime()>", exc_info = True)
    # disconnect from server
    db.close()
    logger.info("selVentilationFanOnOffTime()> DB connection is closed")

def selPumpOnOffTime():
    global pumpOnOffTimeDict
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("selPumpOnOffTime()> DB connection is open")
    # prepare a cursor object using cursor() method
    # By default the cursor() method returns a tuple so we are using mysql.cursor.DictCursor as the argument so our data will be  dictionary.
    cursor = db.cursor(MySQLdb.cursors.DictCursor)      
    try:
       # Execute the SQL command
       cursor.execute('SELECT * FROM pumponofftime')
       pumpOnOffTimeDict = cursor.fetchall()  
       logger.info("selPumpOnOffTime()> pumpOnOffTimeDict= "+ str(pumpOnOffTimeDict))
    except Exception as e:
        logger.error("selPumpOnOffTime()>", exc_info = True)
    # disconnect from server
    db.close()
    logger.info("selPumpOnOffTime()> DB connection is closed")

# here 'state' is to be state.
def startStopDevice(deviceName, deviceId, deviceGpioPin, state):
    try:
        if(state =='on'):
            GPIO.output(deviceGpioPin,GPIO.HIGH)
        else:
            GPIO.output(deviceGpioPin,GPIO.LOW)
        logger.info("startStopDevice()> "+ deviceName + " , device id- " +  deviceId + " (GPIO Pin: "+ str(deviceGpioPin) + ") is "+ state)
        query= '''INSERT INTO devicestate(timestamp, deviceid, state) VALUES (%s,%s,%s)'''
        values= (datetime.now(), deviceId,state)
        insertData(query,values)
    except Exception, e:
        logger.error("startStopDevice()>", exc_info = True)

def startCooler():
    try:
        global cState
        
        deviceIndex= deviceIds.index('C1')
        deviceGpioPin = gpioPins[deviceIndex]
        GPIO.output(deviceGpioPin,GPIO.HIGH)
        logger.info("startCooler()> Cooler C1 (Index: "+ str(deviceIndex) + ", GPIO Pin: "+ str(deviceGpioPin) + ") is started")
        cState = 'on'

        query= '''INSERT INTO devicestate(timestamp, deviceid, state) VALUES (%s,%s,%s)'''
        values= (datetime.now(), 'C1',cState)
        insertData(query,values)
    except Exception, e:
        logger.error("startCooler()>", exc_info = True)

def stopCooler():
    try:
        global cState       
        deviceIndex= deviceIds.index('C1')
        deviceGpioPin = gpioPins[deviceIndex]
        GPIO.output(deviceGpioPin,GPIO.LOW)
        logger.info("stopCooler()> Cooler C1 (Index: "+ str(deviceIndex) + ", GPIO Pin: "+ str(deviceGpioPin) + ") is stopped")
        cState = 'off'

        query= '''INSERT INTO devicestate(timestamp, deviceid, state) VALUES (%s,%s,%s)'''
        values= (datetime.now(), 'C1',cState)
        insertData(query,values)
    except Exception, e:
        logger.error("stostopCoolerpPump()>", exc_info = True)
    
def humidityAndTemp(sensorid,sensortype):
    global lastTempReading
    global cState
    try:
        # Try to grab a sensor reading.  Use the read_retry method which will retry up
        # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpioPin)

        # Un-comment the line below to convert the temperature to Fahrenheit.
        # temperature = temperature * 9/5.0 + 32

        # Note that sometimes you won't get a reading and the results will be null (because Linux can't
        # guarantee the timing of calls to read the sensor). If this happens try again!

        if humidity is not None and temperature is not None:
            temp= "{0:0.1f}".format(temperature)            
            relativeHumidity = "{0:0.1f}".format(humidity)
            logger.info("humidityAndTemp()> Temp= " + str(temp) + " , RH = " + str(relativeHumidity))  
            query= 'INSERT INTO sensordata(timestamp,sensorid, sensortype, temperature, humidity) VALUES (%s,%s,%s,%s,%s)'''
            values= (datetime.now(), sensorid, sensortype, temp, relativeHumidity)
            insertData(query,values)

            # At the start of program lastTempReading will always be 0
            if(lastTempReading != 0):
                avgTemp = (float(lastTempReading) + float(temp) ) / 2
            else:
                avgTemp = float(temp)
            logger.info("humidityAndTemp()> avgTemp= " + str(avgTemp))              
            logger.info("humidityAndTemp()> cState= " + cState) 
            lastTempReading = float(temp)

            if(avgTemp >= 32):
                if(cState == 'off'):
                    startCooler();
                    logger.info("humidityAndTemp()> Since temperature is more than or equal to 32 C, cooler started")
                else:
                    logger.info("humidityAndTemp()> Temperature is still on higher side, keeping cooler on")
            else:
                if(cState == 'on'):
                    stopCooler();
                    logger.info("humidityAndTemp()> Since temperature is less than 32 C, cooler stopped")
                else:
                    logger.info("humidityAndTemp()> Temperature is still on lower side, keeping cooler off")

        else:
            logger.warn("humidityAndTemp()> Failed to get reading")   
    except Exception, e:
        logger.error("humidityAndTemp()>", exc_info = True)

def insertData(query, values):
    # Open database connection
    db = MySQLdb.connect("localhost","root","admin@mysql","hydroponic" )
    logger.info("insertData()> DB connection is open")
    logger.info("insertData()> query= " + query)
    logger.info("insertData()> values= " + str(values))
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    try:
       # Execute the SQL command
       cursor.execute(query,values)
       # Commit your changes in the database
       db.commit()
       logger.info("insertData()> Data inserted successfully")
    except Exception as e:
        logger.error("insertData()>", exc_info = True)
        # Rollback in case there is any error
        db.rollback()
    # disconnect from server
    db.close()
    logger.info("insertData()> DB connection is closed")

def get_cpu_temperature():
    try:
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        return float(output[output.index('=') + 1:output.rindex("'")])
    except Exception, e:
        logger.error("insertPiStats()>", exc_info = True)

def insertPiStats():
    try:
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()      
        cpu_temperature = float(output[output.index('=') + 1:output.rindex("'")])
        logger.info("insertPiStats()> cpu_temperature= " + str(cpu_temperature) + " C")

        cpu_usage = psutil.cpu_percent()
        logger.info("insertPiStats()> cpu_usage= " + str(cpu_usage) + "%")

        ram = psutil.virtual_memory()
        ram_total = ram.total / 2**20 # MiB.
        ram_used = ram.used / 2**20
        ram_free = ram.available / 2**20
        ram_percent_used = ram.percent    
        logger.info("insertPiStats()> ram_total= " + str(round(ram_total)) + " MB, ram_used= " + str(round(ram_used)) + " MB, ram_free= " + str(round(ram_free)) + " MB, ram_percent_used= " + str(ram_percent_used) + " %")
        
        disk = psutil.disk_usage('/')
        disk_total = disk.total / 2**30     # GiB.
        disk_used = disk.used / 2**30
        disk_free = disk.free / 2**30
        disk_percent_used = disk.percent
        logger.info("insertPiStats()> disk_total= " + str(round(disk_total)) + ", disk_used= " + str(round(disk_used)) + ", ram_perdisk_freecent_used= " + str(round(disk_free)) + ", disk_percent_used= " + str(disk_percent_used))

        query= '''INSERT INTO pistats(timestamp, cputemp, cpuused, ramused, diskused) VALUES (%s,%s,%s,%s,%s)'''
        values= (datetime.now(), cpu_temperature, cpu_usage, ram_percent_used, disk_percent_used)
        insertData(query,values)
    except Exception, e:
        logger.error("insertPiStats()>", exc_info = True)

##Main Thread
try:
    selSensors()
    selDeviceId()
    selExhaustFanOnOffTime()
    selInletFanOnOffTime()
    selVentilationFanOnOffTime()
    selPumpOnOffTime()    

    counter = 0
    while True:	
        hourMinute = datetime.now().strftime('%H:%M')
        logger.info("Main()> hourMinute= "+ hourMinute)   	
    
        for t in exhaustFanOnOffTimeDict:
            if(hourMinute == t["hourminute"]):
                if(eState.lower().strip() != t['state'].lower().strip()):
                    for d in deviceIdDict:
                        if(d['type'].lower().strip()=='exhaustfan'):
                            startStopDevice(d['name'],d['id'],d['pin'], t['state'])
                            eState = t['state'].lower().strip()
                            logger.info("Main()> eState= "+ eState) 

        for t in inletFanOnOffTimeDict:
            if(hourMinute == t["hourminute"]):
                if(iState != t['state']):
                    for d in deviceIdDict:
                        if(d['type']=='inletfan'):
                            startStopDevice(d['name'],d['id'],d['pin'], t['state'])
                            iState = t['state']
                            logger.info("Main()> iState= "+ iState) 

        for t in ventilationFanOnOffTimeDict:
            if(hourMinute == t["hourminute"]):
                if(vState != t['state']):
                    for d in deviceIdDict:
                        if(d['type']=='ventilationfan'):
                            startStopDevice(d['name'],d['id'],d['pin'], t['state'])
                            vState = t['state']
                            logger.info("Main()> vState= "+ vState) 

        for t in pumpOnOffTimeDict:
            if(hourMinute == t["hourminute"]):
                if(pState != t['state']):
                    for d in deviceIdDict:
                        if(d['type']=='waterpump'):
                            startStopDevice(d['name'],d['id'],d['pin'], t['state'])
                            pState = t['state']
                            logger.info("Main()> pState= "+ pState)
              

        time.sleep(5)
        counter = counter + 1
        if(counter >= 60): # Measure temp, humidity and pi stats after every 5 minutes
            #humidityAndTemp(1,'DTH22');
            #humidityAndTemp(2,'DTH22');
            insertPiStats();
            counter = 0           

# End program cleanly with keyboard or sys.exit(0)
except KeyboardInterrupt:
    logger.info("Main()> Quit (Ctrl+C)")
except SystemExit:
    logger.info("Main()> Quit (SIGTERM)")

# Reset GPIO settings
GPIO.cleanup()
logger.info("Main()> **** END ****\n")
