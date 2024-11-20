# Use the official Python image from the Docker Hub
FROM python:3.12.3-slim
 
# Set the working directory in the container
WORKDIR /app

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \ 
    rm -rf /var/lib/apt/lists/*
 
# Copy only the requirements file to leverage Docker cache
COPY app/requirements.txt /app/requirements.txt
 
# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
 
# Copy the rest of the app code into the working directory
COPY app /app
 
# Specify the command to run on container start
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:create_app()"]
 
# Expose the port Flask runs on (default is 5000)
EXPOSE 5001