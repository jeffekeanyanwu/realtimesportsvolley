# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install virtualenv and create a virtual environment within the container
RUN python -m venv /app/venv

# Activate the virtual environment and install dependencies
RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Update the PATH environment variable to prioritize the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy the rest of the application code into the container
COPY . /app

# Expose port 80 for the application
EXPOSE 80

# Command to run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

