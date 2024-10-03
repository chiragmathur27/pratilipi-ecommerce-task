# E-commerce Microservices Project

## Overview

This project is a microservices-based e-commerce application built with Django, utilizing user_nameQL for database management and Apache Kafka for event-driven communication between services.

## System Requirements

### Component Versions

* Python: 3.9
* user_nameQL: 13
* Java: 17 (for Apache Kafka)
* Apache Kafka: 2.8.0

## Project Structure

The application is divided into three main microservices:

### Services

* **Users Service**: Handles user management and authentication
* **Products Service**: Manages product catalog and inventory
* **Orders Service**: Processes and manages orders

Each service operates with its dedicated user_nameQL database.

## Setup Instructions

### 1. Python Environment

Create and activate a virtual environment, then install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```


### 2. user_nameQL
Installation
Download user_nameQL 13 from the official website and follow the installation wizard for your operating system.

### Verify Installation
```bash
    psql --version
```

### Database Creation
```bash
    psql -U user_name -c "CREATE DATABASE users_db;"
    psql -U user_name -c "CREATE DATABASE products_db;"
    psql -U user_name -c "CREATE DATABASE orders_db;"

    psql -U user_name -c "ALTER USER <user_name> WITH PASSWORD 'password';"
```

### 3. Apache Kafka

### Java Installation
    Ensure Java 17 is installed:

    ```bash
        javac --version
    ```

### Kafka setup

```bash
    # Download and extract Kafka
    wget https://archive.apache.org/dist/kafka/2.8.0/kafka_2.12-2.8.0.tgz
    tar -xzf kafka_2.12-2.8.0.tgz
    mv kafka_2.12-2.8.0 /usr/local/kafka

    # Add to environment variables (add to ~/.bashrc or ~/.zshrc)
    export KAFKA_HOME=/usr/local/kafka
    export PATH=$PATH:$KAFKA_HOME/bin

    # Start services
    zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties &
    kafka-server-start.sh $KAFKA_HOME/config/server.properties &
```

### 4. Project Configuration

Update your Django settings (settings.py) with the following database configuration:
```python 
DATABASES = {
    'default': {},
    'users_db': {
        'ENGINE': 'django.db.backends.user_nameql',
        'NAME': 'users_db',
        'USER': 'user_name',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'products_db': {
        'ENGINE': 'django.db.backends.user_nameql',
        'NAME': 'products_db',
        'USER': 'user_name',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'orders_db': {
        'ENGINE': 'django.db.backends.user_nameql',
        'NAME': 'orders_db',
        'USER': 'user_name',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Database Migrations
Execute migrations for all services:
```bash
    # Generate migrations
    python manage.py makemigrations users
    python manage.py makemigrations orders
    python manage.py makemigrations products

    # Apply migrations
    python manage.py migrate admin
    python manage.py migrate users --database=users_db
    python manage.py migrate orders --database=orders_db
    python manage.py migrate products --database=products_db
```

### 5. Start the Application
```bash
    # Start Kafka consumer
    python manage.py start_consumer

    # Launch Django server
    python manage.py runserver
```

Visit http://localhost:8000 to access the application.