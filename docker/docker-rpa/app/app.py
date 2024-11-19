from flask import Flask, render_template, redirect, url_for, request, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import cv2, os, serial, time

app = Flask(__name__)

# initialize database for authentication
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "account"

# define the user model for authentication
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), unique=True, nullable=False)
	password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# arduino = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.1)
arduino = serial.Serial()

# only open the camera once - this allows the app to run in debug mode
if os.environ.get("WERKZEUG_RUN_MAIN"):
	camera = cv2.VideoCapture(0) #/dev/video0

def generate_frames():
	# read the camera frames indefinitely (always stream)
	while True:
		success,frame = camera.read() # returns true if frames are grabbed from the camera

		if not success:
			break
		else:
			ret,buffer = cv2.imencode(".jpg", frame) # encode images as .jpeg and store in memory buffer
			frame=buffer.tobytes() # convert the image stream into raw bytes
		
		yield(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

def send_arduino(num):
	arduino.write(bytes(num, "utf-8"))
	time.sleep(0.05)

@app.route("/")
@login_required
def index():
	return render_template("index.html", username=current_user.username)

# miscellaneous functionality routes
@app.route("/video")
def video():
	print(generate_frames())
	return Response(generate_frames(),mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/reset")
def reset():
	print("reset button clicked")
	send_arduino("2")
	return Response("", 204)

@app.route("/transmit")
def transmit():
	print("transmit buton clicked")
	send_arduino("1")
	return Response("", 204)

# routes pertinent to account maintenance
@app.route("/account", methods=["GET", "POST"])
def account():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		action = request.form["action"]  # determine which button was clicked
		
		if action == "login":
			user = User.query.filter_by(username=username).first()
			if user and check_password_hash(user.password, password):
				login_user(user)
				return redirect(url_for("index"))
			else:
				flash("Login failed. Check your username and password.", "error")
		
		elif action == "signup":
			existing_user = User.query.filter_by(username=username).first()
			if existing_user:
				flash("Username already exists. Please choose a different one.", "error")
			else:
				hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
				new_user = User(username=username, password=hashed_password)
				db.session.add(new_user)
				db.session.commit()
				flash("Account created successfully!", "success")
				return redirect(url_for("account"))
	
	return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash("You have been logged out.", "success")
	return redirect(url_for("account"))

if __name__ == "__main__":
	app.run(host="0.0.0.0", port="5001", debug=True)
