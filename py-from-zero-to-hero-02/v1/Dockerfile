# Use official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flask runs on
EXPOSE 80

# Use environment variables for configuration
ENV APP_SECRET_KEY=super_secure_random_key_123
ENV APP_DB_URL=sqlite:///dev_users.db
ENV APP_ENV=development
ENV APP_PORT=80

# Run the application using waitress (production-ready)
CMD ["python", "-m", "waitress", "--port=80", "app:app"]
