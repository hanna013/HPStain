
# A new version(direction change) of the converter.py has been applied.
# length = value(#pulse)*2*pi*r/resolution
import sched
import RPi.GPIO as GPIO
from encoder import Encoder
from guizero import App, Drawing, PushButton, info, Text, Box, ButtonGroup
from math import pi
import pyautogui # after method
import time

app_size=320
size=300 # rectanglar size = 3m
resolution_x = 720 
resolution_y = 480 #screen resolution
chk=10
y1=0
y2=20 # retangular y cooridinate
resolution=100 # encoder resolution
radius=2
pin_length=42

factor_w = int(resolution_x/size) # for maximizing the app
factor_h = int(resolution_y/200)
circum = 2*pi*radius # unit

list_p = [[0,0]] # save length
detect = 2 # marking CFA status 
over_3M=2
point = [] # save x coordinate
plus=0
flag_del=0
a=1 #list_p length
b=0 #list_t length
c=0 #list_p length_stain cal
total=0 # point[0]
draw_count=0 # minimize load because of drawing
no_stain=0 #flag
buz_case=0
del_R=0
time1=0
ROT=[]
list_t=[[0,0]]
point=[[0,0]]
stain=0 # there is a gap between saving and showing
sensing=0
s_flag=0
pre_point=[[0,0]]

def rotation_off():
    rotation_off.bg = "light gray"
    GPIO.output(rot,GPIO.LOW)

def buzzer_off():
    buzzer_off.bg = "light gray"
    GPIO.output(buzzer,GPIO.LOW)

def light_off():
    light_off.bg = "light gray"
    GPIO.output(light,GPIO.LOW)
    
def reset():
    global list_p, pre_point, detect, over_3M, s_flag, point, plus, stain, sensing, flag_del, a, b, c, total, draw_count, no_stain, buz_case, del_R, time1, ROT, list_t
    
    list_p = [[0,0]] # save length
    detect = 2 # marking CFA status 
    over_3M=2
    point = [] # save x coordinate
    plus=0
    a=1 #list_p length
    b=0 #list_t length
    c=0 #list_p length_stain cal
    total=0 # point[0]
    draw_count=0 # minimize load because of drawing
    no_stain=0 #flag
    buz_case=0
    del_R=0
    time1=0
    ROT=[]
    list_t=[[0,0]]
    point=[[0,0]]
    stain=0
    sensing=0
    flag_del=0
    s_flag=0
    pre_point=[[0,0]]
    
    rotation_off.bg = "light gray"
    GPIO.output(rot,GPIO.LOW)
    buzzer_off.bg = "light gray"
    GPIO.output(buzzer,GPIO.LOW)
    light_off.bg = "light gray"
    GPIO.output(light,GPIO.LOW)
    
    text_1.value="Ready"
    text_1.text_color = "black"
    drawing.rectangle(0,y1,size*factor_w, y2, color="gold") #x1,y1,x2,y2
    
    write_file("\n\n< RESET >\n")
    write_file("1. time     2. length[cm] (S:Stain, 0:Pin)\n")
    
    e1.resetValue()

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

def stop_rot():
    rotation_off.bg="light gray"
    GPIO.output(rot,GPIO.LOW)

def stop_buz():
    buzzer_off.bg="light gray"
    GPIO.output(buzzer,GPIO.LOW)

def warning_rot_light():
    GPIO.output(light,GPIO.LOW)
    GPIO.output(light,GPIO.LOW)
    rotation_off.bg="orange"
    GPIO.output(rot,GPIO.HIGH)
    light_off.bg="orange" 
    GPIO.output(light,GPIO.HIGH)
    rotation_off.after(3000,stop_rot)

def valueChanged(value, direction): #----------------------------------------------------------------------------------------------------------------
    global choice, pre_point, list_p, detect, over_3M, pin_length, s_flag, point, plus, stain, sensing, flag_del, a, b, c, total, draw_count, no_stain, buz_case, del_R, time1, ROT, list_t
    
    #print("p=",point)
    #print(sensing)
    #print("v=",value)
    #print("t=", list_t)
    #print(list_p)
   
