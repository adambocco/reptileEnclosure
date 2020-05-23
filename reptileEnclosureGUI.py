try:
    from Tkinter import *
except ImportError:
    from tkinter import *
from picamera import PiCamera
from PIL import ImageTk, Image
import tk_tools
import datetime
import calendar
import time
import RPi.GPIO as GPIO
import time
from time import sleep as sleep
import os
import sys
from PCF8574 import PCF8574_GPIO
from datetime import datetime
from tkinter.font import Font
from motor import right, left

buttonPhys1 = 27  # physical button signal input pins
buttonPhys2 = 17
buttonPhys3 = 22
buttonPhys4 = 12
buttonPhys5 = 16
dht = 23  # dht signal input pins
dht2 = 25
dht3 = 24

thermoStatus = 0
setGap = 1.5  # default range of temperatures to reach is setGap*2 (setGap of 2 at setTemp of 75 would regulate temp to 73-77)
setTemp = 75  # thermostat set temp
motorPos2 = 50

loopMargin = 8000

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
root = Tk()
text = Text(root)
myFont = Font(family="Helvetica", size=22)
text.configure(font=myFont)
graphList = []
graphX = 0
camera = PiCamera()
img2 = ImageTk.PhotoImage(Image.open("snake.jpeg"))

motorFile = open("log.txt", "r")
motorPos1 = motorFile.readlines()
motorPos1 = int(motorPos1[0])


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buttonPhys1, GPIO.IN)
    GPIO.setup(buttonPhys2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(buttonPhys3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(buttonPhys4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(buttonPhys5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dht, GPIO.IN)
    GPIO.setup(dht2, GPIO.IN)
    GPIO.setup(dht3, GPIO.IN)


def thermo():
    gap = abs(setTemp - tempAvg)
    print(gap)
    if setTemp >= tempAvg:
        if gap > 10:  # if temp is much higher than set temp, turn dial down a lot
            motor1UpThermo(20)
        if gap <= 10 and gap > 5:  # is temp is less than 1.5 degrees above setTemp, do nothing(pass)
            motor1UpThermo(10)
        if gap <= 5 and gap > setGap:
            motor1UpThermo(2)
        else:
            pass

    if setTemp <= tempAvg:
        if gap > 10:  # if temp is much lower than set temp, turn dial up a lot
            motor1DownThermo(20)
        if gap <= 10 and gap > 5:  # is temp is less than 1.5 degrees below setTemp, do nothing(pass)
            motor1DownThermo(10)
        if gap <= 5 and gap > setGap:
            motor1DownThermo(2)
        else:
            pass


def thermoOn():
    global thermoStatus
    thermoStatus = 1
    labelThermoStatus.config(text="Thermo is ON")


def thermoOff():
    global thermoStatus
    thermoStatus = 0
    labelThermoStatus.config(text="Thermo is OFF")


def openGap():
    global setGap
    setGap += 0.1
    label99.config(text=str(round(setGap * 2, 2)))


def closeGap():
    global setGap
    setGap -= 0.1
    label99.config(text=str(round(setGap * 2, 2)))


def motor1UpThermo(a):
    global motorPos1
    if motorPos1 < 100:
        motor.right(a)
        print('turning motor right')
        motorPos1 += a
        gauge1.set_value(motorPos1)
        motorWrite = open("log.txt", "w")
        motorWrite.write(str(motorPos1))
    else:
        pass


def motor1DownThermo(a):
    global motorPos1
    if motorPos1 > 0:
        motor.left(50)
        print('turning motor left')
        motorPos1 -= 10
        gauge1.set_value(motorPos1)
        motorWrite = open("log.txt", "w")
        motorWrite.write(str(motorPos1))
    else:
        pass


def motor1Up():
    global motorPos1
    if motorPos1 < 100:
        motor.right(50)
        print('turning motor right')
        motorPos1 += 10
        gauge1.set_value(motorPos1)
        motorWrite = open("log.txt", "w")
        motorWrite.write(str(motorPos1))
    else:
        pass


def motor1Down():
    global motorPos1
    if motorPos1 > 0:
        motor.left(50)
        print('turning motor left')
        motorPos1 -= 10
        gauge1.set_value(motorPos1)
        motorWrite = open("log.txt", "w")
        motorWrite.write(str(motorPos1))
    else:
        pass


def motor2Up():
    if motorPos2 < 100:
        motorPos2 += 10
        gauge2.set_value(motorPos2)
    else:
        pass


def motor2Down():
    if motorPos2 > 0:
        motorPos2 -= 10
        gauge2.set_value(motorPos2)
    else:
        pass


def dhtSetup():
    global temp1, temp2, temp3, hum1, hum2, hum3, tempAvg, humAvg
    hum1, temp1 = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, dht)
    print("DHT1 reading")
    if hum1 is not None and temp1 is not None:
        temp1 = temp1 * 9 / 5 + 32
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temp1, hum1))
    else:
        print('Failed to get reading')
    hum2, temp2 = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, dht2)
    print("DHT2 reading")
    if hum2 is not None and temp2 is not None:
        temp2 = temp2 * 9 / 5 + 32
        print('Temp2={0:0.1f}*  Humidity2={1:0.1f}%'.format(temp2, hum2))
    else:
        print('Failed to get reading')
    hum3, temp3 = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, dht3)
    print("DHT3 reading")
    if hum3 is not None and temp3 is not None:
        temp3 = temp3 * 9 / 5 + 32
        print('Temp3={0:0.1f}*  Humidity3={1:0.1f}%'.format(temp3, hum3))
    else:
        print('Failed to get reading')
    tempAvg = round(float((temp2 + temp3) / 2), 1)
    humAvg = round(float((hum2 + hum3) / 2), 1)


