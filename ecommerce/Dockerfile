# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the Docker container
WORKDIR /ecommerce/

# Install necessary dependencies for Kafka and PostgreSQL
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    wget \
    openjdk-17-jre-headless \  
    netcat-openbsd && \
    apt-get clean

    	
# Install Kafka
RUN wget https://archive.apache.org/dist/kafka/2.8.0/kafka_2.12-2.8.0.tgz && \
tar -xzf kafka_2.12-2.8.0.tgz && \
mv kafka_2.12-2.8.0 /usr/local/kafka
# Set environment variables for Kafka
ENV KAFKA_HOME=/usr/local/kafka
ENV PATH=$PATH:$KAFKA_HOME/bin
# Copy the requirements file into the container
COPY requirements.txt /ecommerce/


# Install Kafka
RUN wget https://archive.apache.org/dist/kafka/2.8.0/kafka_2.12-2.8.0.tgz && \
    tar -xzf kafka_2.12-2.8.0.tgz && \
    mv kafka_2.12-2.8.0 /usr/local/kafka

# Set environment variables for Kafka
ENV KAFKA_HOME=/usr/local/kafka
ENV PATH=$PATH:$KAFKA_HOME/bin

# Copy the requirements file into the container
COPY requirements.txt /ecommerce/

# Install the Python dependencies in the container
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project into the container
COPY . /ecommerce/

# Expose port 8000 for Django
EXPOSE 8000

# Expose Kafka ports
# Run Django's server
EXPOSE 9093
EXPOSE 2182
# Start Kafka, Zookeeper, and Django
CMD ["bash", "-c", "\
    /usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties & \
    /usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties & \
    python manage.py runserver 0.0.0.0:8000"]
