from servo import PositionServo
from machine import Pin
import network, ubinascii
import time
import math
import mqtt

servo1 = PositionServo(15)
servo2 = PositionServo(14)
servo3 = PositionServo(13)
servo4 = PositionServo(12)
suction = Pin(0, mode=Pin.OUT)

servos = [servo1, servo2, servo3, servo4]
L = [6.5, 6.5]

#connect to wifi
ssid = 'Tufts_Wireless'
password = ''

def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print("MAC " + mac)
    
    station.connect(ssid, password)
    while not station.isconnected():
        time.sleep(1)
    print('Connection successful')
    print(station.ifconfig())
    
connect_wifi(ssid, password)
broker_address = "broker.hivemq.com"
client = mqtt.MQTTClient("Kelli's Pico", broker_address, keepalive=10000,port=1883)
client.connect()

def IK(Xe, Ye):
    angles_list = []
    d = 4.724 #center to center distance of link
    Xe_End = Xe - 1 #account for actual end being further in
    Ye_End = Ye - 1.6 #account for actual end being further in
    Theta_1 = 45 #just place holder this number does not matter 
    beta = math.atan(Ye_End/Xe_End)
    csquare = math.pow(Xe_End, 2) + math.pow(Ye_End, 2)
    inner3 = math.acos((2 * math.pow(d, 2) - csquare) / (2 * d * d))
    theta3 = math.pi - inner3
    if theta3 < 0:
        theta3 = abs(theta3)
    Theta_3 = round(math.degrees(theta3), 1)
    theta2 = beta + math.acos((csquare + math.pow(d, 2) - math.pow(d, 2)) / (2 * d * math.sqrt(csquare)))
    Theta_2 = round(math.degrees(theta2), 1)
        
    #set horizontal end effector
    if Xe <= 9:
        beta_Fake = math.atan(Ye/Xe)
        csquare_Fake = math.pow(Xe, 2) + math.pow(Ye, 2)
        inner3_Fake = math.acos((2 * math.pow(d, 2) - csquare_Fake) / (2 * d * d))
        theta2_Fake = beta + math.acos((csquare_Fake + math.pow(d, 2) - math.pow(d, 2)) / (2 * d * math.sqrt(csquare_Fake)))
        halfInner3 = inner3_Fake/2
        theta4 = math.pi - theta2_Fake - inner3_Fake
        Theta_4 = round(math.degrees(theta4), 1) + 100
    elif Xe < 10 and Xe > 9:
        Theta_4 = 130
    elif Xe >= 10 and Xe < 10.6:
        Theta_4 = 120
    elif Xe >= 10.6 and Xe < 10.8:
        Theta_4 = 110
    elif Xe >= 10.8 and Xe < 11:
        Theta_4 = 100
    else:
        Theta_4 = 90
        
    angles_list.append([Theta_1, Theta_2, Theta_3, Theta_4])
    print(angles_list)
    
    return angles_list #can just set servos in here instead of doing it in a main loop

def lowerArm(Xe, Ye, Angle):
    armAngles = (IK(Xe, Ye - 3.5))[0]
    armAngles[0] = Angle
    servo4.set_position(armAngles[3])
    set_servo_positions(armAngles, 1)

def suctionOn():
    suction.on()

def suctionOff():
    suction.off()

def raiseArm(Xe, Ye, Angle):
    armAngles = (IK(Xe, Ye))[0]
    armAngles[0] = Angle 
    set_servo_positions(armAngles, 1)
    
def set_servo_positions(angles, ramp_duration):
    for servo, angle in zip(servos, angles):
        print(f"Setting servo to angle: {angle}")
        servo.set_position(int(angle), ramp_duration)
    time.sleep(.1)  # Optional delay to observe the position

radius = 0
angle = 0
def whenCalled(topic, message):
    global radius, angle
    topic = topic.decode()
    message = message.decode()  
    if topic == "radius":
        radius = float(message)
        print(radius)
    elif topic == "angle":
        angle = float(message)
        print(angle)
    elif topic == 'mode':
        if message == "initialize":
            home = IK(1.8, 3)[0]
            home[0] = 90
            set_servo_positions(home, 0.01)
        if message == "work":
            print(radius)
            print(angle)
            piece = IK(radius, 3)[0]
            piece[0] = angle
            set_servo_positions(piece, 0.01)
        if message == "down":
            lowerArm(radius, 3, angle)
            suctionOn()
            time.sleep(3)
            raiseArm(radius, 3, angle)
            dropPiece = IK(9, 1.5)[0]
            dropPiece[0] = 55
            set_servo_positions(dropPiece, 1)
            suctionOff()

def main():
    home = IK(1.8, 3)[0]
    home[0] = 90
    set_servo_positions(home, 0.01)
    #suctionOn()
    time.sleep(1)
    #lowerArm(7, 3, 90)
    #suctionOn()
    #time.sleep(1)
    #raiseArm(7, 1, 90)
    #suctionOff()
    #raiseArm(7, 2, 90)
    #raiseArm(7, 3, 90)
    client.set_callback(whenCalled)
    client.subscribe("mode")
    client.subscribe("radius")
    client.subscribe("angle")
    try:
        while True:
            client.check_msg()
            time.sleep(0.01)
    except Exception as e:
        print(e)
        
#connect_wifi(ssid, password)
main()