def displaySetup():
    global lcd
    try:
        mcp = PCF8574_GPIO(PCF8574_address)
    except:
        try:
            mcp = PCF8574_GPIO(PCF8574A_address)
        except:
            print('I2C Address Error !')
            exit(1)
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)
    mcp.output(3, 1)  # turn on LCD backlight
    lcd.begin(16, 2)  # set number of LCD lines and columns
    lcd.clear()
    lcd.setCursor(0, 0)


def manSetTemp():
    setTemp = int(entry1.get())
    print("Set temperature to " + str(setTemp))
    label2.config(text=str(setTemp))


def changeColor():
    if tempAvg <= 65:
        labelTemp.config(bg="navy")
    if tempAvg > 65 and tempAvg <= 70:
        labelTemp.config(bg="blue2")
    if tempAvg > 70 and tempAvg <= 74:
        labelTemp.config(bg="orange")
    if tempAvg > 74 and tempAvg <= 78:
        labelTemp.config(bg="dark orange")
    if tempAvg > 78 and tempAvg <= 82:
        labelTemp.config(bg="orange red")
    if tempAvg > 82 and tempAvg <= 86:
        labelTemp.config(bg="red")
    if tempAvg > 86 and tempAvg <= 90:
        labelTemp.config(bg="red2")
    if tempAvg > 90 and tempAvg <= 94:
        labelTemp.config(bg="red3")
    if tempAvg > 94:
        labelTemp.config(color="red4")


def setTempUp(ev=None):
    global setTemp
    setTemp += 1
    label2.config(text=str(setTemp))


def setTempDown(ev=None):
    global setTemp
    setTemp -= 1
    label2.config(text=str(setTemp))


def clearGraph():
    graphX = 0
    graph1.draw_axes()


def fastLoop():
    global loopMargin
    loopMargin = 5000
    labelLoop.config(text="Running")
    loop()


def slowLoop():
    global loopMargin
    loopMargin = 100000
    labelLoop.config(text="Running slowly")
    loop()


def takePicture():
    global img
    camera.resolution = (400, 280)
    camera.capture('/home/pi/Desktop/Project1/Project1A/image.jpg')
    img = ImageTk.PhotoImage(Image.open("image.jpg"))
    label95.config(image=img)


