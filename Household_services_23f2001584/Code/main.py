from flask import Flask, jsonify, request, render_template,send_file
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Admin, Customer, Professional, Service, ServiceRequest
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from celery import Celery
from worker import celery_init_app
import logging
from celery.result import AsyncResult
import flask_excel as excel
from tasks import download_csv,daily_remainder,check_pending_service_requests,generate_and_send_monthly_report
from celery.schedules import crontab
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mailservices import send_test_email
from flask_caching import Cache
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "abcde"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config['CACHE_TYPE'] = 'simple'
db.init_app(app)
jwt = JWTManager(app)
celery_app=celery_init_app(app)
excel.init_excel(app)
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_OPTIONS': {
        'connect_timeout': 5,
        'socket_timeout': 5
    }
})

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=10, minute=46),
        check_pending_service_requests.s(),
    )
    sender.add_periodic_task(
        crontab(hour=9, minute=50, day_of_month=1),
        generate_and_send_monthly_report.s(),
    )



@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user_name = data.get('user_name')
        password = data.get('password')
        email_id = data.get('email_id')
        name = data.get('name')
        role = data.get('role')

        if not user_name or not password or not email_id or not name or not role:
            return jsonify({"msg": "Missing fields"}), 400

        hashed_password = generate_password_hash(password)

        if User.query.filter_by(email_id=email_id).first():
            return jsonify({"msg": "Email already exists"}), 400

        if User.query.filter_by(user_name=user_name).first():
            return jsonify({"msg": "Username already exists"}), 400
        
        if role not in ['admin', 'customer', 'professional']:
            return jsonify({"msg": "Invalid role"}), 400

        new_user = User(
            name=name,
            user_name=user_name,
            email_id=email_id,
            password=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        if role == 'admin':
            new_admin = Admin(user_id=new_user.user_id)
            db.session.add(new_admin)
        elif role == 'customer':
            new_customer = Customer(user_id=new_user.user_id)
            db.session.add(new_customer)
        elif role == 'professional':
            new_professional = Professional(user_id=new_user.user_id)
            db.session.add(new_professional)
        db.session.commit()

        return jsonify({"msg": "Registration successful!"}), 201
    except Exception as e:
        return jsonify({"msg": "An error occurred during registration", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
@cache.cached(timeout=50)
def login():
    try:
        data = request.get_json()
        user_name = data.get('user_name')
        password = data.get('password')

        if not user_name or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
        if user.is_blocked:
            return jsonify({"msg": "User is blocked"}), 403

        if not check_password_hash(user.password, password):
            return jsonify({"msg": "Incorrect password"}), 401

        access_token = create_access_token(identity={"user_id": user.user_id, "role": user.role})
        return jsonify({"msg": "Login successful", "access_token": access_token}), 200
    except Exception as e:
        return jsonify({"msg": "An error occurred during login", "error": str(e)}), 500
    print(f"Caching to Redis: {cache.config['CACHE_REDIS_URL']}") 

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/admin/view_users', methods=['GET'])
@cache.cached(timeout=10)
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    user = User.query.filter_by(user_id=current_user['user_id']).first()

    if user.role != 'admin':
        return jsonify({"msg": "Access forbidden: Only admins can view the user list"}), 403

    users = User.query.filter(User.role != 'admin').all()
    user_list = [{
        'user_id': u.user_id,
        'user_name': u.user_name,
        'role': u.role,
        'is_blocked': u.is_blocked
    } for u in users]
    return jsonify(user_list), 200
@app.route('/admin/approve_professionals', methods=['POST', 'GET'])
@jwt_required()
def approve_professionals():
    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access forbidden"}), 403

    if request.method == 'GET':
        # Handle GET request to list all unapproved professionals
        professionals = Professional.query.filter_by(approved=False).all()
        professional_list = [
            {
                'professional_id': pro.professional_id,
                'user': {
                    'user_name': pro.user.user_name,
                    'email_id': pro.user.email_id,
                }
            } for pro in professionals
        ]
        return jsonify(professional_list), 200

    elif request.method == 'POST':
        # Handle POST request to approve a professional
        data = request.get_json()
        if not data or 'professional_id' not in data:
            return jsonify({"msg": "Missing professional_id in request body"}), 400

        professional_id = data.get('professional_id')

        # Find the professional by ID
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"msg": "Professional not found"}), 404

        # Update the approval status
        professional.approved = True
        db.session.commit()

        return jsonify({"msg": "Professional approved successfully"}), 200
@app.route('/admin/users', methods=['GET'])
@jwt_required()
def manage_users():
    current_user = get_jwt_identity()
    print(current_user)
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access forbidden"}), 403
    
    users = User.query.filter(
        ((User.role == 'customer') | (User.role == 'professional')) & 
        (User.is_blocked == False)
    ).all()
    user_list = [
        {
            'user_id': user.user_id,
            'name': user.name,
            'user_name': user.user_name,
            'email_id': user.email_id,
            'role': user.role,
        } for user in users
    ]
    return jsonify(user_list), 200

@app.route('/admin/block_users', methods=['POST'])
@jwt_required()
def block_users():
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access forbidden"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    if user.role == 'admin':
        return jsonify({"msg": "Cannot block an admin user"}), 400
    
    user.is_blocked = True
    db.session.commit()
    return jsonify({"msg": "User blocked successfully"}), 200
@app.route('/admin/create_service', methods=['POST'])
@jwt_required()
def create_service():
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access forbidden"}), 403
    
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data or 'location' not in data or 'description' not in data:
        return jsonify({"msg": "Missing required fields"}), 400
    
    name = data['name']
    price = data['price']  # Use price as the base price
    location = data['location']
    description = data['description']
    
    new_service = Service(name=name, price=price, location=location, description=description)
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify({"msg": "Service created successfully"}), 201
@app.route('/admin/manage_services', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_services():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access forbidden"}), 403

    if request.method == 'GET':
        services = Service.query.all()
        service_list = [
            {
                'service_id': service.service_id,
                'name': service.name,
                'price': service.price,
                'location': service.location,
                'description': service.description,
            } for service in services
        ]
        return jsonify(service_list), 200

    elif request.method == 'PUT':
        data = request.get_json()
        if not data or 'service_id' not in data:
            return jsonify({"msg": "Missing service_id in request body"}), 400
        
        service_id = data['service_id']
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"msg": "Service not found"}), 404
        
        if 'name' in data:
            service.name = data['name']
        if 'price' in data:
            service.price = data['price']
        if 'location' in data:
            service.location = data['location']
        if 'description' in data:
            service.description = data['description']
        
        db.session.commit()
        return jsonify({"msg": "Service updated successfully"}), 200

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'service_id' not in data:
            return jsonify({"msg": "Missing service_id in request body"}), 400
        
        service_id = data['service_id']
        service = Service.query.get(service_id)
        if not service: 
            return jsonify({"msg": "Service not found"}), 404
        
        db.session.delete(service)
        db.session.commit()
        return jsonify({"msg": "Service deleted successfully"}), 200
