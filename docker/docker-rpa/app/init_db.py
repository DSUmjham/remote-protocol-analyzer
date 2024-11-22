from app import create_app, db
from app import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
	# Create tables
	db.create_all()

	# Seed admin user
	if not User.query.filter_by(username="admin").first():
		admin_user = User(
			username="admin",
			password=generate_password_hash("admin123", method="pbkdf2:sha256:600000"),
		)
		db.session.add(admin_user)
		db.session.commit()
		print("Admin user created with default credentials.")
	else:
		print("Admin user already exists.")