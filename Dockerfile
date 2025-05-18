# syntax = docker/dockerfile:1
FROM python:3.11-slim

LABEL fly_launch_runtime="Python"

# Set production environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    FLASK_ENV=production

# Python/Flask app lives here
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Node.js for Tailwind CSS processing
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y nodejs npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create static directory and copy CSS files first
RUN mkdir -p /app/static/css

# Copy package files for Tailwind
COPY package.json package-lock.json ./
COPY static/css/input.css /app/static/css/

# Install Tailwind CSS globally
RUN npm install
RUN npm install -g tailwindcss@4.1.3

# Build CSS with Tailwind CLI
RUN npx tailwindcss@4.1.3 -i /app/static/css/input.css -o /app/static/css/output.css

# Copy the rest of the application code
COPY . .

# Clean up npm to reduce image size
RUN rm -rf node_modules

# Make port available
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]