#Todo:
#Make Incrimenting stop when value is reached
#Make sure this works in revese
#This isn't much, but this helps to define color codes for different colors!
import random
import subprocess
import threading
import time as timelib
import web
from web import form
#Setting up the Pi...
complete = 0
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
#Web
render = web.template.render('templates/')
urls = ('/', 'index')
app = web.application(urls, globals())

myform = form.Form(
    form.Radio(name='AM/PM', args=['AM', 'PM'],value='AM'),
    form.Radio(name='Style', args=['Increase', 'Decrease'],value='Increase'),
    form.Radio(name='Brightness', args=['Low', 'Medium', 'High'],value='Medium'),
    form.Dropdown(name='Hour', args=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],value='6'),
    form.Dropdown(name='Minute', args=['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'], value='30'),
    form.Textbox("Length",
        form.notnull,
        form.regexp('\d+', 'Need a numerical length here...')))
#    form.Textbox("Color",
#       form.notnull))

print("Welcome to the prototype sunrise alarm clock. Follow the prompts to decide on a color, fade in time, blink rate, etc")
#Todo: Multiple colors here. Maybe a menu type prompt? (1 leads to A, 2 leads to B, etc)
def led(red,green,blue):
	subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (rLed,red), shell=True)
	subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (gLed,green), shell=True)
	subprocess.call("echo '%d'='%f' > /dev/pi-blaster" % (bLed,blue), shell=True)

def fade(ired,igreen,iblue,time,direction):
    try:
#	print('Fade Started')
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
#	print("Fade 2")
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
		if redthread.is_alive() or bluethread.is_alive() or greenthread.is_alive():
		    timelib.sleep(0.25)
		else:
		    led_event.clear()
		    print("LED activity has finished, waiting for fade() to be called again.")
		    break
		if reset == 1:
		    led_event.clear()
		    break		
    	led_event = threading.Event()
        led_event.set()
#	print("Fade 3")
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
def prompt():
    try:
	global complete
        global redvalue
	global greenvalue
	global bluevalue
	global time
	global direction
	#if complete == 1:
	 #   break
        while True:
	    try:
	        redvalue = input("Red Value: 0 - 100:")
	        if 0 <= redvalue <= 100:
	            break
	        else:
	            print ("I can't compute that. Try again?")
            except (ValueError, NameError):
                print ("I can't compute that. Try again?")
	    except SyntaxError:
	        redvalue = random.randint(0,100)
		break
	while True:
	    try:
	        greenvalue = input("Green Value: 0 - 100:")
		if 0 <= greenvalue <= 100:
		    break
		else:
		    print("I can't compute that. Try again?")
	    except (ValueError, NameError):
		print("I can't compute that. Try again?")
	    except SyntaxError:
		greenvalue = random.randint(0,100)
		break
        while True:
	    try:
	        bluevalue = input("Blue Value: 1 - 100:")
	        if 0 <= bluevalue <= 100:
		    break
		else:
		    print("I can't compute that. Try again?")
	    except (ValueError, NameError):
		print("I can't compute that. Try again?")
	    except SyntaxError:
		bluevalue = random.randint(0,100)
		break
        while True:
	    try:
		time = input("Fade-in Time (In Minutes)")
		time = float(time)
		if 0 < time or time == 0:
		    break
		else:
		    print("I need an actual time...")
	    except (ValueError, NameError): 
		print("I don't speak alphabet.")
	    except (SyntaxError):
	        print("Please enter a time")
	while True:
	    try:
		direction = input("Direction (ON = 1, OFF = 0)")
		if direction == 0 or direction == 1:
		    break
		else:
		    print("Need a 0 or 1 here, buddy")
	    except:
		print("Need a 0 or 1 here, buddy")
        print
        print("Working...")
        print
        print("Great! Take a look at the LED and if you like what you see, jot down these color values:")
        print(redvalue, greenvalue, bluevalue)
    except KeyboardInterrupt:
        print	
        print("Goodbye!")

def startfade(red,green,blue,time,direction):
    global reset
    led(0,0,0)
    timelib.sleep(0.1)
    led(0,1,0)
    timelib.sleep(0.1)
    led(0,0,0)
    timelib.sleep(0.1)
    led(0,1,0)
    timelib.sleep(0.1)
    led(0,0,0)
    reset = 1
    timelib.sleep(0.5)
    reset = 0
    fade(red,green,blue,time,direction)


class index:
    def GET(self):
        form = myform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.formtest(form)
	print ("Page Opened")
    def POST(self):
	global redvalue
	global greenvalue
	global bluevalue
	def hex_to_rgb(value):
	    global redvalue
	    global greenvalue
	    global bluevalue
	    lv = len(value)
	    color = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
	    redvalue = (100*float(color[0]))/255
	    greenvalue = (100*float(color[1]))/255
	    bluevalue = (100*float(color[2]))/255
	    print("Colors Calculated")
        form = myform()
        if not form.validates():
            return render.formtest(form)
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
	    color = web.input().newcolor
	    time = form.d.Length
	    if form.d.Style == 'Increase':
		style = 1
	    else:
		style = 0	    
#	    style = form.d.Style
	    hex_to_rgb(color)
#	    print(color,redvalue,greenvalue,bluevalue,int(time),style)
	    if form.d.Brightness == 'Low':
		redvalue = float(redvalue) * 0.33
		greenvalue = float(greenvalue) * 0.33
		bluevalue = float(bluevalue) * 0.33
	    elif form.d.Brightness == 'Medium':
		redvalue = float(redvalue) * 0.66
		greenvalue = float(greenvalue) * 0.66
		bluevalue = float(bluevalue) * 0.66
	    elif form.d.Brightness == 'High':
		#Do Nothin
		pass
	    ledthread=threading.Thread(target=startfade, args=(float(redvalue),float(greenvalue),float(bluevalue),float(time),style))
            ledthread.start()
#	    fade(float(redvalue),float(greenvalue),float(bluevalue),float(time),style)	
            return "Done. Color: %s, %f, %f, %f. Time: %d Style: %d" % (str(color), float(redvalue), float(greenvalue), float(bluevalue), int(time), int(style))
if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
#prompt()
#fade(redvalue,greenvalue,bluevalue,time,direction)
