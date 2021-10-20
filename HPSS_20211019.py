# A new version(direction change) of the converter.py has been applied.
# length = value(#pulse)*2*pi*r/resolution
import sched
import RPi.GPIO as GPIO
from encoder import Encoder
from guizero import App, Drawing, PushButton, info, Text, Box
from math import pi
import pyautogui
import time

app_size=320
size=300 # rectanglar size = 3m
resolution_x = 720 
resolution_y = 480 #screen resolution

factor_w = int(resolution_x/size) # for maximizing the app
factor_h = int(resolution_y/200)

list_p = [[0,0]] # save length
resolution=100 # encoder resolution
radius=2
circum = 2*pi*radius
detect = 2 # marking CFA status 
add_3M=2
point = [] # save x coordinate
plus=0
a=1 #list_p length
total=0 # point[0]
draw_count=0 # minimize load because of drawing
y1=0
y2=20 # retangular y cooridinate
d=0 # save 'value' at that time
no_stain=0 #flag
del_flag=0


def rotation_off():
    rotation_off.bg = "gray"
    GPIO.output(rot,GPIO.LOW)

def buzzer_off():
    buzzer_off.bg = "gray"
    GPIO.output(buzzer,GPIO.LOW)

def light_off():
    light_off.bg = "gray"
    GPIO.output(light,GPIO.LOW)


def write_file(data):
    today= time.strftime('%m%d',time.localtime(time.time()))
    
    path="/home/pi/Desktop/HPSS_LOG"
    filename="/log"+str(today)+".txt"
    
    try:
        f = open(path+filename, "a")
        f.write(str(data))
        f.close()
    except Exception:
        print("Could not write to file")

def handle_exit():
    GPIO.output(light,GPIO.LOW)
    GPIO.output(rot,GPIO.LOW)
    GPIO.output(buzzer,GPIO.LOW)
    
    #rotation_off.cancel(stop_rot)
    #buzzer_off.cancel(stop_buz)
    
    app.destroy()
    

def valueChanged(value):
    global list_p, detect, add_3M, point, plus, a, total, draw_count, d, no_stain, del_flag
    
    d = value # rotation once
    no_stain=0
    
    #light, text, detect changing
    if GPIO.input(CFA)==0:
        #write detecting time
        if value<=1:
            time1= time.strftime('%X',time.localtime(time.time()))
            write_file(time1)
        #save or not
        if detect == 0:
            list_p.append([0,round(((value-1)*circum/resolution)%300,2)])
            e1.resetValue()
        detect = 1
        text_1.value="Stain is detected",round(value*circum/resolution,2),"cm"
        text_1.text_color = "red"
    else:
        #save or not
        if detect == 1:
            write_file(" "+str(round(((value-1)*circum/resolution)%300,2))+"cm\n")
            list_p.append([1,round((value-1)*circum/resolution,2)])
            e1.resetValue()
        detect = 0
        text_1.value="No Stain"
        #text_1.value="No Stain",round((value-1)*circum/resolution,2),"cm"
        text_1.text_color = "green"

    draw_count += 1
    
    sensing= round((value*circum/resolution)%300,2)
          
    # list-> point
    if a < len(list_p) or add_3M==1: #do not repeat every time
        add_3M=0
        point=[0]*len(list_p)
        for i in range(len(list_p)): # 0 1 2 ...
            for j in range(i,len(list_p)):
                plus = round(plus + list_p[j][1],2)
            if i==0:
                total = plus
            point[i]=[list_p[i][0],plus]
            plus=0  

#draw
    if draw_count%10==0:
        #print(list_p)
        #print("point=",point)
        for k in range(1,len(point)):
            if point[k][0] == 1:
                drawing.rectangle((size-point[k][1]-sensing)*factor_w, y1, (size-point[k][1]-sensing+list_p[k][1])*factor_w, y2, color="gray")
            elif point[k][0] == 0:
                drawing.rectangle((size-point[k][1]-sensing)*factor_w, y1, size*factor_w, y2, color="gold")
    
        if value > 0 and detect ==0:
            drawing.rectangle((size-sensing)*factor_w, y1, size*factor_w, y2, color="gold")
        elif value > 0 and detect ==1:
            drawing.rectangle((size-sensing)*factor_w, y1, size*factor_w, y2, color="gray")

