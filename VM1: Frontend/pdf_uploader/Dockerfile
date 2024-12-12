FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y gcc build-essential libxml2-dev libxslt1-dev zlib1g-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages needed
# Added jinja2 for templates
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy mysql-connector-python PyPDF2 kafka-python httpx python-dotenv passlib[bcrypt] jinja2 python-multipart

# Copy all files into /app
COPY . .

# Expose the application port
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
