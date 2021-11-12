#psychopy
from psychopy import visual, logging, core
#from psychopy import *
from psychopy import parallel
from psychopy.iohub import launchHubServer

from psychopy import logging
import time
logging.LogFile(f='logs/new log ' + str(time.time()) + '.txt', level=logging.DATA)

response_box = False
send_triggers = True

if response_box:
    import pyxid

#other libs
import numpy as np

#own files
from car import Car
from track import Track

if send_triggers:
    port = parallel.ParallelPort(address=0x0378)
    port2 = parallel.ParallelPort(address=0xCCD0)

def send_event(data):
    logging.data('trigger ' + str(data))
    if send_triggers: 
        port.setData(data)
        port2.setData(data)
        core.wait(0.005)
        port.setData(0)
        port2.setData(0)

if response_box:
    devices = pyxid.get_xid_devices()
    print('devices')
    print(devices)
    for dev in devices:
        dev.reset_base_timer
        dev.reset_rt_timer()

io = launchHubServer()
keyboard = io.devices.keyboard


win = visual.Window(size=(1280, 1024), fullscr=True, units='pix', screen=0, allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True
    )


#timer = core.Clock() #for sending "heartbeat" trigger

laptimer = core.Clock()


background = visual.ImageStim(win, image="empty.png")
background.pos = (background.size[0] * 0.5 - win.size[0] * 0.5, background.size[1] * 0.5 - win.size[1] * 0.5)
background.setAutoDraw(True)


textboxbg = visual.Rect(win, width=200, height=100)
textboxbg.setFillColor((0,0,0), 'rgb255')
textbox = visual.TextStim(win, font='Helvetica', text = '', color=(255, 255, 255), colorSpace='rgb255')

def clearTextBox():
    textbox.text = ''
    textboxbg.setAutoDraw(False)
    textbox.setAutoDraw(False)


if response_box:
    keys = {
        'left': 2,
        'right': 3,
        'forward': 12,
        'backward':  13
    }
else:
    keys = {
        'left': 'k',
        'right': 'o',
        'forward': 'u',
        'backward': 'h'
    }

triggers = { # triggers for keys, maybe not necessary
    'left': 11,
    'right': 12,
    'forward': 13,
    'backward': 14
}

def newLap():
    textboxbg.setAutoDraw(True)
    textbox.setAutoDraw(True)
    textbox.text = 'Kierrosaika: {0:.2f}'.format(laptimer.getTime())
    laptimer.reset()
    send_event(42) #lap start trigger

def runTrack(trackname):
    global keys
    #variables unique for each run start here
    
    clock = core.MonotonicClock() # timing the track events
    myTrack = Track('radat/' + trackname + '.png', newLap)
    background.image = 'radat/' + trackname + '_bg.png'
    myCar = Car(win, track = myTrack, keys=keys, acceleration = 0.2, max_velocity = 20, turn_strength = 0.07, friction = 0.02)
    pressed_keys = []
    
    begin = False
    
    while clock.getTime() < 97:
        #if timer.getTime() >= 1: # heartbeat
        #    send_event(1)
        #    timer.add(1)
        if clock.getTime() <= 4:
            textboxbg.setAutoDraw(True)
            textbox.setAutoDraw(True)
            textbox.text = 'Koe Alkaa'
        elif clock.getTime() < 5:
            textbox.text = '3'
        elif clock.getTime() < 6:
            textbox.text = '2'
        elif clock.getTime() < 7:
            textbox.text = '1'
        elif not begin:
            textbox.text = 'AJAKAA!'
            laptimer.reset()
            begin = True
        
        if response_box:
            new_keys = [k for k in pressed_keys]
            for i, dev in enumerate(devices):
                dev.poll_for_response()
                if dev.response_queue_size() > 0:
                    res = dev.get_next_response()
                    key = i * 10 + res['key']
                    if res['pressed']:
                        new_keys.append(key)
                    else:
                        new_keys = [k for k in new_keys if k != key]
        else:
            new_keys = keyboard.state
        
        for k in myCar.keys:
            key = myCar.keys[k]
            if not key in pressed_keys and key in new_keys: # press up
                logging.data(k + ' down')
                if k is 'forward':
                    myCar.stimulus.image = 'car_1.png'
            elif key in pressed_keys and not key in new_keys: # press down
                logging.data(k + ' up')
                if k is 'forward':
                    myCar.stimulus.image = 'car_2.png'
        
        pressed_keys = [k for k in new_keys]
        
        res = 0
        
        if begin:
            res = myCar.update(pressed_keys)
            
            if laptimer.getTime() > 2:
                clearTextBox()
        if 'q' in keyboard.state:
            break
        
        win.flip()
        
        # sending trigger here for consistent timing
        if res:
            send_event(res)
        logging.flush()
        
    myCar.stimulus.setAutoDraw(False)
    clearTextBox()
    
    win.recordFrameIntervals = False


def show_fixation(seconds):
    background.image = 'empty.png'
    # fixation cross
    fixation = visual.ShapeStim(win, 
        vertices=((0, -50), (0, 50), (0,0), (-50,0), (50, 0)),
        lineWidth=5,
        closeShape=False,
        lineColor="white"
    )
    fixation.setAutoDraw(True)
    win.flip()
    fixation.setAutoDraw(False)
    core.wait(seconds)
    

def setDriver(d):
    global keys
    if response_box:
        if d == 0:
            keys = {
                    'left': 2,
                    'right': 3,
                    'forward': 4,
                    'backward': 5
                }
        elif d == 1:
            keys = {
                    'left': 2,
                    'right': 3,
                    'forward': 12,
                    'backward': 13
                }
        elif d == 2:
            keys = {
                    'left': 12,
                    'right': 13,
                    'forward': 2,
                    'backward': 3
                }
    else:
        if d == 0:
            keys = {
                    'left': 'a',
                    'right': 'd',
                    'forward': 'w',
                    'backward': 's'
                }
        elif d == 1:
            keys = {
                    'left': 'k',
                    'right': 'o',
                    'forward': 'u',
                    'backward': 'h'
                }
        elif d == 2:
            keys = {
                    'left': 'h',
                    'right': 'u',
                    'forward': 'o',
                    'backward': 'k'
                }

