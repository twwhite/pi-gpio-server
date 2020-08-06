from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import datetime
import sys
import RPi.GPIO as GPIO
import threading

# Raspberry Pi GPIO Config
rPiOutputPin 	= 18
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(rPiOutputPin,GPIO.OUT)

serverIP	= "192.168.1.84" # Set to local IP of Pi
serverPort 	= 80		# Desired port, in my case HTTP
int_Sunrise 	= 8		# Integer hour beween 0-24
int_Sunset	= 20		# Integer hour beween 0-24
lightMode 	= "Auto" 	# ("Auto" | "On" | "Off")
lightStatus	= GPIO.input(rPiOutputPin) # Current status of GPIO pin.

def webServer(serverIP, serverPort):
	# Initiate a webserver in Thread-1 using MyServer simple HTTP handler
	webServer = HTTPServer((serverIP, serverPort), MyServer)
	try:
        	webServer.serve_forever()
	except KeyboardInterrupt:
		pass

	webServer.server_close()
	print("Server stopped.")

def autoLights():
	global lightMode, lightStatus, rPiOutputPin
	# Infinite loop Thread-2 checking global lightMode and lightStatus flags
	while(1):
		if(lightMode == "Auto"):
			now = datetime.datetime.now()
			testVar = now
			if (int_Sunrise < now.hour < int_Sunset):
				if(lightStatus == False):
					print("Status: Turning Lights ON")
					GPIO.output(18,GPIO.HIGH)
					lightStatus = False
			else:
				if(lightStatus == True):
					print("Status: Turning Lights OFF")
					GPIO.output(18,GPIO.LOW)
					lightStatus = False

		elif(lightMode == "On"):
			if(lightStatus == False):
				print("Status: Turning Lights ON")
				GPIO.output(18,GPIO.HIGH)
				lightStatus = True

		elif(lightMode == "Off"):
			if(lightStatus == On):
				print("Status: Turning Lights OFF")
				GPIO.output(18,GPIO.LOW)
				lightStatus = False

		time.sleep(5)
		print("Light Status:  "+ str(lightStatus) +" | Light Mode:  " + lightMode)


class MyServer(BaseHTTPRequestHandler):
	# GET request function
	def do_GET(self):
		global lightMode, lightStatus

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("<html><head><title>AutoLights</title></head>", "utf-8"))
		self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
		self.wfile.write(bytes("<body>", "utf-8"))

		# Case strucure for simple request handler. Toggle global LightMode
		if(self.path=="/on"):
			lightMode = "On"

		elif(self.path=="/off"):
			lightMode = "Off"

		elif(self.path=="/auto"):
			lightMode = "Auto"

		else:
			self.wfile.write(bytes("<p>Please go to /on, /off, or /auto to control the lights.</p>","utf-8"))

		print("Light Mode: "+lightMode)
		self.wfile.write(bytes("<p>Current status of lights:  "+str(lightStatus)+"</p>", "utf-8"))
		self.wfile.write(bytes("<p>Current status of automode:  "+str(lightMode)+"</p>", "utf-8"))
		self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":

	th_webserver = threading.Thread(target=webServer, args=(serverIP, serverPort,))
	print("Server started http://%s:%s" % (serverIP, serverPort))
	th_webserver.start()

	th_lights = threading.Thread(target=autoLights)
	print("Light monitor started")
	th_lights.start()
