# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container
COPY main.py .

# Copy the .env file into the container
COPY .env .

# Run the script when the container launches
CMD ["python", "main.py"]