def gui():
    global listbox1, label3a, label4a, label5a, labelTemp, graph1, img, label95, graph1, labelLoop, gauge1, label99, label2, labelThermoStatus, label2
    frame1 = Frame(root, width=600, height=400, relief=SUNKEN)
    frame1.pack()
    frame2 = Frame(root, relief=SUNKEN)
    frame2.pack()
    listbox1 = Listbox(frame1, bd=4, bg="black", fg="white", height=20, width=30)
    listbox1.grid(column=1, row=1, rowspan=5)
    scrollbar1 = Scrollbar(frame1)
    scrollbar1.grid(column=1, row=1, sticky="ENS", rowspan=5)
    scrollbar1.config(command=listbox1.yview, orient="vertical")
    listbox1.config(yscrollcommand=scrollbar1.set)
    label1 = Label(frame1, text="Temp Set To:", fg="black", relief="ridge", font=Font(size=13))
    label1.grid(column=2, row=1, sticky="NW")
    label2 = Label(frame1, text=str(setTemp), bg="green", borderwidth=2, relief="ridge", font=Font(size=25))
    label2.grid(column=2, row=1, sticky="NE")
    buttonMan = Button(frame1, text="Run Loop", bg="white", command=lambda: loop())
    buttonMan.grid(column=4, row=1, sticky=E)
    labelLoop = Label(frame1, text="OFF")
    labelLoop.grid(column=4, row=1, sticky="NE")
    label3 = Label(frame1, text="DHT left reading")
    label3.grid(column=2, row=2)
    label4 = Label(frame1, text="DHT mid reading")
    label4.grid(column=3, row=2)
    label5 = Label(frame1, text="DHT right reading:")
    label5.grid(column=4, row=2)
    label3a = Label(frame1, text="{}F  {}%".format(str(temp1), str(hum1)), bg="green", borderwidth=2, relief="ridge",
                    font=Font(size=20))
    label3a.grid(column=2, row=3)
    label4a = Label(frame1, text="{}F  {}%".format(str(temp2), str(hum2)), bg="green", borderwidth=2, relief="ridge",
                    font=Font(size=20))
    label4a.grid(column=3, row=3)
    label5a = Label(frame1, text="{}F  {}%".format(str(temp3), str(hum3)), bg="green", borderwidth=2, relief="ridge",
                    font=Font(size=20))
    label5a.grid(column=4, row=3)
    label6 = Label(frame1, text="Heater 1", font=Font(size=12), bg="blue", relief="ridge", fg="white")
    label6.grid(column=2, row=4, sticky=N)
    label7 = Label(frame1, text="Heater 2", font=Font(size=12), bg="blue", relief="ridge", fg="white")
    label7.grid(column=4, row=4, sticky=N)
    gauge1 = tk_tools.Gauge(frame1, max_value=100, label='Heat 1', unit='%')
    gauge1.grid(column=2, row=5)
    gauge2 = tk_tools.Gauge(frame1, max_value=100, label="Heat 2", unit='%')
    gauge2.grid(column=4, row=5)
    gauge1.set_value(motorPos1)
    gauge2.set_value(motorPos2)
    labelTemp = Label(frame1, text=str(round(float(tempAvg), 2)), bg="red", fg="white", borderwidth=2, relief="ridge",
                      font=Font(size=25))
    labelTemp.grid(column=3, row=1, sticky=NE)
    labelTempa = Label(frame1, text="Temp:", font=Font(size=13), relief='ridge')
    labelTempa.grid(column=3, row=1, sticky=NW)
    button1 = Button(frame1, text="-", command=lambda: motor1Down())
    button1.grid(column=2, row=4, sticky=SW)
    button2 = Button(frame1, text="+", command=lambda: motor1Up())
    button2.grid(column=2, row=4, sticky=SE)
    button3 = Button(frame1, text="-", command=lambda: motor2Down())
    button3.grid(column=4, row=4, sticky=SW)
    button4 = Button(frame1, text="+", command=lambda: motor2Up())
    button4.grid(column=4, row=4, sticky=SE)
    button5 = Button(frame1, text="-", command=lambda: setTempDown())
    button5.grid(column=2, row=1, sticky="SW")
    button6 = Button(frame1, text="+", command=lambda: setTempUp())
    button6.grid(column=2, row=1, sticky="SE")
    entry1 = Entry(frame1, width=2)
    entry1.grid(column=2, row=1)
    button7 = Button(frame1, text="Set", command=lambda: manSetTemp())
    button7.grid(column=2, row=1, sticky=S)
    button8 = Button(frame1, text="Run", command=lambda: fastLoop())
    button8.grid(column=4, row=1, sticky=NW)
    button9 = Button(frame1, text="Stop(slow)", command=lambda: slowLoop())
    button9.grid(column=4, row=1, sticky=SW)
    button10 = Button(frame1, text="Widen gap", command=lambda: openGap())
    button10.grid(column=3, row=4, sticky=NW)
    button11 = Button(frame1, text="Close gap", command=lambda: closeGap())
    button11.grid(column=3, row=4, sticky=SW)
    label99 = Label(frame1, text=str(setGap * 2))
    label99.grid(column=3, row=4, sticky=E)
    button99 = Button(frame1, text="Capture", command=lambda: takePicture())
    button99.grid(column=3, row=5, sticky=NE)
    button98 = Button(frame1, text="Clear Graph", command=lambda: clearGraph())
    button98.grid(column=3, row=5, sticky=NW)
    button97 = Button(frame1, text="Thermo ON", command=lambda: thermoOn())
    button97.grid(column=3, row=5, sticky=SW)
    button96 = Button(frame1, text="Thermo OFF", command=lambda: thermoOff())
    button96.grid(column=3, row=5, sticky=SE)
    graph1 = tk_tools.Graph(frame2, x_min=0, x_max=100, y_min=50, y_max=100, x_tick=10, y_tick=5)
    graph1.grid(column=1, row=1)
    label95 = Label(frame2, width=400, height=280, image=img2)
    label95.grid(column=2, row=1)
    labelThermoStatus = Label(frame1, text="Thermo is OFF")
    labelThermoStatus.grid(column=3, row=5)


