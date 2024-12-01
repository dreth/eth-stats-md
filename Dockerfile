# Use the official Python slim image
FROM python:3.13.0-slim-bookworm

# Install firefox-esr and clean up
RUN apt-get update && apt-get install -y firefox-esr && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for Selenium
ENV MOZ_HEADLESS=1

# Run the main script
CMD ["python", "main.py"]
