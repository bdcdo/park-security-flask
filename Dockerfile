# syntax = docker/dockerfile:1

# Python version
FROM python:3.11-slim

LABEL fly_launch_runtime="Python"

# Python/Flask app lives here
WORKDIR /app

# Set production environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Node.js for Tailwind CSS
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y nodejs npm

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Node dependencies and build CSS
COPY package.json package-lock.json ./
RUN npm ci
COPY static/css/input.css ./static/css/
RUN npm run build:css

# Copy application code
COPY . .

# Start the server by default, this can be overwritten at runtime
EXPOSE 8080
ENV PORT=8080

# Run the application
CMD ["python", "app.py"]