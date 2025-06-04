# backend/Dockerfile

FROM python:3.10

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install  -r requirements.txt

# Expose Flask port
EXPOSE 5004

# Run the app
CMD ["python", "app.py"]
