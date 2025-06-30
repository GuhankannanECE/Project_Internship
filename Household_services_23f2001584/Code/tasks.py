from celery import shared_task
from models import User
import flask_excel as excel
from mailservices import send_test_email 
from datetime import datetime,timedelta
from models import db, Professional, ServiceRequest,Customer
import logging
logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def download_csv():
    servicereq_dow=ServiceRequest.query.with_entities(ServiceRequest.servicerequest_id, ServiceRequest.service_id, ServiceRequest.professional_id,ServiceRequest.customer_id,ServiceRequest.status).all()

    users_csv=excel.make_response_from_query_sets(servicereq_dow, ["servicerequest_id","service_id","professional_id","customer_id","status"],"csv",filename="test1.csv")
    filename="test.csv"

    with open(filename, 'wb') as f:
        f.write(users_csv.data)
    return filename
@shared_task(ignore_result=False)
def daily_remainder(to, subject): 
    send_test_email(to,subject, 'hello')
    return "OK"

@shared_task(ignore_result=False)
def check_pending_service_requests():
    print("Starting task to send emails to professionals with pending service requests")
    
    # Get all professionals
    all_professionals = Professional.query.all()
    print(f"Total Professionals Count: {len(all_professionals)}")
    
    # Debug: Print details for each professional
    for professional in all_professionals:
        print(f"Professional: {professional.user.name}")
        print(f"Service Requests: {[req.status for req in professional.service_requests]}")
    
    # Filter professionals with pending service requests
    professionals_with_pending = [
        professional for professional in all_professionals
        if any(request.status == 'Pending' for request in professional.service_requests)
    ]
    print(f"Professionals with Pending Requests: {len(professionals_with_pending)}")
    
    # Send email alerts to professionals with pending requests
    for professional in professionals_with_pending:
        try:
            pending_requests = [req for req in professional.service_requests if req.status == 'Pending']
            subject = "Pending Service Requests Alert"
            body = f"""<html><body>
            Dear {professional.user.name},<br><br>
            You have {len(pending_requests)} pending service request(s). Please log in to your account to review and respond to these requests.<br><br>
            Pending Service Requests:<br>
            """
            for request in pending_requests:
                body += f"- Request ID: {request.servicerequest_id}<br>"
            body += "<br>Best Regards,<br>Service Team</body></html>"
            
            send_test_email(professional.user.email_id, subject, body)
            print(f"Email sent to: {professional.user.email_id}")
            print(f"Pending Service Requests for {professional.user.name}:")
            for request in pending_requests:
                print(f"- Request ID: {request.servicerequest_id}, Status: {request.status}")
        except Exception as e:
            print(f"Email send error for {professional.user.email_id}: {e}")
    
    return f"Task completed. Emails sent to {len(professionals_with_pending)} professionals with pending requests."
@shared_task(ignore_result=False)
def generate_and_send_monthly_report():
    print("generate_and_send_monthly_report task started")
    
    # Get the first and last day of the previous month
    today = datetime.today()
    print(f"Today's date: {today}")
    first_day_of_month = today.replace(day=1)
    print(f"First day of the current month: {first_day_of_month}")
    last_day_of_previous_month = first_day_of_month - timedelta(days=1)
    print(f"Last day of the previous month: {last_day_of_previous_month}")
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    print(f"First day of the previous month: {first_day_of_previous_month}")

    # Fetch data for the previous month
    service_requests = ServiceRequest.query.filter(
        ServiceRequest.request_date >= first_day_of_previous_month,
        ServiceRequest.request_date <= last_day_of_previous_month
    ).all()
    print(f"Fetched service requests: {service_requests}")

    # Group data by customer
    customer_data = {}
    for request in service_requests:
        customer_id = request.customer_id
        if customer_id not in customer_data:
            customer_data[customer_id] = {
                'name': request.customer.user.name,
                'total_requests': 0,
                'pending_requests': 0
            }
        customer_data[customer_id]['total_requests'] += 1
        if request.status == 'Pending':
            customer_data[customer_id]['pending_requests'] += 1
    print(f"Grouped customer data: {customer_data}")

    # Generate and send simple HTML report
    for customer_id, data in customer_data.items():
        html_content = generate_simple_html_report(data)
        customer_email = Customer.query.get(customer_id).user.email_id
        print(f"Sending email to {customer_email} with content: {html_content}")
        send_test_email(customer_email, "Monthly Activity Report", html_content)

    print("Monthly reports sent successfully.")
    return "Monthly reports sent successfully."

def generate_simple_html_report(data):
    # Generate simple HTML content
    html_content = f"""
    <html>
    <body>
        <h1>Monthly Activity Report for {data['name']}</h1>
        <p>Total Number of Service Requests: {data['total_requests']}</p>
        <p>Number of Pending Requests: {data['pending_requests']}</p>
    </body>
    </html>
    """
    return html_content