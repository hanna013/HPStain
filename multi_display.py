
from RPi import GPIO
from time import sleep
import cv2
import numpy as np
from math import pi

#raspberry pi GPIO setting
GPIO.setmode(GPIO.BCM) # define with GPIO pin number
GPIO.setwarnings(False)

A = 22
B = 10
Z = 11 # encoder
CFA=13
led=23

GPIO.setup(A,GPIO.IN)
GPIO.setup(B,GPIO.IN)
GPIO.setup(Z,GPIO.IN)
GPIO.setup(CFA,GPIO.IN)
GPIO.setup(led,GPIO.OUT, initial=GPIO.LOW)

ALastState = GPIO.input(A)
ZLastState = GPIO.input(Z)

# counter, flag
on = 0 # detect on counter
off = 0 # detect off counter
draw_count = 0
detect = 2
flag = 0 # get stain point
list_p = []
point = []
plus=0
a=0 # list_p length memory

# button setting
button=[60,100,50,250] #[y1,y2,x1,x2]

#OFF BUTTON

def process_click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        if y > button[0] and y < button[1] and x > button[2] and x < button[3]:
            print("THE END")
            cv2.destroyAllWindows()
            GPIO.cleanup()
            #GPIO.output(led, GPIO.LOW)
 
# window setting
cv2.namedWindow('screen')
cv2.setMouseCallback('screen',process_click)

#create button image
x_size=300
button_img = np.zeros((200,x_size,3),np.uint8)
button_img[button[0]:button[1],button[2]:button[3]]=180
cv2.putText(button_img,'OFF',(120,90),cv2.FONT_HERSHEY_PLAIN,2,(0),3)

#create canvas
canvas = np.zeros((200,x_size,3), dtype ="uint8")
stain=(234,234,234)
pin=(102,37,0)
green=(0,255,0)

print("Let's start")

try:
    while(1):
        
        #sensing
        if GPIO.input(CFA)==0:
            
            #save or not
            if detect == 0 and flag == 1:
                list_p.append([0,int(off*360/200*2*pi)]) # int(off*360/2000*1*pi)
                off=0
                on=0
            
                #stain O
            GPIO.output(led,GPIO.HIGH)
            Astate = GPIO.input(A)
            Bstate = GPIO.input(B)
            if Astate != ALastState:
                if Bstate != Astate:
                    on += 1
                else:
                    on -= 1
            
                    ALastState = Astate
            detect = 1
            flag=1

        else:
            #save or not
            if detect == 1:
                list_p.append([1,int(on*360/200*2*pi)]) ## int(on*360/2000*1*pi)
                on=0
                off=0

            #stain X    
            GPIO.output(led,GPIO.LOW)
            Astate = GPIO.input(A)
            Bstate = GPIO.input(B)
            if Astate != ALastState:
                if Bstate != Astate:
                    off += 1
                else:
                    off -= 1
            ALastState = Astate
            detect = 0

        # count for display
        draw_count +=1

        # caculate_point
        if draw_count%10==0:
            on_sensing= int(on*360/2000*1*pi)
            off_sensing= int(off*360/2000*1*pi)

            cv2.rectangle(canvas,(0,100-5),(x_size,100+5),pin,-1)#initialize / -1 = fill inside of rectangle

            # list-> point
            if a < len(list_p): #while(1) -> repeat
                point=[0]*len(list_p)
                for i in range(len(list_p)): # 0 1 2
                    for j in range(i,len(list_p)):
                        plus = plus + list_p[j][1]
                    point[i]=[list_p[i][0],plus]
                    plus=0

            a = len(list_p)   

            # draw
            for k in range(len(point)):
                if point[k][0] == 1:
                    cv2.rectangle(canvas,(x_size-point[k][1]-on_sensing-off_sensing,100-5),(x_size,100+5),stain,-1)
                elif point[k][0] == 0:
                    cv2.rectangle(canvas,(x_size-point[k][1]-on_sensing-off_sensing,100-5),(x_size,100+5),pin,-1)

            if off == 0 and on > 0:
                cv2.rectangle(canvas,(x_size-on_sensing,100-5),(x_size,100+5),stain,-1) # draw sensing list_p
            elif on ==0 and off > 0:
                cv2.rectangle(canvas,(x_size-off_sensing,100-5),(x_size,100+5),pin,-1) # draw sensing off list_p

            #connect images
            img_result=cv2.hconcat([button_img,canvas])
            img_result=cv2.vconcat([button_img,canvas])
            cv2.imshow('screen',img_result)
            cv2.waitKey(1)

except KeyboardInterrupt:

    GPIO.cleanup()