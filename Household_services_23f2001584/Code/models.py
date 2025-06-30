from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
class Admin(db.Model):
    __tablename__ = 'admins'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    admin_id = db.Column(db.Integer, unique=True, nullable=False)
    user = db.relationship('User', backref=db.backref('admin', uselist=False))

# Model for Customer
class Customer(db.Model):
    __tablename__ = 'customers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    customer_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    user = db.relationship('User', backref=db.backref('customer', uselist=False))

# Model for Professional
class Professional(db.Model):
    __tablename__ = 'professionals'
    professional_id = db.Column(db.Integer, primary_key=True)
    approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('professional', uselist=False))
    service_requests = db.relationship('ServiceRequest', back_populates='professional', lazy=True)
# Model for Service
class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

# Model for Service Request
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    servicerequest_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.professional_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    service = db.relationship('Service', backref=db.backref('service_requests', lazy=True))
    professional = db.relationship('Professional', back_populates='service_requests', lazy=True)
    customer = db.relationship('Customer', backref=db.backref('service_requests', lazy=True))
with app.app_context():
    db.create_all()
    if not User.query.first():  # Check if any users exist
        # Create the admin user
        admin_user = User(
            name='Admin User',  # Default name for the admin user
            user_name='admin',  # Default username for admin
            email_id='admin@example.com',  # Admin email
            password=generate_password_hash('admin_password'),  # Default hashed password for admin
            role='admin'  # Admin role
        )

        db.session.add(admin_user)
        db.session.commit()

        # Create corresponding Admin record
        admin = Admin(
            user_id=admin_user.user_id,
            admin_id=1, 
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")
if __name__ == "__main__":
    app.run(debug=True)

    
    
        