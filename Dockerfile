# mini-gen/frontend-service/Dockerfile
FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .


# Expose Flask default port
EXPOSE 5000

# Run the app
ENV FLASK_ENV=production
CMD ["python", "app.py"]
