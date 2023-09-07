import serial
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os
import socket

DEBUG = False
MQTT = True
TCP = False

COMPORT = 'COM5'
TCPADDR = "10.0.10.100"
TCPPORT = 5555

print('MQTT - RDS')

if not DEBUG:
    if TCP:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((TCPADDR,TCPPORT))
    else:
        print('Trying to open serial port..')
        ser = serial.Serial(COMPORT,19200,timeout=5)
        print('Using serial port: '+ser.name)
else:
    print("RUNNING IN DEBUG MODE")

if MQTT:
    print('Connecting to mqtt: '+os.getenv("MQTTHOST"))
    mqttc = mqtt.Client(client_id='mqtt-rds', userdata=None, protocol=mqtt.MQTTv5, transport='tcp')
    mqttc.username_pw_set(os.getenv("MQTTUSER"), password=os.getenv("MQTTPASS"))
    mqttc.connect(os.getenv("MQTTHOST"))
    mqttc.subscribe("basic_status/site1")

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    
    try:
        jmsg = json.loads(msg)
    except:
        print("Error decoding json: "+msg)
        return
    
    #print("message topic=",message.topic)
    #TODO: change to site topics
    if('siteid' in jmsg and jmsg['siteid'] == 1):
        print("message received " ,msg)
        if('status' in jmsg and jmsg['status'] == "no running tests"):
            sendCommand('PS', "no test")
            getResp(True,True)
            sendCommand('RT1', "No running tests")
            getResp(True,True)
        if('PS' in jmsg):
            print("sending cmd(PS): "+jmsg['PS'])
            sendCommand('PS', jmsg['PS'][0:7])
            getResp(True,True)
        if('RT1' in jmsg):
            print("sending cmd(RT1): "+jmsg['RT1'])
            sendCommand('RT1', jmsg['RT1'][0:63])
            getResp(True,True)
        if('DPS1' in jmsg):
            print("sending cmd(DPS1): "+jmsg['DPS1'])
            sendCommand('DPS1', jmsg['DPS1'])
            getResp(True,True)
        if('name' in jmsg):
            print("sending name cmd(PS): "+jmsg['name'])
            sendCommand('PS', jmsg['name'])
            getResp(True,True)
        if('description' in jmsg):
            rt1 = jmsg['description']
            if('comment' in jmsg and len(jmsg['description'])+len(jmsg['comment']) < 64):
                rt1 = jmsg['description']+' - '+jmsg['comment']
                print("sending desc and comment cmd(RT1): "+rt1[0:63])
                sendCommand('RT1', rt1[0:63])
                getResp(True,True)
            else:
                print("sending description cmd(RT1): "+jmsg['description'])
                sendCommand('RT1', jmsg['description'][0:63])
                getResp(True,True)

if MQTT:
    mqttc.on_message=on_message         #attach function to callback
    mqttc.loop_start()                  #start the loop

def getResp(decode=False,printit=False):
    global sock
    if not DEBUG:
        if TCP:
            resp = sock.recv(1024)
            sock.close()
        else:
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
    global sock
    if not TCP:
        if not DEBUG:
            if(data == None):
                ser.write(cmd.encode()+b'\n\r')
            else:
                ser.write(cmd.encode()+b'='+data.encode()+b'\n\r')
        else:
            print("DEBUG: "+cmd+'='+data+'\n\r')
    else:
        if not DEBUG:
            '''
            try:
                if(sock.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT) == b''):
                    print("socket closed")
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((TCPADDR,TCPPORT))
                print("send cmd")
            except:
                print('Sock error')
            '''
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((TCPADDR,TCPPORT))
                
            if(data == None):
                sock.sendall(cmd.encode()+b'\n\r')
            else:
                sock.sendall(cmd.encode()+b'='+data.encode()+b'\n\r')
        else:
            print("DEBUG: "+cmd+'='+data+'\n\r')

while(True):
    cmd = input("Choose command (HELP, DPS1, CMD, Q, PS, RT1, TIME, DATE, EXIT): ")
    if(cmd == 'HELP' or cmd == 'h'):
        print('DPS1 (d): dynamic program name (text 255)')
        print('CMD (c): send command to RDS')
        print('Q (q): send quary command')
        print('PS (p): program name (text 8)')
        print('RT1 (r): radio text (text 64)')
        print('TIME: set time (text HH:MM)')
        print('DATE: set date (text dd.mm.yy)')
        print('EXIT (e): exit application')
        continue
    elif(cmd == 'DPS1' or cmd == 'd'):
        data = input("data:")
        sendCommand('DPS1',data)
    elif(cmd == 'CMD' or cmd == 'c'):
        com = input('command:')
        data = input("data:")
        sendCommand(com,data)
    elif(cmd == 'Q' or cmd == 'q'):
        data = input("query cmd:")
        sendCommand(data,None)
    elif(cmd == 'PS' or cmd == 'p'):
        data = input("data:")
        sendCommand('PS',data)
    elif(cmd == 'RT1' or cmd == 'r'):
        data = input("data:")
        sendCommand('RT1',data)
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
        if not DEBUG and not TCP:
            ser.close()
        if MQTT:    
            mqttc.loop_stop()
            mqttc.disconnect()
        exit()
    else:
        print("Unknown command: "+cmd)
        continue

    getResp(True,True)

'''
HELP
ADR, AF, AFCH, ALL, AT+I, CC, COMSPD, CT, DATE, DI, DPS, DPSx, DPSxEN, DPSxMOD, DPSxREP, DPS1ENQ, DPS2MSG, DTTMOUT, EAS..., ECC, ECCEN, ECHO, EON, EONxAF, EONxAFCH, EONxEN, EONxPI, EONxPS, EONxPSN, EONxPTY, EONxTA, EONxTP, EQTEXT1, EXTSYNC, G, GRPSEQ, H, I, IPA, HELP, INIT, LABPER, LIC, LEVEL, LTO, MEM ..., MJD, MS, MSGxx, MSGxxD, MSGLIST, PAC..., PHASE, PILOT, PI, PROGRAM, PS, PS_SCROLL, PSNMAIN, PSW, PTY, PTYN, PTYNEN, Rxxxxx,xx, RDS2MOD, RDSGEN, READWEB, RESET, RSTDPS, RT2MSG, RT2TYPE, RTP, RTPRUN, RTPER, RTTYPE, RTx, RTxEN, SCRLSPD, SEN, SETCMD, SETRDS, SETSPY, SET..., SHORTRT, SITE, SLIST, SPEED, SPSPER, STATUS, STORE, Sxxx, TA, TATMOUT, TEXT, TIME, TP, TPS, UDGx, UECP, VER, XCMD, xSNx, ??
+
'''