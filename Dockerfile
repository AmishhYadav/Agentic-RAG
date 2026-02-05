# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose port 8000 for the app
EXPOSE 8000

# Define environment variable
ENV APP_ENV=production
ENV PYTHONUNBUFFERED=1

# Run app_server.py when the container launches
CMD ["python", "app_server.py"]
