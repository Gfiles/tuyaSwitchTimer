# import pygame module in this program
import pygame
import tinytuya
import json
import os
import sys
import time
import datetime

hasTuya = False

def readConfig():
    settingsFile = os.path.join(cwd, "appconfig.json")
    if os.path.isfile(settingsFile):
        with open(settingsFile) as json_file:
            data = json.load(json_file)
    else:
        data = {
                "description_devices" : ["dev_Name", "dev_id", "address",  "local_key"],
                "devices" : [
                    ["YDSw062", "eb08ef8fb69aaa787bvgv9", "Auto", "clnqKF2G':k&R6}L"],
                    ["YDSw010", "ebafa25ecda29bb830esad", "Auto", "WDz1P=g_)wMSKTP|"]
                ],
                "timeOn" : 1.5,
                "timeOff" : 7,
                "startTime" : "10:15",
                "stopTime" : "21:30",
                "dayWeekOn" : [0, 1, 1, 1, 1, 1, 1]
        }
        # Serializing json
        json_object = json.dumps(data, indent=4)
 
        # Writing to config.json
        with open(settingsFile, "w") as outfile:
            outfile.write(json_object)
    return data

def textDraw(textWrite, color):
    # create a text surface object,
    # on which text is drawn on it.
    text = font.render(textWrite, True, black)
    display_surface.fill(color)
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()

    # set the center of the rectangular object.
    textRect.center = (X // 2, Y // 2)
    
    display_surface.blit(text, textRect)
    # Draws the surface object to the screen.
    pygame.display.update()

#----------Functions----------

# Get the current working 
# directory (CWD)
try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
if getattr(sys, 'frozen', False):
    cwd = os.path.dirname(sys.executable)
else:
    cwd = os.path.dirname(this_file)
    
#print("Current working directory:", cwd)

# Read Config File
config = readConfig()
devices = config["devices"]
timeOn = config["timeOn"]*60
timeOff = config["timeOff"]*60
startTime = config["startTime"]
stopTime = config["stopTime"]
dayWeekOn = config["dayWeekOn"]

# Get Time Objets
currentDateAndTime = datetime.datetime.now()

oT = startTime.split(':')
onTime = datetime.datetime(currentDateAndTime.year, currentDateAndTime.month, currentDateAndTime.day, int(oT[0]), int(oT[1]))

sT = stopTime.split(':')
offTime = datetime.datetime(currentDateAndTime.year, currentDateAndTime.month, currentDateAndTime.day, int(sT[0]), int(sT[1]))

# activate the pygame library
# initiate pygame and give permission
# to use pygame's functionality.
pygame.init()

# define the RGB value for white,
# green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
red = (255, 0, 0)
black = (0, 0, 0)

# assigning values to X and Y variable
X = 600
Y = 600

# create the display surface object
# of specific dimension..e(X, Y).
display_surface = pygame.display.set_mode((X, Y))

# set the pygame window name
pygame.display.set_caption('Tomada das Bolhas')

# create a font object.
# 1st parameter is the font file
# which is present in pygame.
# 2nd parameter is size of the font
font = pygame.font.Font('freesansbold.ttf', 64)

textDraw("Conecting", green)
# infinite loop
deviceOnLine = False
lastSwitchState = False
timerOffTime = time.time()
timerDeviceOffline = 0
while True:
    if hasTuya:
        while not deviceOnLine:
            try:
                if time.time() - timerDeviceOffline > 60:
                    timerDeviceOffline = time.time()
                    print("Testing Conection")
                    switch = tinytuya.OutletDevice(dev_id=devices[0][1], address=devices[0][2],local_key=devices[0][3],version=3.3)
                    
                    #switchState = switch.status()['dps']['1']
                    #print(f"Switch state: {switchState}")

                    switch.turn_on()

                    timerOn = time.time()
                    #timerOff = 0
                    switchMode = True
                    lasttimePassed = 0
                    deviceOnLine = True
            except:
                deviceOnLine = False
                textDraw("Device Offline", red)
    else:
        if not deviceOnLine:
            deviceOnLine = True
            switchMode = True
            timerOn = time.time()
            lasttimePassed = 0
    # Get Time Objets
    currentDateAndTime = datetime.datetime.now()
    dayOfWeek = currentDateAndTime.weekday()
    switchInTime = onTime < currentDateAndTime < offTime
    
    #print(f"{onTime.strftime("%H:%M:%S")} < {currentDateAndTime.strftime("%H:%M:%S")} < {offTime.strftime("%H:%M:%S")}")
    if hasTuya:
        try:
            switchState = switch.status()['dps']['1']
            lastSwitchState = switchState
        except:
            switchState = lastSwitchState
    else:
        switchState = lastSwitchState
    #print(switchInTime)
    if switchInTime and dayWeekOn[dayOfWeek]:
        #print(f"Switch state: {switchState}")
        if switchMode:
            #print("Runnning")
            #print(f"{time.time()} - {timerOn} < {timeOn}")
            if (time.time() - timerOn < timeOn):
                timePassed = int(time.time() - timerOn)
                #print(timePassed)
                if timePassed != lasttimePassed:
                    #print(f"On - {timePassed} s")
                    textDraw(f"On - {timePassed} s", green)
                    lasttimePassed = timePassed
                if switchState == False:
                    print("Switch On")
                    lastSwitchState = True
                    if hasTuya:
                        switch.turn_on()
                    switchMode = True
            else:
                switchMode = False
                timerOff = time.time()
        else:
            if (time.time() - timerOff < timeOff):
                timePassed = int(time.time() - timerOff)
                if timePassed != lasttimePassed:
                    #print(f"Off - {timePassed} s")
                    textDraw(f"Off - {timePassed} s", red)
                    lasttimePassed = timePassed
                if switchState:
                    print("Switch Off")
                    lastSwitchState = False
                    if hasTuya:
                        switch.turn_off()
                    switchMode = False
            else:
                switchMode = True
                timerOn = time.time()
    else:
        textDraw(f"Off Time", red)
        if (time.time() - timerOffTime > 60):
            timerOffTime = time.time()
            if switchState:
                print("Switch Off")
                lastSwitchState = False
                if hasTuya:
                    switch.turn_off()
                
	
	# copying the text surface object
	# to the display surface object
	# at the center coordinate.

	# iterate over the list of Event objects
	# that was returned by pygame.event.get() method.
    for event in pygame.event.get():

		# if event object type is QUIT
		# then quitting the pygame
		# and program both.
        if event.type == pygame.QUIT:

			# deactivates the pygame library
            pygame.quit()

			# quit the program.
            quit()
