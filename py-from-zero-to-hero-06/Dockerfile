# Use official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flask runs on
EXPOSE 80

# Run the application using waitress (production-ready)
CMD ["python", "-m", "waitress", "--port=80", "src.app:app"]
