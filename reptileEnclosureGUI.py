#!/usr/bin/env python3

from tkinter import *

import tkinter.font as tkfont

import tk_tools

import time

from PIL import Image, ImageTk

import temp

import motor

from picamera import PiCamera

from datetime import datetime

from math import ceil,floor

import RPi.GPIO as GPIO

import Adafruit_DHT

now = datetime.now()





lights=16

dht1 = 23

dht2 = 24

def setupGPIO():

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(lights,GPIO.OUT)

        GPIO.output(lights, False)

        GPIO.setup(dht1, GPIO.IN)

        GPIO.setup(dht2, GPIO.IN)



class App(Frame):

    def __init__(self, master=None):

        self.f1 = Frame.__init__(self, master, bg="black")

        self.place()

        self.fontSmall = tkfont.Font(family="Helvetica", size=20)

        self.fontLarge = tkfont.Font(family="Helvetica", size=40)

        self.colorSpectrum =  ['#FFF800', '#FFF200', '#FFEB00', '#FFE500', '#FFDF00', '#FFD800', 

 '#FFD200', '#FFCC00', '#FFC500', '#FFBF00', '#FFB800', '#FFB200', 

 '#FFAC00', '#FFA500', '#FF9F00', '#FF9900', '#FF9200', '#FF8C00', 

 '#FF8500', '#FF7F00', '#FF7900', '#FF7200', '#FF6C00', '#FF6600', 

 '#FF5F00', '#FF5900', '#FF5200', '#FF4C00', '#FF4600', '#FF3F00', 

 '#FF3900', '#FF3300', '#FF2C00', '#EF2600', '#DF1F00', '#CF1900', 

 '#BF1300', '#AF0C00', '#9F0600', '#8F0000'] 



        self.setTemp = 75

        self.loopOffset = 0

        self.openMotorValues= open('motorPosition.txt', 'r')



        try:

            self.heaterValue = int(self.openMotorValues.readline())

        except ValueError:

            self.heaterValue = 0

            self.openMotorValues = open('motorPosition.txt', 'w')

            self.openMotorValues.write(str(self.heaterValue))

        self.openMotorValues.close()

        self.openSetTemp = open('setTemperature.txt', 'r')

        try:

            self.setTemp = float(self.openSetTemp.readline())

        except ValueError:

            self.openSetTemp.write(str(self.setTemp))

        self.openSetTemp.close()

        self.openTimerValues = open('timerValues.txt', 'r')

        self.timerValues = self.openTimerValues.readline().split()

        self.morningTemp, self.morningTime, self.nightTemp, self.nightTime = int(self.timerValues[0]), int(self.timerValues[1]), int(self.timerValues[2]), int(self.timerValues[3])

        self.arrowDown = [(self.nightTime, 100), (self.nightTime,95), (self.nightTime-0.1,97), (self.nightTime,95), (self.nightTime+0.1,97)]

        self.arrowUp = [(self.morningTime,95), (self.morningTime,100), (self.morningTime-0.1, 98), (self.morningTime, 100), (self.morningTime+0.1, 98)]

        self.therm = False

        self.timer = False

        self.lightsState = False

        self.actualTemp = 0.0

        self.dht1Temp, self.dht1Hum = 0, 0

        self.dht2Temp, self.dht2Hum = 0, 0

        self.dhtSetup()

        self.radio = IntVar()

        self.radio.set(30000)

        self.contents = StringVar()

        self.contents.set("Set Temperature")

        self.loadimg = Image.open('snakepic.png')

        self.render = ImageTk.PhotoImage(self.loadimg)

        self.img = Label(image=self.render, bg="black", border=-2)

        self.img.place(x=550, y=100)



        self.setTempFrame = Frame(height=400, width=450, bg="#000000")

        self.setTempFrame.place(x=50, y=120)

        self.l1 = Label(self.setTempFrame, text=f"Set Temp: {self.setTemp} F", bg="#000000", fg="#FFFFFF", font=self.fontLarge)

        self.l1.place(x=0, y=0)

        self.b2 = Button(self.setTempFrame, text='-',font=self.fontLarge, command = self.lowerSetTemp, bg="dark blue", fg="white", width=5)

        self.b2.place(x=25, y=70)

        self.b1 = Button(self.setTempFrame, text='+', font=self.fontLarge, command=self.raiseSetTemp, fg="white", bg="maroon", width=5)

        self.b1.place(x=200, y=70)

        self.entrythingy = Entry(self.setTempFrame, bg="dark grey", font=self.fontSmall)

        self.entrythingy.place(x=50, y=150)

        self.entrythingy["textvariable"] = self.contents

        self.entrythingy.bind('<Key-Return>', self.postSetTemp)

        self.led = Label(self.setTempFrame, bg='red', border = 2, width = 5,height = 1, relief='ridge', text='OFF')

        self.led.place(x=177, y=205)

        self.led2 = Label(self.setTempFrame, bg='red', border = 2, width = 5,height = 1, relief='ridge', text='OFF')

        self.led2.place(x=177, y=255)

        self.b9 = Button(self.setTempFrame, text="Thermostat On", command=lambda:self.thermOn())

        self.b9.place(x=240, y=200)

        self.b10 = Button(self.setTempFrame, text="Thermostat Off", command=lambda:self.thermOff())

        self.b10.place(x=35, y=200)

        self.b9a = Button(self.setTempFrame, text="Timer On", command=lambda:self.timerOn())

        self.b9a.place(x=255, y=250)

        self.b10a = Button(self.setTempFrame, text="Timer Off", command=lambda:self.timerOff())

        self.b10a.place(x=50, y=250)





        

        self.frameListbox = Frame() #Listbox record of actions

        self.frameListbox.place(x=20, y=820)

        self.list1 = Listbox(self.frameListbox, width=33, height=7, bg="black", fg="white", font=self.fontSmall)

        self.scroll1 = Scrollbar(self.frameListbox, highlightcolor="blue")

        self.scroll1.pack(side=RIGHT, fill=Y)

        self.list1.pack()

        self.list1['yscrollcommand']=self.scroll1.set

        self.scroll1["command"] = self.list1.yview

        



        self.graph = tk_tools.Graph(parent=self.f1,x_min=0, y_min=67, x_max=24, y_max=100, x_tick=6, y_tick=10, width=1500)

        self.graph.canvas["bg"] = 'black'

        self.graph.canvas['bd'] = 0

        self.graph.canvas['highlightthickness'] = 0

        self.graph.canvas.config(width=1500) #float(self.canvas.config('width')[4])

        self.graph.place(x=540, y=820)

        

        self.readingsFrame = Frame(width=1450, height= 80, bg= "#333333", bd="4", relief=RIDGE)

        self.readingsFrame.place(x=15, y=15)

        self.l2 = Label(self.readingsFrame, text=f"Actual: {self.actualTemp} F", bg="#333333", fg="#FFFFFF", font=self.fontLarge, bd="3")

        self.l2.place(x=0, y=0)

        self.dht2 = Label(self.readingsFrame, text=f"DHT L: {self.dht2Temp} F, {self.dht2Hum}%", bg="#333333", fg = "#FFFFFF", font=self.fontLarge, bd="3")

        self.dht2.place(x=400, y=0)

        self.dht1 = Label(self.readingsFrame, text=f"DHT R: {self.dht1Temp} F, {self.dht1Hum}%", bg="#333333", fg="#FFFFFF", font=self.fontLarge, bd="3")

        self.dht1.place(x=900, y=0)







        self.heaterFrame = Frame(height=350, width=400, bg="black")

        self.heaterFrame.place(x=50, y=430)

        self.motorPosition = tk_tools.Gauge(self.heaterFrame, red_low = 20, yellow_low=30, divisions=10, yellow=70, red=80, bg="black", min_value=0, max_value=20, label='Heater',width=400, height=200)

        self.motorPosition._canvas['bd'] = 0

        self.motorPosition._canvas['highlightthickness'] = 0

        self.motorPosition.place(x=10, y=0)

        self.motorPosition.set_value(self.heaterValue)

        self.heaterLabel = Label(self.heaterFrame, text="Left Heater", bg = "#000000", fg= "#FFFFFF", font= self.fontLarge)

        self.heaterLabel.place(x=80, y=195)

        self.b4 = Button(self.heaterFrame, text='-',font=self.fontLarge, command =lambda: self.heater(-1), bg="dark blue", fg="white", width=5)

        self.b4.place(x=30, y=270)

        self.b5 = Button(self.heaterFrame, text='+', font=self.fontLarge, command=lambda: self.heater(1), fg="white", bg="maroon", width=5)

        self.b5.place(x=205, y=270)

        

        self.miscButtonsFrame = Frame(width=210, height=200, bg="black")

        self.miscButtonsFrame.place(x=1670, y=600)

        self.b6 = Button(self.miscButtonsFrame, text='Clear Listbox', font=self.fontSmall, command= self.clearList, width=12)

        self.b6.place(x=0, y=0)

        self.b7 = Button(self.miscButtonsFrame, text="Take a Picture", command=self.takePicture, font=self.fontSmall, width=12)

        self.b7.place(x=0, y=50)

        self.b8 = Button(self.miscButtonsFrame, text="Reset Graph", command=self.clearGraph, font=self.fontSmall, width=12)

        self.b8.place(x=0,  y=150)

        self.lightsButton = Button(self.miscButtonsFrame, text=f"Lights: {self.lightsState}", command = self.lightsToggle, font=self.fontSmall, width = 12)

        self.lightsButton.place(x=0, y=100)

        

        self.r1 = Radiobutton(bg="black", fg="white", text="OFF", value=1, variable=self.radio, command=lambda: self.loopControl("OFF"))

        self.r1.place(x=1500, y=40)

        self.r2 = Radiobutton(bg="black", fg="white", text="1 Second", value=1000, variable=self.radio, command=lambda: self.loopControl("1 Second"))

        self.r2.place(x=1500, y=70)

        self.r3 = Radiobutton(bg="black", fg="white", text="30 Seconds", value=30000, variable=self.radio, command=lambda: self.loopControl("30 Seconds"))

        self.r3.place(x=1500, y=100)

        self.r4 = Radiobutton(bg="black", fg="white", text="1 Minute", value=60000, variable=self.radio, command=lambda: self.loopControl("1 Minute"))

        self.r4.place(x=1500, y=130)

        self.l3 = Label(bg="black", fg="white", text= "Loop Time: 30 seconds")

        self.l3.place(x=1500, y=10)

        self.b11 = Button(text="+", command=self.regUp, font = self.fontSmall, width=2)

        self.b11.place(x = 1740, y = 30)

        self.b11 = Button(text="-", command=self.regDown, font = self.fontSmall, width=2)

        self.b11.place(x = 1675, y = 30)

        self.loopOffsetValue = 250

        self.regLabel = Label(text=f"Adjust After {self.loopOffsetValue} Loops", bg="black", fg = 'white')

        self.regLabel.place(x=1660, y=10)

        self.loopTimer = self.after(1, self.loop)



        self.timerFrame = Frame(width=450, height=150, bg="black")

        self.timerFrame.place(x=650, y=718)

        self.scale1 = Scale(self.timerFrame, from_=0.0, to=24.0, orient=HORIZONTAL, length=200)

        self.scale1.place(x= 0, y = 107)

        self.scale2 = Scale(self.timerFrame, from_=0.0, to=24.0, orient=HORIZONTAL, length=200)

        self.scale2.place(x= 230, y = 107)

        self.scale1.set(self.morningTime)

        self.scale2.set(self.nightTime)

        self.scale1Label = Label(self.timerFrame, text="Morning Time", bg="black", fg="white")

        self.scale1Label.place(x= 0, y=82)

        self.scale2Label = Label(self.timerFrame, text = "Night Time", bg="black", fg="white")

        self.scale2Label.place(x= 230, y=82)

        self.scale1Button = Button(self.timerFrame, text= "Set", width=2, height=1, command = self.morningSet)

        self.scale1Button.place(x=130, y= 0)

        self.scale2Button = Button(self.timerFrame, text= "Set", width=2, height=1, command=self.nightSet)

        self.scale2Button.place(x=360, y= 0)

        self.scale3Label = Label(self.timerFrame, text="Morning Temp", bg="black", fg="white")

        self.scale3Label.place(x= 0, y=2)

        self.scale4Label = Label(self.timerFrame, text = "Night Temp", bg="black", fg="white")

        self.scale4Label.place(x= 230, y=2)

        self.scale3 = Scale(self.timerFrame, from_=70, to=100, orient=HORIZONTAL, length=200)

        self.scale3.place(x= 0, y = 32)

        self.scale4 = Scale(self.timerFrame, from_=70, to=100, orient=HORIZONTAL, length=200)

        self.scale4.place(x= 230, y = 32)

        self.scale3.set(self.morningTemp)

        self.scale4.set(self.nightTemp)

        

        

        self.dateAndTime = Label(bg='black',fg="white", text = now.strftime("%m/%d/%Y %H:%M"), font=self.fontLarge, border = 2, relief = 'ridge')

        self.dateAndTime.place(x=680,y=240)

        self.b3 = Button(text="EXIT", bg="dark red", command=quit, font=self.fontSmall)

        self.b3.place(x=1840, y=0)





    def lightsToggle(self):

        if self.lightsState:

            GPIO.output(lights, False)

            self.lightsState=False

        else:

            GPIO.output(lights, True)

            self.lightsState =True

        self.lightsButton['text'] = f"Lights: {self.lightsState}"



    def morningSet(self):

        x = self.therm

        self.timerOff()

        self.morningTemp = int(self.scale3.get())

        self.morningTime = int(self.scale1.get())

        self.timerValues[0], self.timerValues[1] = str(self.morningTemp), str(self.morningTime)

        y = open('timerValues.txt', 'w')

        y.write(" ".join(self.timerValues))

        y.close()

        if x:

            self.timerOn()



    def nightSet(self):

        x = self.therm

        self.timerOff()

        self.nightTime = int(self.scale2.get())

        self.nightTemp = int(self.scale4.get())

        self.timerValues[2], self.timerValues[3] = str(self.nightTemp), str(self.nightTime)

        y = open('timerValues.txt', 'w')

        y.write(" ".join(self.timerValues))

        y.close()

        if x:

            self.timerOn()



    

    def dhtSetup(self):

        self.dht1Hum, self.dht1Temp= Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, dht1)

        if self.dht1Hum is not None and self.dht1Temp is not None:

            self.dht1Temp = self.dht1Temp *9/5 +32

        else:

            print('Failed to get reading')

        # self.dht2Hum, self.dht2Temp= Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, dht2)

        # if self.dht2Hum is not None and self.dht2Temp is not None:

            # self.dht2Temp = self.dht2Temp *9/5 +32

        # else:

            # print('Failed to get reading')

            

    def regUp(self):

        self.loopOffsetValue += 1

        self.regLabel['text'] = f"Adjust After {self.loopOffsetValue} Loops"

    def regDown(self):

        self.loopOffsetValue -= 1

        self.regLabel['text'] = f"Adjust After {self.loopOffsetValue} Loops"

    def thermOn(self):

        self.led['bg'] = 'green'

        self.led['text'] = 'ON'

        self.therm = True

    def timerOn(self):

        self.led2['bg'] = 'green'

        self.led2['text'] = 'ON'

        self.timer = True

        morningTempTuple = (self.morningTime, self.morningTemp)

        nightTempTuple = (self.nightTime, self.nightTemp)

        self.arrowDown = [(self.nightTime, 100), (self.nightTime,95), (self.nightTime-0.1,97), (self.nightTime,95), (self.nightTime+0.1,97)]

        self.arrowUp = [(self.morningTime,95), (self.morningTime,100), (self.morningTime-0.1, 98), (self.morningTime, 100), (self.morningTime+0.1, 98)]

        self.graph.plot_line(self.arrowUp, color="white")

        self.graph.plot_line(self.arrowDown, color="white")

        self.graph.plot_point(size=8, x=nightTempTuple[0], y=nightTempTuple[1], color="blue")

        self.graph.plot_point(size=8, x=morningTempTuple[0], y=morningTempTuple[1], color="blue")

    def thermOff(self):

        self.led['bg'] = 'red'

        self.led['text'] = 'OFF'

        self.therm = False

    def timerOff(self):

        self.led2['bg'] = 'red'

        self.led2['text'] = 'OFF'

        self.timer = False

        self.arrowDown = [(self.nightTime, 100), (self.nightTime,95), (self.nightTime-0.1,97), (self.nightTime,95), (self.nightTime+0.1,97)]

        self.arrowUp = [(self.morningTime,95), (self.morningTime,100), (self.morningTime-0.1, 98), (self.morningTime, 100), (self.morningTime+0.1, 98)]

        morningTempTuple = (self.morningTime, self.morningTemp)

        nightTempTuple = (self.nightTime, self.nightTemp)

        self.graph.plot_line(self.arrowUp, color="black")

        self.graph.plot_line(self.arrowDown, color="black")

        self.graph.plot_point(size=8, x=nightTempTuple[0], y=nightTempTuple[1], color="black")

        self.graph.plot_point(size=8, x=morningTempTuple[0], y=morningTempTuple[1], color="black")

    def clearGraph(self):

        self.graph.draw_axes()

        print("axes drawn flag")

        if self.timer:

            self.timerOn()

    def takePicture(self):

        camera = PiCamera()

        camera.rotation = 180

        camera.resolution = (1500 , 1200)

        camera.annotate_text = 'Jim - BCI ' + now.strftime("%m/%d/%Y %H:%M:%S")

        camera.start_preview()

        camera.framerate =1

        time.sleep(0.2)

        camera.capture('/home/pi/SnakeEnclosure/snakeimg.png')

        camera.close()

        loadimg2 = Image.open('snakeimg.png')

        render2 = ImageTk.PhotoImage(loadimg2)

        img2 = Label(image=render2, bg="black", border=-2)

        img2.image = render2

        Label(Toplevel(), image =render2).grid()



    def heater(self, incr):

        if 0 <= self.heaterValue + incr <= 20:

            self.heaterValue += incr

            self.motorPosition.set_value(self.heaterValue)

            self.open1 = open('motorPosition.txt', 'w')

            self.open1.write(str(self.heaterValue))

            self.open1.close()

            if incr < 0:

                motor.left(abs(20*incr))

                print("left")

            if incr >0:

                motor.right(20*incr)

                print("right")



    def clearList(self):

        self.list1.delete(0,'end')



    def loopControl(self, pace):

        if self.radio.get() == 1:

            self.after_cancel(self.loopTimer)

            self.l3["text"] = f" Loop Time: {pace}"

        else:

            self.after_cancel(self.loopTimer)

            self.l3["text"] = f"Loop Time {pace}"

            self.loopTimer = self.after(self.radio.get(), self.loop)



    def postSetTemp(self, event):

        try:

            self.setTemp = float(self.contents.get())

            self.l1.config(text = "Set Temp: %.1f F"%self.setTemp)

            self.entrythingy['bg'] = 'white'

            self.open2 = open('setTemperature.txt', 'w')

            self.open2.write(str(self.setTemp))

            self.open2.close()

            if 65 > self.setTemp or 95 < self.setTemp:

                self.contents.set("Out of normal range")

                self.entrythingy['bg'] = 'yellow'

                self.list1.insert(END, f"Temperature set to {self.setTemp}")

        except ValueError:

            self.contents.set("Enter a number")

            self.entrythingy['bg'] = "red"



    def raiseSetTemp(self):

        self.setTemp += 1

        self.open2 = open('setTemperature.txt', 'w')

        self.open2.write(str(self.setTemp))

        self.open2.close()

        self.l1.config(text=str("Set Temp: %.1f F" % self.setTemp))

        self.entrythingy.config(bg="white")

        self.list1.insert(END, f"Temperature raised to {self.setTemp}")



    def lowerSetTemp(self):

        self.setTemp -= 1

        self.open2 = open('setTemperature.txt', 'w')

        self.open2.write(str(self.setTemp))

        self.open2.close()

        self.l1.config(text=str("Set Temp: %.1f F" % self.setTemp))

        self.entrythingy.config(bg="white")

        self.list1.insert(END, f"Temperature lowered to {self.setTemp}")





    def loop(self):

        self.actualTemp = temp.read_temp()[1]

        currTime = time.localtime().tm_hour+(time.localtime().tm_min/60)

        now =datetime.now()

        self.dateAndTime["text"] = now.strftime("%m/%d/%Y %H:%M")

        self.loopTimer = self.after(self.radio.get(), self.loop)

        self.l2["text"] = "Actual: %.1f F" %self.actualTemp

        self.dht1['text'] = f"DHT R: {self.dht1Temp} F, {self.dht1Hum}%"

        self.dht2['text'] = f"DHT L: {self.dht2Temp} F, {self.dht2Hum}%"

        if  60 < self.actualTemp < 99:

                self.l2['fg'] = self.colorSpectrum[int(self.actualTemp)-60]

        if  60 < self.dht1Temp < 99:

                self.dht1['fg'] = self.colorSpectrum[int(self.dht1Temp)-60]

        if  60 < self.dht2Temp < 99:

                self.dht2['fg'] = self.colorSpectrum[int(self.dht2Temp)-60]

        self.loopOffset +=1

        if self.therm and (self.loopOffset -1) < 0.5* self.loopOffsetValue < (self.loopOffset+1):

            self.graph.plot_point(x=currTime, y=self.actualTemp, size=5, color = "#FFAA00")

            self.dhtSetup()

        if self.therm and self.loopOffset > self.loopOffsetValue:

            self.graph.plot_point(x=currTime, y=self.setTemp, size=5, color='#FFFFFF')

            self.loopOffset = 0

            if self.setTemp - self.actualTemp >4:

                self.heater(3)

            if self.actualTemp - self.setTemp >4:

                self.heater(-3)

            elif self.setTemp - self.actualTemp > 2:

                self.heater(2)

            elif self.actualTemp - self.setTemp > 2:

                self.heater(-2)

            elif self.setTemp - self.actualTemp > 1:

                self.heater(1)

            elif self.actualTemp - self.setTemp > 1:

                self.heater(-1)

            if self.morningTime < currTime < (self.morningTime+0.25) and self.timer:

                self.setTemp = self.morningTemp

                self.open2 = open('setTemperature.txt', 'w')

                self.open2.write(str(self.setTemp))

                self.open2.close()

                self.l1.config(text=str("Set Temp: %.1f F" % self.setTemp))

                self.entrythingy.config(bg="white")

                self.list1.insert(END, f"Morning! Temp changed to {self.setTemp}")

            if self.nightTime <currTime < (self.nightTime+0.25) and self.timer:

                self.setTemp = self.nightTemp

                self.open2 = open('setTemperature.txt', 'w')

                self.open2.write(str(self.setTemp))

                self.open2.close()

                self.l1.config(text=str("Set Temp: %.1f F" % self.setTemp))

                self.entrythingy.config(bg="white")

                self.list1.insert(END, f"Night! Temp changed to {self.setTemp}")

            if 0 < currTime < 0.25:

                self.clearGraph()





if __name__ == '__main__':

        setupGPIO()

        root = Tk()

        root.attributes('-fullscreen', True)

        root.config(bg="black")

        root.title("Snake Enclosure Monitoring System")

        app = App(master=root)

        app.mainloop()









