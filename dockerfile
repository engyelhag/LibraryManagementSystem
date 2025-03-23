# Use a smaller base image for efficiency
FROM python:3.9-slim  

# Set the working directory
WORKDIR /app  

# Copy application files
COPY . .  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# Expose the application port
EXPOSE 5000  

# Start the application
CMD ["python", "app.py"]  
