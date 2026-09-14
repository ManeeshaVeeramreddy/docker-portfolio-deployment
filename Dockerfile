FROM python:3.12-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY source-code/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (backend + frontend)
COPY source-code/app.py .
COPY source-code/static/ static/

# Initialize the database on container start and run the app
CMD python app.py

