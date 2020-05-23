try:
    from tkinter import *
except ImportError:
    from Tkinter import *
import tkinter.font as tkfont
import tk_tools
import time
from PIL import Image, ImageTk
import temp
from picamera import PiCamera
from datetime import datetime
import motor
from math import ceil, floor

print(str(tk_tools.__file__))
now = datetime.now()


class App(Frame):
    def __init__(self, master=None):
        self.f1 = Frame.__init__(self, master, bg="black")
        self.place()
        self.fontSmall = tkfont.Font(family="Helvetica", size=20)
        self.fontLarge = tkfont.Font(family="Helvetica", size=40)
        self.setTemp = 0
        self.loopOffset = 29
        self.open1 = open('motorPosition.txt', 'r')
        self.open2 = open('setTemperature.txt', 'r')
        try:
            self.heaterValue = int(self.open1.readline())
        except ValueError:
            self.heaterValue = 0
            self.open1 = open('motorPosition.txt', 'w')
            self.open1.write(str(self.heaterValue))
        try:
            self.setTemp = float(self.open2.readline())
        except:
            pass
        self.open1.close()
        self.open2.close()
        self.morningTemp = 86
        self.morningTime = 8
        self.nightTemp = 79
        self.nightTime = 21
        self.therm = False
        self.timer = False
        self.led = Label(bg='red', border=2, width=5, height=1, relief='ridge', text='OFF')
        self.led.place(x=300, y=230)
        self.led2 = Label(bg='red', border=2, width=5, height=1, relief='ridge', text='OFF')
        self.led2.place(x=300, y=270)
        self.actualTemp = 0.0
        self.radio = IntVar()
        self.radio.set(1)
        self.contents = StringVar()
        self.contents.set("Set Temperature")
        self.loadimg = Image.open('snakepic.png')
        self.render = ImageTk.PhotoImage(self.loadimg)
        self.img = Label(image=self.render, bg="black", border=-2)
        self.img.image = self.render
        self.img.place(x=760, y=100)
        self.l2 = Label(text=f"Actual: {self.actualTemp} F", bg="black", fg="green", font=self.fontLarge)
        self.l2.place(x=0, y=0)
        self.l1 = Label(text=f"Set Temp: {self.setTemp} F", bg="black", fg="yellow", font=self.fontLarge)
        self.l1.place(x=0, y=80)
        self.b1 = Button(text='+', font=self.fontLarge, command=self.raiseSetTemp, fg="white", bg="maroon", width=5)
        self.b1.place(x=185, y=150)
        self.b2 = Button(text='-', font=self.fontLarge, command=self.lowerSetTemp, bg="dark blue", fg="white", width=5)
        self.b2.place(x=10, y=150)
        self.r1 = Radiobutton(bg="black", fg="white", text="OFF", value=1, variable=self.radio,
                              command=lambda: self.loopControl("OFF"))
        self.r1.place(x=1500, y=40)
        self.r2 = Radiobutton(bg="black", fg="white", text="1 Second", value=1000, variable=self.radio,
                              command=lambda: self.loopControl("1 Second"))
        self.r2.place(x=1500, y=70)
        self.r3 = Radiobutton(bg="black", fg="white", text="30 Seconds", value=30000, variable=self.radio,
                              command=lambda: self.loopControl("30 Seconds"))
        self.r3.place(x=1500, y=100)
        self.r4 = Radiobutton(bg="black", fg="white", text="1 Minute", value=60000, variable=self.radio,
                              command=lambda: self.loopControl("1 Minute"))
        self.r4.place(x=1500, y=130)
        self.l3 = Label(bg="black", fg="white", text="Loop Time: 1 Second")
        self.l3.place(x=1500, y=10)
        self.entrythingy = Entry(bg="dark grey", font=self.fontSmall)
        self.entrythingy.place(x=10, y=310)
        self.entrythingy["textvariable"] = self.contents
        self.entrythingy.bind('<Key-Return>', self.postSetTemp)
        self.list1 = Listbox(width=30, height=20, bg="black", fg="white", font=self.fontSmall)
        self.scroll1 = Scrollbar(highlightcolor="blue")
        self.list1.config(yscrollcommand=self.scroll1.set)
        self.list1.place(x=0, y=440)
        self.scroll1["command"] = self.list1.yview
        self.scroll1.place(x=453, y=440, relheight=0.615)
        self.b3 = Button(text="EXIT", bg="dark red", command=self.exit, font=self.fontSmall)
        self.b3.place(x=1840, y=0)
        self.graph = tk_tools.Graph(parent=self.f1, x_min=0, y_min=67, x_max=24, y_max=100, x_tick=6, y_tick=10,
                                    width=1500)
        self.graph.canvas["bg"] = 'black'
        self.graph.canvas['bd'] = 0
        self.graph.canvas['highlightthickness'] = 0
        self.graph.canvas.config(width=1500)  # float(self.canvas.config('width')[4])
        self.graph.place(x=540, y=820)

        self.motorPosition = tk_tools.Gauge(red_low=20, yellow_low=30, divisions=10, yellow=70, red=80, bg="black", \
                                            parent=self.f1, min_value=0, max_value=20, label='Heater', width=400,
                                            height=200)
        self.motorPosition._canvas['bd'] = 0
        self.motorPosition._canvas['highlightthickness'] = 0
        self.motorPosition.place(x=450, y=0)
        self.motorPosition.set_value(self.heaterValue)
        self.b4 = Button(text='-', font=self.fontLarge, command=lambda: self.heater(-1), bg="dark blue", fg="white",
                         width=5)
        self.b4.place(x=470, y=230)
        self.b5 = Button(text='+', font=self.fontLarge, command=lambda: self.heater(1), fg="white", bg="maroon",
                         width=5)
        self.b5.place(x=645, y=230)
        self.b6 = Button(text='Clear Listbox', font=self.fontSmall, command=self.clearList, fg="black", bg="white",
                         width=10)
        self.b6.place(x=20, y=360)
        self.b7 = Button(text="Take a Picture", bg="grey", command=self.takePicture)
        self.b7.place(x=1000, y=0)
        self.b8 = Button(text="Reset", command=self.clearGraph)
        self.b8.place(x=1685, y=830, border="outside")
        self.b9 = Button(text="Thermostat On", command=lambda: self.thermOn("therm"))
        self.b9.place(x=10, y=230)
        self.b10 = Button(text="Thermostat Off", command=lambda: self.thermOff("therm"))
        self.b10.place(x=150, y=230)
        self.b9a = Button(text="Timer On", command=lambda: self.thermOn("timer"))
        self.b9a.place(x=10, y=270)
        self.b10a = Button(text="Timer Off", command=lambda: self.thermOff("timer"))
        self.b10a.place(x=150, y=270)
        self.b11 = Button(text="+", command=self.regUp, font=self.fontSmall, width=2)
        self.b11.place(x=1740, y=30)
        self.b11 = Button(text="-", command=self.regDown, font=self.fontSmall, width=2)
        self.b11.place(x=1675, y=30)
        self.loopOffsetValue = 250
        self.regLabel = Label(text=f"Adjust After {self.loopOffsetValue} Loops", bg="black", fg='white')
        self.regLabel.place(x=1660, y=10)
        self.loopTimer = self.after(1, self.loop)

        self.arrowDown = [(self.nightTime, 100), (self.nightTime, 95), (self.nightTime - 0.1, 97), (self.nightTime, 95),
                          (self.nightTime + 0.1, 97)]
        self.arrowUp = [(self.morningTime, 95), (self.morningTime, 100), (self.morningTime - 0.1, 98),
                        (self.morningTime, 100), (self.morningTime + 0.1, 98)]
        self.scale1 = Scale(from_=0.0, to=24.0, orient=HORIZONTAL, length=200)
        self.scale1.place(x=600, y=825)
        self.scale2 = Scale(from_=0.0, to=24.0, orient=HORIZONTAL, length=200)
        self.scale2.place(x=830, y=825)
        self.scale1.set(self.morningTime)
        self.scale2.set(self.nightTime)
        self.scale1Label = Label(text="Morning Time", bg="black", fg="white")
        self.scale1Label.place(x=600, y=800)
        self.scale2Label = Label(text="Night Time", bg="black", fg="white")
        self.scale2Label.place(x=830, y=800)
        self.scale1Button = Button(text="Set", width=2, height=1, command=lambda: self.morningSet())
        self.scale1Button.place(x=730, y=718)
        self.scale2Button = Button(text="Set", width=2, height=1, command=lambda: self.nightSet())
        self.scale2Button.place(x=960, y=718)
        self.scale3Label = Label(text="Morning Temp", bg="black", fg="white")
        self.scale3Label.place(x=600, y=720)
        self.scale4Label = Label(text="Night Temp", bg="black", fg="white")
        self.scale4Label.place(x=830, y=720)
        self.scale3 = Scale(from_=70, to=100, orient=HORIZONTAL, length=200)
        self.scale3.place(x=600, y=750)
        self.scale4 = Scale(from_=70, to=100, orient=HORIZONTAL, length=200)
        self.scale4.place(x=830, y=750)
        self.scale3.set(self.morningTemp)
        self.scale4.set(self.nightTemp)
        self.dateAndTime = Label(bg='black', fg="white", text=now.strftime("%m/%d/%Y %H:%M"), font=self.fontSmall,
                                 border=2, relief='ridge')
        self.dateAndTime.place(x=1200, y=800)

    def morningSet(self):
        x = self.therm
        self.thermOff("timer")
        self.morningTime = int(self.scale1.get())
        self.morningTemp = int(self.scale3.get())
        if x:
            self.thermOn("timer")

    def nightSet(self):
        x = self.therm
        self.thermOff("timer")
        self.nightTime = int(self.scale2.get())
        self.nightTemp = int(self.scale4.get())
        if x:
            self.thermOn("timer")

    def regUp(self):
        self.loopOffsetValue += 1
        self.regLabel['text'] = f"Adjust After {self.loopOffsetValue} Loops"

    def regDown(self):
        self.loopOffsetValue -= 1
        self.regLabel['text'] = f"Adjust After {self.loopOffsetValue} Loops"

    def thermOn(self, timerOrTherm):
        if timerOrTherm == "therm":
            print("therm on")
            self.led['bg'] = 'green'
            self.led['text'] = 'ON'
            self.therm = True
        if timerOrTherm == "timer":
            self.led2['bg'] = 'green'
            self.led2['text'] = 'ON'
            self.timer = True
            morningTempTuple = (self.morningTime, self.morningTemp)
            nightTempTuple = (self.nightTime, self.nightTemp)
            self.arrowDown = [(self.nightTime, 100), (self.nightTime, 95), (self.nightTime - 0.1, 97),
                              (self.nightTime, 95), (self.nightTime + 0.1, 97)]
            self.arrowUp = [(self.morningTime, 95), (self.morningTime, 100), (self.morningTime - 0.1, 98),
                            (self.morningTime, 100), (self.morningTime + 0.1, 98)]
            self.graph.plot_line(self.arrowUp, color="white")
            self.graph.plot_line(self.arrowDown, color="white")
            self.graph.plot_point(size=8, x=nightTempTuple[0], y=nightTempTuple[1], color="blue")
            self.graph.plot_point(size=8, x=morningTempTuple[0], y=morningTempTuple[1], color="blue")

    def thermOff(self, timerOrTherm):
        if timerOrTherm == "therm":
            print("therm off")
            self.led['bg'] = 'red'
            self.led['text'] = 'OFF'
            self.therm = False
        if timerOrTherm == "timer":
            self.led2['bg'] = 'red'
            self.led2['text'] = 'OFF'
            self.timer = False
            self.arrowDown = [(self.nightTime, 100), (self.nightTime, 95), (self.nightTime - 0.1, 97),
                              (self.nightTime, 95), (self.nightTime + 0.1, 97)]
            self.arrowUp = [(self.morningTime, 95), (self.morningTime, 100), (self.morningTime - 0.1, 98),
                            (self.morningTime, 100), (self.morningTime + 0.1, 98)]
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
            self.thermOn("timer")
        else:
            self.thermOff("timer")

    def takePicture(self):
        camera = PiCamera()
        camera.rotation = 180
        camera.resolution = (700, 500)
        camera.annotate_text = 'Jim - BCI ' + now.strftime("%m/%d/%Y %H:%M:%S")
        camera.start_preview()
        time.sleep(0.2)
        camera.capture('/home/pi/Desktop/Project1/snakeimg.png')
        camera.close()
        loadimg2 = Image.open('snakeimg.png')
        render2 = ImageTk.PhotoImage(loadimg2)
        img2 = Label(image=render2, bg="black", border=-2)
        img2.image = render2
        Label(Toplevel(), image=render2).grid()

    def heater(self, incr):
        if 0 <= self.heaterValue + incr <= 20:
            self.heaterValue += incr
            self.motorPosition.set_value(self.heaterValue)
            self.open1 = open('motorPosition.txt', 'w')
            self.open1.write(str(self.heaterValue))
            self.open1.close()
            if incr < 0:
                motor.left(abs(20 * incr))
                print("left")
            if incr > 0:
                motor.right(20 * incr)
                print("right")

    def clearList(self):
        self.list1.delete(0, 'end')

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
            self.l1.config(text="Set Temp: %.1f F" % self.setTemp)
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

    def exit(self):
        quit()

    def loop(self):
        self.actualTemp = temp.read_temp()[1]
        currTime = time.localtime().tm_hour + (time.localtime().tm_min / 60)
        now = datetime.now()
        self.dateAndTime["text"] = now.strftime("%m/%d/%Y %H:%M")
        self.loopTimer = self.after(1000, self.loop)
        self.l2["text"] = "Actual: %.1f F" % self.actualTemp
        self.loopOffset += 1
        if self.therm and (self.loopOffset - 1) < 0.5 * self.loopOffsetValue < (self.loopOffset + 1):
            self.graph.plot_point(x=currTime, y=self.actualTemp, size=5, color='green')
        if self.therm and self.loopOffset > self.loopOffsetValue:
            self.graph.plot_point(x=currTime, y=self.setTemp, size=5, color='yellow')
            self.loopOffset = 0
            if self.setTemp - self.actualTemp > 4:
                self.heater(3)
            if self.actualTemp - self.setTemp > 4:
                self.heater(-3)
            elif self.setTemp - self.actualTemp > 2:
                self.heater(2)
            elif self.actualTemp - self.setTemp > 2:
                self.heater(-2)
            elif self.setTemp - self.actualTemp > 1:
                self.heater(1)
            elif self.actualTemp - self.setTemp > 1:
                self.heater(-1)
            if self.morningTime < currTime < (self.morningTime + 0.2) and self.timer:
                self.setTemp = self.morningTemp
                self.open2 = open('setTemperature.txt', 'w')
                self.open2.write(str(self.setTemp))
                self.open2.close()
                self.l1.config(text=str("Set Temp: %.1f F" % self.setTemp))
                self.entrythingy.config(bg="white")
                self.list1.insert(END, f"Morning! Temp changed to {self.setTemp}")
            if self.nightTime < currTime < (self.nightTime + 0.2) and self.timer:
                self.setTemp = self.nightTemp
                self.open2 = open('setTemperature.txt', 'w')
                self.open2.write(str(self.setTemp))
                self.open2.close()
                self.l1.config(text=str("Set Temp: %.1f F" % self.setTemp))
                self.entrythingy.config(bg="white")
                self.list1.insert(END, f"Night! Temp changed to {self.setTemp}")
            if 0 < currTime < 0.1:
                self.clearGraph()


if __name__ == '__main__':
    root = Tk()
    root.attributes('-fullscreen', True)
    root.config(bg="black")
    root.title("SNAKE CAGE")
    app = App(master=root)
    app.mainloop()


