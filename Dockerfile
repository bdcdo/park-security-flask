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

# Create static directory
RUN mkdir -p /app/static/css

# Copy source code
COPY . .

# Install Tailwind CSS
RUN npm install
RUN npm install -g tailwindcss
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css

# Clean up npm to reduce image size
RUN rm -rf node_modules

# Make port available
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]