def loop():
    global graphList, loopMargin, graphX, x, root
    dhtSetup()
    ts = datetime.now().strftime("%m/%d-%H:%M")
    lcd.setCursor(0, 0)
    if thermoStatus == 1:
        x = "Thermo ON"
    else:
        x = "Thermo is OFF"
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.message(x)
    lcd.setCursor(14, 0)
    lcd.message(str(setTemp))
    lcd.setCursor(0, 1)
    lcd.message("T:{}F  H:{}%".format(str("%.1f" % tempAvg), str(humAvg)))
    root.after(loopMargin, loop)
    global listbox1, labelTemp, label3a, label4a, label5a
    listbox1.insert(0, str(tempAvg) + "F  " + str(humAvg) + "%  Set: " + str(setTemp) + "F " + ts)
    labelTemp.config(text=str(round(float(tempAvg), 2)))
    label3a.config(text="{}F  {}%".format(str(temp1), str(hum1)))
    label4a.config(text="{}F  {}%".format(str(temp2), str(hum2)))
    label5a.config(text="{}F  {}%".format(str(temp3), str(hum3)))

    graphX += 1  # draw point on graph x = time; y = temp avg
    if graphX >= 100:
        graphX = 1
    point1 = (graphX, float(tempAvg))
    graphList.append(point1)
    graph1.plot_line(graphList)
    graph1.grid(column=1, row=1)
    changeColor()
    if thermoStatus == 1:
        thermo()


def destroy():
    pass


if __name__ == '__main__':  # Program start from here
    setup()
    dhtSetup()
    displaySetup()
    try:
        GPIO.add_event_detect(buttonPhys1, GPIO.RISING, callback=setTempUp, bouncetime=200)
        GPIO.add_event_detect(buttonPhys2, GPIO.RISING, callback=setTempDown, bouncetime=200)
        GPIO.add_event_detect(buttonPhys3, GPIO.RISING, callback=setTempUp, bouncetime=200)
        GPIO.add_event_detect(buttonPhys4, GPIO.RISING, callback=setTempUp, bouncetime=200)
        GPIO.add_event_detect(buttonPhys5, GPIO.RISING, callback=setTempUp, bouncetime=200)
        gui()
        mainloop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
