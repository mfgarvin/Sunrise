import sys
import wiringpi as wpi
import time
import serial
import subprocess
import multiprocessing

redPin = 2 #21 on the BCM GPIO Pinout, though wiringpi makes its own numbering scheme up.
greenPin = 3 #22
bluePin = 0 #17
serialPort = '/dev/ttyACM0'
btaddress = "F4:F1:E1:40:7E:04"
btname = "XT1049"
fadedelay = 60 #seconds
#My maximum delay resoloution (so refresh rate) is 100 microseconds, so 100 hertz. Don't exceed that here!
# I need to set up my LED pins as softPWM pins, so do that config here.
wpi.wiringPiSetup()
wpi.softPwmCreate(redPin,0,100)
wpi.softPwmCreate(greenPin,0,100)
wpi.softPwmCreate(bluePin,0,100)

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
	[100, 58, 16, float(1), "up"],
	[100, 58, 16, float(1), "down"],
]

# This works for codes 0 - 4. 5-9, as well as 1, are filtered out.

# Create something to control the direction of the fade
#fadedir = "up"
#Temporary test variables. 
#redvalue = 94
#greenvalue = 45
#bluevalue = 76
#timetofade = float(5)

#Defining my LED code
def redfade(value,fade,dir):
	if dir == "up":
		for x in xrange(value):
			wpi.softPwmWrite(redPin,x)
			print(float(fade/value),x)
			time.sleep(float(fade/value))
	if dir == "down":
		for x in reversed(value):
			wpi.softPwmWrite(redPin,x)
			print(float(fade/value),x)
			time.sleep(fade/value)
def greenfade(value,fade,dir):
	if dir == "up":
		for x in xrange(value):
			wpi.softPwmWrite(greenPin,x)
			print(float(fade/value),x)
			time.sleep(fade/value)
	if dir == "down":
		for x in reversed(value):
			wpi.softPwmWrite(greenPin,x)
			time.sleep(fade/value)
def bluefade(value,fade,dir):
	if dir == "up":
		for x in xrange(value):
			wpi.softPwmWrite(bluePin,x)
			print(float(fade/value),x)
			time.sleep(fade/value)
	if dir == "down":
		for x in reversed(value):
			wpi.softPwmWrite(bluePin,x)
			time.sleep(fade/value)

def serialWatch():		#Watch for serial input. This will run continuously via loop.
	try:
		oldN = 0
		while fin.is_set() == False:
			n = ser.read(3).strip()
			print (oldN, "old")
			print (n, "Just came in")
			if n == oldN:
				print("It stayed the same")
				pass
			if n != oldN:
				oldN = n
				print("Something Changed!")
				fadeall(colordict[int(n)][0], colordict[int(n)][1], colordict[int(n)][2], colordict[int(n)][3], colordict[int(n)][4])
				print ("Fadeall was called")
				#run my led code. Simply launch fade all, which will then spread into processes
	except IndexError:
		print ("There's been an Index Error. Check your code")
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
#	if t == 1:
#		time.sleep(fadedelay)
	print ("T set")
	rled = multiprocessing.Process(target = redfade, args=(r,float(t),d))
	gled = multiprocessing.Process(target = greenfade, args=(g,float(t),d))
	bled = multiprocessing.Process(target = bluefade, args=(b,float(t),d))
	print ("Init")
	rled.start()
	gled.start()
	bled.start()
	print ("Started")


#Sets a value for 
#fadeall(35,54,86,timetofade,"up")

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
		time.sleep(1)
		if bt.is_alive():
			print("Bluetooth didn't exit gracefully, forcing down now.")
			bt.terminate()
		if io.is_alive():
			print("Serial didn't exit gracefully, forcing down now.")
			io.terminate()
