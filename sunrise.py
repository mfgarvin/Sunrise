#Todo:
import subprocess
import threading
import time as timelib
import web
from web import form
import RPi.GPIO as GPIO
#Setting up the Pi...
bLed = 17
gLed = 22
rLed = 21
red = 0
green = 0 
blue = 0 #Placeholders for Global interaction
redvalue = 0
greenvalue = 0
bluevalue = 0
reset = 0
nosched = True
#Web
render = web.template.render('templates/')
urls = ('/', 'index')
app = web.application(urls, globals())

#Button Press Config
SHORT_PRESS = 300 #milliseconds
LONG_PRESS = 1500 
#Software GPIO for Button Inputs
print(GPIO.VERSION)
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)

myform = form.Form(
    form.Radio(name='Style', args=['Increase', 'Decrease'],value='Increase'),
    form.Radio(name='Brightness', args=['Low', 'Medium', 'High'],value='Medium'),
    form.Dropdown(name='Hour', args=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],value='6'),
    form.Dropdown(name='Minute', args=['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'], value='30'),
    form.Radio(name='AM/PM', args=['AM', 'PM'],value='AM'),
    form.Checkbox('Now', id='Now', value='True'),
    form.Textbox("Length",
        form.notnull,
        form.regexp('\d+', 'Need a numerical length here...')))

print("Welcome to the prototype sunrise alarm clock. Follow the online prompts to decide on a color, fade in time, blink rate, etc")
def button():
    global running
    global reset
    global red
    global green
    global blue
    override = 0
    presstime = 0
    while True:
	try:
	    timelib.sleep(0.05)
	    GPIO.wait_for_edge(24, GPIO.FALLING)
#	    print("Button Pressed")
	    presstime = timelib.time()
	    timelib.sleep(0.05)
	    GPIO.wait_for_edge(24, GPIO.RISING)
#	    print("Button Released")
	    releasetime = timelib.time()
	    presstime = releasetime - presstime
	    print(presstime)
	except RuntimeError:
	    print ("There's been an error")
	if .1 <= presstime <= 2:
	    print("Short Press")
	    if red > 0 or green > 0 or blue > 0 or override == 1:
		global reset
		running = 0
		reset = 1
		red = 0
		green = 0
		blue = 0
		timelib.sleep(0.1)
		led(0,0,0)
		override = 0	
		#RESET LED values and turn off
		print ("Stop 1")
	    else:
		running = 0
		reset = 1
		override = 1
		led(1,0.63137255,0.09803922) #Turn on preset color
	elif 2 < presstime:
	    print("Long Press")
	timelib.sleep(0.05)

def led(red,green,blue):
	subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (rLed,red), shell=True)
	subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (gLed,green), shell=True)
	subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (bLed,blue), shell=True)

def fade(ired,igreen,iblue,time,direction):
    try:
	global red
	global green
	global blue
	global reset
	red = float(ired)/100
    	green = float(igreen)/100
        blue = float(iblue)/100
        redorig = red
        blueorig = blue
        greenorig = green
        print(red,green,blue)
        if direction == 1:
            red = 0
            green = 0
            blue = 0
	    led(red,green,blue)
        else:
	    led(red,green,blue)
        def redfade():        
	    while led_event.is_set():
	        try:
	            global red
	            if direction == 1:
	                if redorig != 0:
			    red = red + 0.0005
	                else:
			    red = 0
			if red >= redorig:
			    break
			if time == 0:
			    red = redorig
		    else:
	                if redorig != 0:
			    red = red - 0.0005
			else:
			    red = 0
		        if red < 0:
			    red  = 0
			    subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (rLed,red), shell=True)
			    break
		    subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (rLed, red), shell=True)
	            if time != 0:
			rsleep = float(((time*60/1000)/(redorig)))
		    	timelib.sleep(rsleep)
		        print ("r",red,rsleep)
		    else:
			print ("r",red,"ON")
			break
	        except:
	            break
        def greenfade():
	    while led_event.is_set():
	        try:
	            global green
	            if direction == 1:
	                if greenorig != 0:
		            green = green + 0.0005
	                else:
			     green = 0
			if green >= greenorig:
			    break
			if time == 0:
			    green = greenorig
		    else:
			if greenorig != 0:
			    green = green - 0.0005
			else:
			    green = 0
			if green < 0:
			    green = 0
			    subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (gLed,green), shell=True)
			    break
		    subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (gLed,green), shell=True)
	            if time != 0:
			gsleep=float(((time*60/1000)/(greenorig)))
	            	timelib.sleep(gsleep)
		    	print ("g",green,gsleep)
	            else:
			print ("g",green,"ON")
			break
		except:
	            break
        def bluefade():
	    while led_event.is_set():
	        try:
	            global blue
	            if direction == 1:
		        if blueorig != 0:
	                    blue = blue + 0.0005
		        else:
			    blue = 0
			if blue >= blueorig:
			    break
			if time == 0:
			    blue = blueorig
	            else:
			if blueorig != 0:
	                    blue = blue - 0.0005
			else:
			    blue = 0
			if blue < 0:
			    blue = 0
			    subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (bLed,blue), shell=True)
			    break
		    subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (bLed,blue), shell=True)
	            if time != 0:
			bsleep=float(((time*60/1000)/(blueorig)))
	            	timelib.sleep(bsleep)
		    	print ("b",blue,bsleep)
	            else:
			print ("b",blue,"ON")
			break
		except:
	            break
	def watch():
	    global reset
	    while led_event.is_set(): 
		if reset == 1:
		    led_event.clear()
		    print("Stop 2")
		    break		
		elif redthread.is_alive() or bluethread.is_alive() or greenthread.is_alive():
		    timelib.sleep(0.25)
		    print(reset)
		else:
		    led_event.clear()
		    print("LED activity has finished, waiting for fade() to be called again.")
		    break
    	led_event = threading.Event()
        led_event.set()
        redthread = threading.Thread(target=redfade)
        greenthread = threading.Thread(target=greenfade)
        bluethread = threading.Thread(target=bluefade)
	watchthread = threading.Thread(target=watch)
	redthread.start()
        greenthread.start()
        bluethread.start() 
	watchthread.start()
	while True: #Used to catch ^C
	    timelib.sleep(0.5)
            if not led_event.is_set():
                break
    except KeyboardInterrupt:
	print "Stopping"
	led_event.clear()
	redthread.join()
	greenthread.join()
	bluethread.join()
	watchthread.join()