# Over 3m, remove, must be after draw source
    if total+sensing >= size:
        add_3M=1
        list_p[1][1] = round(list_p[1][1]-(total+sensing)-size,2)
        if list_p[1][1]<=1:
            del list_p[1]
            drawing.rectangle(0,y1,1*factor_w, y2, color="gold")
            
            a=len(list_p)
            del_flag=1
    
    #warning_1_rot & light
    if detect == 1 and d < 10 : # stain find & exist
        GPIO.output(light,GPIO.LOW)
        rotation_off.bg="orange"
        GPIO.output(rot,GPIO.HIGH)
        light_off.bg="orange"
        GPIO.output(light,GPIO.HIGH)
        rotation_off.after(5000,stop_rot)
        
    if detect==0 and sensing>=299 and add_3M!=2:
    # light auto off
        light_off.bg="gray"
        no_stain=1
        GPIO.output(light,GPIO.LOW)
    
    # warning2_buzzer
    if a > 1 and add_3M==0:
        if list_p[1][0]==0 and list_p[1][1] >= 42 and point[0][1]+sensing >= 299: # == 299 (x)
            buzzer_off.bg="orange"
            buzzer_off.after(5000,stop_buz)
            GPIO.output(buzzer,GPIO.HIGH) # ---------------------------------------------------------------------------------------
    if no_stain==1:
        buzzer_off.bg="orange"
        buzzer_off.after(5000,stop_buz)
        GPIO.output(buzzer,GPIO.HIGH) # ---------------------------------------------------------------------------------------
        
    del_flag=0

  
def stop_rot():
    rotation_off.bg="gray"
    GPIO.output(rot,GPIO.LOW)

def stop_buz():
    buzzer_off.bg="gray"
    GPIO.output(buzzer,GPIO.LOW)
        

# encoder setting
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

A = 22
B = 10
Z = 11 # encoder
CFA=13
#led=23

rot= 21
light= 20
buzzer= 16


e1 = Encoder(A, B, valueChanged)
GPIO.setup(CFA,GPIO.IN)
#GPIO.setup(led,GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(rot,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(light,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.LOW)

# app
app=App(title="Hairpin Stain Sensor", width=app_size*factor_w, height=200*factor_h, bg="ivory")
app.when_closed=handle_exit
app.set_full_screen()

text_1 = Text(app, text="ready", width="fill", height="2",size=30)

#button
button_box= Box(app,layout="grid",grid=[0,1])
rotation_off=PushButton(button_box,command=rotation_off, text="Rotation OFF", grid=[0,0],padx=20,pady=25)
rotation_off.bg="gray"
rotation_off.text_size=15
buzzer_off=PushButton(button_box,command=buzzer_off, text="Buzzer OFF", grid=[1,0],padx=30,pady=25)
buzzer_off.bg="gray"
buzzer_off.text_size=15
light_off=PushButton(button_box,command=light_off, text="Light OFF", grid=[2,0],padx=30,pady=25)
light_off.bg="gray"
light_off.text_size=15

#draw
Text(app,text="⇇",size=20, width="fill", height="2")

drawing = Drawing(app, width=size*factor_w, height=25)
drawing.rectangle(1,y1,size*factor_w, y2, color="gold") #x1,y1,x2,y2

#show distance line
d_line = Drawing(app,width=size*factor_w, height=35)
d_line.line(0, 10, 0, 30, width=3) # 3m
d_line.line(100*factor_w, 10, 100*factor_w, 30, width=3) # 2m
d_line.line(200*factor_w, 10, 200*factor_w, 30, width=3) # 1m
d_line.line(300*factor_w-2, 10, 300*factor_w-2, 30, width=3) # 0m

box0 = Box(app,width=app_size*factor_w,height=35)
Text(box0,text="3m ",align="left")
Text(box0,text="0m",align="right")

box = Box(app,width=app_size*factor_w,height=35)
Text(box,text="⇧ ",align="left")
Text(box,text="Cutting Point",align="left")
Text(box,text=" ⇧",align="right")
Text(box,text="Sensing Point",align="right")

write_file("\n\n-start-\n")

app.display()



