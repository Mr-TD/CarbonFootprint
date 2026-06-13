FROM python:3.11-slim

WORKDIR /app

# Create a user to run the app (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user

# Install required packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Set ownership to the non-root user so the app can create and write to carboncredit.db
RUN chown -R user:user /app

# Switch to the non-root user
USER user

# Expose port 7860 which is the default for Hugging Face Spaces
EXPOSE 7860

# Use run:app (the create_app factory is invoked in run.py)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "120", "run:app"]