@app.route('/customer/view_professionals', methods=['GET'])
@cache.cached(timeout=10)
@jwt_required()
def view_professionals():
    professionals = Professional.query.all()
    result = []
    for professional in professionals:
        professional_data = {
            'professional_id': professional.professional_id,
            'approved': professional.approved
        }
        result.append(professional_data)
    return jsonify(result)
@app.route('/customer/create_service_request', methods=['POST','GET']) 
@jwt_required()
def create_service_request():
    try:
        current_user = get_jwt_identity()
        print("Current user:", current_user)
        
        if current_user['role'] != 'customer':
            return jsonify({"msg": "Access forbidden"}), 403
        
        data = request.get_json()
        print("Request data:", data)
        if not data or 'service_id' not in data or 'professional_id' not in data or 'request_date' not in data:
            return jsonify({"msg": "Missing required fields"}), 400
        
        service_id = data['service_id']
        professional_id = data['professional_id']
        request_date = data['request_date']

        print("Service ID:", service_id)
        print("Professional ID:", professional_id) 
        print("Request Date:", request_date)
        
        # Validate the service
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"msg": "Service not found"}), 404
        
        # Validate the professional
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"msg": "Professional not found"}), 404
        
        # Validate the customer
        customer = Customer.query.filter_by(user_id=current_user['user_id']).first() 
        app.logger.info(f"Customer object fetched: {customer}")
        if not customer:
            return jsonify({"msg": "Customer not found"}), 404
        request_date = datetime.strptime(data['request_date'], '%Y-%m-%d')
        
        
        # Create a new service request
        new_request = ServiceRequest(
            service_id=service_id,
            professional_id=professional_id,
            customer_id=customer.customer_id,
            request_date=request_date,
            status='Pending'
        )
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify({
            "msg": "Service request created successfully",
            "service_request": {
                "service_id": new_request.service_id,
                "professional_id": new_request.professional_id,
                "customer_id": new_request.customer_id,
                "request_date": new_request.request_date,
                "status": new_request.status
            }
        }), 201
    except Exception as e:
        # Add detailed error logging
        app.logger.error(f"Error creating service request: {str(e)}")
        return jsonify({"msg": str(e)}), 500

  