# 1. value 초기화
    if sensing> 300: # 버저 여러 번 안 울리기 위해서는 초기화 값 조정이 중요
        e1.resetValue()
    
    no_stain=0
    p_flag=0

# 2. 얼룩 <-> 핀, p에 값 저장
    if GPIO.input(CFA)==0 : # Adjust the optical fiber sensor so that there's no wrong value.
        ROT.append([1]) # To check if it's a real stain

            #write detecting time
        if len(ROT)==2: #
            time1= time.strftime('%X',time.localtime(time.time()))
  
        #save or not
        if detect == 0:
            if round((value*circum/resolution),2) >= chk:
                list_p[-1][1]=round(((value)*circum/resolution),2)
                e1.resetValue()
                s_flag=0
                p_flag=1
            else:
                list_p.append([0,round(((value)*circum/resolution),2)])
                e1.resetValue() # 
        detect = 1 
    else:
        #save or not
        if detect == 1:
            list_p.append(["S",round((value)*circum/resolution,2)])
            e1.resetValue()
        if value==int(chk*resolution/circum)+1: # sensing = 10.048cm, value=79+1
            list_p.append([0,round((value)*circum/resolution,2)])
            s_flag=1
        detect = 0
# 3. sensing 값 조정 - s_flag가 뜨면 10cm가 두번 계산됨   
    # sensing value adjust - s_flag
    if s_flag==1:
        sensing= round(((value-int(chk*resolution/circum)+1)*circum/resolution),2)
    else:
        sensing= round(((value+1)*circum/resolution),2) # 정의

# 4. stain(=얼룩 실시간 디스플레이용) 계산
# 작은 얼룩일 때용으로 만든거라 현재 센싱 중인 작은 값에 대해서는 더해지지 않아서 실제보단 살짝 짧음.
# for문으로 돌리는 게 아니라 한번 구문이 수행될 때 추가되는 값이라서 sensing 값은 그릴 때 추가해서 그려야 함.
    # Calculating small spots(=stain) in real time.
    if len(ROT)>=1 and c < len(list_p): # 시작을 10cm 미만의 핀으로 하면 실시간으로 보여줄 때는 이 값까지 stain으로 묶어서 보여줌 
      if list_p[-1][1]<chk:
        stain += list_p[-1][1] # no add sensing value

# 5. 드로우 카운트 초기화    
    draw_count += 1
    if draw_count == 1000:
        draw_count = 0

# 6. 텍스트 변경 및 ROT, stain 초기화    
    # text
    if choice.value == "P":
        if detect==1 and stain>0: 
            #text_1.value="Stain"
            text_1.value="Stain:",round(stain,2),"cm" # can be tiny differance 
            text_1.text_color = "red"
        elif detect==0 and s_flag==1: # ----------------------------------------text delay
            text_1.value="No Stain"
            text_1.text_color = "green"
            ROT=[] 
            stain=0
    elif choice.value == "L":
        if detect == 1:
            text_1.value="Stain:",round(value*circum/resolution,2),"cm"
            text_1.text_color = "red"
        else:
            text_1.value="No Stain"
            text_1.text_color = "green"

 # 7. t, point 새로 계산    
    # SET list_t, point
    if a < len(list_p) or over_3M==1 or del_R==1 or p_flag==1:
        list_t=[[0,0]]
        over_3M=0
        del_R=0
        # tie small stains : list_p -> list_t
        t=0
        S=[] # stain or not 
        
        # 7.1 t 계산
        if choice.value == "P": #-----------------------------------------------------------------------------------------------------
            #list_p -> list_t
            for o in range(1, len(list_p)): # 1 2 ...
            
                if list_p[o][1] < chk:
                    t += list_p[o][1]
                    S.append(list_p[o][0]) # sign: adding small stains
                else:
                    if len(S)>0:
                        list_t.append(["S",round(t,2)]) #cfa value not precise, all small value become stain -> error cause?
                        write_file(str(time1)+"    "+str(list_t[-1])+"\n")
                        S=[]
                        t=0
                        list_t.append([list_p[o][0],list_p[o][1]]) # it might be not pin, it can be long full-stain.
                        if list_p[o][0]=="S":
                            write_file(str(time1)+"    "+str(list_t[-1])+"  Please calculate by adding this and the previous stain length\n")
    
                    else:
                        list_t.append([list_p[o][0],list_p[o][1]])
                        if list_p[o][0]=="S":
                            write_file(str(time1)+"    "+str(list_t[-1])+"\n")
        # 7.3 pre_point 선정                    
        if choice.value == "P":
            pre_point= list_t
        elif choice.value == "L":
            pre_point= list_p
        
        # 7.4 point 계산
        # pre_point -> point
        point=[[0,0]]*len(pre_point)
        for i in range(len(pre_point)): # 0 1 2 ...
            for j in range(i,len(pre_point)):
                plus = round(plus + pre_point[j][1],2)
            if i==0:
                total = plus
            point[i]=[pre_point[i][0],plus]
            plus=0
    
