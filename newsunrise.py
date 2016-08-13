import wiringpi as wpi
import time
import serial
import threading
import subprocess

redPin = 2 #21 on the BCM GPIO Pinout, though wiringpi makes its own numbering scheme up.
greenPin = 3 #22
bluePin = 0 #17
serialPort = '/dev/ttyACM0'
btaddress = "F4:F1:E1:40:7E:04"
btname = "XT1049"

#My maximum delay resoloution (so refresh rate) is 100 microseconds, so 100 hertz. Don't exceed that here!
# I need to set up my LED pins as softPWM pins, so do that config here.
wpi.wiringPiSetup()
wpi.softPwmCreate(redPin,0,100)
wpi.softPwmCreate(greenPin,0,100)
wpi.softPwmCreate(bluePin,0,100)

# Setup Serial
ser = serial.Serial(serialPort, timeout=None)
print ("Serial port opened on" + ser.name)

# Create something to control the direction of the fade
fadedir = "up"
#Temporary test variables. 
redvalue = 94
greenvalue = 45
bluevalue = 76
timetofade = float(5)


def main():
	def fadeall(r,g,b,t,d):
		def redfade(value,fade,dir):
			if dir == "up":
				for x in xrange(value):
					if primedEvent.is_set():
		    				wpi.softPwmWrite(redPin,x)
			    			print(float(fade/value),x)
    						time.sleep(float(fade/value))
			if dir == "down":
				for x in reversed(value):
					if primedEvent.is_set():
						wpi.softPwmWrite(redPin,x)
						print(float(fade/value),x)
						time.sleep(fade/value)
		def greenfade(value,fade,dir):
			if dir == "up":
				for x in xrange(value):
					if primedEvent.is_set():
						wpi.softPwmWrite(greenPin,x)
						print(float(fade/value),x)
						time.sleep(fade/value)
			if dir == "down":
				for x in reversed(value):
					if primedEvent.is_set():
						wpi.softPwmWrite(greenPin,x)
						time.sleep(fade/value)
		def bluefade(value,fade,dir):
			if dir == "up":
				for x in xrange(value):
					if primedEvent.is_set():
						wpi.softPwmWrite(bluePin,x)
						print(float(fade/value),x)
						time.sleep(fade/value)
			if dir == "down":
				for x in reversed(value):
					if primedEvent.is_set():
						wpi.softPwmWrite(bluePin,x)
						time.sleep(fade/value)
		redthread = threading.Thread(target=redfade, args=(r,t,d))
		greenthread = threading.Thread(target=greenfade, args=(g,t,d))
		bluethread = threading.Thread(target=bluefade, args=(b,t,d))
		redthread.start()
		greenthread.start()
		bluethread.start()
	def serialWatch():		#Watch for serial input. This will run continuously via loop.
		while primedEnding.is_set():
			n = ser.read()
			print n	#Really compare this number, and run fadeall with certain arguments based on the number

	def bluetoothWatch():		#This is run every loop, delayed for 5 seconds artificially within the function
		while primedEnding.is_set():
			command = subprocess.check_output("hcitool name '%s'" % (btaddress), shell=True)
			print command
			if command.strip() == btname:
				ser.write(command)
			#	print(command)
			if command.strip() != btname:
				ser.write("Disconn." + '\n')
			#	print("Disconn.")
			time.sleep(5)
	
	primedEnding = threading.Event()
	primedEnding.set()
	serialthread = threading.Thread(target=serialWatch)
	bluetooththread = threading.Thread(target=bluetoothWatch)
	serialthread.start()
	bluetooththread.start()
	while True:
		try:
			time.sleep(0.5) #waste time
		except KeyboardInterrupt:
			primedEnding.clear()
			serialthread.join()
			bluetooththread.join()


#Sets a value for 
#fadeall(35,54,86,timetofade,"up")


if __name__=="__main__":	#So, only run these once
	    #We're gonna watch the serial connection for data continuously
	    # while at the same time polling for BT connectivity. These might
	    # need to be in different threads?
	main()

