# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the script into the container
COPY scraper.py .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Set the entrypoint
ENTRYPOINT ["python3", "scraper.py --year 2026 --month 2-4"]
