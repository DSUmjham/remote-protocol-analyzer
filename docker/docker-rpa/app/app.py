from flask import Flask, render_template, redirect, url_for, request, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError, OperationalError
import cv2, os, serial, time

# initialize extensions globally
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "account"

# allowed file extensions for file uploads
ALLOWED_EXTENSIONS = {'py', 'json'}

# define the user model for authentication
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), unique=True, nullable=False)
	password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# helper function to validate file extensions
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# application factory
def create_app():
	app = Flask(__name__)
	
	# app configuration for the db
	app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
	app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

	# file upload configurations
	app.config['UPLOAD_FOLDER'] = 'uploads'
	app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
	os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

	# initialize extensions
	db.init_app(app)
	login_manager.init_app(app)
	
	# initialize Arduino and Camera
	try:
		# arduino = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.1)
		arduino = serial.Serial()
	except Exception as e:
		arduino = None
		print(f"Error initializing Arduino: {e}")
	
	try:
		camera = cv2.VideoCapture(0) if os.environ.get("WERKZEUG_RUN_MAIN") else None
	except Exception as e:
		camera = None
		print(f"Error initializing camera: {e}")

	# register routes
	register_routes(app, camera, arduino)

	# teardown resources to release the camera and arduino when finished
	@app.teardown_appcontext
	def cleanup(exception=None):
		if camera:
			camera.release()
		if arduino and arduino.is_open:
			arduino.close()
			
	return app

# define routes
def register_routes(app, camera, arduino):
	@app.route("/")
	@login_required
	def index():
		return render_template("index.html", username=current_user.username)

	@app.route("/account", methods=["GET", "POST"])
	def account():
		if request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			action = request.form["action"]
			
			if action == "login":
				user = User.query.filter_by(username=username).first()
				if user and check_password_hash(user.password, password):
					login_user(user)
					return redirect(url_for("index"))
				else:
					flash("Login failed. Check your username and password.", "error")
			
			elif action == "signup":
				if User.query.filter_by(username=username).first():
					flash("Username already exists. Please choose a different one.", "error")
				else:
					hashed_password = generate_password_hash(password, method="pbkdf2:sha256:600000")
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

	@app.route("/video")
	def video():
		def generate_frames():
			while True:
				success, frame = camera.read()
				if not success:
					break
				else:
					ret, buffer = cv2.imencode(".jpg", frame)
					frame = buffer.tobytes()
				yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
		
		return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

	@app.route("/reset")
	def reset():
		if arduino and arduino.is_open:
			arduino.write(bytes("2", "utf-8"))
			time.sleep(0.05)
		return Response("", 204)

	@app.route("/transmit")
	def transmit():
		if arduino and arduino.is_open:
			arduino.write(bytes("1", "utf-8"))
			time.sleep(0.05)
		return Response("", 204)

	@app.route("/upload", methods=["GET", "POST"])
	def upload_file():
		if request.method == "POST":
			# Check if the file is in the request
			if 'file' not in request.files:
				flash('No file part', 'error')
				return redirect(request.url)

			file = request.files['file']

			# Check if a file was uploaded
			if file.filename == '':
				flash('No selected file', 'error')
				return redirect(request.url)

			# Validate file type
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				flash(f'File {filename} uploaded successfully!', 'success')
				return redirect(url_for("upload_file"))
			else:
				flash('Invalid file type. Only .py and .json are allowed.', 'error')
				return redirect(request.url)

		return render_template("upload.html")

# run the application
if __name__ == "__main__":
	app = create_app()
	app.run(host="0.0.0.0", port=5001, debug=True)