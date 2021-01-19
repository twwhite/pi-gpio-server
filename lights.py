from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import time
import datetime
import sys
import RPi.GPIO as GPIO
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

serverIP	= "0.0.0.0"
serverPort 	= 80
int_Sunrise 	= 8		# Integer hour beween 0-24
int_Sunset	= 21		# Integer hour beween 0-24
lightMode 	= "auto" 	# ("auto" | "on" | "off")
lightStatus	= GPIO.input(18)

logging.basicConfig(format='%(asctime)s: %(message)s; ', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/home/alarm/lights-webserver.log', level=logging.DEBUG)
logging.debug('Lights.py started...')


def webServer(serverIP, serverPort):
	webServer = HTTPServer((serverIP, serverPort), MyServer)
	logging.debug('Webserver thread initiated')
	try:
		webServer.serve_forever()

	except KeyboardInterrupt:
		logging.debug('Webserver keyboard interrupt.')
		pass

	webServer.server_close()
	logging.debug('Webserver and thread stopped.')
	print("Server stopped.")

def autoLights():
	global lightMode, lightStatus
	while(1):
		if(lightMode == "auto"):
			now = datetime.datetime.now()
			testVar = now
			if (int_Sunrise < now.hour < int_Sunset):
				if(lightStatus == False):
					print("Status: Turning Lights ON")
					GPIO.output(18,GPIO.HIGH)
					logging.debug('Lights on - Auto')
					lightStatus = True
			else:
				if(lightStatus == True):
					print("Status: Turning Lights OFF")
					GPIO.output(18,GPIO.LOW)
					logging.debug('Lights off - Auto')
					lightStatus = False

		if(lightMode == "on"):
			if(lightStatus == False):
				print("Status: Turning Lights ON")
				GPIO.output(18,GPIO.HIGH)
				logging.debug('Lights on - Manual')
				lightStatus = True

		if(lightMode == "off"):
			if(lightStatus == True):
				print("Status: Turning Lights OFF")
				GPIO.output(18,GPIO.LOW)
				logging.debug('Lights off - Manual')
				lightStatus = False

		time.sleep(5)
		print("Light Status:  "+ str(lightStatus) +" | Light Mode:  " + lightMode)


class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		global lightMode, lightStatus

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("<html><head><title>Bedroom Lights</title>", "utf-8"))
		self.wfile.write(bytes("</head>", "utf-8"))


		self.wfile.write(bytes("<body><h1>Bedroom Lights v2.0</h1>", "utf-8"))

		if(self.path=="/on"):
			lightMode = "on"
			logging.debug('Light mode set to Manual: On')

		elif(self.path=="/off"):
			lightMode = "off"
			logging.debug('Light mode set to Manual: Off')

		elif(self.path=="/toggle"):
			if(lightStatus):
				LightMode = "off"
			else:
				LightMode = "on"
			logging.debug('Light mode set to Manual: Toggle')

		elif(self.path=="/auto"):
			lightMode = "auto"
			logging.debug('Light mode set to Auto')

		else:
			self.wfile.write(bytes("<p>Please go to /on, /off, /toggle, or /auto to control the lights.</p>","utf-8"))

		print("Light Mode: "+lightMode)
		with open('/home/alarm/lights-webserver.log') as f: s = f.read()
		self.wfile.write(bytes('<div class="controls"><a class="lights-on" href="/on">Lights On</a><a class="lights-off" href="/off">Lights Off</a><a class="lights-auto" href="/auto">Auto Lights</a></div>', "utf-8"))
		self.wfile.write(bytes('<div class="info">'+"<p>Current time:  "+str(datetime.datetime.now())+"</p><h4>Debug Info</h4><p>"+ str(s.replace(";","<br>")) + "</p></div></body></html>", "utf-8"))
		self.wfile.write(bytes("<style>.controls {width: 100%;} h4 {text-align: left !important; padding-left: 1rem; margin-bottom: 0} h1 {padding-top: 0.5rem; font-size: 1.5rem; color: #333} .controls>a{display: inline-block; padding: 2rem; background-color: white; margin: 1rem; text-decoration: none; color: black; box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23); border-radius: 5px;}.controls>a:hover{background-color: #ecf0f2} .lights-"+str(lightMode)+"{background-color: #acf4ff !important;} .info{width:100%} .info>p:last-of-type{margin-top: 0.5rem; height: 150px; overflow-x: hidden; overflow-y: auto; text-align: left; background-color: #cecece; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)} body{display:flex; align-content:space-between; flex-wrap:wrap; justify-content: space-around; align-items: center; width: 100%; height: 100%; background-color: #dadadd; overflow:hidden;  font-family: Sans-Serif; text-align: center;}body>p:first-of-type{margin-top:16px;}body>p{display: block; border-radius:7px; padding: 1rem; background-color: white; box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);}</style>", "utf-8"))


if __name__ == "__main__":

	logging.debug('Threading Webserver and Light controls')
	th_webserver = threading.Thread(target=webServer, args=(serverIP, serverPort,))
	print("Server started http://%s:%s" % (serverIP, serverPort))
	logging.debug("Server started http://%s:%s" % (serverIP, serverPort))
	th_webserver.start()

	th_lights = threading.Thread(target=autoLights)
	print("Light monitor started")
	th_lights.start()