# 8. 핀이 후진 시 값 변경(기록값 뺄셈)
    if direction=="R" and sensing<0:
        list_p[-1][1] = round(list_p[-1][1]+sensing,2)
        print("minus")
        if list_p[-1][1]<=0.01:
            del list_p[-1]
            del_R=1
            print("del latest one")
    
# 9. 디스플레이
    #draw
    if draw_count%10==0:
        # 9.1 얼룩 묶음으로 저장된 값
        drawing.rectangle(0,y1,size*factor_w, y2, color="gold") # initialize
        for k in range(1,len(point)): # sensing ++ -> 
            if point[k][0] == "S":
                drawing.rectangle((size-point[k][1]-sensing-stain)*factor_w, y1, (size-point[k][1]-sensing-stain+pre_point[k][1])*factor_w, y2, color="red")
        # 9.2 현재 센싱 및 판별 중인 값
        # To display it in real time-------------------------------------------------------------------------------------------------------------------------@
        if len(ROT)>0 and choice.value=="P":
            drawing.rectangle((size-stain-sensing)*factor_w, y1, size*factor_w, y2, color="orange")
            # can be tiny differance but it's not critical.
        elif value > 0 and detect ==1 and choice.value=="L":
            drawing.rectangle((size-sensing)*factor_w, y1, size*factor_w, y2, color="orange")

# 10. 3m 넘어가는 값 삭제(뺄셈)  
    # Over 3m, remove / must be after draw source
    if total+sensing >= size: 
        over_3M=1
        list_p[1][1] = round(list_p[1][1]-(total+sensing-size),2)
        if list_p[1][1]<=0.1: 
            del list_p[1]
            print("delete") # 값이 중간에 사라지는 이유는 아직 확실 x
            buz_case=1