def startfade(red,green,blue,time,direction,hour,minute,s):
    global reset
    global running
    global nosched
    running = 1
    reset = 1
    led(0,0,0)
    timelib.sleep(0.1)
    led(0,0.1,0)
    timelib.sleep(0.1)
    led(0,0,0)
    timelib.sleep(0.1)
    led(0,0.1,0)
    timelib.sleep(0.1)
    led(0,0,0)
    timelib.sleep(0.5)
    reset = 0
    if str(s) == 'PM':
	if hour == 12:
	    pass
	else:
	    hour = hour + 12
    if str(s) == 'AM' and hour == 12:
	hour = 0
    while running == 1:
	try:
            now = timelib.localtime()
	    if hour == now.tm_hour and minute == now.tm_min or nosched == 'True':
	        fade(red,green,blue,time,direction)
	        return
            else:
		print ("Sleeping")
	        timelib.sleep(1)
        except KeyboardInterrupt:
	    print ("Stopping")
	    break	
class index:
    global nosched
    def GET(self):
        form = myform()
        return render.formtest(form)
    def POST(self):
	global redvalue
	global greenvalue
	global bluevalue
	global running
	global nosched
	def hex_to_rgb(value):
	    global redvalue
	    global greenvalue
	    global bluevalue
	    lv = len(value)
	    color = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
	    redvalue = (100*float(color[0]))/255
	    greenvalue = (100*float(color[1]))/255
	    bluevalue = (100*float(color[2]))/255
        form = myform()
        if not form.validates():
            return render.formtest(form)
        else:
	    color = web.input().newcolor
	    time = form.d.Length
	    hour = form.d.Hour
	    minute = form.d.Minute
	    try:
		nosched = str(web.input().Now)
	    except AttributeError:
		nosched = False
	    s = form['AM/PM'].value
	    if form.d.Style == 'Increase':
		style = 1
	    else:
		style = 0	    
	    hex_to_rgb(color)
	    if form.d.Brightness == 'Low':
		redvalue = float(redvalue) * 0.33
		greenvalue = float(greenvalue) * 0.33
		bluevalue = float(bluevalue) * 0.33
	    elif form.d.Brightness == 'Medium':
		redvalue = float(redvalue) * 0.66
		greenvalue = float(greenvalue) * 0.66
		bluevalue = float(bluevalue) * 0.66
	    elif form.d.Brightness == 'High':
		#Do Nothing
		pass
	    ledthread=threading.Thread(target=startfade, args=(float(redvalue),float(greenvalue),float(bluevalue),float(time),style,int(hour),int(minute),str(s)))
	    while ledthread.isAlive():
		running = 0
		time.sleep(0.5)
	    if not ledthread.isAlive():
		ledthread.start()
            return "Done. Color: %s, %f, %f, %f. Time: %d Style: %d Schedule: %d:%d %s Now? %s " % (str(color), float(redvalue), float(greenvalue), float(bluevalue), int(time), int(style), int(hour), int(minute), str(s), nosched)
if __name__=="__main__":
    web.internalerror = web.debugerror
    buttonwatch = threading.Thread(target=button)
    buttonwatch.start()
    app.run()
