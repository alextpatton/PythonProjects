###GUI tool that will keypress after a delay or left or right click after a delay
###I use it to AFK battlegrounds in WoW
import win32gui, win32api, win32con, win32com.client, time, math
from tkinter import *
import tkinter as tk
from tkinter.ttk import *

learnx = 0
learny = 0
keypressarray = [' ','10']
keypressrunning = None
clickerrunning = None
grid_row = {}
grid_row['title'] = 0
grid_row['input1'] = 2
grid_row['input2'] = 3
grid_row['buttons'] = 4
grid_row['countdown']=5
keypresscounter = 0
clickcounter = 0

#keyboard
def keypress(key):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys(key)
#initiate keypress
def initkeypress():
    global keypresscounter
    stopkeypress()
    retrieve_input()
    keypresscounter = keypressarray[1]
    keypressloop()
        
#loop keypress
def keypressloop():
    global keypressarray, keypressrunning, keypresscounter
    countdowntext.set('Time until Press: ' + str(keypresscounter))
    keypresscounter = int(keypresscounter)-1
    if keypresscounter < 0:
        keypress(keypressarray[0])
        initkeypress()
    else:    
        keypressrunning = root.after(1000,keypressloop)
    
#stop keypressloop    
def stopkeypress():
    global keypressrunning
    countdowntext.set('Stopped')
    if keypressrunning is not None:
        root.after_cancel(keypressrunning)
        keypressrunning = None
        
#retrieve textbox input
def retrieve_input():
    global keypressarray
    keypressarray[0] = textinput_key.get("1.0",'end-1c') #need to add error checking
    keypressarray[1] = textinput_time.get("1.0",'end-1c')#need to add error checking

#mouse
#clicks the mouse at coords
def click(x,y):
    if LR_int.get() == 0:
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
    else:
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    
#gets the mouse pos and saves it
def setCursorPos():
    global learnx, learny
    flags, hcursor, (x,y) = win32gui.GetCursorInfo()
    learnx = x
    learny = y
#init clicker
def initclicker():
    global clickcounter
    stopclicker()
    clickcounter = textinput_clicktime.get("1.0",'end-1c')#add error checking
    clickerloop()
    
#start auto clicker    
def clickerloop():
    global clickerrunning, clickarray, learnx, learny, clickcounter
    setCursorPos()
    countdowntext2.set('Click @ ('+str(learnx)+', '+str(learny)+') in: ' + str(clickcounter))
    clickcounter = int(clickcounter) - 1
    if clickcounter < 0:
        click(learnx,learny)
        initclicker()
    else:
        clickerrunning = root.after(1000,clickerloop)
#stop clicker
def stopclicker():
    global clickerrunning
    countdowntext2.set('Stopped')
    if clickerrunning is not None:
        root.after_cancel(clickerrunning)
        clickerrunning = None

#tk stuff
root = tk.Tk()
#init countdown text
countdowntext = StringVar()
countdowntext.set('Not Running')
countdowntext2 = StringVar()
countdowntext2.set('Not Running')
#radio button var
LR_int = IntVar()
LR_int.set(0)
#window title
root.wm_title("WoWHelper")
#tabs
n = Notebook(root)
f1 = Frame(n);
f2 = Frame(n);
n.add(f1, text='Key Presser')
n.add(f2, text='Mouse Clicker')
n.grid(row=0, columnspan=2)



#key press on frame 1
#Text input of the key to be pressed
keytext = Label(f1, text="Key To Press").grid(row=grid_row['input1'])
textinput_key = Text(f1, height=1, width=5)
textinput_key.grid(row=grid_row['input1'], column=1)
textinput_key.insert(END, " ")
#Time between presses, default 15seconds
timetext = Label(f1, text="Time Delay(Sec)").grid(row=grid_row['input2'])
textinput_time = Text(f1, height=1, width=5)
textinput_time.grid(row=grid_row['input2'], column=1)
textinput_time.insert(END, "10")
#quitbutton
b1_0 = Button(f1, text="Quit", command=root.destroy).grid(row=grid_row['buttons'], column=2)
#startbutton
b1_1 = Button(f1, text="Start", command=initkeypress).grid(row=grid_row['buttons'])
b1_2 = Button(f1, text="Stop", command=stopkeypress).grid(row=grid_row['buttons'],column=1)
#run announcement+countdown
countdowntext_label = Label(f1, textvariable=countdowntext).grid(row=grid_row['countdown'])

#Mouse Clicker on Frame 2
LR_label = Label(f2, text="Left or Right").grid(row=0,columnspan=3)
RB0 = Radiobutton(f2, text='L', variable=LR_int, value=0)
RB0.grid(row=1)
RB1 = Radiobutton(f2, text='R', variable=LR_int, value=1)
RB1.grid(row=1,column=2)
label_clicktime = Label(f2, text="Time Delay(Sec)").grid(row=2)
textinput_clicktime = Text(f2, height=1, width=5)
textinput_clicktime.grid(row=2, column=1)
textinput_clicktime.insert(END, "10")
#buttons
b2_0 = Button(f2, text="Quit", command=root.destroy).grid(row=grid_row['buttons'],column=2)
b2_1 = Button(f2, text="Start", command=initclicker).grid(row=grid_row['buttons'])
b2_2 = b1_2 = Button(f2, text="Stop", command=stopclicker).grid(row=grid_row['buttons'],column=1)
countdowntext2_label = Label(f2, textvariable=countdowntext2).grid(row=grid_row['countdown'])

#tk loop, -topmost flag to keep always on top
root.call('wm', 'attributes', '.', '-topmost', '1')
root.mainloop()