@app.route('/customer/view_services', methods=['GET'])
@cache.cached(timeout=10)
@jwt_required()
def get_services():
    try:
        services = Service.query.all()
        service_list = [
            {
                'service_id': service.service_id,
                'name': service.name,
                'description': service.description,
                'price': service.price
         
            } for service in services
        ]
        return jsonify(service_list), 200
    except Exception as e:
        app.logger.error(f"Error in get_services: {str(e)}")
        return jsonify({"msg": f"Server error: {str(e)}"}), 500
@app.route('/customer/manage_service_requests', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_service_requests():
    try:
        current_user = get_jwt_identity()
        app.logger.info(f"Current user: {current_user}")
        
        if current_user['role'] != 'customer':
            return jsonify({"msg": "Access forbidden"}), 403

        customer = Customer.query.filter_by(user_id=current_user['user_id']).first()
        app.logger.info(f"Customer: {customer}")
        
        if not customer:
            return jsonify({"msg": "Customer not found"}), 404

        if request.method == 'GET':
            service_requests = ServiceRequest.query.filter_by(customer_id=customer.customer_id).all()
            app.logger.info(f"Service requests: {service_requests}")
            
            request_list = [
                {
                    'servicerequest_id': req.servicerequest_id,
                    'service_id': req.service_id,
                    'professional_id': req.professional_id,
                    'request_date': req.request_date.strftime('%Y-%m-%d'),
                    'status': req.status,
                    'service_name': req.service.name,
                    'professional_name': req.professional.user.name
                } for req in service_requests
            ]
            return jsonify(request_list), 200

        elif request.method == 'PUT':
            data = request.get_json()
            app.logger.info(f"PUT data: {data}")

            if not data or 'servicerequest_id' not in data:
                return jsonify({"msg": "Missing servicerequest_id"}), 422

            service_request = db.session.get(ServiceRequest, data['servicerequest_id'])
            if not service_request:
                return jsonify({"msg": "Service request not found"}), 404

            if service_request.customer_id != customer.customer_id:
                return jsonify({"msg": "Access forbidden"}), 403

            if 'service_name' in data:
                service = Service.query.filter_by(name=data['service_name']).first()
                if not service:
                    return jsonify({"msg": "Service not found"}), 404
                service_request.service_id = service.service_id

            if 'professional_name' in data:
                professional = Professional.query.join(User).filter(User.name == data['professional_name'], Professional.user_id == User.user_id).first()
                if not professional:
                    return jsonify({"msg": "Professional not found"}), 404
                service_request.professional_id = professional.professional_id

            if 'request_date' in data:
                service_request.request_date = datetime.strptime(data['request_date'], '%Y-%m-%d')
            if 'status' in data:
                service_request.status = data['status']

            db.session.commit()
            return jsonify({"msg": "Service request updated successfully"}), 200

        elif request.method == 'DELETE':
            data = request.get_json()
            print("this", data)
            app.logger.info(f"DELETE data: {data}")

            if not data or 'servicerequest_id' not in data:
                return jsonify({"msg": "Missing servicerequest_id"}), 422

            service_request = db.session.get(ServiceRequest, data['servicerequest_id'])
            if not service_request:
                return jsonify({"msg": "Service request not found"}), 404

            if service_request.customer_id != customer.customer_id:
                return jsonify({"msg": "Access forbidden"}), 403

            db.session.delete(service_request)
            db.session.commit()
            return jsonify({"msg": "Service request deleted successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error in manage_service_requests: {str(e)}")
        return jsonify({"msg": f"Server error: {str(e)}"}), 500
@app.route('/professional/view_services', methods=['GET'])
@cache.cached(timeout=10)
@jwt_required()
def get_services_prof():
    try:
        services = Service.query.all()
        service_list = [
            {
                'service_id': service.service_id,
                'name': service.name,
                'description': service.description,
                'price': service.price
         
            } for service in services
        ]
        return jsonify(service_list), 200
    except Exception as e:
        app.logger.error(f"Error in get_services: {str(e)}")
        return jsonify({"msg": f"Server error: {str(e)}"}), 500
@app.route('/professional/service_requests', methods=['GET']) 
@jwt_required()
def get_all_service_requests():
    current_user = get_jwt_identity()

    if current_user['role'] != 'professional':
        return jsonify({"msg": "Access forbidden"}), 403

    professional = Professional.query.filter_by(user_id=current_user['user_id']).first()
    if not professional:
        return jsonify({"msg": "Professional not found"}), 404

    service_requests = ServiceRequest.query.filter_by(professional_id=professional.professional_id).all()
    request_list = [
        {
            'servicerequest_id': req.servicerequest_id,
            'service_name': Service.query.get(req.service_id).name,
            'customer_name': Customer.query.get(req.customer_id).user.name,
            'request_date': req.request_date.strftime('%Y-%m-%d'),
            'status': req.status
        } for req in service_requests
    ]

    return jsonify(request_list), 200
@app.route('/professional/service_requests/update_status', methods=['POST'])
@jwt_required()
def update_service_request_status():
    try:
        current_user = get_jwt_identity()
        if (current_user['role'] != 'professional'):
            return jsonify({"msg": "Access forbidden"}), 403

        req_data = request.get_json()
        service_request_id = req_data.get('servicerequest_id')
        action = req_data.get('action')

        # Log the received data for debugging
        app.logger.info(f"Received data: servicerequest_id={service_request_id}, action={action}")

        service_request = ServiceRequest.query.filter_by(servicerequest_id=service_request_id).first()

        if not service_request:
            return jsonify({"msg": "Service request not found"}), 404

        if action == 'accept':
            service_request.status = 'Accepted'
        elif action == 'reject':
            service_request.status = 'Rejected'
        elif action == 'close':
            service_request.status = 'Closed'
        else:
            return jsonify({"msg": "Invalid action"}), 400

        db.session.commit()
        return jsonify({"msg": f"Service request {action}ed successfully"}), 200
    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error updating service request status: {e}")
        return jsonify({"msg": "Internal Server Error"}), 500
@app.route('/customer/search_services', methods=['GET'])
@jwt_required()
def search_services():
    current_user = get_jwt_identity()
    # Debugging: Print the current user's role
    print(f"Current User Role: {current_user.get('role')}")

    if current_user['role'] != 'customer':
        return jsonify({"msg": "Access forbidden"}), 403

    # Get query parameters
    name = request.args.get('name')

    query = Service.query

    if name:
        query = query.filter(Service.name.ilike(f'%{name}%'))

    services = query.all()

    service_list = [
        {
            'service_id': service.service_id,
            'name': service.name,
            'location': service.location,
            'description': service.description
        } for service in services
    ]

    return jsonify(service_list), 200
@app.route('/admin/search_professionals', methods=['GET'])
@jwt_required()
def search_professionals():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Access forbidden"}), 403

    name = request.args.get('name')
    query = Professional.query.join(User).filter(User.name.ilike(f'%{name}%'))

    professionals = query.all()

    professional_list = [
        {
            'professional_id': professional.professional_id,
            'name': professional.user.name,  # Assuming 'name' is a field in the User model
            'is_blocked': professional.approved  # Assuming 'approved' indicates blocked status
        } for professional in professionals
    ]

    return jsonify(professional_list), 200
logging.basicConfig(level=logging.INFO)
@app.get('/download-csv')
def download_csv_data():
    task=download_csv.delay()
    return jsonify({"task-id":task.id})

@app.get('/get-csv/<task_id>')
def get_csv(task_id):
    res = AsyncResult(task_id)
    if res.ready():
        filename=res.result
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({"message":"task is pending"}),404


@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')
if __name__ == "__main__":
    app.run(debug=True)


