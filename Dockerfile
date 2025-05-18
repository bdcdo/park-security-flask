# Python Flask application using a single-stage build
FROM python:3.11-slim

LABEL fly_launch_runtime="Python"

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    FLASK_ENV=production

# Application directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Create static/css directory if it doesn't exist
RUN mkdir -p /app/static/css

# Create a simple CSS file (skipping Tailwind build)
RUN echo "/* Simplified CSS file */" > /app/static/css/output.css

# Make port available
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]