# ALX Travel App 0x03

## Background Task Management

This project uses **Celery** with **RabbitMQ** to handle background tasks and send email notifications for bookings.

### Setup Celery

1. Install dependencies:
pip install celery django-celery-beat

2. Ensure RabbitMQ is installed and running:
sudo systemctl start rabbitmq-server

3. Start Celery worker:
celery -A alx_travel_app worker --loglevel=info
