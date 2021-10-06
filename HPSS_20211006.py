# Sample code to demonstrate Encoder class.  Prints the value every 5 seconds, and also whenever it changes.

import time
import RPi.GPIO as GPIO
from encoder import Encoder
from guizero import App, Drawing, PushButton, info, Text, Box
from math import pi

def onoff():
    info("On/Off_Button", "hi / bye")
    print("turn on/off")

def buzzer_off():
    print("buzzer off")

def light_off():
    print("light off")

# counter, flag
x_offset=30
multiply=1
size=300*multiply + x_offset*2

list_p = []
resolution=100
radius=1
circum = 2*pi*radius*multiply
detect = 2
flag = 0
point = []
plus=0
a=0 # list_p length memory
draw_count=0

def valueChanged(value):
    global list_p
    global detect
    global flag
    global point
    global plus
    global a
    global draw_count
    
    print("* New value: {}".format(value))
    
    if GPIO.input(CFA)==0:
        GPIO.output(led,GPIO.HIGH)
        #save or not
        if detect == 0:
            list_p.append([0,int(value/resolution*circum)])
            e1.resetValue()
        detect = 1
        #flag=1
    else:
        GPIO.output(led,GPIO.LOW)
        #save or not
        if detect == 1:
            list_p.append([1,int(value/resolution*circum)])
            e1.resetValue()
        detect = 0

    draw_count += 1
    
    sensing= int(value/resolution*circum)
          
    # list-> point
    if a < len(list_p): # do not repeat every time
        point=[0]*len(list_p)
        for i in range(len(list_p)): # 0 1 2 ...
            for j in range(i,len(list_p)):
                plus = plus + list_p[j][1]
            point[i]=[list_p[i][0],plus]
            plus=0
    a = len(list_p)
        
    #draw
    if draw_count%10==0:
        for k in range(len(point)):
            if point[k][0] == 1:
                drawing.rectangle(size-x_offset-point[k][1]-sensing, 10, size-x_offset, 30, color="gray")
            elif point[k][0] == 0:
                drawing.rectangle(size-x_offset-point[k][1]-sensing, 10, size-x_offset, 30, color="gold")
    
        if value > 0 and detect ==0:
            drawing.rectangle(size-x_offset-sensing, 10, size-x_offset, 30, color="gold")
        elif value > 0 and detect ==1:
            drawing.rectangle(size-x_offset-sensing, 10, size-x_offset, 30, color="gray")





# encoder setting
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

A = 22
B = 10
Z = 11 # encoder
CFA=13
led=23

e1 = Encoder(A, B, valueChanged)
GPIO.setup(CFA,GPIO.IN)
GPIO.setup(led,GPIO.OUT, initial=GPIO.LOW)

# app
app=App(title="Hairpin Stain Sensor", width=size*multiply, height=200, layout="grid",bg="ivory")

#button
box0 = Box(app,layout="grid",grid=[0,0])
OnOff=PushButton(box0,command=onoff, text="ON/OFF", grid=[0,0])
OnOff.bg="gray"
buzzer_off=PushButton(box0,command=buzzer_off, text="Buzzer OFF", grid=[1,0])
buzzer_off.bg="gray"
Light_off=PushButton(box0,command=light_off, text="Light OFF", grid=[2,0])
Light_off.bg="gray"

#draw
drawing = Drawing(app,width=size*multiply, height=40, grid=[0,1])
drawing.rectangle(x_offset, 10, x_offset+300*multiply, 30, color="gold") #x1,y1,x2,y2

#show distance line
d_line = Drawing(app,width=size*multiply, height=20, grid=[0,2])
d_line.line(x_offset, 0, x_offset, 20,width=2) #x1,y1,x2,y2
d_line.line(x_offset+100*multiply, 0, x_offset+100*multiply, 20,width=2) #x1,y1,x2,y2
d_line.line(x_offset+200*multiply, 0, x_offset+200*multiply, 20,width=2) #x1,y1,x2,y2
d_line.line(x_offset+300*multiply, 0, x_offset+300*multiply, 20,width=2) #x1,y1,x2,y2

""" # width problem
#show distance value
box = Box(app, layout="grid",grid=[0,3],align="left")
Text(box,text="",width="1",grid=[0,0],align="left") # offset
Text(box,text="3m",width="3",grid=[1,0],align="left") # 3m
Text(box,text="2m",width="15",grid=[2,0],align="right") # 2m
Text(box,text="1m",width="3",grid=[3,0],align="right") # 1m
Text(box,text="0m",width="15",grid=[4,0],align="right") # 0m
"""
app.display()

