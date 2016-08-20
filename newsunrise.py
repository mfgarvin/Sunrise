''' To do:
=Only allow one fade to happen at a time (check to see if the fade process is alive)
Fade between colors instead of hard jumping between them
=Fade off (Have to store the color used, fade down from those values)
=Set fadeall() as a process, not a thread
=I need to write 0 values to fifo. 
'''

import sys
import wiringpi as wpi
import time
import serial
import subprocess
import multiprocessing
import os

redPin = 21 #21 on the BCM GPIO Pinout, though wiringpi makes its own numbering scheme up.
greenPin = 22 #22
bluePin = 17 #17
serialPort = '/dev/ttyACM0'
btaddress = "F4:F1:E1:40:7E:04"
btname = "XT1049"
fadedelay = 60 #seconds
fadesleep = 0
#My maximum delay resoloution (so refresh rate) is 100 microseconds, so 100 hertz. Don't exceed that here!
# I need to set up my LED pins as softPWM pins, so do that config here.
#wpi.wiringPiSetupGpio()
#wpi.softPwmCreate(redPin,0,100)
#wpi.softPwmCreate(greenPin,0,100)
#wpi.softPwmCreate(bluePin,0,100)
#wpi.softPwmWrite(0,100)
# Setup Serial
ser = serial.Serial(serialPort, timeout=None)
print ("Serial port opened on" + ser.name)

# Color / LED Control Dictionary
colordict = [
	[0, 0, 0, 0, "down"],
	[0, 0, 0, "delay", "down"],
	[100, 100, 100, float(1), "up"],
	[100, 58, 16, float(1), "up"],
	[0, 0, 50, float(1), "up"],
	[0, 58, 16, float(1), "up"],
	[100, 0, 16, float(1), "down"],
]
lastFade = [0, 0, 0, 0, 0]
# This works for codes 0 - 4. 5-9, as well as 1, are filtered out.

# Create something to control the direction of the fade
#fadedir = "up"
#Temporary test variables. 
#redvalue = 94
#greenvalue = 45
#bluevalue = 76
#timetofade = float(5)

#Defining my LED code

def ledUpdate(pin,value):
	fifo = open("/dev/pi-blaster","w")
	fifo.write(`pin`+"="+`value`+"\n")
	fifo.close()

def redfade(value,fade,dir):
	if dir == "up":
		for x in range(value):
			ledUpdate(redPin,float(x)/100)
#			print(float(x)/value)
			delay = float(fade/value)
#			if delay <= 0:
#				delay = 0
			time.sleep(delay)
		if value == 0:
			ledUpdate(redPin,0)
	if dir == "down":
		for x in range(lastFade[0],-1,-1):
			ledUpdate(redPin,float(x)/100)
			time.sleep(float(fade/lastFade[0]))
def greenfade(value,fade,dir):
	if dir == "up":
		for x in range(value):
			ledUpdate(greenPin,float(x)/100)
			time.sleep(float(fade/value))
		if value == 0:
			ledUpdate(greenPin,0)
	if dir == "down":
		for x in range(lastFade[1],-1,-1):
			ledUpdate(greenPin,float(x)/100)
			time.sleep(float(fade/lastFade[1]))
def bluefade(value,fade,dir):
	if dir == "up":
		for x in range(value):
			ledUpdate(bluePin,float(x)/100)
			time.sleep(float(fade/value))
		if value == 0:
			ledUpdate(bluePin,0)
	if dir == "down":
		for x in range(lastFade[2],-1,-1):
			ledUpdate(bluePin,float(x)/100)
			time.sleep(float(fade/lastFade[2]))

def serialWatch():		#Watch for serial input. This will run continuously via loop.
	try:
		oldN = 0
		while fin.is_set() == False:
			n = ser.read(3).strip()
			print (oldN, "old")
			print (n, "Just came in")
			n = int(n)
			if n == 0 or n == 1 or n == 2 or n == 3 or n == 4:
				if n == oldN:
					print("It stayed the same")
					pass
				if n != oldN:
					oldN = n
					print("Something Changed!")
					if fadesleep == 1: #If we're waiting for a delay
						if n == 0 or n == 2 or n == 3 or n == 4: # And if we get a signal that requires an interuption of that delay
							fadepc.terminate() #Then terminate the process (and start it again)
							fadepc = multiprocessing.Process(target = fadeall, args=(colordict[int(n)][0], colordict[int(n)][1], colordict[int(n)][2], colordict[int(n)][3], colordict[int(n)][4])
							fadepc.start()
							if colordict[int(n)][4] == "up":
								for x in range(5):
									lastFade[x] = colordict[int(n)][x]

						else:
							pass
					else:
						fadepc = multiprocessing.Process(target = fadeall, args=(colordict[int(n)][0], colordict[int(n)][1], colordict[int(n)][2], colordict[int(n)][3], colordict[int(n)][4])
						fadepc.start()
						if colordict[int(n)][4] == "up":
							for x in range(5):
								lastFade[x] = colordict[int(n)][x]
	except IndexError:
		print ("There's been an Index Error. Check your code")
		pass
	except ValueError:
		print ("Received malformed serial data. Try again")
		pass

def bluetoothWatch():		#This is run every loop, delayed for 5 seconds artificially within the function
	while fin.is_set() == False:
		command = subprocess.check_output("hcitool name '%s'" % (btaddress), shell=True)
		print command
		if command.strip() == btname:
			ser.write(command)
		#	print(command)
		if command.strip() != btname:
			ser.write("Disconn." + '\n')
		#	print("Disconn.")
		time.sleep(5)
	
#Initialize Processes
bt = multiprocessing.Process(target = bluetoothWatch)
io = multiprocessing.Process(target = serialWatch)
#LED Process Initializers are set in fadeall(), as they need arguments that only that function distributes.
fin = multiprocessing.Event()
def fadeall(r,g,b,t,d):
	print("fadeall started")
	print(r,g,b,t,d)
	if t == 1:
		fadesleep = 1
		time.sleep(fadedelay)
		fadesleep = 0
	print ("T set")
	rled = multiprocessing.Process(target = redfade, args=(r,t,d))
	gled = multiprocessing.Process(target = greenfade, args=(g,t,d))
	bled = multiprocessing.Process(target = bluefade, args=(b,t,d))
	print ("Init")
	if rled.is_alive() or gled.is_alive() or bled.is_alive():
		print("Leds are changing already, so we're going to wait")
	else:
		rled.start()
		gled.start()
		bled.start()
		print ("Started")


if __name__=="__main__":	#So, only run these once
	try:
		bt.start()
		io.start()
		fin.wait()
	    #We're gonna watch the serial connection for data continuously
	    # while at the same time polling for BT connectivity. These might
	    # need to be in different threads?
	except KeyboardInterrupt:
		print("Caught Ctrl-C")
		fin.set()
		os.system("echo '%d'='%f' > /dev/pi-blaster" % (redPin,0))
		os.system("echo '%d'='%f' > /dev/pi-blaster" % (greenPin,0))
		os.system("echo '%d'='%f' > /dev/pi-blaster" % (bluePin,0))
		time.sleep(1)
		if bt.is_alive():
			print("Bluetooth didn't exit gracefully, forcing down now.")
			bt.terminate()
		if io.is_alive():
			print("Serial didn't exit gracefully, forcing down now.")
			io.terminate()
