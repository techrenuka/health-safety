# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Install system dependencies including wkhtmltopdf and its dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure wkhtmltopdf directory has correct permissions
RUN chmod -R 755 /app/wkhtmltopdf

# Create a wrapper script for xvfb-run with wkhtmltopdf
RUN echo '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" wkhtmltopdf "$@"' > /usr/local/bin/wkhtmltopdf.sh \
    && chmod +x /usr/local/bin/wkhtmltopdf.sh

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the application
CMD ["streamlit", "run", "app.py"]
