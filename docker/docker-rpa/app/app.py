from flask import Flask,render_template,Response
from requests import get
import cv2, os, serial, time

app = Flask(__name__)
arduino = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.1)

# only open the camera once - this allows the app to run in debug mode
if os.environ.get('WERKZEUG_RUN_MAIN'):
	camera = cv2.VideoCapture(0) #/dev/video0

def generate_frames():
	# read the camera frames indefinitely (always stream)
	while True:
		success,frame = camera.read() # returns true if frames are grabbed from the camera

		if not success:
			break
		else:
			ret,buffer = cv2.imencode('.jpg', frame) # encode images as .jpeg and store in memory buffer
			frame=buffer.tobytes() # convert the image stream into raw bytes
		
		yield(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def send_arduino(num):
	arduino.write(bytes(num, 'utf-8'))
	time.sleep(0.05)

@app.route("/")
def index():
	ip_addr = get("https://api.ipify.org").content.decode("UTF-8")
	return render_template('index.html', ip=ip_addr)

@app.route('/video')
def video():
	print(generate_frames())
	return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reset')
def  reset():
	print("reset button clicked")
	send_arduino("2")
	return Response('', 204)

@app.route('/transmit')
def transmit():
	print("transmit buton clicked")
	send_arduino("1")
	return Response('', 204)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)