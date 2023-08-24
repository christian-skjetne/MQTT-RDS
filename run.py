import serial
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os

DEBUG = True

print('MQTT - RDS')
if not DEBUG:
    print('Trying to open serial port..')
    ser = serial.Serial('COM5',2400,timeout=5)
    print('Using serial port: '+ser.name)
else:
    print("RUNNING IN DEBUG MODE")

print('Connecting to mqtt: '+os.getenv("MQTTHOST"))
mqttc = mqtt.Client(client_id='mqtt-rds', userdata=None, protocol=mqtt.MQTTv5, transport='tcp')
mqttc.username_pw_set(os.getenv("MQTTUSER"), password=os.getenv("MQTTPASS"))
mqttc.connect(os.getenv("MQTTHOST"))
mqttc.subscribe("basic_status/rds")

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("message received " ,msg)
    try:
        jmsg = json.loads(msg)
    except:
        print("Error decoding json: "+msg)
        return
    
    #print("message topic=",message.topic)
    if('PS' in jmsg):#jmsg.has_key('PS')):
        print("sending cmd(PS): "+jmsg['PS'])
        sendCommand('PS', jmsg['PS'])
        getResp(True,True)
    if('RT1' in jmsg):
        print("sending cmd(RT1): "+jmsg['RT1'])
        sendCommand('RT1', jmsg['RT1'])
        getResp(True,True)
    if('DPS1' in jmsg):
        print("sending cmd(DPS1): "+jmsg['DPS1'])
        sendCommand('DPS1', jmsg['DPS1'])
        getResp(True,True)


mqttc.on_message=on_message         #attach function to callback
mqttc.loop_start()                  #start the loop

def getResp(decode=False,printit=False):
    if not DEBUG:
        resp = ser.read_until(b'\r\n\r\n')
        
        if(decode):
            if(printit):
                print(str(resp,'utf-8'))
            return str(resp,'utf-8')
        else:
            if(printit):
                print(resp)
            return resp
    return "DEBUG"
    
def sendCommand(cmd, data):
    if not DEBUG:
        ser.write(cmd.encode()+b'='+data.encode()+b'\n\r')
    else:
        print("DEBUG: "+cmd+'='+data+'\n\r')

while(True):
    cmd = input("Choose command (HELP, DPS1, PS, RT1, TIME, DATE, EXIT): ")
    if(cmd == 'HELP' or cmd == 'h'):
        print('DPS1 (d): dynamic program name (text 255)')
        print('PS (p): program name (text 8)')
        print('RT1 (r): radio text (text 255)')
        print('TIME: set time (text HH:MM)')
        print('DATE: set date (text dd.mm.yy)')
        print('EXIT (e): exit application')
        continue
    elif(cmd == 'DPS1' or cmd == 'd'):
        data = input("data:")
        sendCommand(cmd,data)
    elif(cmd == 'PS' or cmd == 'p'):
        data = input("data:")
        sendCommand(cmd,data)
    elif(cmd == 'RT1' or cmd == 'r'):
        data = input("data:")
        sendCommand(cmd,data)
    elif(cmd == 'TIME'):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        print('Setting time to: '+current_time)
        sendCommand('TIME',current_time)
    elif(cmd == 'DATE'):
        now = datetime.now()
        current_date = now.strftime("%d.%m.%y")
        print('Setting date to: '+current_date)
        sendCommand('DATE',current_date)
    elif(cmd == "EXIT" or cmd == "e"):
        if not DEBUG:
            ser.close()
        mqttc.loop_stop()
        exit()
    else:
        print("Unknown command: "+cmd)
        continue

    print(getResp(True))