# 11. 경광등
    #buzzer3_끝과 끝
    if buz_case==1 and list_t[-1][1]+stain >= size:
        flag_del += 1
    if choice.value == "L":
        if buz_case==1 and list_p[-1][1]+stain >= size:
            flag_del += 1
    
    #warning_1_rot & light
    if detect == 1 and len(ROT)==2  : # stain find & exist
        warning_rot_light()

    if detect==0 and round((value*circum/resolution),2)>=299 and over_3M!=2: # 경광등이 여러번 울리면 2번째 조건 때문에 울리는 것. 그래서 value 초기화 값 조정해야 함.
    # light auto off
        light_off.bg="light gray"
        # buzzer 2, if 조건이 해당되서 경광등이 여러번 울리는 것을 막기 위해, value == 몇으로?
        no_stain =1
        GPIO.output(light,GPIO.LOW)
    
    # warning2_buzzer
    # buzzer 1: 중간에 42 이상 값 있을 때
    if choice.value == "P":
        if len(list_t) > 1 and over_3M==0: # ------------------------------------------------------------------------------- a>1
            if list_t[1][0]==0 and list_t[1][1] >= pin_length and point[0][1]+round(value*circum/resolution,2)>= 299: # == 299 (x) #리스트 0번째 값 없애면 여기도 수정하기.
                buzzer_off.bg="orange"
                buzzer_off.after(5000,stop_buz)
                GPIO.output(buzzer,GPIO.HIGH)
    elif choice.value == "L":
        if len(list_p) > 1 and over_3M==0: # ------------------------------------------------------------------------------- a>1
            if list_p[1][0]==0 and list_p[1][1] >= pin_length and point[0][1]+round(value*circum/resolution,2)>= 299: # == 299 (x) #리스트 0번째 값 없애면 여기도 수정하기.
                buzzer_off.bg="orange"
                buzzer_off.after(5000,stop_buz)
                GPIO.output(buzzer,GPIO.HIGH)
    # buzzer 2: 마지막 얼룩이 3m를 모두 지나갔을 때
    if no_stain==1:
        buzzer_off.bg="orange"
        buzzer_off.after(5000,stop_buz)
        GPIO.output(buzzer,GPIO.HIGH)
    # buzzer 3: 
    if flag_del!=0 and flag_del<3: # flag_del=1 이면 안 되는 이유? 그 사이에 구문이 여러번 반복되서 딱 1이 아닐 수 있음. 그냥 안 올리고 1, 0으로 하면?
        flag_del=0
        buz_case=0
        buzzer_off.bg="orange"
        buzzer_off.after(5000,stop_buz)
        GPIO.output(buzzer,GPIO.HIGH)
        
        
    a=len(list_p)
    b=len(list_t)
    c=len(list_p)
    
"""
------------------------------------- Main --------------------------------------
"""

# encoder setting
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

A = 22
B = 10
Z = 11 # encoder
CFA=13

rot= 21
light= 20
buzzer= 16

e1 = Encoder(A, B, valueChanged)
GPIO.setup(CFA,GPIO.IN)

GPIO.setup(rot,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(light,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(buzzer,GPIO.OUT, initial=GPIO.LOW)

# app
app=App(title="Hairpin Stain Sensor", width=app_size*factor_w, height=200*factor_h, bg="ivory")
app.when_closed=handle_exit
#app.set_full_screen()

ch_box= Box(app,layout="grid",grid=[0,0])
text_ch = Text(ch_box, text="Stain:", grid=[0,0])
choice = ButtonGroup(ch_box, options=[ ["Point", "P"], ["Line", "L"]], selected="P", horizontal=True, grid=[1,0])

text_1 = Text(app, text="Ready", width="fill", height="2",size=25) #heihgt=2, size=30

#button
button_box= Box(app,layout="grid",grid=[0,2])
onoff=PushButton(button_box,command=handle_exit, text="Turn Off", grid=[0,0], pady=25)
onoff.bg="gray"
onoff.text_size=15
rotation_off=PushButton(button_box,command=rotation_off, text="Rotation OFF", grid=[1,0], pady=25)
rotation_off.bg="light gray"
rotation_off.text_size=15
buzzer_off=PushButton(button_box,command=buzzer_off, text="Buzzer OFF", grid=[2,0], pady=25)
buzzer_off.bg="light gray"
buzzer_off.text_size=15
light_off=PushButton(button_box,command=light_off, text="Light OFF", grid=[3,0], pady=25)
light_off.bg="light gray"
light_off.text_size=15
reset=PushButton(button_box,command=reset, text="RESET", grid=[4,0], pady=25)
reset.bg="gray"
reset.text_size=15

Text(app,text="⇇",size=20, width="fill", height="2")

drawing = Drawing(app, width=size*factor_w, height=25)
drawing.rectangle(0,y1,size*factor_w, y2, color="gold") #x1,y1,x2,y2

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

write_file("\n\n< START >\n")
write_file("1. time     2. length[cm]  (S:Stain, 0:Pin)\n")

app.display()






