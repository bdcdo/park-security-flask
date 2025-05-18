# Python Flask application
FROM python:3.11-slim AS python-base

LABEL fly_launch_runtime="Python"

# Python environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    FLASK_ENV=production

# Python/Flask app lives here
WORKDIR /app

# Install Python dependencies first
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create output directory for CSS
RUN mkdir -p /app/static/css

# Use a separate Node.js stage to build Tailwind CSS
FROM node:slim AS css-builder

WORKDIR /build

# Copy only what's needed for CSS build
COPY package.json package-lock.json ./
COPY static/css/input.css ./static/css/input.css
COPY tailwind.config.js ./

# Install Tailwind and build CSS
RUN npm install
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css

# Final stage using Python image
FROM python-base

# Copy Python app files
COPY . .

# Copy built CSS from Node.js stage
COPY --from=css-builder /build/static/css/output.css /app/static/css/output.css

# Make port available
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]