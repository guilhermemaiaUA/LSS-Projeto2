# =================================================================
#  Docker Image Build Configuration - LSS Project
#  This file defines the build steps for the Collector microservice.
# =================================================================

# Use an official Python runtime as the parent image
# The 'slim' variant is chosen to keep the final image lightweight and secure
FROM python:3.11-slim

# Set the working directory inside the container
# All subsequent instructions will be executed within this directory
WORKDIR /app

# Copy the dependency list from the host to the container's working directory
COPY requirements.txt .

# Install the required Python packages specified in requirements.txt
# This includes paho-mqtt for messaging and psycopg2-binary for database operations
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code script into the container image
COPY collector.py .

# Define the default command to run when the container starts
# Launches the standalone Python runtime executing the collector script
CMD ["python", "collector.py"]